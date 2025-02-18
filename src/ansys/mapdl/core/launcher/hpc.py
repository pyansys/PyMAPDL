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
import socket
import subprocess  # nosec B404
import time
from typing import Any, Callable, Dict, List, Optional, Union

from ansys.mapdl.core import LOG
from ansys.mapdl.core.errors import MapdlDidNotStart
from ansys.mapdl.core.launcher.grpc import launch_grpc
from ansys.mapdl.core.launcher.tools import (
    generate_start_parameters,
    get_port,
    submitter,
)
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc

LAUNCH_ON_HCP_ERROR_MESSAGE_IP = (
    "PyMAPDL cannot ensure a specific IP will be used when launching "
    "MAPDL on a cluster. Hence the 'ip' argument is not compatible. "
    "If you want to connect to an already started MAPDL instance, "
    "just connect normally as you would with a remote instance. "
    "For example:\n\n"
    ">>> mapdl = launch_mapdl(start_instance=False, ip='123.45.67.89')\n\n"
    "where '123.45.67.89' is the IP of the machine where MAPDL is running."
)


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


def kill_job(jobid: int) -> subprocess.Popen:
    """Kill SLURM job"""
    submitter(["scancel", str(jobid)])


def send_scontrol(args: str) -> subprocess.Popen:
    cmd = f"scontrol {args}".split(" ")
    return submitter(cmd)


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
    stdout = process.stdout.read().decode()
    if "Submitted batch job" not in stdout:
        stderr = process.stderr.read().decode()
        raise MapdlDidNotStart(
            "PyMAPDL failed to submit the sbatch job:\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )

    jobid = get_jobid(stdout)
    LOG.info(f"HPC job successfully submitted. JobID: {jobid}")
    return jobid


def get_job_info(
    start_parm: Dict[str, str], jobid: Optional[int] = None, timeout: int = 30
) -> None:
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
        :func:`ansys.mapdl.core.launcher.hpc.get_hostname_host_cluster`.
    """
    timeout = timeout or start_parm.get("start_instance")

    jobid = jobid or start_parm["jobid"]

    batch_host, batch_ip = get_hostname_host_cluster(jobid, timeout=timeout)

    start_parm["ip"] = batch_ip
    start_parm["hostname"] = batch_host
    start_parm["jobid"] = jobid


def get_hostname_host_cluster(job_id: int, timeout: int = 30) -> str:
    options = f"show jobid -dd {job_id}"
    LOG.debug(f"Executing the command 'scontrol {options}'")

    ready = False
    time_start = time.time()
    counter = 0
    while not ready:
        proc = send_scontrol(options)

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


def launch_mapdl_on_cluster_locally(
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

    launch_mapdl_args : Dict[str, Any], optional
        Any keyword argument from the :func:`ansys.mapdl.core.launcher.grpc.launch_mapdl_grpc` function.

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

    """
    # from ansys.mapdl.core.launcher import launch_mapdl

    # Processing the arguments
    launch_mapdl_args["launch_on_hpc"] = True
    launch_mapdl_args["running_on_hpc"] = True

    if launch_mapdl_args.get("license_server_check", False):
        raise ValueError(
            "The argument 'license_server_check' is not allowed when launching on an HPC platform."
        )

    launch_mapdl_args["license_server_check"] = False

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

    if launch_mapdl_args.get("mapdl_output", False):
        raise ValueError(
            "The 'mapdl_output' argument is not allowed when launching on an HPC platform."
        )

    return launch_mapdl_grpc_on_hpc(
        nproc=nproc,
        scheduler_options=scheduler_options,
        **launch_mapdl_args,
    )


def launch_mapdl_grpc_on_hpc(
    *,
    exec_file: Optional[str] = None,
    run_location: Optional[str] = None,
    jobname: str = "file",
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
    args = pack_arguments(locals())  # packs args and kwargs

    check_kwargs(args)  # check if passing wrong key arguments

    pre_check_args(args)

    if is_running_on_slurm(args):
        LOG.info("On Slurm mode.")

        # extracting parameters
        get_slurm_options(args, kwargs)

    get_start_instance_arg(args)

    get_cpus(args)

    get_ip(args)

    args["port"] = get_port(args["port"], args["start_instance"])

    if args.get("mode", "grpc") != "grpc":
        raise ValueError("Invalid 'mode'.")
    args["port"] = get_port(args["port"], args["start_instance"])

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
    )

    # wrapping command if on HPC
    cmd = generate_sbatch_command(cmd, scheduler_options=args.get("scheduler_options"))

    try:
        #
        process = launch_grpc(
            cmd=cmd,
            run_location=args["run_location"],
            env_vars=env_vars,
            launch_on_hpc=args.get("launch_on_hpc"),
            mapdl_output=args.get("mapdl_output"),
        )

        start_parm["jobid"] = check_mapdl_launch_on_hpc(process, start_parm)
        get_job_info(start_parm=start_parm, timeout=args["start_timeout"])

    except Exception as exception:
        LOG.error("An error occurred when launching MAPDL.")

        jobid: int = start_parm.get("jobid", "Not found")

        if start_parm.get("finish_job_on_exit", True) and jobid not in [
            "Not found",
            None,
        ]:

            LOG.debug(f"Killing HPC job with id: {jobid}")
            kill_job(jobid)

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
        jobid = start_parm.get("jobid", "'Not found'")
        LOG.error(
            f"An error occurred when connecting to the MAPDL instance running on job {jobid}."
        )
        raise exception

    return mapdl


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
                args["ram"] = int(ram)
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
