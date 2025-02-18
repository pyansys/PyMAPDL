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

import os

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
import subprocess  # nosec B404
from typing import Any, Dict, Optional, Union

from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher.local import processing_local_arguments
from ansys.mapdl.core.launcher.tools import (
    check_mapdl_launch,
    generate_mapdl_launch_command,
    generate_start_parameters,
    get_port,
    submitter,
)
from ansys.mapdl.core.licensing import LicenseChecker
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc


def launch_mapdl_grpc(
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
) -> MapdlGrpc:
    """Start MAPDL locally with gRPC interface.

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
    MapdlGrpc
        An instance of Mapdl.
    """
    args = processing_local_arguments(locals())

    args["port"] = get_port(args["port"], args["start_instance"])

    start_parm = generate_start_parameters(args)

    # Check the license server
    if args["license_server_check"]:
        LOG.debug("Checking license server.")
        lic_check = LicenseChecker(timeout=args["start_timeout"])
        lic_check.start()

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
    )

    try:
        # Launching MAPDL
        process = launch_grpc(
            cmd=cmd,
            run_location=args["run_location"],
            env_vars=args["env_vars"],
            launch_on_hpc=args.get("launch_on_hpc"),
            mapdl_output=args.get("mapdl_output"),
        )

        # Local mapdl launch check
        check_mapdl_launch(process, args["run_location"], args["start_timeout"], cmd)

    except Exception as exception:
        LOG.error("An error occurred when launching MAPDL.")

        if args["license_server_check"]:
            LOG.debug("Checking license server.")
            lic_check.check()

        raise exception

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


def launch_grpc(
    cmd: list[str],
    run_location: str = None,
    env_vars: Optional[Dict[str, str]] = None,
    launch_on_hpc: bool = False,
    mapdl_output: Optional[str] = None,
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
    )  # nosec B604
