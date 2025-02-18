# Copyright (C) 2016 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for launching MAPDL locally or connecting to a remote instance with gRPC."""

import atexit
from functools import wraps
import os
import platform
from queue import Empty, Queue
import re
import socket

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
import subprocess  # nosec B404
import threading
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
import warnings

import psutil

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import _HAS_ATP, _HAS_PIM, LOG
from ansys.mapdl.core._version import SUPPORTED_ANSYS_VERSIONS
from ansys.mapdl.core.errors import (
    LockFileException,
    MapdlDidNotStart,
    NotEnoughResources,
    PortAlreadyInUse,
    PortAlreadyInUseByAnMAPDLInstance,
    VersionError,
)
from ansys.mapdl.core.licensing import ALLOWABLE_LICENSES, LicenseChecker
from ansys.mapdl.core.mapdl_core import _ALLOWED_START_PARM
from ansys.mapdl.core.mapdl_grpc import MAX_MESSAGE_LENGTH, MapdlGrpc
from ansys.mapdl.core.misc import (
    check_valid_ip,
    check_valid_port,
    create_temp_dir,
    threaded,
)

if _HAS_PIM:
    import ansys.platform.instancemanagement as pypim

if _HAS_ATP:
    from ansys.tools.path import find_mapdl, get_mapdl_path
    from ansys.tools.path import version_from_path as _version_from_path

    @wraps(_version_from_path)
    def version_from_path(*args, **kwargs):
        """Wrap ansys.tool.path.version_from_path to raise a warning if the
        executable couldn't be found"""
        if kwargs.pop("launch_on_hpc", False):
            try:
                return _version_from_path(*args, **kwargs)
            except RuntimeError:
                warnings.warn("PyMAPDL could not find the ANSYS executable. ")
        else:
            return _version_from_path(*args, **kwargs)


if TYPE_CHECKING:  # pragma: no cover
    from ansys.mapdl.core.mapdl_console import MapdlConsole

# settings directory
SETTINGS_DIR = pymapdl.USER_DATA_PATH
if not os.path.isdir(SETTINGS_DIR):
    try:
        os.makedirs(SETTINGS_DIR)
        LOG.debug(f"Created settings directory: {SETTINGS_DIR}")
    except:
        warnings.warn(
            "Unable to create settings directory.\n"
            "Will be unable to cache MAPDL executable location"
        )

CONFIG_FILE = os.path.join(SETTINGS_DIR, "config.txt")
ALLOWABLE_MODES = ["console", "grpc"]
ALLOWABLE_VERSION_INT = tuple(SUPPORTED_ANSYS_VERSIONS.keys())

ALLOWABLE_LAUNCH_MAPDL_ARGS = [
    "add_env_vars",
    "additional_switches",
    "cleanup_on_exit",
    "clear_on_connect",
    "exec_file",
    "force_intel",
    "ip",
    "jobname",
    "launch_on_hpc",
    "license_server_check",
    "license_type",
    "log_apdl",
    "loglevel",
    "mapdl_output",
    "mode",
    "nproc",
    "override",
    "port",
    "print_com",
    "ram",
    "remove_temp_dir_on_exit",
    "replace_env_vars",
    "run_location",
    "running_on_hpc",
    "scheduler_options",
    "set_no_abort",
    "start_instance",
    "start_timeout",
    "version",
    # Non documented args
    "_debug_no_launch",
    "just_launch",
    "on_pool",
    "use_vtk",
]

ON_WSL = os.name == "posix" and (
    os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP")
)

if ON_WSL:
    LOG.info("On WSL: Running on WSL detected.")
    LOG.debug("On WSL: Allowing 'start_instance' and 'ip' arguments together.")

LOCALHOST = "127.0.0.1"
MAPDL_DEFAULT_PORT = 50052

INTEL_MSG = """Due to incompatibilities between this MAPDL version, Windows, and VPN connections,
the flat '-mpi INTELMPI' is overwritten by '-mpi msmpi'.

If you still want to use 'INTEL', set:

launch_mapdl(..., force_intel=True, additional_switches='-mpi INTELMPI')

Be aware of possible errors or unexpected behavior with this configuration.
"""

LAUNCH_ON_HCP_ERROR_MESSAGE_IP = (
    "PyMAPDL cannot ensure a specific IP will be used when launching "
    "MAPDL on a cluster. Hence the 'ip' argument is not compatible. "
    "If you want to connect to an already started MAPDL instance, "
    "just connect normally as you would with a remote instance. "
    "For example:\n\n"
    ">>> mapdl = launch_mapdl(start_instance=False, ip='123.45.67.89')\n\n"
    "where '123.45.67.89' is the IP of the machine where MAPDL is running."
)
GALLERY_INSTANCE = [None]


def _cleanup_gallery_instance() -> None:  # pragma: no cover
    """This cleans up any left over instances of MAPDL from building the gallery."""
    if GALLERY_INSTANCE[0] is not None:
        mapdl = MapdlGrpc(
            ip=GALLERY_INSTANCE[0]["ip"],
            port=GALLERY_INSTANCE[0]["port"],
        )
        mapdl.exit(force=True)


atexit.register(_cleanup_gallery_instance)


def _is_ubuntu() -> bool:
    """Determine if running as Ubuntu.

    It's a bit complicated because sometimes the distribution is
    Ubuntu, but the kernel has been recompiled and no longer has the
    word "ubuntu" in it.

    """

    # must be running linux for this to be True
    if os.name != "posix":
        return False

    # args value is controlled by the library.
    # awk is not a partial path - Bandit false positive.
    # Excluding bandit check.
    proc = submitter(["awk", "-F=", "/^NAME/{print $2}", "/etc/os-release"])

    if "ubuntu" in proc.stdout.read().decode().lower():
        return True

    # try lsb_release as this is more reliable, but not always available.
    try:
        import lsb_release

        if lsb_release.get_distro_information()["ID"].lower() == "ubuntu":
            return True
    except ImportError:
        # finally, check platform
        return "ubuntu" in platform.platform().lower()


def close_all_local_instances(port_range: range = None) -> None:
    """Close all MAPDL instances within a port_range.

    This function can be used when cleaning up from a failed pool or
    batch run.

    Parameters
    ----------
    port_range : list, optional
        Defaults to ``range(50000, 50200)``.  Expand this range if
        there are many potential instances of MAPDL in gRPC mode.

    Examples
    --------
    Close all instances on in the range of 50000 and 50199.

    >>> import ansys.mapdl.core as pymapdl
    >>> pymapdl.close_all_local_instances()

    """
    if port_range is None:
        port_range = range(50000, 50200)

    @threaded
    def close_mapdl(port: Union[int, str], name: str = "Closing mapdl thread."):
        # Name argument is used by the threaded decorator.
        try:
            mapdl = MapdlGrpc(port=port, set_no_abort=False)
            mapdl.exit()
        except OSError:
            pass

    ports = check_ports(port_range)
    for port, state in ports.items():
        if state:
            close_mapdl(port)


def check_ports(port_range: range, ip: str = "localhost") -> List[int]:
    """Check the state of ports in a port range"""
    ports = {}
    for port in port_range:
        ports[port] = port_in_use(port, ip)
    return ports


def port_in_use(port: Union[int, str], host: str = LOCALHOST) -> bool:
    """Returns True when a port is in use at the given host.

    Must actually "bind" the address.  Just checking if we can create
    a socket is insufficient as it's possible to run into permission
    errors like:

    - An attempt was made to access a socket in a way forbidden by its
      access permissions.
    """
    return port_in_use_using_socket(port, host) or port_in_use_using_psutil(port)


