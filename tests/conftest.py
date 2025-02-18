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

from collections import namedtuple
from collections.abc import Generator
import os
from pathlib import Path
from shutil import get_terminal_size
from sys import platform
from typing import Literal, Union
from unittest.mock import patch

from _pytest.terminal import TerminalReporter  # for terminal customization
import pytest

from ansys.mapdl.core.helpers import is_installed as has_dependency
from common import (
    Element,
    Node,
    debug_testing,
    get_details_of_elements,
    get_details_of_nodes,
    has_dpf,
    has_grpc,
    is_on_ci,
    is_on_local,
    is_on_ubuntu,
    is_running_on_student,
    is_smp,
    log_test_start,
    make_sure_not_instances_are_left_open,
    restart_mapdl,
    support_plotting,
    testing_minimal,
)

################################################################
#
# Setting testing environment
# ---------------------------
#
DEBUG_TESTING = debug_testing()
TESTING_MINIMAL = testing_minimal()

ON_LOCAL = is_on_local()
ON_CI = is_on_ci()
ON_STUDENT = is_running_on_student()

ON_UBUNTU = is_on_ubuntu()  # Tells if MAPDL is running on Ubuntu system or not.
# Whether PyMAPDL is running on an ubuntu or different machine is irrelevant.
ON_WINDOWS = platform == "win32"
ON_LINUX = platform == "linux" or platform == "linux2"
ON_MACOS = platform == "darwin"

HAS_GRPC = has_grpc()
HAS_DPF = has_dpf()
SUPPORT_PLOTTING = support_plotting()
IS_SMP = is_smp()

QUICK_LAUNCH_SWITCHES = "-smp -m 100 -db 100"
VALID_PORTS = []

## Skip ifs
skip_on_windows = pytest.mark.skipif(ON_WINDOWS, reason="Skip on Windows")
skip_on_linux = pytest.mark.skipif(ON_LINUX, reason="Skip on Linux")

skip_no_xserver = pytest.mark.skipif(
    not SUPPORT_PLOTTING, reason="Requires active X Server"
)

skip_if_not_local = pytest.mark.skipif(
    not ON_LOCAL,
    reason="Skipping because not on local. ",
)

skip_if_not_remote = pytest.mark.skipif(
    ON_LOCAL,
    reason="Skipping because not on remote. ",
)

skip_if_on_cicd = pytest.mark.skipif(
    ON_CI,
    reason="""Skip if on CI/CD.""",
)

skip_if_no_has_grpc = pytest.mark.skipif(
    not HAS_GRPC,
    reason="""Requires gRPC.""",
)

skip_if_no_has_dpf = pytest.mark.skipif(
    not HAS_DPF,
    reason="""Requires DPF.""",
)

requires_linux = pytest.mark.skipif(not ON_LINUX, reason="This test requires Linux")
requires_windows = pytest.mark.skipif(
    not ON_WINDOWS, reason="This test requires Windows"
)
requires_on_cicd = pytest.mark.skipif(
    not ON_CI, reason="This test requires to be on CICD"
)

skip_if_running_student_version = pytest.mark.skipif(
    ON_STUDENT,
    reason="This tests does not work on student version.",
)

_REQUIRES_ARG = Union[
    Literal[
        "GRPC",
        "DPF",
        "LOCAL",
        "REMOTE",
        "CICD",
        "NOCICD",
        "XSERVER",
        "LINUX",
        "NOLINUX",
        "WINDOWS",
        "NOWINDOWS",
        "NOSTUDENT",
        "CONSOLE",
    ],
    str,
]


def requires(requirement: _REQUIRES_ARG):
    """Check requirements"""
    requirement = requirement.lower()

    if "grpc" == requirement:
        return skip_if_no_has_grpc

    elif "dpf" == requirement:
        return skip_if_no_has_dpf

    elif "local" == requirement:
        return skip_if_not_local

    elif "remote" == requirement:
        return skip_if_not_remote

    elif "cicd" == requirement:
        return skip_if_on_cicd

    elif "nocicd" == requirement:
        return skip_if_on_cicd

    elif "xserver" == requirement:
        return skip_no_xserver

    elif "linux" == requirement:
        return requires_linux

    elif "nolinux" == requirement:
        return skip_on_linux

    elif "windows" == requirement:
        return requires_windows

    elif "nowindows" == requirement:
        return skip_on_windows

    elif "nostudent" == requirement:
        return skip_if_running_student_version

    elif "console" == requirement:
        return pytest.mark.console

    else:
        return requires_dependency(requirement)


def requires_dependency(dependency: str):
    if has_dependency(dependency):
        return pytest.mark.skipif(
            False, reason=f"Required package ('{dependency}') is installed"
        )  # faking a null skipif decorator
    else:
        # package does not exist
        return pytest.mark.skip(reason=f"Requires '{dependency}' package")


