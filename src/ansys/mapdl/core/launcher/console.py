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

from typing import Optional, Union

from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher.local import processing_local_arguments
from ansys.mapdl.core.launcher.tools import generate_start_parameters
from ansys.mapdl.core.licensing import LicenseChecker
from ansys.mapdl.core.mapdl_console import MapdlConsole


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


def launch_mapdl_console(
    exec_file: Optional[str] = None,
    run_location: Optional[str] = None,
    jobname: str = "file",
    *,
    nproc: Optional[int] = None,
    ram: Optional[Union[int, str]] = None,
    override: bool = False,
    loglevel: str = "ERROR",
    additional_switches: str = "",
    start_timeout: Optional[int] = None,
    log_apdl: Optional[Union[bool, str]] = None,
):
    ########################################
    # Processing arguments
    # --------------------
    #
    # processing arguments
    args = processing_local_arguments(locals())

    # Check for a valid connection mode
    if args.get("mode", "console") != "console":
        raise ValueError("Invalid 'mode'.")

    start_parm = generate_start_parameters(args)

    # Early exit for debugging.
    if args["_debug_no_launch"]:
        # Early exit, just for testing
        return args  # type: ignore

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
    ########################################
    # Launch MAPDL on console mode
    # ----------------------------
    #
    start_parm = check_console_start_parameters(start_parm)
    mapdl = MapdlConsole(
        loglevel=args["loglevel"],
        log_apdl=args["log_apdl"],
        use_vtk=args["use_vtk"],
        **start_parm,
    )

    # Stop license checker
    if args["license_server_check"]:
        LOG.debug("Stopping check on license server.")
        lic_check.stop()

    return mapdl
