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
import warnings

from ansys.mapdl.core import _HAS_ATP, LOG

LOCALHOST = "127.0.0.1"
MAPDL_DEFAULT_PORT = 50052

ON_WSL = os.name == "posix" and (
    os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP")
)

if ON_WSL:
    LOG.info("On WSL: Running on WSL detected.")
    LOG.debug("On WSL: Allowing 'start_instance' and 'ip' arguments together.")


from ansys.mapdl.core.launcher.console import launch_mapdl_console
from ansys.mapdl.core.launcher.grpc import launch_mapdl_grpc
from ansys.mapdl.core.launcher.hpc import launch_mapdl_on_cluster_locally
from ansys.mapdl.core.launcher.launcher import launch_mapdl
from ansys.mapdl.core.launcher.remote import connect_to_mapdl
from ansys.mapdl.core.launcher.tools import (
    close_all_local_instances,
    get_default_ansys,
    get_default_ansys_path,
    get_default_ansys_version,
)

if _HAS_ATP:
    from functools import wraps

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
