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
from unittest.mock import patch

import pytest

from ansys.mapdl.core.launcher.local import processing_local_arguments


@pytest.mark.parametrize("start_instance", [True, False, None, ""])
@patch("ansys.mapdl.core.launcher.local.get_cpus", lambda *args, **kwargs: None)
@patch("psutil.cpu_count", lambda *args, **kwargs: 4)
def test_processing_local_arguments_start_instance(start_instance):
    args = {
        "exec_file": "my_path/v242/ansys/bin/ansys242",  # To skip checks
        "launch_on_hpc": True,  # To skip checks
        "kwargs": {},
    }

    if start_instance == "":
        processing_local_arguments(args)
    else:
        args["start_instance"] = start_instance

        if start_instance is False:
            with pytest.raises(ValueError):
                processing_local_arguments(args)
        else:
            processing_local_arguments(args)
