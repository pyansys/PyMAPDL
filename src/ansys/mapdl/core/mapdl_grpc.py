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

"""A gRPC specific class and methods for the MAPDL gRPC client"""

import fnmatch
from functools import wraps
import glob
import io
import json
import os
import pathlib
import re
import shutil
import socket

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
import subprocess  # nosec B404
import tempfile
import threading
import time
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union
from uuid import uuid4
from warnings import warn
import weakref

from ansys.tools.versioning.utils import version_string_as_tuple
import grpc
from grpc._channel import _InactiveRpcError, _MultiThreadedRendezvous
import numpy as np
from numpy.typing import NDArray
import psutil

MSG_IMPORT = """There was a problem importing the ANSYS MAPDL API module `ansys-api-mapdl`.
Please make sure you have the latest updated version using:

'pip install ansys-api-mapdl' or 'pip install --upgrade ansys-api-mapdl'

If this does not solve it, please reinstall 'ansys.mapdl.core'
or contact Technical Support at 'https://github.com/ansys/pymapdl'."""

from ansys.mapdl import core as pymapdl

try:
    from ansys.api.mapdl.v0 import ansys_kernel_pb2 as anskernel
    from ansys.api.mapdl.v0 import mapdl_pb2 as pb_types
    from ansys.api.mapdl.v0 import mapdl_pb2_grpc as mapdl_grpc
except ImportError:  # pragma: no cover
    raise ImportError(MSG_IMPORT)

from ansys.mapdl.core import _HAS_TQDM, __version__
from ansys.mapdl.core.common_grpc import (
    ANSYS_VALUE_TYPE,
    DEFAULT_CHUNKSIZE,
    DEFAULT_FILE_CHUNK_SIZE,
    parse_chunks,
)
from ansys.mapdl.core.errors import (
    MapdlConnectionError,
    MapdlError,
    MapdlExitedError,
    MapdlRuntimeError,
    protect_from,
    protect_grpc,
)
from ansys.mapdl.core.mapdl import MapdlBase
from ansys.mapdl.core.mapdl_types import KwargDict, MapdlFloat, MapdlInt
from ansys.mapdl.core.misc import (
    check_valid_ip,
    last_created,
    only_numbers_and_dots,
    random_string,
    run_as,
    supress_logging,
)
from ansys.mapdl.core.parameters import interp_star_status

# Checking if tqdm is installed.
# If it is, the default value for progress_bar is true.
if _HAS_TQDM:
    from tqdm import tqdm

if TYPE_CHECKING:  # pragma: no cover
    from queue import Queue

    from ansys.platform.instancemanagement import Instance as PIM_Instance

    from ansys.mapdl.core.database import MapdlDb
    from ansys.mapdl.core.xpl import ansXpl

TMP_VAR = "__tmpvar__"
VOID_REQUEST = anskernel.EmptyRequest()

# Default 256 MB message length
MAX_MESSAGE_LENGTH = int(os.environ.get("PYMAPDL_MAX_MESSAGE_LENGTH", 256 * 1024**2))

VAR_IR = 9  # Default variable number for automatic variable retrieving (/post26)


SESSION_ID_NAME = "__PYMAPDL_SESSION_ID__"

DEFAULT_TIME_STEP_STREAM = None
DEFAULT_TIME_STEP_STREAM_NT = 500
DEFAULT_TIME_STEP_STREAM_POSIX = 100

# Retry policy for gRPC calls.
SERVICE_DEFAULT_CONFIG = {
    # see https://github.com/grpc/proposal/blob/master/A6-client-retries.md#retry-policy-capabilities
    "methodConfig": [
        {
            # Match all packages and services.
            # Otherwise: "name": [{"service": "<package>.<service>"}],
            "name": [{}],
            "retryPolicy": {
                "maxAttempts": 5,
                "initialBackoff": "0.01s",
                "maxBackoff": "3s",
                "backoffMultiplier": 3,
                "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"],
            },
        }
    ]
}


def get_start_instance(*args, **kwargs) -> bool:
    """Wraps get_start_instance to avoid circular imports"""
    from ansys.mapdl.core.launcher import get_start_instance

    return get_start_instance(*args, **kwargs)


def chunk_raw(raw, save_as):
    with io.BytesIO(raw) as f:
        while True:
            piece = f.read(DEFAULT_FILE_CHUNK_SIZE)
            length = len(piece)
            if length == 0:
                return
            yield pb_types.UploadFileRequest(
                file_name=os.path.basename(save_as),
                chunk=anskernel.Chunk(payload=piece, size=length),
            )