def port_in_use_using_socket(port: Union[int, str], host: str) -> bool:
    """Returns True when a port is in use at the given host using socket library.

    Must actually "bind" the address.  Just checking if we can create
    a socket is insufficient as it's possible to run into permission
    errors like:

    - An attempt was made to access a socket in a way forbidden by its
      access permissions.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return False
        except:
            return True


def is_ansys_process(proc: psutil.Process) -> bool:
    """Check if the given process is an Ansys MAPDL process"""
    return (
        bool(proc)
        and proc.name().lower().startswith(("ansys", "mapdl"))
        and "-grpc" in proc.cmdline()
    )


def get_process_at_port(port) -> Optional[psutil.Process]:
    """Get the process (psutil.Process) running at the given port"""
    for proc in psutil.process_iter():
        try:
            # just to check if we can access the port
            connections = proc.connections()
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:
            # process already died
            continue

        for conns in connections:
            if conns.laddr.port == port:
                return proc

    return None


def port_in_use_using_psutil(port: Union[int, str]) -> bool:
    """Returns True when a port is in use at the given host using psutil.

    This function iterate over all the process, and their connections until
    it finds one using the given port.
    """
    if get_process_at_port(port):
        return True
    else:
        return False


def generate_mapdl_launch_command(
    exec_file: str = "",
    jobname: str = "file",
    nproc: int = 2,
    ram: Optional[int] = None,
    port: int = MAPDL_DEFAULT_PORT,
    additional_switches: str = "",
    launch_on_hpc=False,
) -> list[str]:
    """Generate the command line to start MAPDL in gRPC mode.

    Parameters
    ----------
    exec_file : str, optional
        The location of the MAPDL executable.  Will use the cached
        location when left at the default :class:`None`.

    jobname : str, optional
        MAPDL jobname.  Defaults to ``'file'``.

    nproc : int, optional
        Number of processors.  Defaults to 2.

    ram : float, optional
        Total size in megabytes of the workspace (memory) used for the initial allocation.
        The default is :class:`None`, in which case 2 GB (2048 MB) is used. To force a fixed size
        throughout the run, specify a negative number.

    port : int
        Port to launch MAPDL gRPC on.  Final port will be the first
        port available after (or including) this port.

    additional_switches : str, optional
        Additional switches for MAPDL, for example ``"-p aa_r"``, the
        academic research license, would be added with:

        - ``additional_switches="-p aa_r"``

        Avoid adding switches like ``"-i"`` ``"-o"`` or ``"-b"`` as
        these are already included to start up the MAPDL server.  See
        the notes section for additional details.


    Returns
    -------
    list[str]
        Command

    """
    cpu_sw = "-np %d" % nproc

    if ram:
        ram_sw = "-m %d" % int(ram)
        LOG.debug(f"Setting RAM: {ram_sw} MB")
    else:
        ram_sw = ""

    job_sw = "-j %s" % jobname
    port_sw = "-port %d" % port
    grpc_sw = "-grpc"

    # Windows will spawn a new window, special treatment
    if os.name == "nt" and not launch_on_hpc:
        exec_file = f"{exec_file}"
        # must start in batch mode on windows to hide APDL window
        tmp_inp = ".__tmp__.inp"
        command_parm = [
            job_sw,
            cpu_sw,
            ram_sw,
            "-b",
            "-i",
            tmp_inp,
            "-o",
            ".__tmp__.out",
            additional_switches,
            port_sw,
            grpc_sw,
        ]

    else:  # linux
        command_parm = [
            job_sw,
            cpu_sw,
            ram_sw,
            additional_switches,
            port_sw,
            grpc_sw,
        ]

    command_parm = [
        each for each in command_parm if each.strip()
    ]  # cleaning empty args.

    # removing spaces in cells
    command_parm = " ".join(command_parm).split(" ")
    command_parm.insert(0, f"{exec_file}")

    LOG.debug(f"Generated command: {' '.join(command_parm)}")
    return command_parm


def launch_grpc(
    cmd: list[str],
    run_location: str = None,
    env_vars: Optional[Dict[str, str]] = None,
    launch_on_hpc: bool = False,
    mapdl_output: Optional[str] = None,
    ssh_session=None,
) -> subprocess.Popen:
    """Start MAPDL locally in gRPC mode.

    Parameters
    ----------
    cmd : str
        Command to use to launch the MAPDL instance.

    run_location : str, optional
        MAPDL working directory.  The default is the temporary working
        directory.

    env_vars : dict, optional
        Dictionary with the environment variables to inject in the process.

    launch_on_hpc : bool, optional
        If running on an HPC, this needs to be :class:`True` to avoid the
        temporary file creation on Windows.

    mapdl_output : str, optional
        Whether redirect MAPDL console output (stdout and stderr) to a file.

    Returns
    -------
    subprocess.Popen
        Process object
    """
    if env_vars is None:
        env_vars = {}

    # disable all MAPDL pop-up errors:
    env_vars.setdefault("ANS_CMD_NODIAG", "TRUE")

    cmd_string = " ".join(cmd)
    if "sbatch" in cmd:
        header = "Running an MAPDL instance on the Cluster:"
        shell = os.name != "nt"
        cmd_ = cmd_string
    else:
        header = "Running an MAPDL instance"
        shell = False  # To prevent shell injection
        cmd_ = cmd

    LOG.info(
        "\n============"
        "\n============\n"
        f"{header}\nLocation:\n{run_location}\n"
        f"Command:\n{cmd_string}\n"
        f"Env vars:\n{env_vars}"
        "\n============"
        "\n============"
    )

    if mapdl_output:
        stdout = open(str(mapdl_output), "wb", 0)
        stderr = subprocess.STDOUT
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    if os.name == "nt":
        # getting tmp file name
        if not launch_on_hpc:
            # if we are running on an HPC cluster (case not considered), we will
            # have to upload/create this file because it is needed for starting.
            tmp_inp = cmd[cmd.index("-i") + 1]
            with open(os.path.join(run_location, tmp_inp), "w") as f:
                f.write("FINISH\r\n")
                LOG.debug(
                    f"Writing temporary input file: {tmp_inp} with 'FINISH' command."
                )

    LOG.debug("MAPDL starting in background.")
    return submitter(
        cmd_,
        shell=shell,  # sbatch does not work without shell.
        cwd=run_location,
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=stderr,
        env_vars=env_vars,
        ssh_session=ssh_session,
    )  # nosec B604


def check_mapdl_launch(
    process: subprocess.Popen, run_location: str, timeout: int, cmd: str
) -> None:
    """Check MAPDL launching process.

    Check several things to confirm MAPDL has been launched:

    * MAPDL process:
      Check process is alive still.
    * File error:
      Check if error file has been created.
    * [On linux, but not WSL] Check if server is alive.
      Read stdout looking for 'Server listening on' string.

    Parameters
    ----------
    process : subprocess.Popen
        MAPDL process object coming from 'launch_grpc'
    run_location : str
        MAPDL path.
    timeout : int
        Timeout
    cmd : str
        Command line used to launch MAPDL. Just for error printing.

    Raises
    ------
    MapdlDidNotStart
        MAPDL did not start.
    """
    LOG.debug("Generating queue object for stdout")
    stdout_queue, thread = _create_queue_for_std(process.stdout)

    # Checking connection
    try:
        LOG.debug("Checking process is alive")
        _check_process_is_alive(process, run_location)

        LOG.debug("Checking file error is created")
        _check_file_error_created(run_location, timeout)

        if os.name == "posix" and not ON_WSL:
            LOG.debug("Checking if gRPC server is alive.")
            _check_server_is_alive(stdout_queue, timeout)

    except MapdlDidNotStart as e:  # pragma: no cover
        msg = (
            str(e)
            + f"\nRun location: {run_location}"
            + f"\nCommand line used: {' '.join(cmd)}\n\n"
        )

        terminal_output = "\n".join(_get_std_output(std_queue=stdout_queue)).strip()
        if terminal_output.strip():
            msg = msg + "The full terminal output is:\n\n" + terminal_output

        raise MapdlDidNotStart(msg) from e


def _check_process_is_alive(process, run_location):
    if process.poll() is not None:  # pragma: no cover
        msg = f"MAPDL process died."
        raise MapdlDidNotStart(msg)


def _check_file_error_created(run_location, timeout):
    # watch for the creation of temporary files at the run_directory.
    # This lets us know that the MAPDL process has at least started
    sleep_time = 0.1
    for _ in range(int(timeout / sleep_time)):
        # check if any error files have been created.  This is
        # more reliable than using the lock file

        files = os.listdir(run_location)
        has_ans = any([filename for filename in files if ".err" in filename])
        if has_ans:
            LOG.debug("MAPDL session successfully started (Error file found)")
            break
        time.sleep(sleep_time)

    if not has_ans:
        msg = f"MAPDL failed to start.\nNo error file (.err) generated in working directory."
        raise MapdlDidNotStart(msg)


def _check_server_is_alive(stdout_queue, timeout):
    if not stdout_queue:
        LOG.debug("No STDOUT queue. Not checking MAPDL this way.")
        return

    t0 = time.time()
    empty_attemps = 3
    empty_i = 0
    terminal_output = ""

    LOG.debug(f"Checking if MAPDL server is alive")
    while time.time() < (t0 + timeout):
        terminal_output += "\n".join(_get_std_output(std_queue=stdout_queue)).strip()

        if not terminal_output and empty_i < empty_attemps:
            # For stability reasons.
            empty_i += 1
            time.sleep(0.1)
            continue

        if (
            "START GRPC SERVER" in terminal_output
            and "Server listening on" in terminal_output
        ):
            listening_on = terminal_output.splitlines()[-1].split(":")
            listening_on = ":".join(listening_on[1:]).strip()
            LOG.debug(f"MAPDL gRPC server successfully launched at: {listening_on}")
            break

    else:
        LOG.debug(
            f"MAPDL gRPC server didn't print any valid output:\n{terminal_output}"
        )
        raise MapdlDidNotStart("MAPDL failed to start the gRPC server")


def _get_std_output(std_queue, timeout=1):
    if not std_queue:
        return [None]

    lines = []
    reach_empty = False
    t0 = time.time()
    while (not reach_empty) or (time.time() < (t0 + timeout)):
        try:
            message = std_queue.get_nowait().decode(encoding="utf-8", errors="replace")
            lines.append(message)
        except Empty:
            reach_empty = True

    return lines


def _create_queue_for_std(
    std: subprocess.PIPE,
) -> Tuple[Optional[Queue[str]], Optional[threading.Thread]]:
    """Create a queue and thread objects for a given PIPE std"""
    if not std:
        LOG.debug("No STDOUT. Not checking MAPDL this way.")
        return None, None

    def enqueue_output(out: subprocess.PIPE, queue: Queue[str]) -> None:
        try:
            for line in iter(out.readline, b""):
                queue.put(line)
            out.close()
        except ValueError:
            # When killing main process, a ValueError is show:
            # ValueError: PyMemoryView_FromBuffer(): info -> buf must not be NULL
            pass

    q: Queue[str] = Queue()
    t: threading.Thread = threading.Thread(target=enqueue_output, args=(std, q))
    t.daemon = True  # thread dies with the program
    t.start()

    return q, t


def launch_remote_mapdl(
    version: Optional[str] = None,
    cleanup_on_exit: bool = True,
) -> MapdlGrpc:
    """Start MAPDL remotely using the product instance management API.

    When calling this method, you need to ensure that you are in an environment where PyPIM is configured.
    This can be verified with :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`.

    Parameters
    ----------
    version : str, optional
        The MAPDL version to run, in the 3 digits format, such as "212".

        If unspecified, the version will be chosen by the server.

    cleanup_on_exit : bool, optional
        Exit MAPDL when python exits or the mapdl Python instance is
        garbage collected.

        If unspecified, it will be cleaned up.

    Returns
    -------
    ansys.mapdl.core.mapdl.MapdlBase
        An instance of Mapdl.
    """
    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    pim = pypim.connect()
    instance = pim.create_instance(product_name="mapdl", product_version=version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )
    return MapdlGrpc(
        channel=channel,
        cleanup_on_exit=cleanup_on_exit,
        remote_instance=instance,
    )


def get_start_instance(start_instance: Optional[Union[bool, str]] = None) -> bool:
    """Check if the environment variable ``PYMAPDL_START_INSTANCE`` exists and is valid.

    Parameters
    ----------
    start_instance : bool
        Value to return when ``PYMAPDL_START_INSTANCE`` is unset.

    Returns
    -------
    bool
        :class:`True` when the ``PYMAPDL_START_INSTANCE`` environment variable is
        true, :class:`False` when PYMAPDL_START_INSTANCE is false. If unset,
        returns ``start_instance``.

    Raises
    ------
    OSError
        Raised when ``PYMAPDL_START_INSTANCE`` is not either true or false
        (case independent).

    Notes
    -----
    If the environment variable ``PYMAPDL_START_INSTANCE`` is set,
    hence the argument ``start_instance`` is overwritten.

    """

    def valid_start_instance(start_instance: str) -> bool:
        return start_instance.lower().strip() in ["true", "false"]

    if start_instance and os.environ.get("PYMAPDL_START_INSTANCE"):
        warnings.warn(
            "The environment variable 'PYMAPDL_START_INSTANCE' is "
            "ignored because 'start_instance' argument is given."
        )

    if isinstance(start_instance, bool):
        return start_instance

    elif start_instance is None or isinstance(start_instance, str):
        if start_instance is None:
            if os.environ.get("PYMAPDL_START_INSTANCE"):
                start_instance = os.environ.get("PYMAPDL_START_INSTANCE", "")
                if not valid_start_instance(start_instance):
                    raise OSError(
                        f'Invalid value "{start_instance}" for "start_instance" (or "PYMAPDL_START_INSTANCE"\n'
                        '"start_instance" should be either "TRUE" or "FALSE"'
                    )
            else:
                LOG.debug(
                    "'PYMAPDL_START_INSTANCE' is unset, and there is no supplied value. Using default, which is 'True'."
                )
                return True  # Default is true

        if not valid_start_instance(start_instance):
            raise ValueError(
                f"The value given for 'start_instance' ({start_instance}) is invalid."
            )

        return start_instance.lower().strip() == "true"

    else:
        raise ValueError("Only booleans are allowed as arguments.")


def get_default_ansys():
    """Searches for ansys path within the standard install location
    and returns the path and version of the latest MAPDL version installed.

    Returns
    -------
    ansys_path : str
        Full path to ANSYS executable.

    version : float
        Version float.  For example, 21.1 corresponds to 2021R1.

    Examples
    --------
    Within Windows

    >>> from ansys.mapdl.core.launcher import get_default_ansys
    >>> get_default_ansys()
    'C:/Program Files/ANSYS Inc/v211/ANSYS/bin/winx64/ansys211.exe', 21.1

    Within Linux

    >>> get_default_ansys()
    (/usr/ansys_inc/v211/ansys/bin/ansys211, 21.1)
    """
    return find_mapdl(supported_versions=SUPPORTED_ANSYS_VERSIONS)


def get_default_ansys_path():
    """Searches for ansys path within the standard install location
    and returns the path of the latest MAPDL version installed.

    Returns
    -------
    str
        Full path to ANSYS executable.

    Examples
    --------
    Within Windows

    >>> from ansys.mapdl.core.launcher import get_default_ansys
    >>> get_default_ansys_path()
    'C:/Program Files/ANSYS Inc/v211/ANSYS/bin/winx64/ansys211.exe'

    Within Linux

    >>> get_default_ansys_path()
    '/usr/ansys_inc/v211/ansys/bin/ansys211'
    """
    return get_default_ansys()[0]


def get_default_ansys_version():
    """Searches for ansys path within the standard install location
    and returns the version of the latest MAPDL version installed.

    Returns
    -------
    float
        Version float.  For example, 21.1 corresponds to 2021R1.

    Examples
    --------
    Within Windows

    >>> from ansys.mapdl.core.launcher import get_default_ansys
    >>> get_default_ansys_version()
    21.1

    Within Linux

    >>> get_default_ansys_version()
    21.1
    """
    return get_default_ansys()[1]


def check_valid_ansys():
    """Checks if a valid version of ANSYS is installed and preconfigured"""
    ansys_bin = get_mapdl_path(allow_input=False)
    if ansys_bin is not None:
        version = version_from_path("mapdl", ansys_bin)
        return not (version < 170 and os.name != "posix")
    return False


def check_lock_file(path, jobname, override):
    LOG.debug("Checking for lock file")
    # Check for lock file
    lockfile = os.path.join(path, jobname + ".lock")
    if os.path.isfile(lockfile):
        if not override:
            raise LockFileException(
                '\nLock file exists for jobname "%s"' % jobname
                + ' at\n"%s"\n\n' % lockfile
                + "Set ``override=True`` to or delete the lock file "
                "to start MAPDL"
            )
        else:
            try:
                os.remove(lockfile)
                LOG.debug("Removed lock file")
            except PermissionError:
                raise LockFileException(
                    "Unable to remove lock file.  "
                    "Another instance of MAPDL might be "
                    f"running at '{path}'"
                )


def set_MPI_additional_switches(
    add_sw: str, force_intel: bool = False, version: Optional[int] = None
) -> str:
    """Validate MPI configuration.

    Enforce Microsoft MPI in version 21.0 or later, to fix a
    VPN issue on Windows.

    Parameters
    ----------
    add_sw : str
        Additional switches.
    force_intel : bool, optional
        Force the usage of intelmpi. The default is :class:`False`.
    version: int, optional
        MAPDL version as integer

    Returns
    -------
    str
        Validated additional switches.

    """
    # Converting additional_switches to lower case to avoid mismatches.
    add_sw_lower_case = add_sw.lower()

    # known issues with distributed memory parallel (DMP)
    if os.name == "nt" and "smp" not in add_sw_lower_case:  # pragma: no cover
        if _HAS_ATP:
            condition = not force_intel and version and (222 > version >= 210)
        else:
            warnings.warn(
                "Because 'ansys-tools-path' is not installed, PyMAPDL cannot check\n"
                "if this Ansys version requires the MPI fix, so if you are on Windows,\n"
                "the fix is applied by default.\n"
                "Use 'force_intel=True' to not apply the fix."
            )

            condition = not force_intel

        if condition:
            # Workaround to fix a problem when launching ansys in 'dmp' mode in the
            # recent windows version and using VPN.
            # This is due to the intel compiler, and only affects versions between
            # 210 and 222.
            #
            # There doesn't appear to be an easy way to check if we
            # are running VPN in Windows in python, it seems we will
            # need to know a local address where to ping but that will
            # change for each client/person using the VPN.
            #
            # Adding '-mpi msmpi' to the launch parameter fix it.
            if "intelmpi" in add_sw_lower_case:
                LOG.debug(
                    "Intel MPI flag detected. Removing it, if you want to enforce it, use ``force_intel`` keyword argument."
                )
                # Remove intel flag.
                regex = "(-mpi)( *?)(intelmpi)"
                add_sw = re.sub(regex, "", add_sw, flags=re.IGNORECASE)
                warnings.warn(INTEL_MSG)

            LOG.debug("Forcing Microsoft MPI (MSMPI) to avoid VPN issues.")
            add_sw += " -mpi msmpi"

    return add_sw


def configure_ubuntu(envvars: Dict[str, Any]):
    # Ubuntu ANSYS fails to launch without I_MPI_SHM_LMT
    if _is_ubuntu():
        LOG.debug("Ubuntu system detected. Adding 'I_MPI_SHM_LMT' env var.")
        envvars["I_MPI_SHM_LMT"] = "shm"

    return envvars


def force_smp_in_student(add_sw, exec_path):
    """Force SMP in student version.

    Parameters
    ----------
    add_sw : str
        Additional switches.
    exec_path : str
        Path to the MAPDL executable.

    Returns
    -------
    str
        Validated additional switches.

    """
    # Converting additional_switches to lower case to avoid mismatches.
    add_sw_lower_case = add_sw.lower()

    if (
        "-mpi" not in add_sw_lower_case
        and "-dmp" not in add_sw_lower_case
        and "-smp" not in add_sw_lower_case
    ):  # pragma: no cover
        if "student" in exec_path.lower():
            add_sw += " -smp"
            LOG.debug("Student version detected, using '-smp' switch by default.")
    return add_sw


def launch_mapdl(
    exec_file: Optional[str] = None,
    run_location: Optional[str] = None,
    jobname: str = "file",
    *,
    nproc: Optional[int] = None,
    ram: Optional[Union[int, str]] = None,
    mode: Optional[str] = None,
    override: bool = False,
    loglevel: str = "ERROR",
    additional_switches: str = "",
    start_timeout: Optional[int] = None,
    port: Optional[int] = None,
    cleanup_on_exit: bool = True,
    start_instance: Optional[bool] = None,
    ip: Optional[str] = None,
    clear_on_connect: bool = True,
    log_apdl: Optional[Union[bool, str]] = None,
    remove_temp_dir_on_exit: bool = False,
    license_server_check: bool = False,
    license_type: Optional[bool] = None,
    print_com: bool = False,
    add_env_vars: Optional[Dict[str, str]] = None,
    replace_env_vars: Optional[Dict[str, str]] = None,
    version: Optional[Union[int, str]] = None,
    running_on_hpc: bool = True,
    launch_on_hpc: bool = False,
    mapdl_output: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> Union[MapdlGrpc, "MapdlConsole"]:
    """Start MAPDL locally.

    Parameters
    ----------
    exec_file : str, optional
        The location of the MAPDL executable.  Will use the cached
        location when left at the default :class:`None` and no environment
        variable is set.

        The executable path can be also set through the environment variable
        :envvar:`PYMAPDL_MAPDL_EXEC`. For example:

        .. code:: console

            export PYMAPDL_MAPDL_EXEC=/ansys_inc/v211/ansys/bin/mapdl

    run_location : str, optional
        MAPDL working directory.  Defaults to a temporary working
        directory.  If directory doesn't exist, one is created.

    jobname : str, optional
        MAPDL jobname.  Defaults to ``'file'``.

    nproc : int, optional
        Number of processors.  Defaults to ``2``. If running on an HPC cluster,
        this value is adjusted to the number of CPUs allocated to the job,
        unless the argument ``running_on_hpc`` is set to ``"false"``.

    ram : float, optional
        Total size in megabytes of the workspace (memory) used for the initial
        allocation. The default is :class:`None`, in which case 2 GB (2048 MB) is
        used. To force a fixed size throughout the run, specify a negative
        number.

    mode : str, optional
        Mode to launch MAPDL.  Must be one of the following:

        - ``'grpc'``
        - ``'console'``

        The ``'grpc'`` mode is available on ANSYS 2021R1 or newer and
        provides the best performance and stability.
        The ``'console'`` mode is for legacy use only Linux only prior to 2020R2.
        This console mode is pending depreciation.
        Visit :ref:`versions_and_interfaces` for more information.

    override : bool, optional
        Attempts to delete the lock file at the ``run_location``.
        Useful when a prior MAPDL session has exited prematurely and
        the lock file has not been deleted.

    loglevel : str, optional
        Sets which messages are printed to the console.  ``'INFO'``
        prints out all ANSYS messages, ``'WARNING'`` prints only
        messages containing ANSYS warnings, and ``'ERROR'`` logs only
        error messages.

    additional_switches : str, optional
        Additional switches for MAPDL, for example ``'aa_r'``, the
        academic research license, would be added with:

        - ``additional_switches="-aa_r"``

        Avoid adding switches like ``-i``, ``-o`` or ``-b`` as these are already
        included to start up the MAPDL server.  See the notes
        section for additional details.

    start_timeout : float, optional
        Maximum allowable time to connect to the MAPDL server. By default it is
        45 seconds, however, it is increased to 90 seconds if running on HPC.

    port : int
        Port to launch MAPDL gRPC on.  Final port will be the first
        port available after (or including) this port.  Defaults to
        ``50052``. You can also provide this value through the environment variable
        :envvar:`PYMAPDL_PORT`. For instance ``PYMAPDL_PORT=50053``.
        However the argument (if specified) has precedence over the environment
        variable. If this environment variable is empty, it is as it is not set.

    cleanup_on_exit : bool, optional
        Exit MAPDL when python exits or the mapdl Python instance is
        garbage collected.

    start_instance : bool, optional
        When :class:`False`, connect to an existing MAPDL instance at ``ip``
        and ``port``, which default to ip ``'127.0.0.1'`` at port ``50052``.
        Otherwise, launch a local instance of MAPDL. You can also
        provide this value through the environment variable
        :envvar:`PYMAPDL_START_INSTANCE`.
        However the argument (if specified) has precedence over the environment
        variable. If this environment variable is empty, it is as it is not set.

    ip : str, optional
        Specify the IP address of the MAPDL instance to connect to.
        You can also provide a hostname as an alternative to an IP address.
        Defaults to ``'127.0.0.1'``.
        Used only when ``start_instance`` is :class:`False`. If this argument
        is provided, and ``start_instance`` (or its correspondent environment
        variable :envvar:`PYMAPDL_START_INSTANCE`) is :class:`True` then, an
        exception is raised.
        You can also provide this value through the environment variable
        :envvar:`PYMAPDL_IP`. For instance ``PYMAPDL_IP=123.45.67.89``.
        However the argument (if specified) has precedence over the environment
        variable. If this environment variable is empty, it is as it is not set.

    clear_on_connect : bool, optional
        Defaults to :class:`True`, giving you a fresh environment when
        connecting to MAPDL. When if ``start_instance`` is specified
        it defaults to :class:`False`.

    log_apdl : str, optional
        Enables logging every APDL command to the local disk.  This
        can be used to "record" all the commands that are sent to
        MAPDL via PyMAPDL so a script can be run within MAPDL without
        PyMAPDL. This argument is the path of the output file (e.g.
        ``log_apdl='pymapdl_log.txt'``). By default this is disabled.

    remove_temp_dir_on_exit : bool, optional
        When ``run_location`` is :class:`None`, this launcher creates a new MAPDL
        working directory within the user temporary directory, obtainable with
        ``tempfile.gettempdir()``. When this parameter is
        :class:`True`, this directory will be deleted when MAPDL is exited.
        Default to :class:`False`.
        If you change the working directory, PyMAPDL does not delete the original
        working directory nor the new one.

    license_server_check : bool, optional
        Check if the license server is available if MAPDL fails to
        start.  Only available on ``mode='grpc'``. Defaults :class:`False`.

    license_type : str, optional
        Enable license type selection. You can input a string for its
        license name (for example ``'meba'`` or ``'ansys'``) or its description
        ("enterprise solver" or "enterprise" respectively).
        You can also use legacy licenses (for example ``'aa_t_a'``) but it will
        also raise a warning. If it is not used (:class:`None`), no specific
        license will be requested, being up to the license server to provide a
        specific license type. Default is :class:`None`.

    print_com : bool, optional
        Print the command ``/COM`` arguments to the standard output.
        Default :class:`False`.

    add_env_vars : dict, optional
        The provided dictionary will be used to extend the MAPDL process
        environment variables. If you want to control all of the environment
        variables, use the argument ``replace_env_vars``.
        Defaults to :class:`None`.

    replace_env_vars : dict, optional
        The provided dictionary will be used to replace all the MAPDL process
        environment variables. It replace the system environment variables
        which otherwise would be used in the process.
        To just add some environment variables to the MAPDL
        process, use ``add_env_vars``. Defaults to :class:`None`.

    version : float, optional
        Version of MAPDL to launch. If :class:`None`, the latest version is used.
        Versions can be provided as integers (i.e. ``version=222``) or
        floats (i.e. ``version=22.2``).
        To retrieve the available installed versions, use the function
        :meth:`ansys.tools.path.path.get_available_ansys_installations`.
        You can also provide this value through the environment variable
        :envvar:`PYMAPDL_MAPDL_VERSION`.
        For instance ``PYMAPDL_MAPDL_VERSION=22.2``.
        However the argument (if specified) has precedence over the environment
        variable. If this environment variable is empty, it is as it is not set.

    running_on_hpc: bool, optional
        Whether detect if PyMAPDL is running on an HPC cluster. Currently
        only SLURM clusters are supported. By default, it is set to true.
        This option can be bypassed if the :envvar:`PYMAPDL_RUNNING_ON_HPC`
        environment variable is set to :class:`True`.
        For more information, see :ref:`ref_hpc_slurm`.

    launch_on_hpc : bool, Optional
        If :class:`True`, it uses the implemented scheduler (SLURM only) to launch
        an MAPDL instance on the HPC. In this case you can pass the
        '`scheduler_options`' argument to
        :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>`
        to specify the scheduler arguments as a string or as a dictionary.
        For more information, see :ref:`ref_hpc_slurm`.

    mapdl_output : str, optional
        Redirect the MAPDL console output to a given file.

    kwargs : dict, Optional
        These keyword arguments are interface-specific or for
        development purposes. For more information, see Notes.

        scheduler_options : :class:`str`, :class:`dict`
          Use it to specify options to the scheduler run command. It can be a
          string or a dictionary with arguments and its values (both as strings).
          For more information visit :ref:`ref_hpc_slurm`.

        set_no_abort : :class:`bool`
          *(Development use only)*
          Sets MAPDL to not abort at the first error within /BATCH mode.
          Defaults to :class:`True`.

        force_intel : :class:`bool`
          *(Development use only)*
          Forces the use of Intel message pass interface (MPI) in versions between
          Ansys 2021R0 and 2022R2, where because of VPNs issues this MPI is
          deactivated by default.
          See :ref:`vpn_issues_troubleshooting` for more information.
          Defaults to :class:`False`.

    Returns
    -------
    Union[MapdlGrpc, MapdlConsole]
        An instance of Mapdl.  Type depends on the selected ``mode``.

    Notes
    -----

    **Ansys Student Version**

    If an Ansys Student version is detected, PyMAPDL will launch MAPDL in
    shared-memory parallelism (SMP) mode unless another option is specified.

    **Additional switches**

    These are the MAPDL switch options as of 2020R2 applicable for
    running MAPDL as a service via gRPC.  Excluded switches not applicable or
    are set via keyword arguments such as ``"-j"`` .

    \\-acc <device>
        Enables the use of GPU hardware.  See GPU
        Accelerator Capability in the Parallel Processing Guide for more
        information.

    \\-amfg
        Enables the additive manufacturing capability.  Requires
        an additive manufacturing license. For general information about
        this feature, see AM Process Simulation in ANSYS Workbench.

    \\-ansexe <executable>
        Activates a custom mechanical APDL executable.
        In the ANSYS Workbench environment, activates a custom
        Mechanical APDL executable.

    \\-custom <executable>
        Calls a custom Mechanical APDL executable
        See Running Your Custom Executable in the Programmer's Reference
        for more information.

    \\-db value
        Initial memory allocation
        Defines the portion of workspace (memory) to be used as the
        initial allocation for the database. The default is 1024
        MB. Specify a negative number to force a fixed size throughout
        the run; useful on small memory systems.

    \\-dis
        Enables Distributed ANSYS
        See the Parallel Processing Guide for more information.

    \\-dvt
        Enables ANSYS DesignXplorer advanced task (add-on).
        Requires DesignXplorer.

    \\-l <language>
        Specifies a language file to use other than English
        This option is valid only if you have a translated message file
        in an appropriately named subdirectory in
        ``/ansys_inc/v201/ansys/docu`` or
        ``Program Files\\ANSYS\\Inc\\V201\\ANSYS\\docu``

    \\-m <workspace>
        Specifies the total size of the workspace
        Workspace (memory) in megabytes used for the initial
        allocation. If you omit the ``-m`` option, the default is 2 GB
        (2048 MB). Specify a negative number to force a fixed size
        throughout the run.

    \\-machines <IP>
        Specifies the distributed machines
        Machines on which to run a Distributed ANSYS analysis. See
        Starting Distributed ANSYS in the Parallel Processing Guide for
        more information.

    \\-mpi <value>
        Specifies the type of MPI to use.
        See the Parallel Processing Guide for more information.

    \\-mpifile <appfile>
        Specifies an existing MPI file
        Specifies an existing MPI file (appfile) to be used in a
        Distributed ANSYS run. See Using MPI Files in the Parallel
        Processing Guide for more information.

    \\-na <value>
        Specifies the number of GPU accelerator devices
        Number of GPU devices per machine or compute node when running
        with the GPU accelerator feature. See GPU Accelerator Capability
        in the Parallel Processing Guide for more information.

    \\-name <value>
        Defines Mechanical APDL parameters
        Set mechanical APDL parameters at program start-up. The parameter
        name must be at least two characters long. For details about
        parameters, see the ANSYS Parametric Design Language Guide.

    \\-p <productname>
        ANSYS session product
        Defines the ANSYS session product that will run during the
        session. For more detailed information about the ``-p`` option,
        see Selecting an ANSYS Product via the Command Line.

    \\-ppf <license feature name>
        HPC license
        Specifies which HPC license to use during a parallel processing
        run. See HPC Licensing in the Parallel Processing Guide for more
        information.

    \\-smp
        Enables shared-memory parallelism.
        See the Parallel Processing Guide for more information.

    **PyPIM**

    If the environment is configured to use `PyPIM <https://pypim.docs.pyansys.com>`_
    and ``start_instance`` is :class:`True`, then starting the instance will be delegated to PyPIM.
    In this event, most of the options will be ignored and the server side configuration will
    be used.

    Examples
    --------
    Launch MAPDL using the best protocol.

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()

    Run MAPDL with shared memory parallel and specify the location of
    the Ansys binary.

    >>> exec_file = 'C:/Program Files/ANSYS Inc/v231/ansys/bin/winx64/ANSYS231.exe'
    >>> mapdl = launch_mapdl(exec_file, additional_switches='-smp')

    Connect to an existing instance of MAPDL at IP 192.168.1.30 and
    port 50001.  This is only available using the latest ``'grpc'``
    mode.

    >>> mapdl = launch_mapdl(start_instance=False, ip='192.168.1.30',
    ...                      port=50001)

    Run MAPDL using the console mode (not recommended, and available only on Linux).

    >>> mapdl = launch_mapdl('/ansys_inc/v194/ansys/bin/ansys194',
    ...                       mode='console')

    Run MAPDL with additional environment variables.

    >>> my_env_vars = {"my_var":"true", "ANSYS_LOCK":"FALSE"}
    >>> mapdl = launch_mapdl(add_env_vars=my_env_vars)

    Run MAPDL with our own set of environment variables. It replace the system
    environment variables which otherwise would be used in the process.

    >>> my_env_vars = {"my_var":"true",
        "ANSYS_LOCK":"FALSE",
        "ANSYSLMD_LICENSE_FILE":"1055@MYSERVER"}
    >>> mapdl = launch_mapdl(replace_env_vars=my_env_vars)
    """
    ########################################
    # Processing arguments
    # --------------------
    #
    # packing arguments
    args = pack_arguments(locals())  # packs args and kwargs

    check_kwargs(args)  # check if passing wrong arguments

    pre_check_args(args)

    ########################################
    # PyPIM connection
    # ----------------
    # Delegating to PyPIM if applicable
    #
    if _HAS_PIM and exec_file is None and pypim.is_configured():
        # Start MAPDL with PyPIM if the environment is configured for it
        # and the user did not pass a directive on how to launch it.
        LOG.info("Starting MAPDL remotely. The startup configuration will be ignored.")

        return launch_remote_mapdl(
            cleanup_on_exit=args["cleanup_on_exit"], version=args["version"]
        )

    ########################################
    # SLURM settings
    # --------------
    # Checking if running on SLURM HPC
    #
    if is_running_on_slurm(args):
        LOG.info("On Slurm mode.")

        # extracting parameters
        get_slurm_options(args, kwargs)

    get_start_instance_arg(args)

    get_cpus(args)

    get_ip(args)

    args["port"] = get_port(args["port"], args["start_instance"])

    if args["start_instance"]:
        ########################################
        # Local adjustments
        # -----------------
        #
        # Only when starting MAPDL (aka Local)

        get_exec_file(args)

        args["version"] = get_version(
            args["version"], args.get("exec_file"), launch_on_hpc=args["launch_on_hpc"]
        )

        args["additional_switches"] = set_license_switch(
            args["license_type"], args["additional_switches"]
        )

        env_vars: Dict[str, str] = update_env_vars(
            args["add_env_vars"], args["replace_env_vars"]
        )

        get_run_location(args)

        # verify lock file does not exist
        check_lock_file(args["run_location"], args["jobname"], args["override"])

        # remove err file so we can track its creation
        # (as way to check if MAPDL started or not)
        remove_err_files(args["run_location"], args["jobname"])

    # Check for a valid connection mode
    args["mode"] = check_mode(args["mode"], args["version"])

    ########################################
    # Context specific launching adjustments
    # --------------------------------------
    #
    if args["start_instance"]:
        # ON HPC:
        # Assuming that if login node is ubuntu, the computation ones
        # are also ubuntu.
        env_vars = configure_ubuntu(env_vars)

        # Set SMP by default if student version is used.
        args["additional_switches"] = force_smp_in_student(
            args["additional_switches"], args["exec_file"]
        )

        # Set compatible MPI
        args["additional_switches"] = set_MPI_additional_switches(
            args["additional_switches"],
            force_intel=args["force_intel"],
            version=args["version"],
        )

        LOG.debug(f"Using additional switches {args['additional_switches']}.")

        if args["running_on_hpc"] or args["launch_on_hpc"]:
            env_vars.setdefault("ANS_MULTIPLE_NODES", "1")
            env_vars.setdefault("HYDRA_BOOTSTRAP", "slurm")

    start_parm = generate_start_parameters(args)

    # Early exit for debugging.
    if args["_debug_no_launch"]:
        # Early exit, just for testing
        return args  # type: ignore

    if not args["start_instance"]:
        ########################################
        # Remote launching
        # ----------------
        #
        LOG.debug(
            f"Connecting to an existing instance of MAPDL at {args['ip']}:{args['port']}"
        )
        start_parm["launched"] = False

        mapdl = MapdlGrpc(
            cleanup_on_exit=False,
            loglevel=args["loglevel"],
            set_no_abort=args["set_no_abort"],
            use_vtk=args["use_vtk"],
            log_apdl=args["log_apdl"],
            **start_parm,
        )
        if args["clear_on_connect"]:
            mapdl.clear()
        return mapdl

    ########################################
    # Sphinx docs adjustments
    # -----------------------
    #
    # special handling when building the gallery outside of CI. This
    # creates an instance of mapdl the first time.
    if pymapdl.BUILDING_GALLERY:  # pragma: no cover
        return create_gallery_instances(args, start_parm)

    ########################################
    # Local launching
    # ---------------
    #
    # Check the license server
    if args["license_server_check"]:
        LOG.debug("Checking license server.")
        lic_check = LicenseChecker(timeout=args["start_timeout"])
        lic_check.start()

    LOG.debug("Starting MAPDL")
    if args["mode"] == "console":  # pragma: no cover
        ########################################
        # Launch MAPDL on console mode
        # ----------------------------
        #
        from ansys.mapdl.core.mapdl_console import MapdlConsole

        start_parm = check_console_start_parameters(start_parm)
        mapdl = MapdlConsole(
            loglevel=args["loglevel"],
            log_apdl=args["log_apdl"],
            use_vtk=args["use_vtk"],
            **start_parm,
        )

    elif args["mode"] == "grpc":
        ########################################
        # Launch MAPDL with gRPC
        # ----------------------
        #
        cmd = generate_mapdl_launch_command(
            exec_file=args["exec_file"],
            jobname=args["jobname"],
            nproc=args["nproc"],
            ram=args["ram"],
            port=args["port"],
            additional_switches=args["additional_switches"],
            launch_on_hpc=args["launch_on_hpc"],
        )

        if args["launch_on_hpc"]:
            # wrapping command if on HPC
            cmd = generate_sbatch_command(
                cmd, scheduler_options=args.get("scheduler_options")
            )

        try:
            #
            process = launch_grpc(
                cmd=cmd,
                run_location=args["run_location"],
                env_vars=env_vars,
                launch_on_hpc=args.get("launch_on_hpc"),
                mapdl_output=args.get("mapdl_output"),
            )

            if args["launch_on_hpc"]:
                start_parm["jobid"] = check_mapdl_launch_on_hpc(process, start_parm)
                get_job_info(start_parm=start_parm, timeout=args["start_timeout"])
            else:
                # Local mapdl launch check
                check_mapdl_launch(
                    process, args["run_location"], args["start_timeout"], cmd
                )

        except Exception as exception:
            LOG.error("An error occurred when launching MAPDL.")

            jobid: int = start_parm.get("jobid")

            if (
                args["launch_on_hpc"]
                and start_parm.get("finish_job_on_exit", True)
                and jobid is not None
            ):

                LOG.debug(f"Killing HPC job with id: {jobid}")
                kill_job(jobid)

            if args["license_server_check"]:
                LOG.debug("Checking license server.")
                lic_check.check()

            raise exception

        if args["just_launch"]:
            out = [args["ip"], args["port"]]
            if hasattr(process, "pid"):
                out += [process.pid]
            return out

        ########################################
        # Connect to MAPDL using gRPC
        # ---------------------------
        #
        try:
            mapdl = MapdlGrpc(
                cleanup_on_exit=args["cleanup_on_exit"],
                loglevel=args["loglevel"],
                set_no_abort=args["set_no_abort"],
                remove_temp_dir_on_exit=args["remove_temp_dir_on_exit"],
                log_apdl=args["log_apdl"],
                process=process,
                use_vtk=args["use_vtk"],
                **start_parm,
            )

        except Exception as exception:
            LOG.error("An error occurred when connecting to MAPDL.")
            raise exception

    return mapdl


def check_mode(mode: ALLOWABLE_MODES, version: Optional[int] = None):
    """Check if the MAPDL server mode matches the allowable version

    If :class:`None`, the newest mode will be selected.

    Returns a value from ``ALLOWABLE_MODES``.
    """
    if not mode and not version:
        return "grpc"
    elif not version:
        warnings.warn(
            "PyMAPDL couldn't detect MAPDL version, hence it could not "
            f"verify that the provided connection mode '{mode}' is compatible "
            "with the current MAPDL installation."
        )
        return mode

    if isinstance(mode, str):
        mode = mode.lower()
        if mode == "grpc":
            if version and version < 211:
                if version < 202 and os.name == "nt":
                    raise VersionError(
                        "gRPC mode requires MAPDL 2020R2 or newer " "on Windows."
                    )
                elif os.name == "posix":
                    raise VersionError(
                        "gRPC mode requires MAPDL 2021R1 or newer on Linux."
                    )

        elif mode == "console":
            if os.name == "nt":
                raise ValueError("Console mode requires Linux.")
            if version and version >= 211:
                warnings.warn(
                    "Console mode not recommended in MAPDL 2021R1 or newer.\n"
                    "Recommend using gRPC mode instead."
                )
        else:
            raise ValueError(
                f'Invalid MAPDL server mode "{mode}".\n\n'
                f"Use one of the following modes: {','.join(ALLOWABLE_MODES)}"
            )

    else:  # auto-select based on best version
        if version and version >= 211:
            mode = "grpc"
        elif version and version == 202 and os.name == "nt":
            # Windows supports it as of 2020R2
            mode = "grpc"
        else:
            if os.name == "nt":
                raise VersionError(
                    "Running MAPDL as a service requires "
                    "MAPDL 2020R2 or greater on Windows."
                )
            mode = "console"

    if version and version < 130:
        warnings.warn("MAPDL as a service has not been tested on MAPDL < v13")
        mode = "console"

    LOG.debug(f"Using mode {mode}")
    return mode


def update_env_vars(add_env_vars: dict, replace_env_vars: dict) -> dict:
    """
    Update environment variables for the MAPDL process.

    Parameters
    ----------
    add_env_vars : dict, None
        Dictionary with a mapping of env variables.
    replace_env_vars : dict, None
        Dictionary with a mapping of env variables.

    Raises
    ------
    TypeError
        'add_env_vars' and 'replace_env_vars' are incompatible. Please provide only one.
    TypeError
        The variable 'add_env_vars' should be a dict with env vars.
    TypeError
        The variable 'replace_env_vars' should be a dict with env vars.
    """

    # Expanding/replacing env variables for the process.
    envvars = os.environ.copy()

    if add_env_vars and replace_env_vars:
        raise ValueError(
            "'add_env_vars' and 'replace_env_vars' are incompatible. Please provide only one."
        )

    elif add_env_vars:
        if not isinstance(add_env_vars, dict):
            raise TypeError(
                "The variable 'add_env_vars' should be a dict with env vars."
            )

        envvars.update(add_env_vars)
        LOG.debug(f"Updating environment variables with: {add_env_vars}")

    elif replace_env_vars:
        if not isinstance(replace_env_vars, dict):
            raise TypeError(
                "The variable 'replace_env_vars' should be a dict with env vars."
            )
        LOG.debug(f"Replacing environment variables with: {replace_env_vars}")
        envvars = replace_env_vars

    return envvars


def set_license_switch(license_type, additional_switches):
    if isinstance(license_type, str):
        # In newer license server versions an invalid license name just get discarded and produces no effect or warning.
        # For example:
        # ```bash
        # mapdl.exe -p meba    # works fine because 'meba' is a valid license in ALLOWABLE_LICENSES.
        # mapdl.exe -p yoyoyo  # The -p flag is ignored and it run the default license.
        # ```
        #
        # In older versions probably it might raise an error. But not sure.
        license_type = license_type.lower().strip()

        if "preppost" in license_type:
            license_type = "preppost"

        elif "enterprise" in license_type and "solver" not in license_type:
            license_type = "ansys"

        elif "enterprise" in license_type and "solver" in license_type:
            license_type = "meba"

        elif "premium" in license_type:
            license_type = "mech_2"

        elif "pro" in license_type:
            license_type = "mech_1"

        elif license_type not in ALLOWABLE_LICENSES:
            allow_lics = [f"'{each}'" for each in ALLOWABLE_LICENSES]
            warn_text = (
                f"The keyword argument 'license_type' value ('{license_type}') is not a recognized\n"
                "license name or has been deprecated.\n"
                "Still PyMAPDL will try to use it but in older MAPDL versions you might experience\n"
                "problems connecting to the server.\n"
                f"Recognized license names: {' '.join(allow_lics)}"
            )
            warnings.warn(warn_text, UserWarning)

        additional_switches += " -p " + license_type
        LOG.debug(
            f"Using specified license name '{license_type}' in the 'license_type' keyword argument."
        )

    elif "-p " in additional_switches:
        # There is already a license request in additional switches.
        license_type = re.findall(r"-p\s+\b(\w*)", additional_switches)[
            0
        ]  # getting only the first product license.

        if license_type not in ALLOWABLE_LICENSES:
            allow_lics = [f"'{each}'" for each in ALLOWABLE_LICENSES]
            warn_text = (
                f"The additional switch product value ('-p {license_type}') is not a recognized\n"
                "license name or has been deprecated.\n"
                "Still PyMAPDL will try to use it but in older MAPDL versions you might experience\n"
                "problems connecting to the server.\n"
                f"Recognized license names: {' '.join(allow_lics)}"
            )
            warnings.warn(warn_text, UserWarning)
            LOG.warning(warn_text)

        LOG.debug(
            f"Using specified license name '{license_type}' in the additional switches parameter."
        )

    elif license_type is not None:
        raise TypeError("The argument 'license_type' does only accept str or None.")

    return additional_switches


def _get_windows_host_ip():
    output = _run_ip_route()
    if output:
        return _parse_ip_route(output)


def _run_ip_route():

    try:
        # args value is controlled by the library.
        # ip is not a partial path - Bandit false positive
        # Excluding bandit check.
        p = subprocess.run(["ip", "route"], capture_output=True)  # nosec B603 B607
    except Exception:
        LOG.debug(
            "Detecting the IP address of the host Windows machine requires being able to execute the command 'ip route'."
        )
        return None

    if p and p.stdout and isinstance(p.stdout, bytes):
        return p.stdout.decode()


def _parse_ip_route(output):
    match = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", output)

    if match:
        return match[0]


def get_slurm_options(
    args: Dict[str, Any],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    def get_value(
        variable: str,
        kwargs: Dict[str, Any],
        default: Optional[Union[str, int, float]] = 1,
        astype: Optional[Callable[[Any], Any]] = int,
    ):
        value_from_env_vars = os.environ.get(variable)
        value_from_kwargs = kwargs.pop(variable, None)
        value = value_from_kwargs or value_from_env_vars or default
        if astype and value:
            return astype(value)
        else:
            return value

    ## Getting env vars
    SLURM_NNODES = get_value("SLURM_NNODES", kwargs)
    LOG.info(f"SLURM_NNODES: {SLURM_NNODES}")
    # ntasks is for mpi
    SLURM_NTASKS = get_value("SLURM_NTASKS", kwargs)
    LOG.info(f"SLURM_NTASKS: {SLURM_NTASKS}")
    # Sharing tasks across multiple nodes (DMP)
    # the format of this envvar is a bit tricky. Avoiding it for the moment.
    # SLURM_TASKS_PER_NODE = int(
    #     kwargs.pop(
    #         "SLURM_TASKS_PER_NODE", os.environ.get("SLURM_TASKS_PER_NODE", 1)
    #     )
    # )

    # cpus-per-task is for multithreading,
    # sharing tasks across multiple CPUs in same node (SMP)
    SLURM_CPUS_PER_TASK = get_value("SLURM_CPUS_PER_TASK", kwargs)
    LOG.info(f"SLURM_CPUS_PER_TASK: {SLURM_CPUS_PER_TASK}")

    # Set to value of the --ntasks option, if specified. See SLURM_NTASKS.
    # Included for backwards compatibility.
    SLURM_NPROCS = get_value("SLURM_NPROCS", kwargs)
    LOG.info(f"SLURM_NPROCS: {SLURM_NPROCS}")

    # Number of CPUs allocated to the batch step.
    SLURM_CPUS_ON_NODE = get_value("SLURM_CPUS_ON_NODE", kwargs)
    LOG.info(f"SLURM_CPUS_ON_NODE: {SLURM_CPUS_ON_NODE}")

    SLURM_MEM_PER_NODE = get_value(
        "SLURM_MEM_PER_NODE", kwargs, default="", astype=str
    ).upper()
    LOG.info(f"SLURM_MEM_PER_NODE: {SLURM_MEM_PER_NODE}")

    SLURM_NODELIST = get_value(
        "SLURM_NODELIST", kwargs, default="", astype=None
    ).lower()
    LOG.info(f"SLURM_NODELIST: {SLURM_NODELIST}")

    if not args["exec_file"]:
        args["exec_file"] = os.environ.get("PYMAPDL_MAPDL_EXEC")

    if not args["exec_file"]:
        # We should probably make a way to find it.
        # We will use the module thing
        pass
    LOG.info(f"Using MAPDL executable in: {args['exec_file']}")

    if not args["jobname"]:
        args["jobname"] = os.environ.get("SLURM_JOB_NAME", "file")
    LOG.info(f"Using jobname: {args['jobname']}")

    # Checking specific env var
    if not args["nproc"]:
        ## Attempt to calculate the appropriate number of cores:
        # Reference: https://stackoverflow.com/a/51141287/6650211
        # I'm assuming the env var makes sense.
        #
        # - SLURM_CPUS_ON_NODE is a property of the cluster, not of the job.
        #
        options = max(
            [
                # 4,  # Fall back option
                SLURM_CPUS_PER_TASK * SLURM_NTASKS,  # (CPUs)
                SLURM_NPROCS,  # (CPUs)
                # SLURM_NTASKS,  # (tasks) Not necessary the number of CPUs,
                # SLURM_NNODES * SLURM_TASKS_PER_NODE * SLURM_CPUS_PER_TASK,  # (CPUs)
                SLURM_CPUS_ON_NODE * SLURM_NNODES,  # (cpus)
            ]
        )
        LOG.info(f"On SLURM number of processors options {options}")

        args["nproc"] = int(os.environ.get("PYMAPDL_NPROC", options))

    LOG.info(f"Setting number of CPUs to: {args['nproc']}")

    if not args["ram"]:
        if SLURM_MEM_PER_NODE:
            # RAM argument is in MB, so we need to convert
            units = None
            if SLURM_MEM_PER_NODE[-1].isalpha():
                units = SLURM_MEM_PER_NODE[-1]
                ram = SLURM_MEM_PER_NODE[:-1]
            else:
                units = None
                ram = SLURM_MEM_PER_NODE

            if not units:
                args["ram"] = int(ram)  # Assuming in MB
            elif units == "T":  # tera
                args["ram"] = int(ram) * (2**10) ** 2
            elif units == "G":  # giga
                args["ram"] = int(ram) * (2**10) ** 1
            elif units == "M":  # mega
                args["ram"] = int(ram)
            elif units == "K":  # kilo
                args["ram"] = int(ram) * (2**10) ** (-1)
            else:  # Mega
                raise ValueError(
                    "The memory defined in 'SLURM_MEM_PER_NODE' env var("
                    f"'{SLURM_MEM_PER_NODE}') is not valid."
                )

    LOG.info(f"Setting RAM to: {args['ram']}")

    # We use "-dis " (with space) to avoid collision with user variables such
    # as `-distro` or so
    if "-dis " not in args["additional_switches"] and not args[
        "additional_switches"
    ].endswith("-dis"):
        args["additional_switches"] += " -dis"

    # Finally set to avoid timeouts
    args["license_server_check"] = False
    args["start_timeout"] = 2 * args["start_timeout"]

    return args


def pack_arguments(locals_):
    args = {}
    for each in ALLOWABLE_LAUNCH_MAPDL_ARGS:
        if each in locals_:
            args[each] = locals_[each]

    args["kwargs"] = locals_["kwargs"]
    args.update(locals_["kwargs"])  # attaching kwargs

    args["set_no_abort"] = locals_.get(
        "set_no_abort", locals_["kwargs"].get("set_no_abort", None)
    )
    args["force_intel"] = locals_.get(
        "force_intel", locals_["kwargs"].get("force_intel", None)
    )
    args["broadcast"] = locals_.get(
        "broadcast", locals_["kwargs"].get("broadcast", None)
    )
    args["use_vtk"] = locals_.get("use_vtk", locals_["kwargs"].get("use_vtk", None))
    args["just_launch"] = locals_.get(
        "just_launch", locals_["kwargs"].get("just_launch", None)
    )
    args["on_pool"] = locals_.get("on_pool", locals_["kwargs"].get("on_pool", None))

    args["_debug_no_launch"] = locals_.get(
        "_debug_no_launch", locals_["kwargs"].get("_debug_no_launch", None)
    )
    args.setdefault("launch_on_hpc", False)
    args.setdefault("ip", None)

    return args


def is_running_on_slurm(args: Dict[str, Any]) -> bool:
    running_on_hpc_env_var = os.environ.get("PYMAPDL_RUNNING_ON_HPC", "True")

    is_flag_false = running_on_hpc_env_var.lower() == "false"

    # Let's require the following env vars to exist to go into slurm mode.
    args["running_on_hpc"] = bool(
        args["running_on_hpc"]
        and not is_flag_false  # default is true
        and os.environ.get("SLURM_JOB_NAME")
        and os.environ.get("SLURM_JOB_ID")
    )
    return args["running_on_hpc"]


def generate_start_parameters(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate start parameters

    Generate a dict with the parameters for launching MAPDL.

    Parameters
    ----------
    args : Dict[str, Any]
        Args dictionary

    Returns
    -------
    Dict[str, Any]
        start_param dictionary

    Raises
    ------
    ValueError
        If there are keys in kwargs after inject them all allowed keys, it means
        a non-allowed key was used.
    """
    # Transferring MAPDL arguments to start_parameters:
    start_parm = {}

    for each_par in _ALLOWED_START_PARM:
        if each_par in args:
            start_parm[each_par] = args[each_par]

    if args["mode"] == "console":
        start_parm["start_timeout"] = args["start_timeout"]

    else:
        start_parm["ram"] = args["ram"]
        start_parm["override"] = args["override"]
        start_parm["timeout"] = args["start_timeout"]

    start_parm["launched"] = True
    start_parm.pop("mode")

    LOG.debug(f"Using start parameters {start_parm}")
    return start_parm


