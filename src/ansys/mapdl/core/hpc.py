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

from functools import wraps
from typing import Any, Dict, Optional, Union

import paramiko
from paramiko.client import SSHClient

from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher import (
    MAPDL_DEFAULT_PORT,
    check_kwargs,
    check_mapdl_launch_on_hpc,
    generate_mapdl_launch_command,
    generate_sbatch_command,
    generate_start_parameters,
    get_cpus,
    get_job_info,
    kill_job,
    launch_grpc,
    pack_arguments,
    pre_check_args,
    set_license_switch,
    set_MPI_additional_switches,
    update_env_vars,
)
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc


def launch_on_remote_hpc(
    hostname: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    exec_file: Optional[str] = None,
    run_location: Optional[str] = None,
    jobname: str = "file",
    *,
    ssh_port: int = 22,
    nproc: Optional[int] = None,
    ram: Optional[Union[int, str]] = None,
    override: bool = False,
    loglevel: str = "ERROR",
    additional_switches: str = "",
    start_timeout: Optional[int] = None,
    port: int = MAPDL_DEFAULT_PORT,
    start_instance: Optional[bool] = None,
    clear_on_connect: bool = True,
    log_apdl: Optional[Union[bool, str]] = None,
    remove_temp_dir_on_exit: bool = False,
    license_type: Optional[bool] = None,
    print_com: bool = False,
    add_env_vars: Optional[Dict[str, str]] = None,
    replace_env_vars: Optional[Dict[str, str]] = None,
    launch_on_hpc: bool = True,
    mapdl_output: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> MapdlGrpc:
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
        Number of processors.  Defaults to ``2``.

    ram : float, optional
        Total size in megabytes of the workspace (memory) used for the initial
        allocation. The default is :class:`None`, in which case 2 GB (2048 MB) is
        used. To force a fixed size throughout the run, specify a negative
        number.

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

    start_instance : bool, optional
        When :class:`False`, connect to an existing MAPDL instance at ``ip``
        and ``port``, which default to ip ``'127.0.0.1'`` at port ``50052``.
        Otherwise, launch a local instance of MAPDL. You can also
        provide this value through the environment variable
        :envvar:`PYMAPDL_START_INSTANCE`.
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
    """
    ########################################
    # Processing arguments
    # --------------------
    #
    # packing arguments
    args = pack_arguments(locals())  # packs args and kwargs

    args["session_ssh"] = SshSession(
        hostname=hostname,
        username=username,
        password=password,
        port=ssh_port,
    )

    check_kwargs(args)  # check if passing wrong arguments

    args["start_instance"] = True
    args["version"] = None

    if args.get("ip", None):
        raise ValueError("Argument IP is not allowed for launching MAPDL on HPC.")

    pre_check_args(args)

    get_cpus(args)

    ########################################
    # Local adjustments
    # -----------------
    #
    # Only when starting MAPDL (aka Local)
    if not args.get("exec_file"):
        raise ValueError("The 'exec_file' argument must be provided.")

    args["additional_switches"] = set_license_switch(
        args["license_type"], args["additional_switches"]
    )

    env_vars: Dict[str, str] = update_env_vars(
        args["add_env_vars"], args["replace_env_vars"]
    )

    get_run_location_hpc(args)

    # Check for a valid connection mode
    args.setdefault("mode", "grpc")
    if args["mode"] != "grpc":
        raise ValueError(
            "Only gRPC mode is allowed for launching MAPDL on an SLURM HPC."
        )

    ########################################
    # Context specific launching adjustments
    # --------------------------------------
    #
    # Set compatible MPI
    args["additional_switches"] = set_MPI_additional_switches(
        args["additional_switches"],
        force_intel=args["force_intel"],
        version=args["version"],
    )

    LOG.debug(f"Using additional switches {args['additional_switches']}.")

    if args["launch_on_hpc"]:
        env_vars.setdefault("ANS_MULTIPLE_NODES", "1")
        env_vars.setdefault("HYDRA_BOOTSTRAP", "slurm")
        env_vars.setdefault("I_MPI_SHM_LMT", "shm")  # ubuntu

    start_parm = generate_start_parameters(args)

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

    cmd = generate_sbatch_command(cmd, scheduler_options=args.get("scheduler_options"))

    try:
        #
        process = launch_grpc(
            cmd=cmd,
            run_location=args["run_location"],
            env_vars=env_vars,
            launch_on_hpc=args.get("launch_on_hpc"),
            mapdl_output=args.get("mapdl_output"),
            ssh_session=args["session_ssh"],
        )

        start_parm["jobid"] = check_mapdl_launch_on_hpc(process, start_parm)
        get_job_info(
            start_parm=start_parm,
            timeout=args["start_timeout"],
            ssh_session=args["session_ssh"],
        )

    except Exception as exception:
        LOG.error("An error occurred when launching MAPDL.")

        jobid: int = start_parm.get("jobid", "Not found")

        if (
            args["launch_on_hpc"]
            and start_parm.get("finish_job_on_exit", True)
            and jobid not in ["Not found", None]
        ):
            LOG.debug(f"Killing HPC job with id: {jobid}")
            kill_job(jobid, ssh_session=args["session_ssh"])

        raise exception

        ########################################
        # Connect to MAPDL using gRPC
        # ---------------------------
        #
    try:
        mapdl = MapdlGrpc(
            cleanup_on_exit=False,
            loglevel=args["loglevel"],
            set_no_abort=args["set_no_abort"],
            remove_temp_dir_on_exit=False,
            log_apdl=args["log_apdl"],
            # process=process,
            use_vtk=args["use_vtk"],
            **start_parm,
        )
        mapdl._ssh_session = args["session_ssh"]

    except Exception as exception:
        LOG.error("An error occurred when connecting to MAPDL.")
        raise exception

    return mapdl


class SshSession:

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 22,
        allow_missing_host_key: bool = False,
    ):
        self.username = username
        self.hostname = hostname
        self.password = password
        self.port = port
        self.allow_missing_host_key = allow_missing_host_key
        self._connected = False

    def __enter__(self):
        self.session = SSHClient()
        if self.allow_missing_host_key:
            self.session.set_missing_host_key_policy(
                paramiko.WarningPolicy()
            )  # nosec B507
        else:
            self.session.set_missing_host_key_policy(paramiko.RejectPolicy())

        self.session.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
        )
        self._connected = True
        return self

    def __exit__(self, *args) -> None:
        self.session.close()
        self._connected = False

    @wraps(SSHClient.exec_command)
    def exec_command(self, *args, **kwargs):
        if not self._connected:
            raise Exception("ssh session is not connected")
        stdin, stdout, stderr = self.session.exec_command(*args, **kwargs)  # nosec B601
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        return stdin, output, error

    def run(self, cmd, environment=None):
        if not self._connected:
            raise Exception("ssh session is not connected")
        if isinstance(cmd, list):
            cmd = " ".join(cmd)

        LOG.debug(cmd)
        _, stdout, stderr = self.exec_command(
            command=cmd, environment=environment
        )  # nosec B78

        if stderr:
            raise Exception(f"ERROR: {stderr}")

        return stdout, stderr

    def submit(self, cmd, cwd, environment):
        try:
            if cwd:
                self.run(f"mkdir -p {cwd}")
                cmd = f"cd {cwd};{cmd}"

            return self.run(cmd, environment=environment)

        except Exception as e:
            raise Exception(f"Unexpected error occurred: {e}")
        finally:
            self.session.close()


def get_run_location_hpc(args: Dict[str, Any]) -> None:
    if args["run_location"] is None:
        args["run_location"] = (
            f"/home/{args['session_ssh'].username}/pymapdl/simulations"
        )

        LOG.debug(
            f"Using default temporary directory for MAPDL run location: {args['run_location']}"
        )
