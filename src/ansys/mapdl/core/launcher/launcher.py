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
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher.pim import is_ready_for_pypim, launch_remote_mapdl
from ansys.mapdl.core.licensing import LicenseChecker
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc

if TYPE_CHECKING:  # pragma: no cover
    from ansys.mapdl.core.mapdl_console import MapdlConsole

from ansys.mapdl.core.launcher.grpc import launch_grpc
from ansys.mapdl.core.launcher.hpc import (
    check_mapdl_launch_on_hpc,
    generate_sbatch_command,
    get_job_info,
    get_slurm_options,
    is_running_on_slurm,
    kill_job,
)
from ansys.mapdl.core.launcher.tools import (
    _cleanup_gallery_instance,
    check_kwargs,
    check_lock_file,
    check_mapdl_launch,
    check_mode,
    configure_ubuntu,
    create_gallery_instances,
    force_smp_in_student,
    generate_mapdl_launch_command,
    generate_start_parameters,
    get_cpus,
    get_exec_file,
    get_ip,
    get_port,
    get_run_location,
    get_start_instance_arg,
    get_version,
    pack_arguments,
    pre_check_args,
    remove_err_files,
    set_license_switch,
    set_MPI_additional_switches,
    update_env_vars,
)

atexit.register(_cleanup_gallery_instance)


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

            export PYMAPDL_MAPDL_EXEC=/ansys_inc/v251/ansys/bin/mapdl

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

    check_kwargs(args)  # check if passing wrong key arguments

    pre_check_args(args)

    ########################################
    # PyPIM connection
    # ----------------
    # Delegating to PyPIM if applicable
    #
    if is_ready_for_pypim(exec_file):
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
        # Assuming that if login node is ubuntu, the computation nodes
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
        # Connecting to a remote instance
        # -------------------------------
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
        from ansys.mapdl.core.launcher.console import check_console_start_parameters
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

            jobid: int = start_parm.get("jobid", "Not found")

            if (
                args["launch_on_hpc"]
                and start_parm.get("finish_job_on_exit", True)
                and jobid not in ["Not found", None]
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