def get_ip_env_var() -> str:
    """Get IP from 'PYMAPDL_IP' env var"""

    # Getting IP from env var
    ip_env_var = os.environ.get("PYMAPDL_IP", "")

    if ip_env_var != "":
        LOG.debug(f"An IP ({ip_env_var}) has been set using 'PYMAPDL_IP' env var.")
        return ip_env_var


def get_ip(args: Dict[str, Any]) -> None:
    """Get IP from env var or arguments

    The environment variable value has priority over the argument.

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict

    Raises
    ------
    MapdlDidNotStart
        Windows host IP could not be found.
    ValueError
        'start_instance' and 'ip' arguments are incompatible.
    """
    if args["ip"] in [None, ""]:

        args["ip"] = get_ip_env_var()

        if not args["ip"] and ON_WSL:
            args["ip"] = _get_windows_host_ip()
            if args["ip"]:
                LOG.debug(
                    f"On WSL: Using the following IP address for the Windows OS host: {args['ip']}"
                )
            else:
                raise MapdlDidNotStart(
                    "You seems to be working from WSL.\n"
                    "Unfortunately, PyMAPDL could not find the IP address of the Windows host machine."
                )

        if not args["ip"]:
            LOG.debug(
                f"No IP address was supplied. Using the default IP address: {LOCALHOST}"
            )
            args["ip"] = LOCALHOST

    # Converting ip or hostname to ip
    args["ip"] = socket.gethostbyname(args["ip"])
    check_valid_ip(args["ip"])  # double check


