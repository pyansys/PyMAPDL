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

from typing import Any, Dict, Optional, Union

from ansys.mapdl.core import LOG
from ansys.mapdl.core.launcher.tools import (
    check_kwargs,
    generate_start_parameters,
    get_ip,
    get_port,
    pack_arguments,
    pre_check_args,
)
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc

_NON_VALID_ARGS = (
    "add_env_vars",
    "additional_switches",
    "exec_file",
    "jobname",
    "launch_on_hpc",
    "license_server_check",
    "license_type",
    "mapdl_output",
    "mode",
    "nproc",
    "override",
    "ram",
    "remove_temp_dir_on_exit",
    "replace_env_vars",
    "run_location",
    "running_on_hpc",
    "start_instance",
    "version",
)


def check_remote_args(args):
    for each_arg in _NON_VALID_ARGS:
        if each_arg in args:
            raise ValueError(
                f"'connect_to_mapdl' does not accept '{each_arg}' argument."
            )
        else:
            if each_arg == "mode":
                args[each_arg] = "grpc"
            elif each_arg == "start_instance":
                args[each_arg] = False
            else:
                args[each_arg] = None  # setting everything as None.


def connect_to_mapdl(
    port: Optional[int] = None,
    ip: Optional[str] = None,
    *,
    loglevel: str = "ERROR",
    start_timeout: Optional[int] = None,
    cleanup_on_exit: bool = True,
    clear_on_connect: bool = True,
    log_apdl: Optional[Union[bool, str]] = None,
    print_com: bool = False,
    **kwargs: Dict[str, Any],
):
    ########################################
    # Processing arguments
    # --------------------
    #
    # packing arguments
    args = pack_arguments(locals())  # packs args and kwargs

    check_kwargs(args)  # check if passing wrong arguments

    check_remote_args(args)

    pre_check_args(args)

    get_ip(args)

    args["port"] = get_port(args["port"], args["start_instance"])

    start_parm = generate_start_parameters(args)

    ########################################
    # Connecting to a remote instance
    # -------------------------------
    #
    LOG.debug(
        f"Connecting to an existing instance of MAPDL at {args['ip']}:{args['port']}"
    )
    start_parm["launched"] = False

    mapdl = MapdlGrpc(
        cleanup_on_exit=args["cleanup_on_exit"],
        loglevel=args["loglevel"],
        set_no_abort=args["set_no_abort"],
        use_vtk=args["use_vtk"],
        log_apdl=args["log_apdl"],
        **start_parm,
    )
    if args["clear_on_connect"]:
        mapdl.clear()
    return mapdl
