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

"""Launch MAPDL locally"""

from typing import Any, Dict

from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher.tools import (
    check_kwargs,
    check_lock_file,
    check_mode,
    configure_ubuntu,
    force_smp_in_student,
    get_cpus,
    get_exec_file,
    get_run_location,
    get_version,
    pack_arguments,
    pre_check_args,
    remove_err_files,
    set_license_switch,
    set_MPI_additional_switches,
    update_env_vars,
)


def processing_local_arguments(args_: Dict[str, Any]):
    # packing arguments
    args = pack_arguments(args_)  # packs args and kwargs

    check_kwargs(args)  # check if passing wrong arguments

    if "start_instance" in args and args["start_instance"] is False:
        raise ValueError(
            "'start_instance' argument is not valid."
            "If you intend to connect to an already started instance use either "
            "'connect_to_mapdl' or the infamous 'launch_mapdl(start_instance=False)'."
        )
    args["start_instance"] = True

    pre_check_args(args)
    args["running_on_hpc"] = False

    get_cpus(args)

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

    args["env_vars"] = update_env_vars(args["add_env_vars"], args["replace_env_vars"])

    get_run_location(args)

    # verify lock file does not exist
    check_lock_file(args["run_location"], args["jobname"], args["override"])

    # remove err file so we can track its creation
    # (as way to check if MAPDL started or not)
    remove_err_files(args["run_location"], args["jobname"])

    # Check for a valid connection mode
    args["mode"] = check_mode(args["mode"], args["version"])

    # ON HPC:
    # Assuming that if login node is ubuntu, the computation ones
    # are also ubuntu.
    args["env_vars"] = configure_ubuntu(args["env_vars"])

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
        args["env_vars"].setdefault("ANS_MULTIPLE_NODES", "1")
        args["env_vars"].setdefault("HYDRA_BOOTSTRAP", "slurm")

    return args