def get_start_instance_arg(args: Dict[str, Any]) -> None:
    """Get start instance argument

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict
    """
    ip_envar = get_ip_env_var() not in ["", None]

    if (args["ip"] not in [None, ""] or ip_envar) and (args["start_instance"] is None):
        # An IP has been supplied. By default, 'start_instance' is equal
        # false, unless it is set through the env vars (which has preference)
        args["start_instance"] = False

    args["start_instance"] = get_start_instance(start_instance=args["start_instance"])
    LOG.debug(f"Using 'start_instance' equal to {args['start_instance']}")


def get_port(port: Optional[int] = None, start_instance: Optional[bool] = None) -> int:
    """Get port argument.

    Parameters
    ----------
    port : Optional[int]
        Port given as argument.

    Returns
    -------
    int
        Port
    """
    if port is None:
        if os.environ.get("PYMAPDL_PORT"):
            LOG.debug(f"Using port from 'PYMAPDL_PORT' env var: {port}")
            return int(os.environ.get("PYMAPDL_PORT"))

        if not pymapdl._LOCAL_PORTS:
            port = MAPDL_DEFAULT_PORT
            LOG.debug(f"Using default port: {port}")
        else:
            port = max(pymapdl._LOCAL_PORTS) + 1
            LOG.debug(f"Using next available port: {port}")

        while (port_in_use(port) and start_instance) or port in pymapdl._LOCAL_PORTS:
            port += 1
            LOG.debug(f"Port in use.  Incrementing port number. port={port}")

    else:
        if start_instance and port_in_use(port):
            proc = get_process_at_port(port)
            if proc:
                if is_ansys_process(proc):
                    raise PortAlreadyInUseByAnMAPDLInstance(port)
                else:
                    raise PortAlreadyInUse(port)

    pymapdl._LOCAL_PORTS.append(port)

    check_valid_port(port)
    LOG.debug(f"Using default port {port}")

    return port