if DEBUG_TESTING:
    from ansys.mapdl.core import LOG

    LOG.setLevel("DEBUG")

    # If the following file name is changed, update `ci.yml`.
    LOG.log_to_file("pymapdl.log")

    # the following files are also generated by MAPDL gRPC:
    # - "pymapdl.apdl": The APDL commands sent to MAPDL by PyMAPDL
    # - "apdl.out" : MAPDL console output. Very likely only contains the output
    #    until connected.

################################################################
#
# Importing packages
# ------------------
#

if has_dependency("ansys-tools-path"):
    from ansys.tools.path import find_mapdl


if has_dependency("pyvista"):
    import pyvista

    from ansys.mapdl.core.plotting.theme import _apply_default_theme

    _apply_default_theme()

    # Necessary for CI plotting
    pyvista.OFF_SCREEN = True
    pyvista.global_theme.allow_empty_mesh = True

import ansys.mapdl.core as pymapdl

pymapdl.RUNNING_TESTS = True

from ansys.mapdl.core import Mapdl
from ansys.mapdl.core.errors import MapdlExitedError, MapdlRuntimeError
from ansys.mapdl.core.examples import vmfiles
from ansys.mapdl.core.launcher import launch_mapdl
from ansys.mapdl.core.launcher.tools import get_start_instance
from ansys.mapdl.core.mapdl_core import VALID_DEVICES

if has_dependency("ansys-tools-visualization_interface"):
    import ansys.tools.visualization_interface as viz_interface

    viz_interface.TESTING_MODE = True

################################################################
#
# Pytest configuration
# --------------------
#

# check if the user wants to permit pytest to start MAPDL
START_INSTANCE = get_start_instance()

################
if os.name == "nt":
    os_msg = """SET PYMAPDL_START_INSTANCE=False
SET PYMAPDL_PORT=<MAPDL Port> (default 50052)
SET PYMAPDL_IP=<MAPDL IP> (default 127.0.0.1)"""
else:
    os_msg = """export PYMAPDL_START_INSTANCE=False
export PYMAPDL_PORT=<MAPDL Port> (default 50052)
export PYMAPDL_IP=<MAPDL IP> (default 127.0.0.1)"""

ERRMSG = f"""Unable to run unit tests without MAPDL installed or
accessible.  Either install Ansys 2021R1 or newer or specify the
remote server with:

{os_msg}

If you do have Ansys installed, you may have to patch PyMAPDL to
automatically find your Ansys installation.

You can request assistance by opening an issue on:

https://github.com/ansys/pymapdl/issues

"""
MAPDL_VERSION = None  # this is cached by mapdl fixture and used in the minimal testing

if START_INSTANCE and not ON_LOCAL:
    raise MapdlRuntimeError(ERRMSG)


@pytest.hookimpl(trylast=True)
def pytest_report_header(config, start_path, startdir):
    text = []
    text += ["Testing variables".center(get_terminal_size()[0], "-")]
    text += [
        f"Session dependent: DEBUG_TESTING ({DEBUG_TESTING}), ON_CI ({ON_CI}), TESTING_MINIMAL ({TESTING_MINIMAL}), SUPPORT_PLOTTING ({SUPPORT_PLOTTING})"
    ]
    text += [
        f"OS dependent: ON_LINUX ({ON_LINUX}), ON_UBUNTU ({ON_UBUNTU}), ON_WINDOWS ({ON_WINDOWS}), ON_MACOS ({ON_MACOS})"
    ]
    text += [
        f"MAPDL dependent: ON_LOCAL ({ON_LOCAL}), ON_STUDENT ({ON_STUDENT}), HAS_GRPC ({HAS_GRPC}), HAS_DPF ({HAS_DPF}), IS_SMP ({IS_SMP})"
    ]

    text += ["Environment variables".center(get_terminal_size()[0], "-")]
    line = ""
    for env_var in [
        "PYMAPDL_START_INSTANCE",
        "PYMAPDL_PORT",
        "PYMAPDL_PORT2",
        "PYMAPDL_DB_PORT",
        "PYMAPDL_IP",
        "PYMAPDL_IP2",
        "DPF_PORT",
        "DPF_START_SERVER",
        "IGNORE_POOL",
    ]:
        env_var_value = os.environ.get(env_var)
        if env_var_value is not None:
            line += f"{env_var} ('{env_var_value}'), "
    text += [line]
    text += ["Pytest configuration".center(get_terminal_size()[0], "-")]
    return "\n".join(text)


## Changing report line length
class MyReporter(TerminalReporter):
    def short_test_summary(self):
        # your own impl goes here, for example:
        self.write_sep("=", "PyMAPDL Pytest short summary")

        failed = self.stats.get("failed", [])
        for rep in failed:
            self.write_line(
                f"[FAILED] {rep.head_line} - {rep.longreprtext.splitlines()[-3]}"
            )

        errored = self.stats.get("error", [])
        for rep in errored:
            self.write_line(
                f"[ERROR] {rep.head_line} - {rep.longreprtext.splitlines()[-3]}"
            )


