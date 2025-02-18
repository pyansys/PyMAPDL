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

###############################################################################
# Imports
# =======
#
import logging
import os
import sys
from typing import Dict, List, Tuple
from warnings import warn

from platformdirs import user_data_dir

###############################################################################
# Logging
# =======
#
from ansys.mapdl.core.logging import Logger

LOG: Logger = Logger(level=logging.ERROR, to_file=False, to_stdout=True)
LOG.debug("Loaded logging module as LOG")

###############################################################################
# Globals
# =======
#
from ansys.mapdl.core._version import __version__
from ansys.mapdl.core.helpers import is_installed, run_every_import, run_first_time

# A dictionary relating PyMAPDL server versions with the unified install ones
VERSION_MAP: Dict[Tuple[int, int, int], str] = {
    (0, 0, 0): "2020R2",
    (0, 3, 0): "2021R1",
    (0, 4, 0): "2021R2",
    (0, 4, 1): "2021R2",
    (0, 5, 0): "2022R1",
    (0, 5, 1): "2022R2",
}

BUILDING_GALLERY: bool = False
RUNNING_TESTS: bool = False

DEPRECATING_MINIMUM_PYTHON_VERSION: bool = False
MINIMUM_PYTHON_VERSION: Tuple[int, int] = (3, 10)

# Import related globals
_HAS_ATP: bool = is_installed("ansys.tools.path")
_HAS_CLICK: bool = is_installed("click")
_HAS_PIM: bool = is_installed("ansys.platform.instancemanagement")
_HAS_PANDAS: bool = is_installed("pandas")
_HAS_PYANSYS_REPORT: bool = is_installed("ansys.tools.report")
_HAS_PYVISTA: bool = is_installed("pyvista")
_HAS_REQUESTS: bool = is_installed("requests")
_HAS_TQDM: bool = is_installed("tqdm")
_HAS_VISUALIZER: bool = is_installed("ansys.tools.visualization_interface")


# Setup directories
USER_DATA_PATH: str = user_data_dir(appname="ansys_mapdl_core", appauthor="Ansys")
EXAMPLES_PATH: str = os.path.join(USER_DATA_PATH, "examples")

# Store ports occupied by local instances
_LOCAL_PORTS: List[int] = []

###############################################################################
# First time
# ==========
#
# This function runs only the first time PyMAPDL is importad after it is installed.
# It creates the required directories and raise Python version related warnings.
#
run_first_time()

###############################################################################
# Runs every time
# ===============
#
# This function runs every time that PyMAPDL is imported.
#
run_every_import()

###############################################################################
# Library imports
# ===============
#
from ansys.mapdl.core._version import SUPPORTED_ANSYS_VERSIONS
from ansys.mapdl.core.convert import convert_apdl_block, convert_script
from ansys.mapdl.core.launcher import close_all_local_instances

# override default launcher when on pyansys.com
if "ANSJUPHUB_VER" in os.environ:  # pragma: no cover
    from ansys.mapdl.core.launcher.jupyter import (
        launch_mapdl_on_cluster as launch_mapdl,
    )
else:
    from ansys.mapdl.core.launcher import launch_mapdl

from ansys.mapdl.core.information import Information
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc as Mapdl
from ansys.mapdl.core.misc import check_has_mapdl
from ansys.mapdl.core.pool import MapdlPool
from ansys.mapdl.core.report import Report

###############################################################################
# Convenient imports
# ==================
#
# For compatibility with other versions or for convenience
if _HAS_ATP:
    from ansys.tools.path.path import (
        change_default_ansys_path,
        find_mapdl,
        get_available_ansys_installations,
        get_mapdl_path,
        save_ansys_path,
    )

if _HAS_VISUALIZER:
    from ansys.tools.visualization_interface import Plotter