def get_version(
    version: Optional[Union[str, int]] = None,
    exec_file: Optional[str] = None,
    launch_on_hpc: bool = False,
) -> Optional[int]:
    """Get MAPDL version

    Parameters
    ----------
    version : Optional[Union[str, int]], optional
        Version argument, by default None

    Returns
    -------
    Optional[int]
        The version as XYZ or None.

    Raises
    ------
    ValueError
        MAPDL version must be one of the following
    """
    if not version:
        version = os.getenv("PYMAPDL_MAPDL_VERSION")

    if not version:
        # verify version
        if exec_file and _HAS_ATP:
            version = version_from_path("mapdl", exec_file, launch_on_hpc=launch_on_hpc)
            if version and version < 202:
                raise VersionError(
                    "The MAPDL gRPC interface requires MAPDL 20.2 or later"
                )
        else:
            # Early exit
            return

    if isinstance(version, float):
        version = int(version * 10)

    if isinstance(version, str):
        if version.lower().strip() == "latest":
            return None  # Default behaviour is latest

        elif version.upper().strip() in [str(each) for each in ALLOWABLE_VERSION_INT]:
            version = int(version)
        elif version.upper().strip() in [
            str(each / 10) for each in ALLOWABLE_VERSION_INT
        ]:
            version = int(float(version) * 10)
        elif version.upper().strip() in SUPPORTED_ANSYS_VERSIONS.values():
            version = [
                key
                for key, value in SUPPORTED_ANSYS_VERSIONS.items()
                if value == version.upper().strip()
            ][0]

    if version is not None and version not in ALLOWABLE_VERSION_INT:
        raise ValueError(
            f"MAPDL version must be one of the following: {list(ALLOWABLE_VERSION_INT)}"
        )

    return version  # return a int version or none