def get_file_chunks(filename, progress_bar=False):
    """Serializes a file into chunks"""
    pbar = None
    if progress_bar:
        if not _HAS_TQDM:  # pragma: no cover
            raise ModuleNotFoundError(
                "To use the keyword argument 'progress_bar', you need to have "
                "installed the `tqdm` package. "
                "To avoid this message set `progress_bar=False`."
            )

        n_bytes = os.path.getsize(filename)

        base_name = os.path.basename(filename)
        pbar = tqdm(
            total=n_bytes,
            desc=f"Uploading {base_name}",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

    with open(filename, "rb") as f:
        while True:
            piece = f.read(DEFAULT_FILE_CHUNK_SIZE)
            length = len(piece)
            if length == 0:
                if pbar is not None:
                    pbar.close()
                return

            if pbar is not None:
                pbar.update(length)

            chunk = anskernel.Chunk(payload=piece, size=length)
            yield pb_types.UploadFileRequest(
                file_name=os.path.basename(filename), chunk=chunk
            )


def save_chunks_to_file(
    chunks, filename, progress_bar=False, file_size=None, target_name=""
):
    """Saves chunks to a local file

    Returns
    -------
    file_size : int
        File size saved in bytes.  ``0`` means no file was written.
    """
    pbar = None
    if progress_bar:
        if not _HAS_TQDM:  # pragma: no cover
            raise ModuleNotFoundError(
                f"To use the keyword argument 'progress_bar', you need to have installed the 'tqdm' package."
                "To avoid this message you can set 'progress_bar=False'."
            )

        pbar = tqdm(
            total=file_size,
            desc="Downloading %s" % target_name,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

    file_size = 0
    with open(filename, "wb") as f:
        for chunk in chunks:
            f.write(chunk.payload)
            payload_size = len(chunk.payload)
            file_size += payload_size
            if pbar is not None:
                pbar.update(payload_size)

    if pbar is not None:
        pbar.close()

    return file_size


class MapdlGrpc(MapdlBase):
    """This class connects to a GRPC MAPDL server and allows commands
    to be passed to a persistent session.

    Parameters
    ----------
    ip : str, optional
        IP address to connect to the server.  The default is 'localhost'.

    port : int, optional
        Port to connect to the MAPDL server.  The default is ``50052``.

    timeout : float, optional
        Maximum allowable time to connect to the MAPDL server.

    loglevel : str, optional
        Sets which messages are printed to the console.  Default
        'INFO' prints out all ANSYS messages, 'WARNING` prints only
        messages containing ANSYS warnings, and 'ERROR' prints only
        error messages.

    cleanup_on_exit : bool, optional
        Exit MAPDL when Python exits or when this instance is garbage
        collected.

    set_no_abort : bool, optional
        Sets MAPDL to not abort at the first error within /BATCH mode.
        The default is ``True``.

    remove_temp_dir : bool, optional
        When this parameter is ``True``, the MAPDL working directory will be
        deleted when MAPDL is exited provided that it is within the temporary
        user directory. The default is ``False``.

    log_file : bool, optional
        Copy the log to a file called `logs.log` located where the
        python script is executed. The default is ``True``.

    print_com : bool, optional
        Print the command ``/COM`` arguments to the standard output.
        The default is ``False``.

    disable_run_at_connect: bool, optional
        Whether to disable the housekeeping commands when connecting.
        The default is ``False``.

    channel : grpc.Channel, optional
        gRPC channel to use for the connection. This parameter can be
        used as an alternative to the ``ip`` and ``port`` parameters.

    remote_instance : ansys.platform.instancemanagement.Instance
        The corresponding remote instance when MAPDL is launched through
        PyPIM. This instance will be deleted when calling
        :func:`Mapdl.exit <ansys.mapdl.core.Mapdl.exit>`.

    file_type_for_plots: ["PNG", "TIFF", "PNG", "VRML", "TERM"], Optional
        Change the default file type for plots using ``/SHOW``, by
        default it is ``PNG``.


    Examples
    --------
    Connect to an instance of MAPDL already running on locally on the
    default port 50052.

    >>> from ansys.mapdl import core as pymapdl
    >>> mapdl = pymapdl.Mapdl()

    Connect to an instance of MAPDL running on the LAN on a default port.

    >>> mapdl = pymapdl.Mapdl('192.168.1.101')

    Connect to an instance of MAPDL running on the LAN on a non-default port.

    >>> mapdl = pymapdl.Mapdl('192.168.1.101', port=60001)

    If you wish to customize the channel, you can also directly connect
    directly to gRPC channels. For example, if you wanted to create an insecure
    channel with a maximum message length of 8 MB.

    >>> import grpc
    >>> channel = grpc.insecure_channel(
    ...     '127.0.0.1:50052',
    ...     options=[
    ...         ("grpc.max_receive_message_length", 8*1024**2),
    ...     ],
    ... )
    >>> mapdl = pymapdl.Mapdl(channel=channel)

    """

    # Required by `_name` method to be defined before __init__ be
    _ip = None
    _port = None

    def __init__(
        self,
        ip: Optional[str] = None,
        port: Optional[MapdlInt] = None,
        timeout: int = 15,
        loglevel: str = "WARNING",
        log_file: bool = False,
        cleanup_on_exit: bool = False,
        log_apdl: Optional[str] = None,
        set_no_abort: bool = True,
        remove_temp_dir_on_exit: bool = False,
        print_com: bool = False,
        disable_run_at_connect: bool = False,
        channel: Optional[grpc.Channel] = None,
        remote_instance: Optional["PIM_Instance"] = None,
        **start_parm,
    ):
        """Initialize connection to the mapdl server"""
        self._name: Optional[str] = None
        self._session_id_: Optional[str] = None
        self._checking_session_id_: bool = False
        self.__distributed: Optional[bool] = None
        self._remote_instance: Optional["PIM_Instance"] = remote_instance
        self._strict_session_id_check: bool = (
            False  # bool to force to check the session id matches in client and server
        )

        if channel is not None:
            if ip is not None or port is not None:
                raise ValueError(
                    "If `channel` is specified, neither `port` nor `ip` can be specified."
                )
        if ip is None:
            ip = start_parm.pop("ip", None) or "127.0.0.1"

        # setting hostname
        if not only_numbers_and_dots(ip):
            # it is a hostname
            self._hostname = ip
            ip = socket.gethostbyname(ip)
        else:
            # it is an IP
            self._hostname = (
                "localhost"
                if ip in ["127.0.0.1", "127.0.1.1", "localhost"]
                else socket.gethostbyaddr(ip)[0]
            )

        check_valid_ip(ip)
        self._ip: str = ip

        # port and ip are needed to setup the log
        if port is None:
            from ansys.mapdl.core.launcher import MAPDL_DEFAULT_PORT

            port = MAPDL_DEFAULT_PORT

        self._port: int = int(port)
        start_parm["port"] = self._port  # store for `open_gui`

        super().__init__(
            loglevel=loglevel,
            log_apdl=log_apdl,
            log_file=log_file,
            print_com=print_com,
            mode="grpc",
            **start_parm,
        )
        self._mode: Literal["grpc"] = "grpc"

        # gRPC request specific locks as these gRPC request are not thread safe
        self._vget_lock: bool = False
        self._get_lock: bool = False

        self._prioritize_thermal: bool = False
        self._locked: bool = False  # being used within MapdlPool
        self._stub: Optional[mapdl_grpc.MapdlServiceStub] = None
        self._cleanup: bool = cleanup_on_exit
        self.remove_temp_dir_on_exit: bool = remove_temp_dir_on_exit
        self._jobname: str = start_parm.get("jobname", "file")
        self._path: Optional[str] = start_parm.get("run_location", None)
        self._start_instance: Optional[str] = (
            start_parm.get("start_instance") or get_start_instance()
        )
        self._busy: bool = False  # used to check if running a command on the server
        self._local: bool = start_parm.get("local", True)
        self._launched: bool = start_parm.get("launched", False)
        self._health_response_queue: Optional["Queue"] = None
        self._exiting: bool = False
        self._exited: Optional[bool] = None
        self._db: Optional[MapdlDb] = None
        self.__server_version: Optional[str] = None
        self._state: Optional[grpc.Future] = None
        self._timeout: int = timeout
        self._env_vars: Dict[str, str] = start_parm.get("env_vars", {})
        self._pids: List[Union[int, None]] = []
        self._channel_state: grpc.ChannelConnectivity = (
            grpc.ChannelConnectivity.CONNECTING
        )

        if channel is None:
            self._log.debug("Creating channel to %s:%s", ip, port)
            self._channel: grpc.Channel = self._create_channel(ip, port)
        else:
            self._log.debug("Using provided channel")
            self._channel: grpc.Channel = channel

        # Subscribe to channel for channel state updates
        self._subscribe_to_channel()

        # connect and validate to the channel
        self._mapdl_process: subprocess.Popen = start_parm.pop("process", None)

        # saving for later use (for example open_gui)
        self._start_parm: Dict[str, Any] = start_parm

        # Storing HPC related stuff
        self._jobid: int = start_parm.get("jobid")
        self._mapdl_on_hpc: bool = bool(self._jobid)
        self.finish_job_on_exit: bool = start_parm.get("finish_job_on_exit", True)

        # Queueing the stds
        if not self._mapdl_on_hpc and self._mapdl_process:
            self._create_process_stds_queue()

        try:
            self._multi_connect(timeout=timeout)
        except MapdlConnectionError as err:  # pragma: no cover
            self._post_mortem_checks()
            self._log.debug(
                "The error wasn't caught by the post-mortem checks.\nThe stdout is printed now:"
            )
            self._log.debug(self._stdout)

            raise err  # Raise original error if we couldn't catch it in post-mortem analysis
        else:
            self._log.debug("Connection established")

        # Avoiding muting when connecting to the session
        # It might trigger some errors later on if not.
        self._run("/gopr")

        # initialize mesh, post processing, and file explorer interfaces
        self._mesh_rep: Optional["MeshGrpc"] = None

        from ansys.mapdl.core.mesh_grpc import MeshGrpc

        self._mesh_rep = MeshGrpc(self)

        # Run at connect
        if not disable_run_at_connect:
            self._run_at_connect()

        # HOUSEKEEPING:
        # Set to not abort after encountering errors.  Otherwise, many
        # failures in a row will cause MAPDL to exit without returning
        # anything useful.  Also avoids abort in batch mode if set.
        if set_no_abort:
            self._set_no_abort()

        # double check we have access to the local path if not
        # explicitly specified
        if "local" not in start_parm:
            self._verify_local()

        # only cache process IDs if launched locally
        if self._local and "exec_file" in start_parm:
            self._cache_pids()

        self._create_session()

    def _after_run(self, command: str) -> None:
        if command[:4].upper() == "/CLE":
            # We have reset the database, so we need to create a new session id
            self._create_session()

    def _before_run(self, _command: str) -> None:
        if self._session_id is not None:
            self._check_session_id()
        else:
            # For some reason the session hasn't been created
            self._create_session()

    def _create_process_stds_queue(self, process=None):
        from ansys.mapdl.core.launcher import (
            _create_queue_for_std,  # Avoid circular import error
        )

        if not process:
            process = self._mapdl_process

        self._stdout_queue, self._stdout_thread = _create_queue_for_std(process.stdout)
        self._stderr_queue, self._stderr_thread = _create_queue_for_std(process.stderr)

    def _create_channel(self, ip: str, port: int) -> grpc.Channel:
        """Create an insecured grpc channel."""

        # open the channel
        channel_str = f"{ip}:{port}"
        self._log.debug("Opening insecure channel at %s", channel_str)
        return grpc.insecure_channel(
            channel_str,
            options=[
                ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
                ("grpc.service_config", json.dumps(SERVICE_DEFAULT_CONFIG)),
            ],
        )

    def _subscribe_to_channel(self):
        """Subscribe to channel status and store the value in 'mapdl._channel_state'"""

        # Callback function to monitor state changes
        def connectivity_callback(connectivity):
            self._log.debug(f"Channel connectivity changed to: {connectivity}")
            self._channel_state = connectivity

        # Subscribe to channel state changes
        self._channel.subscribe(connectivity_callback, try_to_connect=True)

    @property
    def channel_state(self) -> str:
        """Returns the gRPC channel state.

        The possible values are:

        - 0 - 'IDLE'
        - 1 - 'CONNECTING'
        - 2 - 'READY'
        - 3 - 'TRANSIENT_FAILURE'
        - 4 - 'SHUTDOWN'
        """
        return self._channel_state.name

    def _multi_connect(self, n_attempts=5, timeout=15):
        """Try to connect over a series of attempts to the channel.

        Parameters
        ----------
        n_attempts : int, optional
            Number of connection attempts.
        timeout : float, optional
            Total timeout.

        """
        # This prevents a single failed connection from blocking other attempts
        connected = False
        attempt_timeout = int(timeout / n_attempts)

        max_time = time.time() + timeout
        i = 1
        while time.time() < max_time and i <= n_attempts:
            self._log.debug("Connection attempt %d", i)
            connected = self._connect(timeout=attempt_timeout)
            i += 1
            if connected:
                self._log.debug("Connected")
                break
        else:
            # Check if mapdl process is alive
            msg = (
                f"Unable to connect to MAPDL gRPC instance at {self._channel_str}.\n"
                f"Reached either maximum amount of connection attempts ({n_attempts}) or timeout ({timeout} s)."
            )

            if self._mapdl_process is not None and psutil.pid_exists(
                self._mapdl_process.pid
            ):
                # Process is alive
                raise MapdlConnectionError(
                    msg
                    + f"The MAPDL process seems to be alive (PID: {self._mapdl_process.pid}) but PyMAPDL cannot connect to it."
                )
            else:
                pid_msg = (
                    f" PID: {self._mapdl_process.pid}"
                    if self._mapdl_process is not None
                    else ""
                )
                raise MapdlConnectionError(
                    msg + f" The MAPDL process has died{pid_msg}."
                )

        self._exited = False

    def _is_alive_subprocess(self):
        """Returns:
        * True if the PID is alive.
        * False if it is not.
        * None if there was no process
        """
        if self._mapdl_process:
            return psutil.pid_exists(self._mapdl_process.pid)

    @property
    def process_is_alive(self):
        """Check if the MAPDL process is alive"""
        return self._is_alive_subprocess()

    def _post_mortem_checks(self, process=None):
        """Check possible reasons for not having a successful connection."""
        # Check early exit
        if process is None:
            process = self._mapdl_process

        if process is None or not self.is_grpc:
            return

        # check the stdout for any errors
        self._read_stds()

        self._check_stds()

    def _read_stds(self):
        """Read the stdout and stderr from the subprocess."""
        from ansys.mapdl.core.launcher import _get_std_output

        if self._mapdl_process is None or not self._mapdl_process.stdout:
            return

        self._log.debug("Reading stdout")
        self._stdout = _get_std_output(self._stdout_queue)
        self._log.debug(f"Read stdout: {self._stdout[:20]}")

        self._log.debug("Reading stderr")
        self._stderr = _get_std_output(self._stderr_queue)
        self._log.debug(f"Read stderr: {self._stderr[:20]}")

    def _check_stds(self, stdout=None, stderr=None):
        """Check the stdout and stderr for any errors."""
        if stdout is None:
            stdout = self._stdout
        if stderr is None:
            stderr = self._stderr

        if not stderr:
            self._log.debug("MAPDL exited without stderr.")
        else:
            self._parse_stderr()

        if not stdout:
            self._log.debug("MAPDL exited without stdout.")
        else:
            self._parse_stdout()

    def _parse_stderr(self, stderr=None):
        """Parse the stderr for any errors."""
        if stderr is None:
            stderr = self._stderr
        errs = self._parse_std(stderr)
        if errs:
            self._log.debug("MAPDL exited with errors in stderr.")

            # Custom errors
            self._raise_custom_stds_errors(errs)

    def _parse_stdout(self, stdout=None):
        """Parse the stdout for any errors."""
        if stdout is None:
            stdout = self._stdout
        errs = self._parse_std(stdout)
        if errs:
            self._log.debug("MAPDL exited with errors in stdout.")

            # Custom errors
            self._raise_custom_stds_errors(errs)

    def _parse_std(self, std):
        # check for errors in stderr
        # split the stderr into groups
        if isinstance(std, list):
            std = "\n".join(std)
            std = std.replace("\n\n", "\n")
        groups = std.split("\r\n\r\n")
        errs = []

        for each in groups:
            if (
                "error" in each.lower()
                or "fatal" in each.lower()
                or "warning" in each.lower()
            ):
                errs.append(each)

        if errs:
            errs = "\r\n\r\n".join(errs)
            errs = errs.replace("\r\n", "\n")
        else:
            errs = ""
        return errs

    def _raise_custom_stds_errors(self, errs_message):
        """Custom errors for stdout and stderr."""
        if "Only one usage of each socket address" in errs_message:
            raise MapdlConnectionError(
                f"A process is already running on the specified port ({self._port}).\n"
                "Only one usage of each socket address (protocol/network address/port) is normally permitted.\n"
                f"\nFull error message:\n{errs_message.split('########', 1)[0]}"
            )

        else:
            raise MapdlConnectionError(errs_message)

    @property
    def _channel_str(self):
        """Return the target string.

        Generally of the form of "ip:port", like "127.0.0.1:50052".

        """
        channel = self._channel
        while channel is not None:
            # When creating interceptors, channels have a nested "_channel" member
            # containing the intercepted channel.
            # Only the actual channel contains the "target" member describing the address
            if hasattr(channel, "target"):
                return channel.target().decode()
            channel = getattr(channel, "_channel", None)
        # This method is relying on grpc channel's private attributes, fallback in case
        # it does not exist
        return "unknown"  #  pragma: no cover Unreachable in the current gRPC version

    def _verify_local(self):
        """Check if Python is local to the MAPDL instance."""
        # Verify if python has assess to the MAPDL directory.
        if self._local:
            directory = self.directory

            if self._jobname is None:
                jobname = self.jobname
            else:
                jobname = self._jobname

            lockfile = os.path.join(directory, jobname + ".err")
            lockfile0 = os.path.join(directory, jobname + "0.err")
            if os.path.isfile(lockfile):
                return
            if os.path.isfile(lockfile0):
                return
            self._local = False

    @property
    def mute(self):
        """Silence the response from all MAPDL functions unless
        explicitly set to ``True``.

        Returns
        -------
        bool
            Current state of the mute.

        Examples
        --------
        >>> mapdl.mute = True
        >>> mapdl.prep7()
        ''

        Temporarily override the instance setting this with
        ``mute=False``.  This is useful for methods that parse the
        MAPDL output like ``k``.

        >>> mapdl.k('', 1, 1, 1, mute=False)
        1

        """
        return self._mute

    @mute.setter
    def mute(self, value):
        self._mute = value

    def __repr__(self):
        info = super().__repr__()
        return info

    def _connect(self, timeout=5):
        """Establish a gRPC channel to a remote or local MAPDL instance.

        Parameters
        ----------
        timeout : float
            Time in seconds to wait until the connection has been established
        """
        self._state = grpc.channel_ready_future(self._channel)
        self._stub = mapdl_grpc.MapdlServiceStub(self._channel)

        # verify connection
        tstart = time.time()
        while ((time.time() - tstart) < timeout) and not self._state._matured:
            time.sleep(0.01)

        if not self._state._matured:  # pragma: no cover
            return False
        self._log.debug("Established connection to MAPDL gRPC")

        # keeps mapdl session alive
        self._timer = None
        if not self._local:
            self._initialised = threading.Event()
            self._t_trigger = time.time()
            self._t_delay = 30
            self._timer = threading.Thread(
                target=MapdlGrpc._threaded_heartbeat,
                args=(weakref.proxy(self),),
            )
            self._timer.daemon = True
            self._timer.start()

        return True

    @property
    def _server_version(self):
        """Return the server version.

        Examples
        --------
        >>> mapdl._server_version
        (0, 3, 0)

        Uses cached ``__server_version`` to avoid unnecessary communication.
        """
        # check cache
        if self.__server_version is None:
            self.__server_version = self._get_server_version()
        return self.__server_version

    def _get_server_version(self):
        """Request version from gRPC server.

        Generally tied to the release version unless on a development release.

        2020R2 --> 0.0.0 (or any unknown version)
        2021R1 --> 0.3.0
        2021R2 --> 0.4.0
        2022R1 --> 0.X.X

        """
        sver = (0, 0, 0)
        verstr = self._ctrl("VERSION")
        if verstr:
            sver = version_string_as_tuple(verstr)
        return sver

    def _launch(self, start_parm, timeout=10):
        """Launch a local session of MAPDL in gRPC mode.

        This should only need to be used for legacy ``open_gui``
        """
        if not self._local:
            raise MapdlRuntimeError(
                "Can only launch the GUI with a local instance of MAPDL"
            )
        from ansys.mapdl.core.launcher import generate_mapdl_launch_command, launch_grpc

        self._exited = False  # reset exit state

        args = self._start_parm
        cmd = generate_mapdl_launch_command(
            exec_file=args["exec_file"],
            jobname=args["jobname"],
            nproc=args["nproc"],
            ram=args["ram"],
            port=args["port"],
            additional_switches=args["additional_switches"],
        )

        process = launch_grpc(
            cmd=cmd, run_location=args["run_location"], env_vars=self._env_vars or None
        )

        self._connect(args["port"])

        # may need to wait for viable connection in open_gui case
        tmax = time.time() + timeout
        success = False
        while time.time() < tmax:
            try:
                self.prep7()
                success = True
                break
            except MapdlRuntimeError:
                time.sleep(1)
                warn("PyMAPDL is taking longer than expected to connect to the server.")

        if not success:
            raise MapdlConnectionError("Unable to reconnect to MAPDL")

        # Update process
        self._mapdl_process = process

    @supress_logging
    def _set_no_abort(self):
        """Do not abort MAPDL."""
        self.nerr(abort=-1, mute=True)

    def _run_at_connect(self):
        """Run house-keeping commands when initially connecting to MAPDL."""
        # increase the number of variables allowed in POST26 to the maximum
        with self.run_as_routine("Begin level"):
            self._run("/verify", mute=False)

        with self.run_as_routine("POST26"):
            self.numvar(200, mute=True)

        # Caching directory
        self.directory

        self.show(self._file_type_for_plots)
        self.version  # Caching version
        self.file_type_for_plots  # Setting /show,png and caching it.

    def _reset_cache(self):
        """Reset cached items."""
        if self._mesh_rep is not None:
            self._mesh_rep._reset_cache()

        if self._geometry is not None:
            self._geometry._reset_cache()

    @property
    def _mesh(self):
        return self._mesh_rep

    def _run(self, cmd: str, verbose: bool = False, mute: Optional[bool] = None) -> str:
        """Sens a command and return the response as a string.

        Parameters
        ----------
        cmd : str
            Valid MAPDL command.

        verbose : bool, optional
            Print the response of a command while it is being run.

        mute : bool, optional
            Whether output is to be sent from the gRPC server. The default
            is ``None``, in which case the global setting specified by
            ``mapdl.mute = <bool>`` is used, which is ``False`` by default.

        Examples
        --------
        Run a basic command.

        >>> mapdl.run('/PREP7')

        Run a command and suppress its output.

        >>> mapdl.run('/PREP7', mute=True)

        Run a command and stream its output while it is being run.

        >>> mapdl.run('/PREP7', verbose=True)

        """
        if mute is None:
            mute = self._mute

        if self._exited:
            raise MapdlExitedError(
                f"The MAPDL instance has been exited before running the command: {cmd}"
            )

        # don't allow empty commands
        if not cmd.strip():
            raise ValueError("Empty commands not allowed")

        if len(cmd) > 639:  # CMD_MAX_LENGTH
            raise ValueError("Maximum command length must be less than 640 characters")

        self._busy = True
        if verbose:
            response = self._send_command_stream(cmd, True)
        else:
            response = self._send_command(cmd, mute=mute)
        self._busy = False

        return response.strip()

    @property
    def busy(self) -> bool:
        """True when MAPDL gRPC server is executing a command."""
        return self._busy

    @property
    def exiting(self) -> bool:
        """Returns true if the MAPDL instance is exiting."""
        return self._exiting

    @property
    def port(self) -> int:
        """Returns the MAPDL gRPC instance port."""
        return self._port

    @property
    def ip(self) -> str:
        """Return the MAPDL gRPC instance IP."""
        return self._ip

    @property
    def hostname(self) -> str:
        """Return the hostname of the machine MAPDL is running in."""
        return self._hostname

    @property
    def jobid(self) -> int:
        """Returns the job id where the MAPDL is running in.
        This is only applicable if MAPDL is running on an HPC cluster."""
        return self._jobid

    @property
    def mapdl_on_hpc(self) -> bool:
        """Returns :class:`True` if the MAPDL instance has been launched using
        an scheduler."""
        return self._mapdl_on_hpc

    @protect_grpc
    def _send_command(self, cmd: str, mute: bool = False) -> Optional[str]:
        """Send a MAPDL command and return the response as a string"""
        opt = ""
        if mute:
            opt = "MUTE"  # suppress any output

        request = pb_types.CmdRequest(command=cmd, opt=opt)
        # TODO: Capture keyboard exception and place this in a thread
        grpc_response = self._stub.SendCommand(request)

        resp = grpc_response.response
        if resp is not None:
            return resp.strip()
        return None

    @protect_grpc
    def _send_command_stream(self, cmd, verbose=False) -> str:
        """Send a command and expect a streaming response"""
        request = pb_types.CmdRequest(command=cmd)
        time_step = self._get_time_step_stream()
        metadata = [("time_step_stream", str(time_step))]
        stream = self._stub.SendCommandS(request, metadata=metadata)
        response = []
        for item in stream:
            cmdout = "\n".join(item.cmdout)
            if verbose:
                print(cmdout)
            response.append(cmdout.strip())

        return "".join(response)

    def _threaded_heartbeat(self):
        """To be called from a thread to verify MAPDL instance is alive"""
        self._initialised.set()
        while True:
            if self._exited:
                break

            try:
                time.sleep(self._t_delay)
                if not self.is_alive:
                    break
            except ReferenceError:
                break
            except Exception:
                self._log.debug("Checking if MAPDL instance is still alive.")

    # Placing logging in the exit method raises exceptions when
    # this is triggered by "__del__"
    @protect_from(ValueError, "I/O operation on closed file.")
    @protect_from(AttributeError, "'MapdlGrpc' object has no attribute '_log'")
    def exit(self, save=False, force=False, **kwargs):
        """Exit MAPDL.

        Parameters
        ----------
        save : bool, optional
            Save the database on exit.  The default is ``False``.
        force : bool, optional
            Override any environment variables that may inhibit exiting MAPDL.

        Notes
        -----
        If Mapdl didn't start the instance, then this will be ignored unless
        ``force=True``.

        If ``PYMAPDL_START_INSTANCE`` is set to ``False`` (generally set in
        remote testing or documentation build), then this will be
        ignored. Override this behavior with ``force=True`` to always force
        exiting MAPDL regardless of your local environment.

        If ``Mapdl.finish_job_on_exit`` is set to ``True`` and there is a valid
        JobID in ``Mapdl.jobid``, then the SLURM job will be canceled.

        Examples
        --------
        >>> mapdl.exit()
        """
        # check if permitted to start (and hence exit) instances
        from ansys.mapdl import core as pymapdl

        self._log.debug(
            f"Exiting MAPLD gRPC instance {self.ip}:{self.port} on '{self._path}'."
        )

        mapdl_path = self._path  # using cached version

        if self._exited:
            # Already exited.
            self._log.debug("Already exited")
            return

        if save:
            self._log.debug("Saving MAPDL database")
            self.save()

        if not force:
            # ignore this method if PYMAPDL_START_INSTANCE=False
            if not self._start_instance or not self._launched:
                self._log.info(
                    "Ignoring exit due to PYMAPDL_START_INSTANCE=False or because PyMAPDL didn't launch the instance."
                )
                return

            # or building the gallery
            if pymapdl.BUILDING_GALLERY:
                self._log.info("Ignoring exit due as BUILDING_GALLERY=True")
                return

        # Exiting MAPDL instance if we launched.
        self._exiting = True
        self._exit_mapdl(path=mapdl_path)
        self._exited = True

        if self.finish_job_on_exit and self._mapdl_on_hpc:
            self.kill_job(self.jobid)
            self._log.debug(f"Job (id: {self.jobid}) has been cancel.")

        # Exiting remote instances
        if self._remote_instance:  # pragma: no cover
            # No cover: The CI is working with a single MAPDL instance
            self._remote_instance.delete()

        self._exiting = False

        # Post-kill tasks
        self._remove_temp_dir_on_exit(mapdl_path)

        if self._local and self._port in pymapdl._LOCAL_PORTS:
            pymapdl._LOCAL_PORTS.remove(self._port)

    def _exit_mapdl(self, path: str = None) -> None:
        """Exit MAPDL and remove the lock file in `path`"""
        # This cannot/should not be faked
        if self._local:
            self._cache_pids()  # Recache processes

            self._exit_mapdl_server()

            self._close_process()

            self._remove_lock_file(path, use_cached=True)
        else:
            self._exit_mapdl_server()

    def _remove_temp_dir_on_exit(self, path=None):
        """Removes the temporary directory created by the launcher.

        This only runs if the current working directory of MAPDL is within the
        user temporary directory.

        """
        if self.remove_temp_dir_on_exit and self._local:
            from pathlib import Path

            path = str(Path(path or self.directory))
            tmp_dir = tempfile.gettempdir()
            ans_temp_dir = str(Path(os.path.join(tmp_dir, "ansys_")))

            if path.startswith(ans_temp_dir):
                self._log.debug("Removing the MAPDL temporary directory %s", path)
                shutil.rmtree(path, ignore_errors=True)
            else:
                self._log.debug(
                    "MAPDL working directory is not in the temporary directory '%s'"
                    ", not removing the MAPDL working directory.",
                    tmp_dir,
                )

    def _exit_mapdl_server(self):
        """Call exit(0) on the server.

        Notes
        -----
        This only shuts down the mapdl server process and leaves the other
        processes orphaned. This is useful for killing a remote process but not
        a local process.

        """
        if self._exited:
            return

        # Default
        if self._version is None or self._version < 24.1:
            self._ctrl("EXIT")

        elif self._version >= 24.1:
            # We can't use the non-cached version because of recursion error.
            # self.run("/EXIT,NOSAVE,,,,,SERVER")
            self.finish()
            self._ctrl("EXIT")

        return

    def _kill_process(self):
        """Kill process stored in self._mapdl_process"""
        if self._mapdl_process is not None:
            self._log.debug("Killing process using subprocess.Popen.terminate")
            process = self._mapdl_process
            if process.poll() is not None:
                # process hasn't terminated
                process.kill()

    def _kill_child_processes(self, timeout=2):
        pids = self._pids.copy()
        pids.reverse()  # First pid is the parent, therefore start by the children (end)

        for pid in pids:
            self._kill_child_process(pid, timeout=timeout)

    def _kill_child_process(self, pid, timeout=2):
        """Kill an individual child process, given a pid."""
        try:
            self._log.debug(f"Killing MAPDL process: {pid}")
            t0 = time.time()
            while time.time() < t0 + timeout:
                if psutil.pid_exists(pid):
                    os.kill(pid, 9)
                    time.sleep(0.5)
                else:
                    self._log.debug(f"Process {pid} killed properly.")
                    break
            else:
                self._log.debug(
                    f"Process {pid} couldn't be killed in {timeout} seconds"
                )

        except OSError:
            self._log.debug(
                f"Failed attempt to kill process: The process with pid {pid} does not exist. Maybe it was already killed?"
            )

        finally:
            if not psutil.pid_exists(pid):
                self._pids.remove(pid)

    def _close_process(self, timeout=2):  # pragma: no cover
        """Close all MAPDL processes.

        Notes
        -----
        This is effectively the only way to completely close down MAPDL locally on
        linux. Just killing the server with ``_exit_mapdl_server`` leaves orphaned
        processes making this method ineffective for a local instance of MAPDL.

        """
        self._log.debug("Closing processes")
        if self._local:
            # killing main process (subprocess)
            self._kill_process()

            # Killing child processes
            self._kill_child_processes(timeout=timeout)

        if self.is_alive:
            raise MapdlRuntimeError("MAPDL could not be exited.")
        else:
            self._log.debug("All MAPDL processes exited")
            self._exited = True

    def _cache_pids(self):
        """Store the process IDs used when launching MAPDL.

        These PIDs are stored in a "cleanup<GUID>.sh/bat" file and are the PIDs
        of the MAPDL process. Killing these kills all dependent MAPDL
        processes.

        """
        self._log.debug("Caching PIDs")
        self._pids = []

        for filename in self.list_files():
            if "cleanup" in filename:  # Linux does not seem to generate this file?
                script = os.path.join(self.directory, filename)
                with open(script) as f:
                    raw = f.read()

                if os.name == "nt":
                    pids = re.findall(r"/pid (\d+)", raw)
                else:
                    pids = set(re.findall(r"-9 (\d+)", raw))
                self._pids = [int(pid) for pid in pids]

        if not self._pids and not self._mapdl_process:
            self._log.debug(
                f"MAPDL process is not provided. PIDs could not be retrieved."
            )
            return
        elif not self._pids:
            # For the cases where the cleanup file is not generated,
            # we relay on the process.
            parent_pid = self._mapdl_process.pid
            try:
                parent = psutil.Process(parent_pid)
            except psutil.NoSuchProcess:
                self._log.debug(f"Parent process does not exist.")
                return

            children = parent.children(recursive=True)

            self._pids = [parent_pid] + [each.pid for each in children]

        self._log.debug(f"Recaching PIDs: {self._pids}")

    def _remove_lock_file(
        self, mapdl_path: str = None, jobname: str = None, use_cached: bool = False
    ):
        """Removes the lock file.

        Necessary to call this as a segfault of MAPDL or exit(0) will
        not remove the lock file.
        """
        if jobname is None and use_cached:
            jobname = self._jobname
        elif jobname is None:
            jobname = self.jobname

        self._log.debug("Removing lock file after exit.")
        if mapdl_path is None:  # pragma: no cover
            mapdl_path = self.directory
        if mapdl_path:
            for lockname in [jobname + ".lock", "file.lock"]:
                lock_file = os.path.join(mapdl_path, lockname)
                if os.path.isfile(lock_file):
                    try:
                        os.remove(lock_file)
                    except OSError:
                        pass

    def list_files(self, refresh_cache: bool = True) -> List[str]:
        """List the files in the working directory of MAPDL.

        Parameters
        ----------
        refresh_cache : bool, optional
            If local, refresh local cache by querying MAPDL for its
            current path.

        Returns
        -------
        list
            List of files in the working directory of MAPDL.

        Examples
        --------
        >>> files = mapdl.list_files()
        >>> for file in files: print(file)
        file.lock
        file0.bat
        file0.err
        file0.log
        file0.page
        file1.err
        file1.log
        file1.out
        file1.page
        """
        if self._local:  # simply return a python list of files
            if refresh_cache:
                local_path = self.directory
            else:
                local_path = self._directory
            if local_path:
                if os.path.isdir(local_path):
                    return os.listdir(local_path)
            return []

        elif self._exited:
            raise MapdlExitedError("Cannot list remote files since MAPDL has exited")

        # this will sometimes return 'LINUX x6', 'LIN', or 'L'
        if "L" in self.parameters.platform[:1]:
            cmd = "ls"
        else:
            cmd = "dir /b /a"

        files = self.sys(cmd).splitlines()
        if not files:
            warn("No files listed")
        return files

    @supress_logging
    def sys(self, cmd, **kwargs):
        """Pass a command string to the operating system.

        APDL Command: /SYS

        Passes a command string to the operating system for execution
        (see the Operations Guide).  Typical strings are system
        commands such as list, copy, rename, etc.  Control returns to
        the ANSYS program after the system procedure is completed.
        ANSYS may not be aware of your specific user environment. For
        example, on Linux this command may not recognize aliases,
        depending on the hardware platform and user environment.

        Parameters
        ----------
        cmd : str
            Command string, up to 639 characters (including blanks,
            commas, etc.). The specified string is passed verbatim to
            the operating system, i.e., no parameter substitution is
            performed.

        Returns
        -------
        str
            Output from the command.

        Examples
        --------
        >>> mapdl.sys('ls')

        """
        # always redirect system output to a temporary file
        tmp_file = f"__tmp_sys_out_{random_string()}__"
        super().sys(f"{cmd} > {tmp_file}", **kwargs)
        if self._local:  # no need to download when local
            with open(os.path.join(self.directory, tmp_file)) as fobj:
                obj = fobj.read()
        else:
            obj = self._download_as_raw(tmp_file).decode()

        self.slashdelete(tmp_file)
        return obj

    def download_result(
        self,
        path: Optional[Union[str, pathlib.Path]] = None,
        progress_bar: bool = False,
        preference: Optional[Literal["rst", "rth"]] = None,
    ) -> str:
        """Download remote result files to a local directory

        Parameters
        ----------
        path : str, Path, optional
          Path where the files are downloaded, by default the current
          python path (``os.getcwd()``)

        progress_bar : bool, optional
          Show the progress bar or not, default to False.

        preference : str
          Preferred type for the result file, which is either ``rst`` or ``rth``.
          This parameter is only required when both files are present. The default is ```None``,
          in which case ``"rst"`` is used.

        Examples
        --------
        Download remote result files into the current working directory

        >>> import os
        >>> mapdl.download_result(os.getcwd())

        """
        if path is None:  # if not path seems to not work in same cases.
            path = os.getcwd()

        def _download(targets: List[str]) -> None:
            for target in targets:
                save_name = os.path.join(path, target)
                self._download(target, save_name, progress_bar=progress_bar)

        if preference:
            if preference not in ["rst", "rth"]:
                raise ValueError("``preference`` must be either 'rst' or 'rth'")

        # result file basename is the jobname
        jobname = self.jobname
        rth_basename = "%s.%s" % (jobname, "rth")
        rst_basename = "%s.%s" % (jobname, "rst")

        remote_files = self.list_files()
        result_file = None

        if self._prioritize_thermal and rth_basename in remote_files:
            result_file = rth_basename
        elif rst_basename in remote_files and rth_basename in remote_files:
            if preference == "rth":
                result_file = rth_basename
            else:
                result_file = rst_basename
        elif rst_basename in remote_files:
            result_file = rst_basename
        elif rth_basename in remote_files:
            result_file = rth_basename

        if result_file:  # found non-distributed result
            save_name = os.path.join(path, result_file)
            self._download(result_file, save_name, progress_bar=progress_bar)
            return save_name

        # otherwise, download all the distributed result files
        if jobname[-1].isnumeric():
            jobname += "_"

        rst_files = []
        rth_files = []
        for filename in remote_files:
            if "rst" in filename and jobname in filename:
                rst_files.append(filename)
            elif "rth" in filename and jobname in filename:
                rth_files.append(filename)

        if self._prioritize_thermal and rth_files:
            targets = rth_files
        else:
            if rst_files and rth_files:
                if preference is None:
                    raise ValueError(
                        "Found both structural and thermal results files."
                        "\nPlease specify which kind to download using:\n"
                        '``preference="rth"`` or ``preference="rst"``'
                    )
                if preference == "rst":
                    targets = rst_files
                elif preference == "rth":
                    targets = rth_files
            elif rst_files:
                preference = "rst"
                targets = rst_files
            elif rth_files:
                preference = "rth"
                targets = rth_files
            else:
                remote_files_str = "\n".join("\t%s" % item for item in remote_files)
                raise FileNotFoundError(
                    "Unable to locate any result file from the "
                    "following remote result files:\n\n" + remote_files_str
                )
        _download(targets)
        return os.path.join(path, jobname + "0." + preference)

    @protect_grpc
    def _ctrl(self, cmd: str, opt1: str = ""):
        """Issue control command to the MAPDL server.

        Available commands:

        - ``EXIT``
            Calls exit(0) on the server.

        - ``set_verb``
            Enables verbose mode on the server.
            In this case, the verbosity level is set using ``opt1`` argument.

        - ``VERSION``
            Returns version string in of the server in the form
            "MAJOR.MINOR.PATCH".  E.g. "0.3.0".  Known versions
            include:

            2020R2 - "0.3.0"
            2021R1 - "0.3.0"
            2021R2 - "0.4.0"

        Unavailable/Flaky:

        - ``time_stats``
            Prints a table for time stats on the server.
            This command appears to be disabled/broken.

        - ``mem-stats``
            To be added

        """
        self._log.debug(f'Issuing CtrlRequest "{cmd}" with option "{opt1}".')
        request = anskernel.CtrlRequest(ctrl=str(cmd), opt1=str(opt1))

        # handle socket closing upon exit
        if cmd.lower() == "exit":
            try:
                # this always returns an error as the connection is closed
                self._stub.Ctrl(request)
            except (_InactiveRpcError, _MultiThreadedRendezvous):
                pass
            return

        resp = self._stub.Ctrl(request)

        if cmd.lower() == "set_verb" and str(opt1) == "0":
            warn("Disabling gRPC verbose ('_ctr') by issuing also '/VERIFY' command.")
            self.run("/verify")

        if hasattr(resp, "response"):
            return resp.response

    @wraps(MapdlBase.cdread)
    def cdread(self, option="", fname="", ext="", fnamei="", exti="", **kwargs):
        """Wraps CDREAD"""
        option = option.strip().upper()

        if option not in ["DB", "SOLID", "COMB"]:
            raise ValueError(
                f'Option "{option}" is not supported.  Please '
                "Input the geometry and mesh files separately "
                r'with "\INPUT" or ``mapdl.input``'
            )
        if option == "ALL":
            raise ValueError(
                f'Option "{option}" is not supported in gRPC mode.  Please '
                "Input the geometry and mesh files separately "
                r'with "\INPUT" or ``mapdl.input``'
            )

        kwargs.setdefault("verbose", False)
        kwargs.setdefault("progress_bar", False)
        kwargs.setdefault("orig_cmd", "CDREAD")
        kwargs.setdefault("cd_read_option", option.upper())

        fname = self._get_file_name(fname, ext, "cdb")
        fname = self._get_file_path(fname, kwargs["progress_bar"])

        self.input(fname, **kwargs)

    @wraps(MapdlBase.tbft)
    def tbft(
        self,
        oper="",
        id_="",
        option1="",
        option2="",
        option3="",
        option4="",
        option5="",
        option6="",
        option7="",
        **kwargs,
    ):
        """Wraps ``MapdlBase.tbft``."""
        extra_info = ""
        if oper.lower() == "eadd":
            # Option 2 is a file and option 4 is the directory.
            # Option 3 is be extension
            option3 = option3.replace(".", "")
            fname = option2 if not option3 else option2 + "." + option3
            filename = os.path.join(option4, fname)

            fname = self._get_file_name(fname=option2, ext=option3)
            if option4:  # if directory is supplied
                fname = os.path.join(option4, fname)

            filename = self._get_file_path(fname, progress_bar=False)

            # since we upload the file, we dont need the full path: not in option2 nor option4.
            if not self._local:
                extra_info = f"PyMAPDL has upload the file {option2} to the MAPDL instance, hence the options for 'TBFT' command have changed."
                option2 = filename
                option3 = ""  # the extension is now included in filename
                option4 = ""

        if extra_info:
            self.com("")
            self._log.debug(extra_info)

        return super().tbft(
            oper,
            id_,
            option1,
            option2,
            option3,
            option4,
            option5,
            option6,
            option7,
            **kwargs,
        )

    @protect_grpc
    def input(
        self,
        fname="",
        ext="",
        dir_="",
        line="",
        log="",
        *,
        verbose=False,
        progress_bar=False,
        time_step_stream=None,
        chunk_size=512,
        orig_cmd="/INP",
        write_to_log=True,
        **kwargs,
    ):
        """Stream a local input file to a remote mapdl instance.
        Stream the response back and deserialize the output.

        .. versionchanged:: 0.65
            From version 0.65 you can use the APDL commands arguments (``ext``, ``dir``, ``line``)
            in within this command.
            However, the gRPC implementation does *not* uses the APDL ``/INPUT`` command,
            rather the gRPC input method with the appropriate configuration to replicate
            ``/INPUT`` behaviour.

        Parameters
        ----------
        fname : str, optional
            MAPDL input file to stream to the MAPDL gRPC server.
            File name and directory path.
            An unspecified directory path defaults to the Python working
            directory; in this case, you can use all 248 characters for the file name.
            The file name defaults to the current ``Jobname`` if ``Ext`` is specified.

        ext : str, optional
            Filename extension (eight-character maximum).

        dir : str, optional
            Directory path. The default is the current working directory.

        line : int, optional
            A value indicating either a line number in the file from which to
            begin reading the input file. The first line is the zero line (Python
            convention).

            (blank), or 0
                Begins reading from the top of the file. Default.

            LINE_NUMBER
                Begins reading from the specified line number in the file.

        log : optional
            Not supported in the gRPC implementation.

        time_step_stream : int, optional
            Time to wait between streaming updates to send back chunks
            from the listener file.  Larger values mean more data per
            chunk and less chunks, but if the command is short, will
            wait until time_step_stream is finished leading to a long
            execution time.

            Due to stability issues, the default time_step_stream is
            dependent on the OS MAPDL is running on.  The defaults are:

            - Windows: ``time_step_stream=500``
            - Linux: ``time_step_stream=100``

            These defaults will be ignored if ``time_step_stream`` is
            manually set. See the *Examples* section to learn how to change
            the default value globally.

        orig_cmd : str, optional
            Original command. There are some cases, were input is
            used to send the file to the grpc server but then we want
            to run something different than ``/INPUT``, for example
            ``CDREAD``.

        Returns
        -------
        str
            Response from MAPDL.

        Notes
        -----
        This method does not use the APDL ``/INPUT`` command.
        However its usage is very similar to it. See *Examples* section.

        If you want to use ``/INPUT`` for some reason, although it is not
        recommended, you can write the desired input file, upload it using
        :func:`Mapdl.upload <ansys.mapdl.core.Mapdl.upload>`, and then use
        run command :func:`Mapdl.run('/INPUT,<FILE>,<EXT>) <ansys.mapdl.core.Mapdl.run>`.
        This does not avoid to use the gRPC input method, but it allows you to
        use the APDL ``/INPUT`` command from the generated input file.
        See *Examples* section for more information.

        Examples
        --------
        Load a simple ``"ds.dat"`` input file generated from Ansys
        Workbench.

        >>> output = mapdl.input('ds.dat')

        Load that same file while streaming the output in real-time.

        >>> output = mapdl.input('ds.dat', verbose=True)

        Use the default APDL ``/INPUT`` command:

        >>> with open('myinput.inp','w').write("/finish\\n/prep7\\n/com, my commands")
        >>> with open('inputtrigger.inp','w').write("/input,myinput,inp")
        >>> mapdl.upload("myinput.inp")
        Uploading myinput.inp: 100%|█████████████████████████████████████████████████| 26.0/26.0 [00:00<00:00, 5.86kB/s]
        'myinput.inp'
        >>> mapdl.upload("inputtrigger.inp")
        Uploading inputtrigger.inp: 100%|████████████████████████████████████████████| 32.0/32.0 [00:00<00:00, 8.92kB/s]
        'inputtrigger.inp'
        >>> with mapdl.non_interactive:
                mapdl.run("/input,inputtrigger,inp") # This inputs 'myinput.inp'

        You can also change them globably using:

        >>> from ansys.mapdl.core import mapdl_grpc
        >>> mapdl_grpc.DEFAULT_TIME_STEP_STREAM=100 # in milliseconds

        """
        # Checking compatibility
        # Checking the user is not reusing old api:
        #
        # fname,
        # verbose=False,
        # progress_bar=False,
        # time_step_stream=None,
        # chunk_size=512,
        # orig_cmd="/INP",
        # write_to_log=True,

        msg_compat = "\nThe 'mapdl.input' method API changed in v0.65. Please check the documentation for information about the new arguments."

        if log:
            raise ValueError(
                "'log' argument is not supported in the gRPC implementation."
            )

        if not isinstance(ext, (str)) and ext is not None:
            raise ValueError(
                "Only strings are allowed in 'ext' argument.\n" + msg_compat
            )

        if not isinstance(dir_, (str)) and dir_ is not None:
            raise ValueError(
                "Only strings are allowed in 'dir_' argument.\n" + msg_compat
            )

        # Getting arguments rights
        if not fname and ext:
            fname = self.jobname

        if not fname:
            raise ValueError("A file name must be supplied.")

        fname = self._get_file_name(fname=fname, ext=ext)

        if not dir_:
            self._log.debug(f"Using python working directory as 'dir_' value.")
            dir_ = os.getcwd()
        else:
            fname = os.path.join(dir_, fname)

        if not line:
            line = 0
        else:
            try:
                line = int(line)
            except ValueError:
                raise ValueError(
                    "Only integers are supported for 'line' argument. Labels are not supported on the gRPC implementation."
                )

        if line != 0:
            # Trimming file
            tmp_modified_file = os.path.join(
                tempfile.gettempdir(), os.path.basename(fname)
            )
            with open(tmp_modified_file, "w") as fid, open(fname, "r") as fid2:
                fid.writelines(fid2.readlines()[line:])

            fname = tmp_modified_file

        # Running method
        #
        if "CDRE" in orig_cmd.upper():
            # CDREAD already uploads the file, and since the priority in
            # `_get_file_path` is for the files in the python working directory,
            # we skip that function here.
            self._log.debug(
                f"Avoid uploading the file {fname} because `CDREAD` should have upload it already."
            )
            filename = fname

        else:
            # Always check if file is present as the grpc and MAPDL errors
            # are unclear
            filename = self._get_file_path(fname, progress_bar)

        time_step_stream = self._get_time_step_stream(time_step_stream)

        metadata = [
            ("time_step_stream", str(time_step_stream)),
            ("chunk_size", str(chunk_size)),
        ]

        if verbose:
            request = pb_types.InputFileRequest(filename=filename)
            strouts = self._stub.InputFileS(request, metadata=metadata)
            responses = []
            for strout in strouts:
                lines = strout.cmdout
                # print out input as it is being run
                print("\n".join(lines))
                responses.extend(lines)
            response = "\n".join(responses)
            return response.strip()

        ##
        # Otherwise, not verbose

        # since we can't directly run /INPUT, we have to write a
        # temporary input file that tells MAPDL to read the input
        # file.
        id_ = random_string()
        tmp_name = f"_input_tmp_{id_}_.inp"
        tmp_out = f"_input_tmp_{id_}_.out"

        if "CDRE" in orig_cmd.upper():
            # Using CDREAD
            option = kwargs.get("cd_read_option", "COMB")
            tmp_dat = f"/OUT,{tmp_out}\n{orig_cmd},'{option}','{filename}'\n"
            delete_uploaded_files = False

        else:
            # Using default INPUT
            tmp_dat = f"/OUT,{tmp_out}\n{orig_cmd},'{filename}'\n"
            delete_uploaded_files = True

        if write_to_log and self._apdl_log is not None:
            if not self._apdl_log.closed:
                self._apdl_log.write(tmp_dat)

        if self._local:
            local_path = self.directory
            tmp_name_path = os.path.join(local_path, tmp_name)
            with open(tmp_name_path, "w") as f:
                f.write(tmp_dat)
        else:
            self._upload_raw(tmp_dat.encode(), tmp_name)

        # Escaping early if inside non_interactive context
        if self._store_commands:
            self._stored_commands.append(tmp_dat.splitlines()[1])
            return None

        request = pb_types.InputFileRequest(filename=tmp_name)

        # even though we don't care about the output, we still
        # need to check.  otherwise, since inputfile is
        # non-blocking, we could corrupt the service
        chunks = self._stub.InputFileS(request, metadata=metadata)
        _ = [chunk.cmdout for chunk in chunks]  # unstable

        # all output (unless redirected) has been written to a temp output
        if self._local:
            tmp_out_path = os.path.join(local_path, tmp_out)
            with open(tmp_out_path) as f:
                output = f.read()

            # delete the files to avoid overwriting:
            try:
                os.remove(tmp_name_path)
            except OSError:
                pass

            try:
                os.remove(tmp_out_path)
            except OSError:
                pass

        # otherwise, read remote file
        else:
            output = self._download_as_raw(tmp_out).decode("latin-1")

            # Deleting the previous files
            self.slashdelete(tmp_name)
            self.slashdelete(tmp_out)
            if filename in self.list_files() and delete_uploaded_files:
                self.slashdelete(filename)

        return output

    def _get_time_step_stream(
        self, time_step: Optional[Union[int, float]] = None
    ) -> str:
        """Return the time step for checking if MAPDL is done writing the
        output to the file which later will be returned as response
        """
        if time_step is None:
            if DEFAULT_TIME_STEP_STREAM is not None:
                time_step = DEFAULT_TIME_STEP_STREAM
            elif self.platform == "windows":
                time_step = DEFAULT_TIME_STEP_STREAM_NT
            elif self.platform == "linux":
                time_step = DEFAULT_TIME_STEP_STREAM_POSIX
            else:
                raise ValueError(
                    f"The MAPDL platform ('{self.platform}') is not recognaised."
                )

        else:
            if time_step <= 0:
                raise ValueError("``time_step`` argument must be greater than 0``")

        self.logger.debug(f"The time_step argument is set to: {time_step}")
        return time_step

    def _get_file_path(self, fname: str, progress_bar: bool = False) -> str:
        """Find files in the Python and MAPDL working directories.

        **The priority is for the Python directory.**

        Hence if the same file is in the Python directory and in the MAPDL directory,
        PyMAPDL will upload a copy from the Python directory to the MAPDL directory,
        overwriting the MAPDL directory copy.
        """

        if os.path.isdir(fname):
            raise ValueError(
                f"`fname` should be a full file path or name, not the directory '{fname}'."
            )

        fPath = pathlib.Path(fname)

        fpath = os.path.dirname(fname)
        fname = fPath.name
        fext = fPath.suffix

        # if there is no dirname, we are assuming the file is
        # in the python working directory.
        if not fpath:
            fpath = os.getcwd()

        ffullpath = os.path.join(fpath, fname)

        if os.path.exists(ffullpath) and self._local:
            return ffullpath

        if self._local:
            if os.path.isfile(fname):
                # And it exists
                filename = os.path.join(os.getcwd(), fname)
            elif not self._store_commands and fname in self.list_files():
                # It exists in the Mapdl working directory
                filename = os.path.join(self.directory, fname)
            elif self._store_commands:
                # Assuming that in non_interactive we have uploaded the file
                # manually.
                filename = os.path.join(self.directory, fname)
            else:
                # Finally
                raise FileNotFoundError(f"Unable to locate filename '{fname}'")

        else:  # Non-local
            # upload the file if it exists locally
            if os.path.isfile(ffullpath):
                self.upload(ffullpath, progress_bar=progress_bar)
                filename = fname

            elif not self._store_commands and fname in self.list_files():
                # It exists in the Mapdl working directory
                filename = fname

            elif self._store_commands:
                # Assuming that in non_interactive, the file exists already in
                # the Mapdl working directory
                filename = fname

            else:
                raise FileNotFoundError(f"Unable to locate filename '{fname}'")

        return filename

    def _get_file_name(
        self,
        fname: str,
        ext: Optional[str] = None,
        default_extension: Optional[str] = None,
    ) -> str:
        """Get file name from fname and extension arguments.

        fname can be the full path.

        Parameters
        ----------
        fname : str
            File name (with our with extension). It can be a full path.

        ext : str, optional
            File extension. The default is None.

        default_extension : str
            Default filename extension. The default is None.
        """

        # the old behaviour is to supplied the name and the extension separately.
        # to make it easier let's going to allow names with extensions

        # Sanitizing ext
        while ext and ext[0] == ".":
            ext = ext[1:]

        if ext:
            fname = fname + "." + ext
        else:
            basename = os.path.basename(fname)

            if len(basename.split(".")) == 1:
                # there is no extension in the main name.
                if default_extension:
                    fname = fname + "." + default_extension

        return fname

    def _flush_stored(self):
        """Writes stored commands to an input file and runs the input
        file.  Used with non_interactive.
        """
        if not self._stored_commands:
            self._log.debug("There is no commands to be flushed.")
            self._store_commands = False
            return

        self._log.debug("Flushing stored commands")

        commands = "\n".join(self._stored_commands)
        if self._apdl_log:
            self._apdl_log.write(commands + "\n")

        self._log.debug(
            "Writing the following commands to a temporary " "apdl input file:\n%s",
            commands,
        )

        # write to a temporary input file
        def build_rand_tmp():
            return os.path.join(tempfile.gettempdir(), f"tmp_{random_string()}.inp")

        # rare case of duplicated tmpfile (birthday problem)
        tmp_filename = build_rand_tmp()
        while os.path.isfile(tmp_filename):
            tmp_filename = build_rand_tmp()

        with open(tmp_filename, "w") as fid:
            fid.writelines(commands)

        self._store_commands = False
        self._stored_commands = []

        # run the stored commands
        out = self.input(
            tmp_filename,
            write_to_log=False,
            verbose=False,
            chunk_size=DEFAULT_CHUNKSIZE,
            progress_bar=False,
        )
        # skip the first line as it simply states that it's reading an input file
        self._response = out[out.find("LINE=       0") + 13 :]
        response_ = "\n".join(self._response.splitlines()[:20])
        self._log.info(response_)

        if not self._ignore_errors:
            self._raise_errors(self._response)

        # try/except here because MAPDL might have not closed the temp file
        try:
            os.remove(tmp_filename)
        except:
            self._log.warning("Unable to remove temporary file %s", tmp_filename)

    @protect_grpc
    def _get(
        self,
        entity: str = "",
        entnum: str = "",
        item1: str = "",
        it1num: MapdlFloat = "",
        item2: str = "",
        it2num: MapdlFloat = "",
        item3: MapdlFloat = "",
        it3num: MapdlFloat = "",
        item4: MapdlFloat = "",
        it4num: MapdlFloat = "",
        **kwargs: KwargDict,
    ) -> Union[float, str]:
        """Sends gRPC *Get request.

        .. warning::
           Not thread safe.  Uses ``_get_lock`` to ensure multiple
           request are not evaluated simultaneously.
        """
        if self._session_id is not None:
            self._check_session_id()

        if self._store_commands:
            raise MapdlRuntimeError(
                "Cannot use `mapdl.get_value` when in `non_interactive` mode. "
                "Exit non_interactive mode before using this method.\n\n"
                "Alternatively you can use `mapdl.get` to specify the name of "
                "the MAPDL parameter where to store the retrieved value.\n"
            )

        cmd = f"{entity},{entnum},{item1},{it1num},{item2},{it2num},{item3}, {it3num}, {item4}, {it4num}"

        # not threadsafe; don't allow multiple get commands
        while self._get_lock:
            time.sleep(0.001)

        self._get_lock = True
        try:
            getresponse = self._stub.Get(pb_types.GetRequest(getcmd=cmd))
        finally:
            self._get_lock = False

        if getresponse.type == 0:
            self._log.debug(
                "The 'grpc' get method seems to have failed. Trying old implementation for more verbose output."
            )

            try:
                out = self.run("*GET,__temp__," + cmd)
                return float(out.split("VALUE=")[1].strip())

            except MapdlRuntimeError as e:
                # Get can thrown some errors, in that case, they are caught in the default run method.
                raise e

            except (IndexError, ValueError):
                raise MapdlError("Error when processing '*get' request output.")

        if getresponse.type == 1:
            return getresponse.dval
        elif getresponse.type == 2:
            return getresponse.sval

        raise MapdlRuntimeError(
            f"Unsupported type {getresponse.type} response from MAPDL"
        )

    def download_project(
        self,
        extensions: Optional[Union[str, List[str], Tuple[str]]] = None,
        target_dir: Optional[str] = None,
        progress_bar: bool = False,
    ) -> List[str]:
        """Download all the project files located in the MAPDL working directory.

        Parameters
        ----------
        extensions : List[str], Tuple[str], optional
            List of extensions to filter the files before downloading,
            by default None.

        target_dir : str, optional
            Path to downloaded the files will to. The default is ``None``.

        progress_bar : bool, optional
            Display a progress bar using
            ``tqdm`` when ``True``.  Helpful for showing download
            progress. The default is ``False``.

        Returns
        -------
        List[Str]
            List of downloaded files.
        """
        if not extensions:
            list_of_files = self.download(
                files="*", target_dir=target_dir, progress_bar=progress_bar
            )

        else:
            list_of_files = []
            for each_extension in extensions:
                list_of_files.extend(
                    self.download(
                        files="*",
                        target_dir=target_dir,
                        extension=each_extension,
                        progress_bar=progress_bar,
                    )
                )

        return list_of_files

    def download(
        self,
        files: Union[str, List[str], Tuple[str, ...]],
        target_dir: Optional[str] = None,
        extension: Optional[str] = None,
        chunk_size: Optional[int] = None,
        progress_bar: Optional[bool] = None,
        recursive: bool = False,
    ) -> List[str]:
        """Download files from the gRPC instance working directory

        .. warning:: This feature is only available for MAPDL 2021R1 or newer.

        Parameters
        ----------
        files : str or List[str] or tuple(str)
            Name of the file on the server. File must be in the same
            directory as the mapdl instance. A list of string names or
            tuples of string names can also be used.
            List current files with :meth:`Mapdl.list_files <MapdlGrpc.list_files>`.

            Alternatively, you can also specify **glob expressions** to
            match file names. For example: `'file*'` to match every file whose
            name starts with `'file'`.

        target_dir : str, optional
            Path where the downloaded files will be located. The default is the current
            working directory.

        extension : str, optional
            Filename with this extension will be considered. The default is None.

        chunk_size : int, optional
            Chunk size in bytes.  Must be less than 4MB. The default is 256 kB.

        progress_bar : bool, optional
            Display a progress bar using ``tqdm`` when ``True``.
            Helpful for showing download progress.

        recursive : bool, optional
            Whether to use recursion when using glob pattern. The default is ``False``.

        Notes
        -----
        There are some considerations to keep in mind when using this command:

        * The glob pattern search does not search recursively in remote instances.
        * In a remote instance, it is not possible to list or download files in different
          locations than the MAPDL working directory.
        * If you are in local and provide a file path, downloading files
          from a different folder is allowed.
          However it is not a recommended approach.

        Examples
        --------
        Download a single file:

        >>> mapdl.download('file.out')

        Download all the files starting with `'file'`:

        >>> mapdl.download('file*')

        Download every single file in the MAPDL working directory:

        >>> mapdl.download('*.*')

        Alternatively, you can download all the files using
        :func:`Mapdl.download_project <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.download_project>` (recommended):

        >>> mapdl.download_project()

        """
        if chunk_size is None:
            chunk_size = DEFAULT_CHUNKSIZE

        if chunk_size > 4 * 1024 * 1024:  # 4MB
            raise ValueError(
                f"Chunk sizes bigger than 4 MB can generate unstable behaviour in PyMAPDL. "
                "Please decrease ``chunk_size`` value."
            )

        if target_dir:
            try:
                os.mkdir(os.path.abspath(target_dir))
            except FileExistsError:
                pass
        else:
            target_dir = os.getcwd()

        if self._local:
            return self._download_on_local(
                files, target_dir=target_dir, extension=extension, recursive=recursive
            )

        else:  # remote session
            if recursive:
                warn(
                    "The 'recursive' parameter is ignored if the session is non-local."
                )
            return self._download_from_remote(
                files,
                target_dir=target_dir,
                extension=extension,
                chunk_size=chunk_size,
                progress_bar=progress_bar,
            )

    def _download_on_local(
        self,
        files: Union[str, List[str], Tuple[str, ...]],
        target_dir: str,
        extension: Optional[str] = None,
        recursive: bool = False,
    ) -> List[str]:
        """Download files when we are on a local session."""

        if isinstance(files, str):
            if not os.path.isdir(os.path.join(self.directory, files)):
                list_files = self._validate_files(
                    files, extension=extension, recursive=recursive
                )
            else:
                list_files = [files]

        elif isinstance(files, (list, tuple)):
            if not all([isinstance(each, str) for each in files]):
                raise ValueError(
                    "The parameter `'files'` can be a list or tuple, but it should only contain strings."
                )
            list_files = []
            for each in files:
                list_files.extend(
                    self._validate_files(each, extension=extension, recursive=recursive)
                )

        else:
            raise ValueError(
                f"The `file` parameter type ({type(files)}) is not supported."
                "Only strings, tuple of strings or list of strings are allowed."
            )

        return_list_files = []
        for file in list_files:
            # file is a complete path
            basename = os.path.basename(file)
            destination = os.path.join(target_dir, basename)
            if os.path.isfile(destination):
                os.remove(destination)
                # the file might have been already downloaded.
                warn(
                    f"The file {file} has been updated in the current working directory."
                )

            if os.path.isdir(os.path.join(self.directory, file)):
                if recursive:  # only copy the directory if recursive is true.
                    shutil.copytree(
                        os.path.join(self.directory, file),
                        target_dir,
                        dirs_exist_ok=True,
                    )
                    return_list_files.extend(
                        glob.iglob(target_dir + "/**/*", recursive=recursive)
                    )

            else:
                return_list_files.append(destination)
                shutil.copy(
                    os.path.join(self.directory, file),
                    destination,
                )

        return return_list_files

    def _download_from_remote(
        self,
        files: Union[str, List[str], Tuple[str, ...]],
        target_dir: str,
        extension: Optional[str] = None,
        chunk_size: Optional[str] = None,
        progress_bar: Optional[str] = None,
    ) -> List[str]:
        """Download files when we are connected to a remote session."""

        if isinstance(files, str):
            list_files = self._validate_files(files, extension=extension)

        elif isinstance(files, list):
            if not all([isinstance(each, str) for each in files]):
                raise ValueError(
                    "The parameter `'files'` can be a list or tuple, but it should only contain strings."
                )
            list_files = []
            for each in files:
                list_files.extend(self._validate_files(each, extension=extension))

        else:
            raise ValueError(
                f"The `file` parameter type ({type(files)}) is not supported."
                "Only strings, tuple of strings or list of strings are allowed."
            )

        for each_file in list_files:
            self._download(
                each_file,
                out_file_name=os.path.join(target_dir, each_file),
                chunk_size=chunk_size,
                progress_bar=progress_bar,
            )

        return list_files

    def _validate_files(
        self, file: str, extension: Optional[str] = None, recursive: bool = True
    ) -> List[str]:
        if extension is not None:
            if not isinstance(extension, str):
                raise TypeError(f"The extension {extension} must be a string.")

            if not extension.startswith("."):
                extension = "." + extension

        else:
            extension = ""

        if self.is_local:
            # filtering with glob (accepting *)
            if not os.path.dirname(file):
                file = os.path.join(self.directory, file)
            list_files = glob.glob(file + extension, recursive=recursive)

        else:
            base_name = os.path.basename(file + extension)
            self_files = self.list_files()

            list_files = fnmatch.filter(self_files, base_name)

        # filtering by extension
        list_files = [file for file in list_files if file.endswith(extension)]

        if len(list_files) == 0:
            raise FileNotFoundError(
                f"No file matching '{file}' in the MAPDL session can be found."
            )

        return list_files

    @protect_grpc
    def _download(
        self,
        target_name: str,
        out_file_name: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNKSIZE,
        progress_bar: bool = False,
    ) -> None:
        """Download a file from the gRPC instance.

        Parameters
        ----------
        target_name : str
            Target file on the server. File must be in the same
            directory as the mapdl instance. List current files with
            ``mapdl.list_files()``

        out_file_name : str, optional
            Save the filename as a different name other than the
            ``target_name``.

        chunk_size : int, optional
            Chunk size in bytes.  Must be less than 4MB.  The default is 256 kB.

        progress_bar : bool, optional
            Display a progress bar using ``tqdm`` when ``True``.
            Helpful for showing download progress. The default is
            ``False`` to avoid excessive command printout.

        Examples
        --------
        Download the remote result file "file.rst" as "my_result.rst"

        >>> mapdl.download('file.rst', 'my_result.rst')
        """

        if progress_bar and _HAS_TQDM:
            progress_bar = True

        if out_file_name is None:
            out_file_name = target_name

        request = pb_types.DownloadFileRequest(name=target_name)
        metadata = [
            ("time_step_stream", "200"),
            ("chunk_size", str(chunk_size)),
        ]
        chunks = self._stub.DownloadFile(request, metadata=metadata)
        file_size = save_chunks_to_file(
            chunks,
            out_file_name,
            progress_bar=progress_bar,
            target_name=target_name,
        )

        if not file_size:
            warn(
                f'File "{target_name}" is empty or does not exist in {self.list_files()}.'
            )

    @protect_grpc
    def upload(self, file_name: str, progress_bar: bool = _HAS_TQDM) -> str:
        """Upload a file to the grpc instance

        file_name : str
            Local file to upload.

        progress_bar : bool, optional
            Whether to display a progress bar using ``tqdm``. The default is ``True``.
            This parameter is helpful for showing download progress.

        Returns
        -------
        str
            Base name of the file uploaded.  File can be accessed
            relative to the mapdl instance with this file name.

        Examples
        --------
        Upload "local_file.inp" while disabling the progress bar

        >>> mapdl.upload('local_file.inp', progress_bar=False)
        """
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"Unable to locate filename {file_name}")
        self._log.debug(f"Uploading file '{file_name}' to the MAPDL instance.")

        chunks_generator = get_file_chunks(file_name, progress_bar=progress_bar)
        response = self._stub.UploadFile(chunks_generator)

        if not response.length:
            raise IOError("File failed to upload")
        return os.path.basename(file_name)

    @protect_grpc
    def _get_array(
        self,
        entity="",
        entnum="",
        item1="",
        it1num="",
        item2="",
        it2num="",
        kloop="",
        **kwargs,
    ):
        """Do a gRPC VGET request.

        Send a vget request, receive a bytes stream, and return it as
        a numpy array.

        Not thread safe as it uses a constant internal temporary
        parameter name.  This method uses _vget_lock to ensure
        multiple simultaneous request fail.

        Returns
        -------
        values : np.ndarray
            Numpy 1D array containing the requested *VGET item and entity.
        """
        if "parm" in kwargs:
            raise ValueError("Parameter name `parm` not supported with gRPC")

        while self._vget_lock:
            time.sleep(0.001)
        self._vget_lock = True

        cmd = f"{entity},{entnum},{item1},{it1num},{item2},{it2num},{kloop}"
        try:
            chunks = self._stub.VGet2(pb_types.GetRequest(getcmd=cmd))
            values = parse_chunks(chunks)
        finally:
            self._vget_lock = False
        return values

    def _screenshot_path(self):
        """Returns the local path of the MAPDL generated screenshot.

        If necessary, downloads the remotely rendered file.
        """
        if self._local:
            return super()._screenshot_path()

        all_filenames = self.list_files()
        filenames = []
        for filename in all_filenames:
            if filename.endswith(".png"):
                filenames.append(filename)
        filenames.sort()
        filename = os.path.basename(filenames[-1])

        temp_dir = tempfile.gettempdir()
        save_name = os.path.join(temp_dir, "tmp.png")
        self._download(filename, out_file_name=save_name)
        return save_name

    @protect_grpc
    def _download_as_raw(self, target_name: str) -> str:
        """Download a file from the gRPC instance as a binary
        string without saving it to disk.
        """
        request = pb_types.DownloadFileRequest(name=target_name)
        chunks = self._stub.DownloadFile(request)
        return b"".join([chunk.payload for chunk in chunks])

    @property
    def is_alive(self) -> bool:
        """True when there is an active connect to the gRPC server"""
        if self.channel_state not in ["IDLE", "READY", None]:
            self._log.debug(
                "MAPDL instance is not alive because the channel is not 'IDLE' o 'READY'."
            )
            return False

        if self._exited:
            self._log.debug("MAPDL instance is not alive because it is exited.")
            return False

        if self.busy:
            self._log.debug("MAPDL instance is alive because it is busy.")
            return True

        if self._exiting:
            # It should be exiting so we should not issue gRPC calls
            self._log.debug("MAPDL instance is expected to be exiting")
            return False

        try:
            check = bool(self._ctrl("VERSION"))
            if check:
                self._log.debug(
                    "MAPDL instance is alive because version was retrieved."
                )
            else:
                self._log.debug(
                    "MAPDL instance is not alive because version was not retrieved. Maybe output is muted?."
                )
            return check

        except Exception as error:
            if self._exited:
                return False

            self._log.debug(
                f"MAPDL instance is not alive because retrieving version failed with:\n{error}"
            )
            return False

    @property
    def xpl(self) -> "ansXpl":
        """MAPDL file explorer

        Iteratively navigate through MAPDL files.

        Examples
        --------
        Read the MASS record from the "file.full" file

        >>> from ansys import Mapdl
        >>> mapdl = Mapdl()
        >>> xpl = mapdl.xpl
        >>> xpl.open('file.full')
        >>> vec = xpl.read('MASS')
        >>> vec.asarray()
        array([ 4,  7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52,
               55, 58,  1], dtype=int32)
        """
        if self._xpl is None:
            from ansys.mapdl.core.xpl import ansXpl

            self._xpl = ansXpl(self)
        return self._xpl

    @protect_grpc
    def scalar_param(self, pname: str) -> float:
        """Return a scalar parameter as a float.

        If parameter does not exist, returns ``None``.

        """
        request = pb_types.ParameterRequest(name=pname, array=False)
        presponse = self._stub.GetParameter(request)
        if presponse.val:
            return float(presponse.val[0])

    @protect_grpc
    def _upload_raw(self, raw, save_as):  # consider private
        """Upload a binary string as a file"""
        chunks = chunk_raw(raw, save_as)
        response = self._stub.UploadFile(chunks)
        if response.length != len(raw):
            raise IOError("Raw Bytes failed to upload")

    # TODO: not fully tested/implemented
    @protect_grpc
    def Param(self, pname):
        presponse = self._stub.GetParameter(pb_types.ParameterRequest(name=pname))
        return presponse.val

    # TODO: not fully tested/implemented
    @protect_grpc
    def Var(self, num):
        presponse = self._stub.GetVariable(pb_types.VariableRequest(inum=num))
        return presponse.val

    @property
    def math(self):
        """Interface to launch PyAnsys Math from PyMAPDL.

         Returns
        -------
        :class:`MapdlMath <ansys.mapdl.core.math.MapdlMath>`

        Examples
        --------
        Get the stiffness matrix from MAPDL
        >>> mm = mapdl.math
        >>> k = mm.stiff()
        >>> k.asarray()
        <60x60 sparse matrix of type '<class 'numpy.float64'>'
            with 1734 stored elements in Compressed Sparse Row format>

        Get the mass matrix from MAPDL
        >>> mm = mapdl.math
        >>> m = mm.stiff()
        >>> m.asarray()
        <60x60 sparse matrix of type '<class 'numpy.float64'>'
            with 1734 stored elements in Compressed Sparse Row format>
        """
        if self._math is None:
            from ansys.math.core.math import AnsMath

            self._math = AnsMath(self)

        return self._math

    @property
    def krylov(self):
        """APDL krylov interface.
        For more information, see the :class:`KrylovSolver <ansys.mapdl.core.krylov.KrylovSolver>`
        Returns
        -------
        :class:`Krylov class <ansys.mapdl.core.krylov.KrylovSolver>`
        """
        if self._krylov is None:
            from ansys.mapdl.core.krylov import KrylovSolver

            self._krylov = KrylovSolver(self)

        return self._krylov

    @property
    def db(self):
        """
        MAPDL database interface.

        Returns
        -------
        :class:`MapdlDb <ansys.mapdl.core.database.MapdlDb>`

        Examples
        --------
        Create a nodes instance.

        >>> from ansys.mapdl.core import launch_mapdl
        >>> mapdl = launch_mapdl()
        >>> # create nodes...
        >>> nodes = mapdl.db.nodes
        >>> print(nodes)
        MAPDL Database Nodes
            Number of nodes:          270641
            Number of selected nodes: 270641
            Maximum node number:      270641

        >>> mapdl.nsel("NONE")
        >>> print(nodes)
        MAPDL Database Nodes
            Number of nodes:          270641
            Number of selected nodes: 0
            Maximum node number:      270641

        Return the selection status and the coordinates of node 22.

        >>> nodes = mapdl.db.nodes
        >>> sel, coord = nodes.coord(22)
        >>> coord
        (1.0, 0.5, 0.0, 0.0, 0.0, 0.0)

        """
        from ansys.mapdl.core.database import MapdlDb

        if self._db is None:
            self._db = MapdlDb(self)
            self._db.start()

        return self._db

    @protect_grpc
    def _data_info(self, pname):
        """Returns the data type of a parameter

        APDLMATH vectors only.
        """
        request = pb_types.ParameterRequest(name=pname)
        return self._stub.GetDataInfo(request)

    @protect_grpc
    def _vec_data(self, pname):
        """Downloads vector data from a MAPDL MATH parameter"""
        dtype = ANSYS_VALUE_TYPE[self._data_info(pname).stype]
        request = pb_types.ParameterRequest(name=pname)
        chunks = self._stub.GetVecData(request)
        return parse_chunks(chunks, dtype)

    @protect_grpc
    def _mat_data(self, pname, raw=False):
        """Downloads matrix data from a parameter and returns a scipy sparse array"""
        try:
            from scipy import sparse
        except ImportError:  # pragma: no cover
            raise ImportError("Install ``scipy`` to use this feature") from None

        minfo = self._data_info(pname)
        stype = ANSYS_VALUE_TYPE[minfo.stype]
        mtype = minfo.objtype
        shape = (minfo.size1, minfo.size2)

        if mtype == 2:  # dense
            request = pb_types.ParameterRequest(name=pname)
            chunks = self._stub.GetMatData(request)
            values = parse_chunks(chunks, stype)
            return np.transpose(np.reshape(values, shape[::-1]))
        elif mtype == 3:  # sparse
            indptr = self._vec_data(pname + "::ROWS")
            indices = self._vec_data(pname + "::COLS")
            vals = self._vec_data(pname + "::VALS")
            if raw:  # for debug
                return vals, indices, indptr, shape
            else:
                return sparse.csr_matrix(
                    (vals, indices, indptr), dtype=stype, shape=shape
                )

        raise ValueError(f'Invalid matrix type "{mtype}"')

    @property
    def locked(self):
        """Instance is in use within a pool."""
        return self._locked

    @locked.setter
    def locked(self, new_value):
        self._locked = new_value

    @supress_logging
    def __str__(self):
        try:
            if self._exited:
                return "MAPDL exited"
            stats = self.slashstatus("PROD", mute=False)
        except:  # pragma: no cover
            return "MAPDL exited"

        st = stats.find("*** Products ***")
        en = stats.find("*** PrePro")
        product = "\n".join(stats[st:en].splitlines()[1:]).strip()

        info = "Mapdl\n"
        info += "-----\n"
        info += f"PyMAPDL Version:     {__version__}\n"
        info += "Interface:           grpc\n"
        info += f"Product:             {product}\n"
        info += f"MAPDL Version:       {self.version}\n"
        info += f"Running on:          {self.hostname}\n"
        info += f"                     ({self.ip})"
        return info

    @supress_logging
    @run_as("PREP7")
    def _generate_iges(self):
        """Save IGES geometry representation to disk"""
        basename = "_tmp.iges"
        if self._local:
            filename = os.path.join(self.directory, basename)
            self.igesout(basename, att=1)
        else:
            self.igesout(basename, att=1)
            filename = os.path.join(tempfile.gettempdir(), basename)
            self._download(basename, filename, progress_bar=False)
        return filename

    @property
    def _distributed_result_file(self):
        """Path of the distributed result file."""
        if not self._distributed:
            return

        try:
            filename = self.inquire("", "RSTFILE")
            if not filename:
                filename = self.jobname
        except:
            filename = self.jobname

        # ansys decided that a jobname ended in a number needs a bonus "_"
        if filename[-1].isnumeric():
            filename += "_"

        rth_basename = "%s0.%s" % (filename, "rth")
        rst_basename = "%s0.%s" % (filename, "rst")

        rth_file = os.path.join(self.directory, rth_basename)
        rst_file = os.path.join(self.directory, rst_basename)

        if self._prioritize_thermal:
            if not os.path.isfile(rth_file):
                raise FileNotFoundError("Thermal Result not available")
            return rth_file

        if os.path.isfile(rth_file) and os.path.isfile(rst_file):
            return last_created([rth_file, rst_file])
        elif os.path.isfile(rth_file):
            return rth_file
        elif os.path.isfile(rst_file):
            return rst_file

    @property
    def thermal_result(self):
        """The thermal result object."""
        self._prioritize_thermal = True
        result = self.result
        self._prioritize_thermal = False
        return result

    def list_error_file(self):
        """Listing of errors written in JOBNAME.err"""
        files = self.list_files()
        jobname = self.jobname
        error_file = None
        for test_file in [f"{jobname}.err", f"{jobname}0.err"]:
            if test_file in files:
                error_file = test_file
                break

        if not error_file:
            return None

        if self._local:
            return open(os.path.join(self.directory, error_file)).read()
        elif self._exited:
            raise MapdlExitedError(
                "Cannot list error file when MAPDL Service has exited"
            )

        return self._download_as_raw(error_file).decode("latin-1")

    @wraps(MapdlBase.cmatrix)
    def cmatrix(
        self,
        symfac="",
        condname="",
        numcond="",
        grndkey="",
        capname="",
        **kwargs,
    ):
        """Run CMATRIX in non-interactive mode and return the response from file."""

        # The CMATRIX command needs to run in non-interactive mode
        if not self._store_commands:
            with self.non_interactive:
                super().cmatrix(symfac, condname, numcond, grndkey, capname, **kwargs)
            self._response = self._download_as_raw("cmatrix.out").decode()
            return self._response

        # otherwise, simply run cmatrix as we're already in
        # non-interactive and there's no output to return
        super().cmatrix(symfac, condname, numcond, grndkey, capname, **kwargs)

    @MapdlBase.name.getter
    def name(self) -> str:
        """Instance unique identifier."""
        if not self._name:
            if self._ip or self._port:
                self._name = f"GRPC_{self._ip}:{self._port}"
            else:
                self._name = f"GRPC_instance_{id(self)}"
        return self._name

    @property
    def _distributed(self) -> bool:
        """MAPDL is running in distributed mode."""
        if self.__distributed is None:
            self.__distributed = self.parameters.numcpu > 1
        return self.__distributed

    @wraps(MapdlBase.ndinqr)
    def ndinqr(self, node, key, **kwargs):
        """Wrap the ``ndinqr`` method to take advantage of the gRPC methods."""
        super().ndinqr(node, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.elmiqr)
    def elmiqr(self, ielem, key, **kwargs):
        """Wrap the ``elmiqr`` method to take advantage of the gRPC methods."""
        super().elmiqr(ielem, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.kpinqr)
    def kpinqr(self, knmi, key, **kwargs):
        """Wrap the ``kpinqr`` method to take advantage of the gRPC methods."""
        super().kpinqr(knmi, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.lsinqr)
    def lsinqr(self, line, key, **kwargs):
        """Wrap the ``lsinqr`` method to take advantage of the gRPC methods."""
        super().lsinqr(line, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.arinqr)
    def arinqr(self, anmi, key, **kwargs):
        """Wrap the ``arinqr`` method to take advantage of the gRPC methods."""
        super().arinqr(anmi, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.vlinqr)
    def vlinqr(self, vnmi, key, **kwargs):
        """Wrap the ``vlinqr`` method to take advantage of the gRPC methods."""
        super().vlinqr(vnmi, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.rlinqr)
    def rlinqr(self, nreal, key, **kwargs):
        """Wrap the ``rlinqr`` method to take advantage of the gRPC methods."""
        super().rlinqr(nreal, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.gapiqr)
    def gapiqr(self, ngap, key, **kwargs):
        """Wrap the ``gapiqr`` method to take advantage of the gRPC methods."""
        super().gapiqr(ngap, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.masiqr)
    def masiqr(self, node, key, **kwargs):
        """Wrap the ``masiqr`` method to take advantage of the gRPC methods."""
        super().masiqr(node, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.ceinqr)
    def ceinqr(self, nce, key, **kwargs):
        """Wrap the ``ceinqr`` method to take advantage of the gRPC methods."""
        super().ceinqr(nce, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.cpinqr)
    def cpinqr(self, ncp, key, **kwargs):
        """Wrap the ``cpinqr`` method to take advantage of the gRPC methods."""
        super().cpinqr(ncp, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.csyiqr)
    def csyiqr(self, ncsy, key, **kwargs):
        """Wrap the ``csyiqr`` method to take advantage of the gRPC methods."""
        super().csyiqr(ncsy, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.etyiqr)
    def etyiqr(self, itype, key, **kwargs):
        """Wrap the ``etyiqr`` method to take advantage of the gRPC methods."""
        super().etyiqr(itype, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.foriqr)
    def foriqr(self, node, key, **kwargs):
        """Wrap the ``foriqr`` method to take advantage of the gRPC methods."""
        super().foriqr(node, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.sectinqr)
    def sectinqr(self, nsect, key, **kwargs):
        """Wrap the ``sectinqr`` method to take advantage of the gRPC methods."""
        super().sectinqr(nsect, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.mpinqr)
    def mpinqr(self, mat, iprop, key, **kwargs):
        """Wrap the ``mpinqr`` method to take advantage of the gRPC methods."""
        super().mpinqr(mat, iprop, key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.dget)
    def dget(self, node, idf, kcmplx, **kwargs):
        """Wrap the ``dget`` method to take advantage of the gRPC methods."""
        super().dget(node, idf, kcmplx, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.fget)
    def fget(self, node, idf, kcmplx, **kwargs):
        """Wrap the ``fget`` method to take advantage of the gRPC methods."""
        super().fget(node, idf, kcmplx, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.erinqr)
    def erinqr(self, key, **kwargs):
        """Wrap the ``erinqr`` method to take advantage of the gRPC methods."""
        super().erinqr(key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.wrinqr)
    def wrinqr(self, key, **kwargs):
        """Wrap the ``wrinqr`` method to take advantage of the gRPC methods."""
        super().wrinqr(key, pname=TMP_VAR, mute=True, **kwargs)
        return self.scalar_param(TMP_VAR)

    @wraps(MapdlBase.file)
    def file(self, fname: str = "", ext: str = "", **kwargs) -> str:
        """Wrap ``MapdlBase.file`` to take advantage of the gRPC methods."""
        # always check if file is present as the grpc and MAPDL errors
        # are unclear
        fname = self._get_file_name(fname, ext, "cdb")
        fname = self._get_file_path(fname, kwargs.get("progress_bar", False))
        file_, ext_, _ = self._decompose_fname(fname)
        fname = fname[: -len(ext_) - 1]  # Removing extension. -1 for the dot.
        if self._local:
            return self._file(filename=fname, extension=ext_, **kwargs)
        else:
            return self._file(filename=file_, extension=ext_)

    @wraps(MapdlBase.vget)
    def vget(
        self,
        par: str = "",
        ir: MapdlInt = "",
        tstrt: MapdlFloat = "",
        kcplx: MapdlInt = "",
        **kwargs: KwargDict,
    ) -> NDArray[np.float64]:
        """Wraps VGET"""
        super().vget(par=par, ir=ir, tstrt=tstrt, kcplx=kcplx, **kwargs)
        if not self._store_commands:
            return self.parameters[par]

    def get_variable(
        self,
        ir: MapdlInt = "",
        tstrt: MapdlFloat = "",
        kcplx: MapdlInt = "",
        **kwargs: KwargDict,
    ) -> NDArray[np.float64]:
        """
        Obtain the variable values.

        Parameters
        ----------
        ir : str, optional
            Reference number of the variable (1 to NV [NUMVAR]).

        tstrt : str, optional
            Time (or frequency) corresponding to start of IR data.  If between
            values, the nearer value is used. By default it is the first value.

        kcplx : str, optional
            Complex number key:

            * ``0`` - Use the real part of the IR data. Default.

            * ``1`` - Use the imaginary part of the IR data.

        Returns
        -------
        np.array
            Variable values as array.
        """
        par = "temp_var"
        variable = self.vget(par=par, ir=ir, tstrt=tstrt, kcplx=kcplx, **kwargs)
        del self.parameters[par]
        return variable

    @wraps(MapdlBase.nsol)
    def nsol(
        self,
        nvar: MapdlInt = VAR_IR,
        node: MapdlInt = "",
        item: str = "",
        comp: str = "",
        name: str = "",
        sector: MapdlInt = "",
        **kwargs: KwargDict,
    ):
        """Wraps NSOL to return the variable as an array."""
        super().nsol(
            nvar=nvar,
            node=node,
            item=item,
            comp=comp,
            name=name,
            sector=sector,
            **kwargs,
        )
        return self.vget("_temp", nvar)

    @wraps(MapdlBase.esol)
    def esol(
        self,
        nvar: MapdlInt = VAR_IR,
        elem: MapdlInt = "",
        node: MapdlInt = "",
        item: str = "",
        comp: str = "",
        name: str = "",
        **kwargs: KwargDict,
    ) -> NDArray[np.float64]:
        """Wraps ESOL to return the variable as an array."""
        super().esol(
            nvar=nvar,
            elem=elem,
            node=node,
            item=item,
            comp=comp,
            name=name,
            **kwargs,
        )
        return self.vget("_temp", nvar)

    def get_nsol(
        self,
        node: MapdlInt = "",
        item: str = "",
        comp: str = "",
        name: str = "",
        sector: MapdlInt = "",
        **kwargs: KwargDict,
    ) -> NDArray[np.float64]:
        """
        Get NSOL solutions

        Parameters
        ----------
        node : int
            Node for which data is to be stored.

        item : str
            Label identifying the item.  Valid item labels are shown in the
            table below. Some items also require a component label.

        comp : str
            Component of the item (if required).  Valid component labels are
            shown in the table below.

        name : str, optional
            Thirty-two character name identifying the item on printouts and
            displays.  The default is a label formed by concatenating the first
            four characters of the ``item`` and ``comp`` labels.

        sector : int, optional
            For a full harmonic cyclic symmetry solution, the sector number for
            which the results from NODE are to be stored.

        Returns
        -------
        np.array
            Variable values

        Notes
        -----
        By default, this command store temporally the variable on the
        variable number set by ``VAR_IR`` in the class MapdlGrpc.
        Therefore, any variable in that slot will be deleted when using
        this command.

        Stores nodal degree of freedom and solution results in a variable. For
        more information, see Data Interpreted in the Nodal Coordinate System
        in the Modeling and Meshing Guide.

        For SECTOR>1, the result is in the nodal coordinate system of the base
        sector, and it is rotated to the expanded sector’s location. Refer to
        Using the /CYCEXPAND Command in the Cyclic Symmetry Analysis Guide for
        more information.

        For SHELL131 and SHELL132 elements with KEYOPT(3) = 0 or 1, use the
        labels TBOT, TE2, TE3, . . ., TTOP instead of TEMP.

        """
        return self.nsol(
            VAR_IR,
            node=node,
            item=item,
            comp=comp,
            name=name,
            sector=sector,
            **kwargs,
        )

    def get_esol(
        self,
        elem: MapdlInt = "",
        node: MapdlInt = "",
        item: str = "",
        comp: str = "",
        name: str = "",
        sector: MapdlInt = "",
        tstrt: MapdlFloat = "",
        kcplx: MapdlInt = "",
        **kwargs: KwargDict,
    ) -> NDArray[np.float64]:
        """Get ESOL data.

        /POST26 APDL Command: ESOL

        Parameters
        ----------
        elem : int
            Element for which data are to be stored.

        node : int
            Node number on this element for which data are to be
            stored. If blank, store the average element value (except
            for ``FMAG`` values, which are summed instead of averaged).

        item : str
            Label identifying the item. Some items also require a component label.

        comp : str
            Component of the item (if required). If Comp is a sequence number (n),
            the ``NODE`` field will be ignored.

        name : str, optional
            Thirty-two character name for identifying the item on the
            printout and displays.  The default is a label formed by
            concatenating the first four characters of the ``item`` and
            ``comp`` labels.

        tstrt : str, optional
            Time (or frequency) corresponding to start of IR data.  If between
            values, the nearer value is used. By default it is the first value.

        kcplx : str, optional
            Complex number key:

            * ``0`` - Use the real part of the IR data. Default.

            * ``1`` - Use the imaginary part of the IR data.

        Returns
        -------
        np.array
            Variable values

        Notes
        -----
        By default, this command store temporally the variable on the
        variable number set by ``VAR_IR`` in the class
        :class:`Mapdl <ansys.mapdl.core.mapdl.MapdlBase>`
        Therefore, any variable in that slot will be deleted when using
        this command.

        The ``ESOL`` command defines element results data to be stored
        from a results file (``FILE``). Not all items are valid for all
        elements. To see the available items for a given element,
        refer to the input and output summary tables in the
        documentation for that element.

        Two methods of data access are available via the ``ESOL``
        command. You can access some simply by using a generic label
        (component name method), while others require a label and
        number (sequence number method).

        Use the component name method to access general element data
        (that is, element data generally available to most element
        types or groups of element types).

        The sequence number method is required for data that is not
        averaged (such as pressures at nodes and temperatures at
        integration points), or data that is not easily described in a
        generic fashion (such as all derived data for structural line
        elements and contact elements, all derived data for thermal
        line elements, and layer data for layered elements).

        Element results are in the element coordinate system, except
        for layered elements where results are in the layer coordinate
        system.  Element forces and moments are in the nodal
        coordinate system. Results are obtainable for an element at a
        specified node. Further location specifications can be made
        for some elements via the ``SHELL``, ``LAYERP26``, and ``FORCE`` commands.

        For more information on the meaning of contact status and its
        possible values, see Reviewing Results in ``POST1`` in the Contact
        Technology Guide.
        """
        self.esol(
            VAR_IR,
            elem=elem,
            node=node,
            item=item,
            comp=comp,
            name=name,
            sector=sector,
            **kwargs,
        )
        # Using get_variable because it deletes the intermediate parameter after using it.
        return self.get_variable(VAR_IR, tstrt=tstrt, kcplx=kcplx)

    def _create_session(self):
        """Generate a session ID."""
        id_ = uuid4()
        id_ = str(id_)[:31].replace("-", "")
        self._session_id_ = id_
        self._run(f"{SESSION_ID_NAME}='{id_}'")

    @property
    def _session_id(self):
        """Return the session ID."""
        return self._session_id_

    def _check_session_id(self):
        """Verify that the local session ID matches the remote MAPDL session ID."""
        if self._checking_session_id_ or not self._strict_session_id_check:
            # To avoid recursion error
            return

        pymapdl_session_id = self._session_id
        if not pymapdl_session_id:
            # We return early if pymapdl_session is not fixed yet.
            return

        self._checking_session_id_ = True
        self._mapdl_session_id = self._get_mapdl_session_id()

        self._checking_session_id_ = False

        if pymapdl_session_id is None or self._mapdl_session_id is None:
            return
        elif pymapdl.RUNNING_TESTS or self._strict_session_id_check:
            if pymapdl_session_id != self._mapdl_session_id:
                self._log.error("The session ids do not match")

            else:
                self._log.debug("The session ids match")
                return True
        else:
            return pymapdl_session_id == self._mapdl_session_id

    def _get_mapdl_session_id(self):
        """Retrieve MAPDL session ID."""
        try:
            parameter = interp_star_status(
                self._run(f"*STATUS,{SESSION_ID_NAME}", mute=False)
            )
        except AttributeError:
            return None

        if parameter:
            return parameter[SESSION_ID_NAME]["value"]
        return None

    @wraps(MapdlBase.igesin)
    def igesin(self, fname, ext="", **kwargs):
        """Wrap the IGESIN command to handle the remote case."""

        fname = self._get_file_name(fname=fname, ext=ext)
        filename = self._get_file_path(fname, progress_bar=False)

        # Entering aux15 preprocessor
        self.aux15()

        if " " in fname:
            # Bug in reading file paths with whitespaces.
            # https://github.com/ansys/pymapdl/issues/1601

            msg_ = f"Applying \\IGESIN whitespace patch.\nSee #1601 issue in PyMAPDL repository.\nReading file {fname}"
            self.input_strings("\n".join([f"! {each}" for each in msg_.splitlines()]))
            self._log.debug(msg_)

            cmd = f"*dim,__iges_file__,string,248\n*set,__iges_file__(1), '{filename}'"
            self.input_strings(cmd)

            out = super().igesin(fname="__iges_file__(1)", **kwargs)
            self.run("__iges_file__ =")  # cleaning array.
            self.run("! Ending \\IGESIN whitespace patch.")
            return out
        else:
            return super().igesin(fname=filename, **kwargs)

    @wraps(MapdlBase.satin)
    def satin(
        self,
        name,
        extension="",
        path="",
        entity="",
        fmt="",
        nocl="",
        noan="",
        **kwargs,
    ):
        """Wraps ~SATIN command"""
        fname = name
        if path:
            fname = os.path.join(path, name)
        fname = self._get_file_name(fname, extension, "sat")
        fname = self._get_file_path(fname, False)
        name, extension, path = self._decompose_fname(fname)

        if path == path.parent:
            path = ""
        else:
            path = str(path)

        # wrapping path in single quotes because of #2286
        path = f"'{path}'"
        return super().satin(
            name=name,
            extension=extension,
            path=path,
            entity=entity,
            fmt=fmt,
            nocl=nocl,
            noan=noan,
            **kwargs,
        )

    @wraps(MapdlBase.cat5in)
    def cat5in(
        self,
        name,
        extension="",
        path="",
        entity="",
        fmt="",
        nocl="",
        noan="",
        **kwargs,
    ):
        """Wraps ~cat5in command"""
        fname = name
        if path:
            fname = os.path.join(path, name)
        fname = self._get_file_name(fname, extension, "CATPart")
        fname = self._get_file_path(fname, False)
        name, extension, path = self._decompose_fname(fname)

        if path == path.parent:
            path = ""
        else:
            path = str(path)

        # wrapping path in single quotes because of #2286
        path = f"'{path}'"
        self.finish()
        return super().cat5in(
            name=name,
            extension=extension,
            path=path,
            entity=entity,
            fmt=fmt,
            nocl=nocl,
            noan=noan,
            **kwargs,
        )

    @wraps(MapdlBase.parain)
    def parain(
        self,
        name,
        extension="",
        path="",
        entity="",
        fmt="",
        scale="",
        **kwargs,
    ):
        """Wraps ~parain command"""
        fname = name
        if path:
            fname = os.path.join(path, name)
        fname = self._get_file_name(fname, extension, "x_t")
        fname = self._get_file_path(fname, False)
        name, extension, path = self._decompose_fname(fname)

        if path == path.parent:
            path = ""
        else:
            path = str(path)

        # wrapping path in single quotes because of #2286
        path = f"'{path}'"
        return super().parain(
            name=name,
            extension=extension,
            path=path,
            entity=entity,
            fmt=fmt,
            scale=scale,
            **kwargs,
        )

    def screenshot(self, savefig: Optional[str] = None):
        """Take an MAPDL screenshot and show it in a popup window.

        Parameters
        ----------
        savefig : Optional[str], optional
            Name of or path to the screenshot file.
            The default is ``None``.

        Returns
        -------
        str
            File name.

        Raises
        ------
        FileNotFoundError
            If the path given in the ``savefig`` parameter is not found or is not consistent.
        ValueError
            If given a wrong type for the ``savefig`` parameter.
        """
        previous_device = self.file_type_for_plots
        self.show("PNG")
        out_ = self.replot()
        self.show(previous_device)  # previous device
        file_name = self._get_plot_name(out_)

        def get_file_name(path):
            """Get a new filename so as not to overwrite an existing one."""
            target_dir = os.path.join(path, "mapdl_screenshot_0.png")
            i = 0
            while os.path.exists(target_dir):
                # Ensuring file is not overwritten.
                i += 1
                target_dir = os.path.join(path, f"mapdl_screenshot_{i}.png")
            return target_dir

        if savefig is None or savefig is False:
            self._display_plot(file_name)

        else:
            if savefig is True:
                # Copying to working directory
                target_dir = get_file_name(os.getcwd())

            elif isinstance(savefig, str):
                if not os.path.dirname(savefig):
                    # File name given only
                    target_dir = os.path.join(os.getcwd(), savefig)

                elif os.path.isdir(savefig):
                    # Given directory path only, but not file name.
                    target_dir = get_file_name(savefig)

                elif os.path.exists(os.path.dirname(savefig)):
                    # Only directory is given. Checking if directory exists.
                    target_dir = savefig

                else:
                    raise FileNotFoundError("The filename or path is not valid.")

            else:
                raise ValueError(
                    "Only strings or Booleans are valid inputs for the 'savefig' parameter."
                )

            shutil.copy(file_name, target_dir)
            return os.path.basename(target_dir)

    def kill_job(self, jobid: int) -> None:
        """Kill an HPC job

        Kill a job given its identifier.

        Parameters
        ----------
        jobid : int
            Job ID.
        """
        from ansys.mapdl.core.launcher import submitter

        cmd = ["scancel", f"{jobid}"]
        # to ensure the job is stopped properly, let's issue the scancel twice.
        submitter(cmd, ssh_session=self._ssh_session)  # nosec B603

    def __del__(self):
        """In case the object is deleted"""
        # We are just going to escape early if needed, and kill the HPC job.
        # The garbage collector remove attributes before we can evaluate this.
        if self._exited:
            return

        if not self._start_instance:
            # Early skip if start_instance is False
            return

        # Killing the instance if we launched it.
        if self._launched:
            self._exit_mapdl(self._path)

        # Exiting HPC job
        if self._mapdl_on_hpc and self.finish_job_on_exit:
            self.kill_job(self.jobid)