# @pytest.mark.trylast
@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    vanilla_reporter = config.pluginmanager.getplugin("terminalreporter")
    my_reporter = MyReporter(config)
    config.pluginmanager.unregister(vanilla_reporter)
    config.pluginmanager.register(my_reporter, "terminalreporter")


def pytest_addoption(parser):
    parser.addoption(
        "--console",
        action="store_true",
        default=False,
        help="run console tests",
    )
    parser.addoption("--gui", action="store_true", default=False, help="run GUI tests")
    parser.addoption(
        "--only-gui",
        action="store_true",
        default=False,
        help="run only GUI tests",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--console"):
        # --console given in cli: run console interface tests
        skip_console = pytest.mark.skip(reason="need --console option to run")
        for item in items:
            if "console" in item.keywords:
                item.add_marker(skip_console)

    if not HAS_GRPC:
        skip_grpc = pytest.mark.skip(
            reason="Requires gRPC connection (at least v211 to run)"
        )
        for item in items:
            if "skip_grpc" in item.keywords:
                item.add_marker(skip_grpc)

    only_gui_filter = config.getoption("--only-gui")
    if only_gui_filter:
        new_items = []
        for item in items:
            mark = item.get_closest_marker("requires_gui")
            if mark and mark.name == "requires_gui":
                new_items.append(item)
        items[:] = new_items

    if not config.getoption("--gui") and not only_gui_filter:
        skip_gui = pytest.mark.skip(reason="Requires to launch MAPDL GUI interface.")
        for item in items:
            if "requires_gui" in item.keywords:
                item.add_marker(skip_gui)


################################################################
#
# Setting configuration fixtures
# ------------------------------
#

if has_dependency("pytest-pyvista"):

    @pytest.fixture(autouse=True)
    def wrapped_verify_image_cache(verify_image_cache, pytestconfig):
        # Configuration
        verify_image_cache.error_value = 500.0
        verify_image_cache.warning_value = 200.0

        # High variance test
        verify_image_cache.var_error_value = 1000.0
        verify_image_cache.var_warning_value = 1000.0

        return verify_image_cache


class Running_test:
    def __init__(self, active: bool = True) -> None:
        self._state = active

    def __enter__(self) -> None:
        pymapdl.RUNNING_TESTS = self._state

    def __exit__(self, *args) -> None:
        pymapdl.RUNNING_TESTS = not self._state


class NullContext:
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def __init__(self):
        pass


@pytest.fixture(scope="function")
def running_test():
    return Running_test


@pytest.fixture(autouse=True, scope="function")
def run_before_and_after_tests(
    request: pytest.FixtureRequest, mapdl: Mapdl
) -> Generator[Mapdl]:
    """Fixture to execute asserts before and after a test is run"""

    # Relaunching MAPDL if dead
    mapdl = restart_mapdl(mapdl)

    # Write test info to log_apdl
    if DEBUG_TESTING:
        log_test_start(mapdl)

    # check if the local/remote state has changed or not
    prev = mapdl.is_local

    yield  # this is where the testing happens

    mapdl.prep7()

    # Check resetting state
    assert prev == mapdl.is_local
    assert not mapdl.exited, "MAPDL is exited after the test. It should have not!"
    assert not mapdl._mapdl_on_hpc, "Mapdl class is on HPC mode. It should not!"
    assert mapdl.finish_job_on_exit, "Mapdl class should finish the job!"
    assert not mapdl.ignore_errors, "Mapdl class is ignoring errors!"
    assert not mapdl.mute
    assert mapdl.file_type_for_plots in VALID_DEVICES

    # Returning to default
    mapdl.graphics("full")

    # Handling extra instances
    make_sure_not_instances_are_left_open(VALID_PORTS)

    # Teardown
    if mapdl.is_local and mapdl._exited:
        # The test exited MAPDL, so it has failed.
        test_name = os.environ.get(
            "PYTEST_CURRENT_TEST", "**test id could not get retrieved.**"
        )

        assert (
            False
        ), f"Test {test_name} failed at the teardown."  # this will fail the test


@pytest.fixture(scope="function")
def set_env_var(request, monkeypatch):
    """Set an environment variable from given requests, this fixture must be used with `parametrize`"""
    env_var_name = request.param[0]
    env_var_value = request.param[1]
    monkeypatch.setenv(f"{env_var_name}", f"{env_var_value}")
    yield request.param


@pytest.fixture(scope="function")
def set_env_var_context(request, monkeypatch):
    """Set MY_VARIABLE environment variable, this fixture must be used with `parametrize`"""
    if not isinstance(request.param, (tuple, list)):
        request_param = [request.param]
    else:
        request_param = request.param

    for each_dict in request_param:
        for each_key, each_value in each_dict.items():
            if each_value is not None:
                monkeypatch.setenv(f"{each_key}", f"{each_value}")

    yield request.param


@pytest.fixture
def path_tests(tmpdir):
    SpacedPaths = namedtuple(
        "SpacedPaths",
        ["path_without_spaces", "path_with_spaces", "path_with_single_quote"],
    )

    p1 = tmpdir.mkdir("./temp/")
    p2 = tmpdir.mkdir("./t e m p/")
    p3 = tmpdir.mkdir("./temp'")
    return SpacedPaths(str(p1), str(p2), str(p3))


def clear(mapdl):
    mapdl.finish()
    # *MUST* be NOSTART.  With START fails after 20 calls...
    # this has been fixed in later pymapdl and MAPDL releases
    mapdl.clear("NOSTART")
    mapdl.header("DEFA")
    mapdl.format("DEFA")
    mapdl.page("DEFA")

    mapdl.prep7()


@pytest.fixture(scope="function")
def cleared(mapdl):
    clear(mapdl)
    yield


################################################################
#
# Setting interface fixtures
# --------------------------
#


@pytest.fixture(scope="session")
def mapdl_console(request):
    if os.name != "posix":
        raise MapdlRuntimeError(
            '"--console" testing option unavailable.  ' "Only Linux is supported."
        )
    console_path = find_mapdl()[0]

    if console_path is None:
        raise MapdlRuntimeError(
            '"--console" testing option unavailable.'
            "No local console compatible MAPDL installation found. "
            "Valid versions are up to 2020R2."
        )

    mapdl = launch_mapdl(
        console_path,
        mode="console",
        log_apdl="pymapdl.apdl" if DEBUG_TESTING else None,
        loglevel="DEBUG" if DEBUG_TESTING else "ERROR",
    )
    from ansys.mapdl.core.mapdl_console import MapdlConsole

    assert isinstance(mapdl, MapdlConsole)
    mapdl._show_matplotlib_figures = False  # CI: don't show matplotlib figures

    # using yield rather than return here to be able to test exit
    yield mapdl

    # verify mapdl exits
    mapdl.exit()
    assert mapdl._exited
    assert "MAPDL exited" in str(mapdl)
    with pytest.raises(MapdlExitedError):
        mapdl.prep7()


@pytest.fixture(scope="session")
def mapdl(request, tmpdir_factory):
    # don't use the default run location as tests run multiple unit testings
    run_path = str(tmpdir_factory.mktemp("ansys"))

    # don't allow mapdl to exit upon collection unless mapdl is local
    cleanup = START_INSTANCE

    mapdl = launch_mapdl(
        override=True,
        run_location=run_path,
        cleanup_on_exit=cleanup,
        license_server_check=False,
        start_timeout=50,
        loglevel="DEBUG" if DEBUG_TESTING else "ERROR",
        # If the following file names are changed, update `ci.yml`.
        log_apdl="pymapdl.apdl" if DEBUG_TESTING else None,
        mapdl_output="apdl.out" if (DEBUG_TESTING and ON_LOCAL) else None,
    )

    mapdl._show_matplotlib_figures = False  # CI: don't show matplotlib figures
    MAPDL_VERSION = mapdl.version  # Caching version

    VALID_PORTS.append(mapdl.port)

    if ON_CI:
        mapdl._local = ON_LOCAL  # CI: override for testing

    if ON_LOCAL and mapdl.is_local:
        assert Path(mapdl.directory) == Path(run_path)

    # using yield rather than return here to be able to test exit
    yield mapdl

    VALID_PORTS.remove(mapdl.port)
    ###########################################################################
    # test exit: only when allowed to start PYMAPDL
    ###########################################################################
    if START_INSTANCE:
        mapdl._local = True
        mapdl._exited = False
        assert mapdl.finish_job_on_exit

        mapdl.exit(save=False, force=True)

        assert mapdl._exited
        assert "MAPDL exited" in str(mapdl)

        # should test if _exited protects from execution
        with pytest.raises(MapdlExitedError):
            mapdl.prep7()

        # actually test if server is shutdown
        if HAS_GRPC:
            with pytest.raises(MapdlExitedError):
                mapdl._send_command("/PREP7")
            with pytest.raises(MapdlExitedError):
                mapdl._send_command_stream("/PREP7")

    # Delete Mapdl object
    mapdl.exit()
    del mapdl


################################################################
#
# MAPDL patches
# -------------
#


# Necessary patches to patch Mapdl launch
def _returns(return_=None):
    return lambda *args, **kwargs: return_


# Methods to patch in MAPDL when launching
def _patch_method(method):
    return "ansys.mapdl.core.mapdl_grpc.MapdlGrpc." + method


_meth_patch_MAPDL_launch = [
    # method, and its return
    (_patch_method("_connect"), _returns(True)),
    (_patch_method("_run"), _returns("")),
    (_patch_method("_create_channel"), _returns("")),
    (_patch_method("inquire"), _returns("/home/simulation")),
    (_patch_method("_subscribe_to_channel"), _returns("")),
    (_patch_method("_run_at_connect"), _returns("")),
    (_patch_method("_exit_mapdl"), _returns(None)),
    # non-mapdl methods
    ("socket.gethostbyname", _returns("123.45.67.99")),
    (
        "socket.gethostbyaddr",
        _returns(
            [
                "mapdlhostname",
            ]
        ),
    ),
]

_meth_patch_MAPDL = _meth_patch_MAPDL_launch.copy()

# For testing
# Patch some of the starting procedures
PATCH_MAPDL_START = [patch(method, ret) for method, ret in _meth_patch_MAPDL_launch]

# Patch all the starting procedures so we can have a pseudo mapdl instance
PATCH_MAPDL = [patch(method, ret) for method, ret in _meth_patch_MAPDL]

################################################################
#
# TestClass
# ---------
#


class TestClass:
    """Base class for testing.

    Provide some helper methods.

    This class cleans automatically the MAPDL database upon creation."""

    @pytest.fixture(scope="class", autouse=True)
    def initializer(self, mapdl):
        self.mapdl = mapdl
        self.clear()

    def clear(self):
        clear(self.mapdl)


############################################################
# Fixtures Models
# ================
#


@pytest.fixture(scope="function")
def cube_geom_and_mesh(cleared, mapdl):
    # setup the full file
    mapdl.block(0, 1, 0, 1, 0, 1)
    mapdl.et(1, 186)
    mapdl.esize(0.5)
    mapdl.vmesh("all")

    # Define a material (nominal steel in SI)
    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio


@pytest.fixture(scope="function")
def cube_solve(cleared, mapdl, cube_geom_and_mesh):
    # solve first 10 non-trivial modes
    out = mapdl.modal_analysis(nmode=10, freqb=1)


@pytest.fixture
def solved_box(mapdl, cleared):
    mapdl.mute = True  # improve stability
    mapdl.et(1, "SOLID5")
    mapdl.block(0, 10, 0, 20, 0, 30)
    mapdl.esize(10)
    mapdl.vmesh("ALL")
    mapdl.units("SI")  # SI - International system (m, kg, s, K).
    # Define a material (nominal steel in SI)
    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("PRXY", 1, 0.3)  # Poisson's Ratio
    # Fix the left-hand side.
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX")
    mapdl.d("ALL", "UY")
    mapdl.d("ALL", "UZ")

    mapdl.nsel("S", "LOC", "Z", 30)
    mapdl.f("ALL", "FX", 1000)
    mapdl.run("/SOLU")
    mapdl.antype("STATIC")
    mapdl.solve()
    mapdl.finish()
    mapdl.mute = False


@pytest.fixture(scope="function")
def make_block(mapdl, cleared):
    mapdl.block(0, 1, 0, 1, 0, 1)
    mapdl.et(1, 186)
    mapdl.esize(0.25)
    mapdl.vmesh("ALL")


@pytest.fixture(scope="function")
def coupled_example(mapdl, cleared):
    # TRANSIENT THERMAL STRESS IN A CYLINDER
    vm33 = vmfiles["vm33"]
    with open(vm33, "r") as fid:
        mapdl_code = fid.read()

    mapdl_code = mapdl_code.replace(
        "SOLVE", "SOLVE\n/COM Ending script after first simulation\n/EOF"
    )
    mapdl.finish()
    mapdl.input_strings(mapdl_code)


@pytest.fixture(scope="function")
def contact_geom_and_mesh(mapdl, cleared):
    mapdl.mute = True

    # Based on tech demo 28.
    # ***** Problem parameters ********
    l = 76.2e-03 / 3  # Length of each plate,m
    w = 31.75e-03 / 2  # Width of each plate,m
    t = 3.18e-03  # Thickness of each plate,m
    r1 = 7.62e-03  # Shoulder radius of tool,m
    h = 15.24e-03  # Height of tool, m
    l1 = r1  # Starting location of tool on weldline
    l2 = l - l1
    tcc1 = 2e06  # Thermal contact conductance b/w plates,W/m^2'C
    tcc2 = 10  # Thermal contact conductance b/w tool &
    # workpiece,W/m^2'C
    fwgt = 0.95  # weight factor for distribution of heat b/w tool
    # & workpiece
    fplw = 0.8  # Fraction of plastic work converted to heat

    # this is also modified in the dependent fixture
    uz1 = t / 4000  # Depth of penetration,m

    # ==========================================================
    # * Material properties
    # ==========================================================
    # * Material properties for 304l stainless steel Plates
    mapdl.mp("ex", 1, 193e9)  # Elastic modulus (N/m^2)
    mapdl.mp("nuxy", 1, 0.3)  # Poisson's ratio
    mapdl.mp("alpx", 1, 1.875e-5)  # Coefficient of thermal expansion, µm/m'c
    # Fraction of plastic work converted to heat, 80%
    mapdl.mp("qrate", 1, fplw)

    # *BISO material model
    EX = 193e9
    ET = 2.8e9
    EP = EX * ET / (EX - ET)
    mapdl.tb("plas", 1, 1, "", "biso")  # Bilinear isotropic material
    mapdl.tbdata(1, 290e6, EP)  # Yield stress & plastic tangent modulus
    mapdl.mptemp(1, 0, 200, 400, 600, 800, 1000)
    mapdl.mpdata("kxx", 1, 1, 16, 19, 21, 24, 29, 30)  # therm cond.(W/m'C)
    mapdl.mpdata("c", 1, 1, 500, 540, 560, 590, 600, 610)  # spec heat(J/kg'C)
    mapdl.mpdata("dens", 1, 1, 7894, 7744, 7631, 7518, 7406, 7406)  # kg/m^3

    # * Material properties for PCBN tool
    mapdl.mp("ex", 2, 680e9)  # Elastic modulus (N/m^2)
    mapdl.mp("nuxy", 2, 0.22)  # Poisson's ratio
    mapdl.mp("kxx", 2, 100)  # Thermal conductivity(W/m'C)
    mapdl.mp("c", 2, 750)  # Specific heat(J/kg'C)
    mapdl.mp("dens", 2, 4280)  # Density,kg/m^3

    # ==========================================================
    # * Geometry
    # ==========================================================
    # * Node for pilot node
    mapdl.n(1, 0, 0, h)
    # * Workpiece geometry (two rectangular plates)
    mapdl.block(0, w, -l1, l2, 0, -t)
    mapdl.block(0, -w, -l1, l2, 0, -t)
    # * Tool geometry
    mapdl.cyl4(0, 0, r1, 0, r1, 90, h)
    mapdl.cyl4(0, 0, r1, 90, r1, 180, h)
    mapdl.cyl4(0, 0, r1, 180, r1, 270, h)
    mapdl.cyl4(0, 0, r1, 270, r1, 360, h)
    mapdl.vglue(3, 4, 5, 6)

    # ==========================================================
    # * Meshing
    # ==========================================================
    mapdl.et(1, "SOLID226", 11)  # Coupled-field solid element,KEYOPT(1) is
    # set to 11 for a structural-thermal analysis
    mapdl.allsel()
    ndiv1 = 2
    ndiv2 = 5
    ndiv3 = 1

    mapdl.lsel("s", "", "", 4, 5)
    mapdl.lsel("a", "", "", 14, 19, 5)
    mapdl.lesize("all", "", "", ndiv1)
    mapdl.lsel("s", "", "", 16, 17)
    mapdl.lsel("a", "", "", 2, 7, 5)
    mapdl.lesize("all", "", "", ndiv1)
    mapdl.lsel("s", "", "", 1)
    mapdl.lsel("a", "", "", 3)
    mapdl.lsel("a", "", "", 6)
    mapdl.lsel("a", "", "", 8)
    mapdl.lsel("a", "", "", 13)
    mapdl.lsel("a", "", "", 15)
    mapdl.lsel("a", "", "", 18)
    mapdl.lsel("a", "", "", 20)
    mapdl.lesize("all", "", "", ndiv2)
    mapdl.lsel("s", "", "", 9, "")
    mapdl.lsel("a", "", "", 22)
    mapdl.lesize("all", "", "", ndiv3)
    mapdl.allsel("all")
    mapdl.mshmid(2)  # midside nodes dropped
    mapdl.vsweep(1)
    mapdl.vsweep(2)
    mapdl.vsel("u", "volume", "", 1, 2)
    mapdl.mat(2)
    mapdl.esize(0.005)
    mapdl.numstr("NODE", 1000)
    mapdl.vsweep("all")
    mapdl.allsel("all")

    # ==========================================================
    # * Contact Pairs
    # ==========================================================
    # * Define Rigid Surface Constraint on tool top surface
    mapdl.et(2, "TARGE170")
    mapdl.keyopt(2, 2, 1)  # User defined boundary condition on rigid
    # target nodes

    mapdl.et(3, "CONTA174")
    mapdl.keyopt(3, 1, 1)  # To include Temp DOF
    mapdl.keyopt(3, 2, 2)  # To include MPC contact algorithm
    mapdl.keyopt(3, 4, 2)  # For a rigid surface constraint
    mapdl.keyopt(3, 12, 5)  # To set the behavior of contact surface as a
    # bonded (always)

    mapdl.vsel("u", "volume", "", 1, 2)  # Selecting Tool volume
    mapdl.allsel("below", "volume")
    mapdl.nsel("r", "loc", "z", h)  # Selecting nodes on the tool top surface
    mapdl.type(3)
    mapdl.r(3)
    mapdl.real(3)
    mapdl.esln()
    mapdl.esurf()  # Create contact elements
    mapdl.allsel("all")

    # * Define pilot node at the top of the tool
    mapdl.nsel("s", "node", "", 1)
    mapdl.tshap("pilo")
    mapdl.type(2)
    mapdl.real(3)
    mapdl.e(1)  # Create target element on pilot node
    mapdl.allsel()

    # * Define contact pair between two plates
    mapdl.et(6, "TARGE170")
    mapdl.et(7, "CONTA174")
    mapdl.keyopt(7, 1, 1)  # Displacement & Temp dof
    mapdl.keyopt(7, 4, 3)  # To include Surface projection based method
    mapdl.mat(1)
    mapdl.asel("s", "", "", 5)
    mapdl.nsla("", 1)
    mapdl.cm("tn.cnt", "node")  # Creating component on weld side of plate1

    mapdl.asel("s", "", "", 12)
    mapdl.nsla("", 1)
    mapdl.cm("tn.tgt", "node")  # Creating component on weld side of plate2

    mapdl.allsel("all")
    mapdl.type(6)
    mapdl.r(6)
    mapdl.rmodif(6, 14, tcc1)  # A real constant TCC,Thermal contact
    # conductance coeffi. b/w the plates, W/m^2'C
    mapdl.rmodif(6, 35, 1000)  # A real constant TBND,Bonding temperature
    # for welding, 'C
    mapdl.real(6)
    mapdl.cmsel("s", "tn.cnt")
    mapdl.esurf()
    mapdl.type(7)
    mapdl.real(6)
    mapdl.cmsel("s", "tn.tgt")
    mapdl.esurf()
    mapdl.allsel("all")

    # * Define contact pair between tool & workpiece
    mapdl.et(4, "TARGE170")
    mapdl.et(5, "CONTA174")
    mapdl.keyopt(5, 1, 1)  # Displacement & Temp dof
    mapdl.keyopt(5, 5, 3)  # Close gap/reduce penetration with auto cnof
    mapdl.keyopt(5, 9, 1)  # Exclude both initial penetration or gap
    mapdl.keyopt(5, 10, 0)  # Contact stiffness update each iteration
    # based

    # Bottom & lateral(all except top) surfaces of tool for target
    mapdl.vsel("u", "volume", "", 1, 2)
    mapdl.allsel("below", "volume")
    mapdl.nsel("r", "loc", "z", 0, h)
    mapdl.nsel("u", "loc", "z", h)
    mapdl.type(4)
    mapdl.r(5)
    mapdl.tb("fric", 5, 6)  # Definition of friction co efficient at
    # different temp
    mapdl.tbtemp(25)
    mapdl.tbdata(1, 0.4)  # friction co-efficient at temp 25
    mapdl.tbtemp(200)
    mapdl.tbdata(1, 0.4)  # friction co-efficient at temp 200
    mapdl.tbtemp(400)
    mapdl.tbdata(1, 0.4)  # friction co-efficient at temp 400
    mapdl.tbtemp(600)
    mapdl.tbdata(1, 0.3)  # friction co-efficient at temp 600
    mapdl.tbtemp(800)
    mapdl.tbdata(1, 0.3)  # friction co-efficient at temp 800
    mapdl.tbtemp(1000)
    mapdl.tbdata(1, 0.2)  # friction co-efficient at temp 1000
    mapdl.rmodif(5, 9, 500e6)  # Max.friction stress
    mapdl.rmodif(5, 14, tcc2)  # Thermal contact conductance b/w tool and
    # workpiece, 10 W/m^2'C
    mapdl.rmodif(5, 15, 1)  # A real constant FHTG,the fraction of
    # frictional dissipated energy converted
    # into heat
    mapdl.rmodif(5, 18, fwgt)  # A real constant  FWGT, weight factor for
    # the distribution of heat between the
    # contact and target surfaces, 0.95
    mapdl.real(5)
    mapdl.mat(5)
    mapdl.esln()
    mapdl.esurf()
    mapdl.allsel("all")

    # Top surfaces of plates nodes for contact
    mapdl.vsel("s", "volume", "", 1, 2)
    mapdl.allsel("below", "volume")
    mapdl.nsel("r", "loc", "z", 0)
    mapdl.type(5)
    mapdl.real(5)
    mapdl.esln()
    mapdl.esurf()
    mapdl.allsel("all")

    # ==========================================================
    # * Boundary conditions
    # ==========================================================
    mapdl.tref(25)  # Reference temperature 25'C
    mapdl.allsel()
    mapdl.nsel("all")
    mapdl.ic("all", "temp", 25)  # Initial condition at nodes,temp 25'C

    # Mechanical Boundary Conditions
    # 20% ends of the each plate is constraint
    mapdl.nsel("s", "loc", "x", -0.8 * w, -w)
    mapdl.nsel("a", "loc", "x", 0.8 * w, w)
    mapdl.d("all", "uz", 0)  # Displacement constraint in x-direction
    mapdl.d("all", "uy", 0)  # Displacement constraint in y-direction
    mapdl.d("all", "ux", 0)  # Displacement constraint in z-direction
    mapdl.allsel("all")

    # Bottom of workpiece is constraint in z-direction
    mapdl.nsel("s", "loc", "z", -t)
    mapdl.d("all", "uz")  # Displacement constraint in z-direction
    mapdl.allsel("all")

    # Thermal Boundary Conditions
    # Convection heat loss from the workpiece surfaces
    mapdl.vsel("s", "volume", "", 1, 2)  # Selecting the workpiece
    mapdl.allsel("below", "volume")
    mapdl.nsel("r", "loc", "z", 0)
    mapdl.nsel("a", "loc", "x", -w)
    mapdl.nsel("a", "loc", "x", w)
    mapdl.nsel("a", "loc", "y", -l1)
    mapdl.nsel("a", "loc", "y", l2)
    mapdl.sf("all", "conv", 30, 25)

    # Convection (high)heat loss from the workpiece bottom
    mapdl.nsel("s", "loc", "z", -t)
    mapdl.sf("all", "conv", 300, 25)
    mapdl.allsel("all")

    # Convection heat loss from the tool surfaces
    mapdl.vsel("u", "volume", "", 1, 2)  # Selecting the tool
    mapdl.allsel("below", "volume")
    mapdl.csys(1)
    mapdl.nsel("r", "loc", "x", r1)
    mapdl.nsel("a", "loc", "z", h)
    mapdl.sf("all", "conv", 30, 25)
    mapdl.allsel("all")

    # Constraining all DOFs at pilot node except the Temp DOF
    mapdl.d(1, "all")
    mapdl.ddele(1, "temp")
    mapdl.allsel("all")
    mapdl.mute = False


@pytest.fixture(scope="function")
def cuadratic_beam_problem(mapdl, cleared):

    # Type of analysis: static.
    mapdl.antype("STATIC")

    # Element type: BEAM188.
    mapdl.et(1, "BEAM188")

    # Special Features are defined by keyoptions of beam element:

    # KEYOPT(3)
    # Shape functions along the length:
    # Cubic
    mapdl.keyopt(1, 3, 3)  # Cubic shape function

    # KEYOPT(9)
    # Output control for values extrapolated to the element
    # and section nodes:
    # Same as KEYOPT(9) = 1 plus stresses and strains at all section nodes
    mapdl.keyopt(1, 9, 3, mute=True)

    mapdl.mp("EX", 1, 30e6)
    mapdl.mp("PRXY", 1, 0.3)

    w_f = 1.048394965
    w_w = 0.6856481
    sec_num = 1
    mapdl.sectype(sec_num, "BEAM", "I", "ISection")
    mapdl.secdata(15, 15, 28 + (2 * w_f), w_f, w_f, w_w)

    # Define nodes
    for node_num in range(1, 6):
        mapdl.n(node_num, (node_num - 1) * 120, 0, 0)

    # Define one node for the orientation of the beam cross-section.
    orient_node = mapdl.n(6, 60, 1)

    for elem_num in range(1, 5):
        mapdl.e(elem_num, elem_num + 1, orient_node)

    # BC for the beams seats
    mapdl.d(2, "UX", lab2="UY")
    mapdl.d(4, "UY")

    # BC for all nodes of the beam
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.d("ALL", "UZ")
    mapdl.d("ALL", "ROTX")
    mapdl.d("ALL", "ROTY")
    mapdl.nsel("ALL")

    # Parametrization of the distributed load.
    w = 10000 / 12

    # Application of the surface load to the beam element.
    mapdl.sfbeam(1, 1, "PRES", w)
    mapdl.sfbeam(4, 1, "PRES", w)
    mapdl.finish()

    mapdl.run("/SOLU")
    mapdl.solve()
    mapdl.finish()


def create_geometry(mapdl):
    mapdl.prep7()
    k0 = mapdl.k(1, 0, 0, 0)
    k1 = mapdl.k(2, 0, 5, 0)
    k2 = mapdl.k(3, 5, 5, 0)
    k3 = mapdl.k(4, 5, 0, 0)
    k4 = mapdl.k(5, 0, 0, 5)
    k5 = mapdl.k(6, 0, 5, 5)
    k6 = mapdl.k(7, 5, 5, 5)
    k7 = mapdl.k(8, 5, 0, 5)
    a0 = mapdl.a(1, 2, 3, 4)
    a1 = mapdl.a(5, 6, 7, 8)
    a2 = mapdl.a(3, 4, 8, 7)
    a3 = mapdl.a(1, 2, 6, 5)
    keypoints = [k0, k1, k2, k3, k4, k5, k6, k7]
    areas = [a0, a1, a2, a3]
    mapdl.esize(5)
    mapdl.mshape(1, "2D")
    mapdl.et(1, "SHELL181")
    mapdl.amesh("ALL")
    return areas, keypoints


@pytest.fixture(scope="function")
def two_dimensional_mesh(mapdl, cleared):
    length = 4
    height = 1
    thickness = 0.2
    mesh_size = 0.1

    mapdl.prep7()

    mapdl.r(r1=thickness)
    mapdl.et(1, "PLANE182", kop3=3, kop6=0)
    mapdl.rectng(0, length, 0, height)
    mapdl.mshkey(1)
    mapdl.mshape(0, "2D")
    mapdl.esize(mesh_size)
    mapdl.amesh("ALL")


@pytest.fixture
def query(mapdl, cleared):
    return mapdl.queries


@pytest.fixture
def common_functions_and_classes():
    return get_details_of_nodes, get_details_of_elements, Node, Element