def create_gallery_instances(
    args: Dict[str, Any], start_parm: Dict[str, Any]
) -> MapdlGrpc:  # pragma: no cover
    """Create MAPDL instances for the documentation gallery built.

    This function is not tested with Pytest, but it is used during CICD docs
    building.

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict
    start_parm : Dict[str, Any]
        MAPDL start parameters

    Returns
    -------
    MapdlGrpc
        MAPDL instance
    """
    LOG.debug("Building gallery.")
    # launch an instance of pymapdl if it does not already exist and
    # we're allowed to start instances
    if GALLERY_INSTANCE[0] is None:
        LOG.debug("Loading first MAPDL instance for gallery building.")
        GALLERY_INSTANCE[0] = "Loading..."
        mapdl = launch_mapdl(
            start_instance=True,
            cleanup_on_exit=False,
            loglevel=args["loglevel"],
            set_no_abort=args["set_no_abort"],
            **start_parm,
        )
        GALLERY_INSTANCE[0] = {"ip": mapdl._ip, "port": mapdl._port}
        return mapdl

    # otherwise, connect to the existing gallery instance if available, but it needs to be fully loaded.
    else:
        while not isinstance(GALLERY_INSTANCE[0], dict):
            # Waiting for MAPDL instance to be ready
            time.sleep(0.1)

        LOG.debug("Connecting to an existing MAPDL instance for gallery building.")
        start_parm.pop("ip", None)
        start_parm.pop("port", None)
        mapdl = MapdlGrpc(
            ip=GALLERY_INSTANCE[0]["ip"],
            port=GALLERY_INSTANCE[0]["port"],
            cleanup_on_exit=False,
            loglevel=args["loglevel"],
            set_no_abort=args["set_no_abort"],
            use_vtk=args["use_vtk"],
            **start_parm,
        )
        if args["clear_on_connect"]:
            mapdl.clear()
        return mapdl


def get_exec_file(args: Dict[str, Any]) -> None:
    """Get exec file argument

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dictionary

    Raises
    ------
    ModuleNotFoundError
        'ansys-tools-path' library could not be found
    FileNotFoundError
        Invalid exec_file path or cannot load cached MAPDL path.
    FileNotFoundError
        Invalid MAPDL executable
    """
    args["exec_file"] = args.get("exec_file") or os.getenv("PYMAPDL_MAPDL_EXEC")

    if not args["start_instance"] and args["exec_file"] is None:
        # 'exec_file' is not needed if the instance is not going to be launch
        args["exec_file"] = ""
        return

    if args["exec_file"] is None:
        if not _HAS_ATP:
            raise ModuleNotFoundError(
                "If you don't have 'ansys-tools-path' library installed, you need "
                "to input the executable path ('exec_file' argument) or use the "
                "'PYMAPDL_MAPDL_EXEC' environment variable."
            )

        if args.get("_debug_no_launch", False):
            args["exec_file"] = ""
            return

        LOG.debug("Using default executable.")
        args["exec_file"] = get_mapdl_path(version=args.get("version"))

        # Edge case
        if args["exec_file"] is None:
            raise FileNotFoundError(
                "Invalid exec_file path or cannot load cached "
                "MAPDL path. Enter one manually by specifying "
                "'exec_file' argument."
            )
    else:  # verify ansys exists at this location
        if not args.get("launch_on_hpc", False) and not os.path.isfile(
            args["exec_file"]
        ):
            raise FileNotFoundError(
                f'Invalid MAPDL executable at "{args["exec_file"]}"\n'
                "Enter one manually using exec_file="
            )


def get_run_location(args: Dict[str, Any]) -> None:
    """Get run_location argument.

    It can change 'remove_temp_dir_on_exit' argument's value.

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict

    Raises
    ------
    FileNotFoundError
        _description_
    """
    if args["run_location"] is None:
        args["run_location"] = create_temp_dir()
        LOG.debug(
            f"Using default temporary directory for MAPDL run location: {args['run_location']}"
        )

    elif not os.path.isdir(args["run_location"]):
        os.makedirs(args["run_location"], exist_ok=True)
        LOG.debug(f"Creating directory for MAPDL run location: {args['run_location']}")

        if args.get("remove_temp_dir_on_exit"):
            LOG.info(
                "The 'run_location' argument is set. Disabling the removal of temporary files."
            )
            args["remove_temp_dir_on_exit"] = False

    elif not os.access(args["run_location"], os.W_OK):
        raise IOError(f'Unable to write to ``run_location``: {args["run_location"]}')

    LOG.debug("Using run location at %s", args["run_location"])


def check_kwargs(args: Dict[str, Any]):
    """Check all the kwargs are valid.

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict

    Raises
    ------
    ValueError
        When an argument is not allowed.
    """
    kwargs = list(args["kwargs"].keys())

    # Raising error if using non-allowed arguments
    for each in kwargs.copy():
        if each in _ALLOWED_START_PARM or each in ALLOWABLE_LAUNCH_MAPDL_ARGS:
            kwargs.remove(each)

    if kwargs:
        ms_ = ", ".join([f"'{each}'" for each in args["kwargs"].keys()])
        raise ValueError(f"The following arguments are not recognized: {ms_}")


def pre_check_args(args: dict[str, Any]):
    if args["start_instance"] and args["ip"] and not args["on_pool"]:
        raise ValueError(
            "When providing a value for the argument 'ip', the argument "
            "'start_instance' cannot be 'True'.\n"
            "Make sure the corresponding environment variables are not setting "
            "those argument values.\n"
            "For more information visit https://github.com/ansys/pymapdl/issues/2910"
        )

    if args["exec_file"] and args["version"]:
        raise ValueError("Cannot specify both ``exec_file`` and ``version``.")

    if args["launch_on_hpc"] and args["ip"]:
        raise ValueError(LAUNCH_ON_HCP_ERROR_MESSAGE_IP)

    # Setting timeout
    if args["start_timeout"] is None:
        if args["launch_on_hpc"]:
            args["start_timeout"] = 90
        else:
            args["start_timeout"] = 45

    # Raising warning
    if args.get("scheduler_options") and args.get("nproc", None) is None:
        raise ValueError(
            "PyMAPDL does not read the number of cores from the 'scheduler_options'. "
            "Hence you need to specify the number of cores you want to use using "
            "the argument 'nproc' in 'launch_mapdl'."
        )


def get_cpus(args: Dict[str, Any]):
    """Get number of CPUs

    Parameters
    ----------
    args : Dict[str, Any]
        Arguments dict

    Raises
    ------
    NotEnoughResources
        When requesting more CPUs than available.
    """

    # Bypassing number of processors checks because VDI/VNC might have
    # different number of processors than the cluster compute nodes.
    # Also the CPUs are set in `get_slurm_options`
    if args.get("running_on_hpc"):
        return

    # Setting number of processors
    machine_cores = psutil.cpu_count(logical=False)

    # Some machines only have 1 core
    min_cpus = machine_cores if machine_cores < 2 else 2

    if not args["nproc"]:
        # Check the env var `PYMAPDL_NPROC`
        args["nproc"] = int(os.environ.get("PYMAPDL_NPROC", min_cpus))

    if not args.get("launch_on_hpc", False) and machine_cores < int(args["nproc"]):
        raise NotEnoughResources(
            f"The machine has {machine_cores} cores. PyMAPDL is asking for {args['nproc']} cores."
        )


def remove_err_files(run_location, jobname):
    # remove any temporary error files at the run location.  This is
    # important because we need to know if MAPDL is already running
    # here and because we're looking for any temporary files that are
    # created to tell when the process has started
    for filename in os.listdir(run_location):
        if ".err" == filename[-4:] and jobname in filename:
            filename = os.path.join(run_location, filename)
            if os.path.isfile(filename):
                try:
                    os.remove(filename)
                    LOG.debug(f"Removing temporary error file: {filename}")
                except Exception as error:
                    LOG.debug(
                        f"Unable to remove {filename}.  There might be "
                        "an instance of MAPDL running at running at "
                        f'"{run_location}"'
                    )
                    raise error


def launch_mapdl_on_cluster(
    nproc: int,
    *,
    scheduler_options: Union[str, Dict[str, str]] = None,
    **launch_mapdl_args: Dict[str, Any],
) -> MapdlGrpc:
    """Launch MAPDL on a HPC cluster

    Launches an interactive MAPDL instance on an HPC cluster.

    Parameters
    ----------
    nproc : int
        Number of CPUs to be used in the simulation.

    scheduler_options : Dict[str, str], optional
        A string or dictionary specifying the job configuration for the
        scheduler. For example ``scheduler_options = "-N 10"``.

    Returns
    -------
    MapdlGrpc
        Mapdl instance running on the HPC cluster.

    Examples
    --------
    Run a job with 10 nodes and 2 tasks per node:

    >>> from ansys.mapdl.core import launch_mapdl
    >>> scheduler_options = {"nodes": 10, "ntasks-per-node": 2}
    >>> mapdl = launch_mapdl(
            launch_on_hpc=True,
            nproc=20,
            scheduler_options=scheduler_options
            )

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    ValueError
        _description_
    """

    # Processing the arguments
    launch_mapdl_args["launch_on_hpc"] = True

    if launch_mapdl_args.get("mode", "grpc") != "grpc":
        raise ValueError(
            "The only mode allowed for launch MAPDL on an HPC cluster is gRPC."
        )

    if launch_mapdl_args.get("ip"):
        raise ValueError(LAUNCH_ON_HCP_ERROR_MESSAGE_IP)

    if not launch_mapdl_args.get("start_instance", True):
        raise ValueError(
            "The 'start_instance' argument must be 'True' when launching on HPC."
        )

    return launch_mapdl(
        nproc=nproc,
        scheduler_options=scheduler_options,
        **launch_mapdl_args,
    )


def get_hostname_host_cluster(job_id: int, timeout: int = 30, ssh_session=None) -> str:
    options = f"show jobid -dd {job_id}"
    LOG.debug(f"Executing the command 'scontrol {options}'")

    ready = False
    time_start = time.time()
    counter = 0
    while not ready:
        proc = send_scontrol(options, ssh_session=ssh_session)

        if isinstance(proc, tuple):
            stdout = proc[0]
        else:
            stdout = proc.stdout.read().decode()

        if "JobState=RUNNING" not in stdout:
            counter += 1
            time.sleep(1)
            if (counter % 3 + 1) == 0:  # print every 3 seconds. Skipping the first.
                LOG.debug("The job is not ready yet. Waiting...")
                print("The job is not ready yet. Waiting...")
        else:
            ready = True
            break

        # Exit by raising exception
        if time.time() > time_start + timeout:
            state = get_state_from_scontrol(stdout)

            # Trying to get the hostname from the last valid message
            try:
                host = get_hostname_from_scontrol(stdout)
                if not host:
                    # If string is empty, go to the exception clause.
                    raise IndexError()

                hostname_msg = f"The BatchHost for this job is '{host}'"
            except (IndexError, AttributeError):
                hostname_msg = "PyMAPDL couldn't get the BatchHost hostname"

            # Raising exception
            raise MapdlDidNotStart(
                f"The HPC job (id: {job_id}) didn't start on time (timeout={timeout}). "
                f"The job state is '{state}'. "
                f"{hostname_msg}. "
                "You can check more information by issuing in your console:\n"
                f" scontrol show jobid -dd {job_id}"
            )

    LOG.debug(f"The 'scontrol' command returned:\n{stdout}")
    batchhost = get_hostname_from_scontrol(stdout)
    LOG.debug(f"Batchhost: {batchhost}")

    # we should validate
    batchhost_ip = socket.gethostbyname(batchhost)
    LOG.debug(f"Batchhost IP: {batchhost_ip}")

    LOG.info(
        f"Job {job_id} successfully allocated and running in '{batchhost}'({batchhost_ip})"
    )
    return batchhost, batchhost_ip


def get_jobid(stdout: str) -> int:
    """Extract the jobid from a command output"""
    job_id = stdout.strip().split(" ")[-1]

    try:
        job_id = int(job_id)
    except ValueError:
        LOG.error(f"The console output does not seems to have a valid jobid:\n{stdout}")
        raise ValueError("PyMAPDL could not retrieve the job id.")

    LOG.debug(f"The job id is: {job_id}")
    return job_id


def generate_sbatch_command(
    cmd: Union[str, List[str]], scheduler_options: Optional[Union[str, Dict[str, str]]]
) -> List[str]:
    """Generate sbatch command for a given MAPDL launch command."""

    def add_minus(arg: str):
        if not arg:
            return ""

        arg = str(arg)

        if not arg.startswith("-"):
            if len(arg) == 1:
                arg = f"-{arg}"
            else:
                arg = f"--{arg}"
        elif not arg.startswith("--") and len(arg) > 2:
            # missing one "-" for a long argument
            arg = f"-{arg}"

        return arg

    if scheduler_options:
        if isinstance(scheduler_options, dict):
            scheduler_options = " ".join(
                [
                    f"{add_minus(key)}='{value}'"
                    for key, value in scheduler_options.items()
                ]
            )
    else:
        scheduler_options = ""

    if "wrap" in scheduler_options:
        raise ValueError(
            "The sbatch argument 'wrap' is used by PyMAPDL to submit the job."
            "Hence you cannot use it as sbatch argument."
        )
    LOG.debug(f"The additional sbatch arguments are: {scheduler_options}")

    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    cmd = ["sbatch", scheduler_options, "--wrap", f"'{cmd}'"]
    cmd = [each for each in cmd if bool(each)]
    return cmd


def get_hostname_from_scontrol(stdout: str) -> str:
    return stdout.split("BatchHost=")[1].splitlines()[0].strip()


def get_state_from_scontrol(stdout: str) -> str:
    return stdout.split("JobState=")[1].splitlines()[0].strip()


def check_mapdl_launch_on_hpc(
    process: subprocess.Popen, start_parm: Dict[str, str]
) -> int:
    """Check if the job is ready on the HPC

    Check if the job has been successfully submitted, and additionally, it does
    retrieve the BathcHost hostname which is the IP to connect to using the gRPC
    interface.

    Parameters
    ----------
    process : subprocess.Popen
        Process used to submit the job. The stdout is read from there.
    start_parm : Dict[str, str]
        To store the job ID, the BatchHost hostname and IP into.

    Returns
    -------
    int :
        The jobID

    Raises
    ------
    MapdlDidNotStart
        The job submission failed.
    """
    if isinstance(process, tuple):
        stdout, stderr = process
    elif isinstance(process, str):
        stdout = process
        stderr = ""
    else:
        stdout = process.stdout.read().decode()
        stderr = process.stderr.read().decode()

    if "Submitted batch job" not in stdout:
        raise MapdlDidNotStart(
            "PyMAPDL failed to submit the sbatch job:\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )

    jobid = get_jobid(stdout)
    LOG.info(f"HPC job successfully submitted. JobID: {jobid}")
    return jobid


def get_job_info(
    start_parm: Dict[str, str],
    jobid: Optional[int] = None,
    timeout: int = 30,
    ssh_session=None,
):
    """Get job info like BatchHost IP and hostname

    Get BatchHost hostname and ip and stores them in the start_parm argument

    Parameters
    ----------
    start_parm : Dict[str, str]
        Starting parameters for MAPDL.
    jobid : int
        Job ID
    timeout : int
        Timeout for checking if the job is ready. Default checks for
        'start_instance' key in the 'start_parm' argument, if none
        is found, it passes :class:`None` to
        :func:`ansys.mapdl.core.launcher.get_hostname_host_cluster`.
    """
    timeout = timeout or start_parm.get("start_instance")

    jobid = jobid or start_parm["jobid"]

    batch_host, batch_ip = get_hostname_host_cluster(
        jobid, timeout=timeout, ssh_session=ssh_session
    )

    start_parm["ip"] = batch_ip
    start_parm["hostname"] = batch_host
    start_parm["jobid"] = jobid


def kill_job(jobid: int, ssh_session=None):
    """Kill SLURM job"""
    submitter(["scancel", str(jobid)], ssh_session=ssh_session)


def send_scontrol(args: str, ssh_session=None):
    cmd = f"scontrol {args}".split(" ")
    return submitter(cmd, ssh_session=ssh_session)


def submitter(
    cmd: Union[str, List[str]],
    *,
    executable: str = None,
    shell: bool = False,
    cwd: str = None,
    stdin: subprocess.PIPE = None,
    stdout: subprocess.PIPE = None,
    stderr: subprocess.PIPE = None,
    env_vars: dict[str, str] = None,
    ssh_session=None,
):

    if executable:
        if isinstance(cmd, list):
            cmd = [executable] + cmd
        else:
            cmd = [executable, cmd]

    if not stdin:
        stdin = subprocess.DEVNULL
    if not stdout:
        stdout = subprocess.PIPE
    if not stderr:
        stderr = subprocess.PIPE

    # cmd is controlled by the library with generate_mapdl_launch_command.
    # Excluding bandit check.
    if ssh_session:
        with ssh_session as ssh:
            return ssh.submit(cmd, cwd, env_vars)

    else:
        return subprocess.Popen(
            args=cmd,
            shell=shell,  # sbatch does not work without shell.
            cwd=cwd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            env=env_vars,
        )


def check_console_start_parameters(start_parm):
    valid_args = [
        "exec_file",
        "run_location",
        "jobname",
        "nproc",
        "additional_switches",
        "start_timeout",
    ]
    for each in list(start_parm.keys()):
        if each not in valid_args:
            start_parm.pop(each)

    return start_parm
