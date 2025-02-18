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
from unittest.mock import patch

import psutil
import pytest

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core._version import SUPPORTED_ANSYS_VERSIONS as versions
from ansys.mapdl.core.errors import NotEnoughResources, VersionError
from ansys.mapdl.core.launcher import LOCALHOST
from ansys.mapdl.core.launcher.tools import (
    ALLOWABLE_LAUNCH_MAPDL_ARGS,
    _is_ubuntu,
    _parse_ip_route,
    check_kwargs,
    check_mode,
    force_smp_in_student,
    generate_mapdl_launch_command,
    generate_start_parameters,
    get_cpus,
    get_exec_file,
    get_ip,
    get_port,
    get_run_location,
    get_start_instance,
    get_version,
    pre_check_args,
    remove_err_files,
    set_license_switch,
    set_MPI_additional_switches,
    update_env_vars,
)
from ansys.mapdl.core.licensing import LICENSES
from ansys.mapdl.core.mapdl_core import _ALLOWED_START_PARM
from ansys.mapdl.core.misc import check_has_mapdl
from conftest import ON_LOCAL, TESTING_MINIMAL, NullContext, requires

_ARGS_VALIDS = ALLOWABLE_LAUNCH_MAPDL_ARGS.copy()
_ARGS_VALIDS.extend(_ALLOWED_START_PARM)
_ARGS = _ARGS_VALIDS.copy()
_ARGS.extend(["asdf", "non_valid_argument"])


@pytest.mark.parametrize("arg", _ARGS)
def test_check_kwargs(arg):
    if arg in _ARGS_VALIDS:
        context = NullContext()
    else:
        context = pytest.raises(ValueError)

    with context:
        check_kwargs({"kwargs": {arg: None}})


@pytest.mark.parametrize(
    "start_instance,context",
    [
        pytest.param(True, NullContext(), id="Boolean true"),
        pytest.param(False, NullContext(), id="Boolean false"),
        pytest.param("true", NullContext(), id="String true"),
        pytest.param("TRue", NullContext(), id="String true weird capitalization"),
        pytest.param("2", pytest.raises(ValueError), id="String number"),
        pytest.param(2, pytest.raises(ValueError), id="Int"),
    ],
)
def test_get_start_instance_argument(monkeypatch, start_instance, context):
    if "PYMAPDL_START_INSTANCE" in os.environ:
        monkeypatch.delenv("PYMAPDL_START_INSTANCE")
    with context:
        if "true" in str(start_instance).lower():
            assert get_start_instance(start_instance)
        else:
            assert not get_start_instance(start_instance)


@pytest.mark.parametrize(
    "start_instance, context",
    [
        pytest.param("true", NullContext()),
        pytest.param("TRue", NullContext()),
        pytest.param("False", NullContext()),
        pytest.param("FaLSE", NullContext()),
        pytest.param("asdf", pytest.raises(OSError)),
        pytest.param("1", pytest.raises(OSError)),
        pytest.param("", NullContext()),
    ],
)
def test_get_start_instance_envvar(monkeypatch, start_instance, context):
    monkeypatch.setenv("PYMAPDL_START_INSTANCE", start_instance)
    with context:
        if "true" in start_instance.lower() or start_instance == "":
            assert get_start_instance(start_instance=None)
        else:
            assert not get_start_instance(start_instance=None)


@requires("ansys-tools-path")
@requires("local")
def test_get_default_ansys():
    from ansys.mapdl.core.launcher import get_default_ansys

    assert get_default_ansys() is not None


def raising():
    raise Exception("An error")


@patch("ansys.mapdl.core.launcher.tools.check_valid_ansys", raising)
def test_check_has_mapdl_failed():
    assert check_has_mapdl() is False


def test_check_has_mapdl():
    if TESTING_MINIMAL:
        assert check_has_mapdl() is False
    else:
        assert check_has_mapdl() == ON_LOCAL


@patch("os.name", "nt")
def test_validate_sw():
    # ensure that windows adds msmpi
    # fake windows path
    version = 211
    add_sw = set_MPI_additional_switches("", version=version)
    assert "msmpi" in add_sw

    with pytest.warns(
        UserWarning, match="Due to incompatibilities between this MAPDL version"
    ):
        add_sw = set_MPI_additional_switches("-mpi intelmpi", version=version)
        assert "msmpi" in add_sw and "intelmpi" not in add_sw

    with pytest.warns(
        UserWarning, match="Due to incompatibilities between this MAPDL version"
    ):
        add_sw = set_MPI_additional_switches("-mpi INTELMPI", version=version)
        assert "msmpi" in add_sw and "INTELMPI" not in add_sw


def test_force_smp_in_student():
    add_sw = ""
    exec_path = (
        r"C:\Program Files\ANSYS Inc\ANSYS Student\v222\ansys\bin\winx64\ANSYS222.exe"
    )
    assert "-smp" in force_smp_in_student(add_sw, exec_path)

    add_sw = "-mpi"
    exec_path = (
        r"C:\Program Files\ANSYS Inc\ANSYS Student\v222\ansys\bin\winx64\ANSYS222.exe"
    )
    assert "-smp" not in force_smp_in_student(add_sw, exec_path)

    add_sw = "-dmp"
    exec_path = (
        r"C:\Program Files\ANSYS Inc\ANSYS Student\v222\ansys\bin\winx64\ANSYS222.exe"
    )
    assert "-smp" not in force_smp_in_student(add_sw, exec_path)

    add_sw = ""
    exec_path = r"C:\Program Files\ANSYS Inc\v222\ansys\bin\winx64\ANSYS222.exe"
    assert "-smp" not in force_smp_in_student(add_sw, exec_path)

    add_sw = "-SMP"
    exec_path = r"C:\Program Files\ANSYS Inc\v222\ansys\bin\winx64\ANSYS222.exe"
    assert "-SMP" in force_smp_in_student(add_sw, exec_path)


@patch("os.name", "nt")
@patch("psutil.cpu_count", lambda *args, **kwargs: 10)
def test_generate_mapdl_launch_command_windows():
    assert os.name == "nt"  # Checking mocking is properly done

    exec_file = "C:/Program Files/ANSYS Inc/v242/ansys/bin/winx64/ANSYS242.exe"
    jobname = "myjob"
    nproc = 10
    port = 1000
    ram = 2024
    additional_switches = "-my_add=switch"

    cmd = generate_mapdl_launch_command(
        exec_file=exec_file,
        jobname=jobname,
        nproc=nproc,
        port=port,
        ram=ram,
        additional_switches=additional_switches,
    )

    assert isinstance(cmd, list)

    assert f"{exec_file}" in cmd
    assert "-j" in cmd
    assert f"{jobname}" in cmd
    assert "-port" in cmd
    assert f"{port}" in cmd
    assert "-m" in cmd
    assert f"{ram}" in cmd
    assert "-np" in cmd
    assert f"{nproc}" in cmd
    assert "-grpc" in cmd
    assert f"{additional_switches}" in cmd
    assert "-b" in cmd
    assert "-i" in cmd
    assert ".__tmp__.inp" in cmd
    assert "-o" in cmd
    assert ".__tmp__.out" in cmd

    cmd = " ".join(cmd)
    assert f"{exec_file}" in cmd
    assert f" -j {jobname} " in cmd
    assert f" -port {port} " in cmd
    assert f" -m {ram} " in cmd
    assert f" -np {nproc} " in cmd
    assert " -grpc" in cmd
    assert f" {additional_switches} " in cmd
    assert f" -b -i .__tmp__.inp " in cmd
    assert f" -o .__tmp__.out " in cmd


@patch("os.name", "posix")
def test_generate_mapdl_launch_command_linux():
    assert os.name != "nt"  # Checking mocking is properly done

    exec_file = "/ansys_inc/v242/ansys/bin/ansys242"
    jobname = "myjob"
    nproc = 10
    port = 1000
    ram = 2024
    additional_switches = "-my_add=switch"

    cmd = generate_mapdl_launch_command(
        exec_file=exec_file,
        jobname=jobname,
        nproc=nproc,
        port=port,
        ram=ram,
        additional_switches=additional_switches,
    )
    assert isinstance(cmd, list)
    assert all([isinstance(each, str) for each in cmd])

    assert isinstance(cmd, list)

    assert f"{exec_file}" in cmd
    assert "-j" in cmd
    assert f"{jobname}" in cmd
    assert "-port" in cmd
    assert f"{port}" in cmd
    assert "-m" in cmd
    assert f"{ram}" in cmd
    assert "-np" in cmd
    assert f"{nproc}" in cmd
    assert "-grpc" in cmd
    assert f"{additional_switches}" in cmd

    assert "-b" not in cmd
    assert "-i" not in cmd
    assert ".__tmp__.inp" not in cmd
    assert "-o" not in cmd
    assert ".__tmp__.out" not in cmd

    cmd = " ".join(cmd)
    assert f"{exec_file} " in cmd
    assert f" -j {jobname} " in cmd
    assert f" -port {port} " in cmd
    assert f" -m {ram} " in cmd
    assert f" -np {nproc} " in cmd
    assert " -grpc" in cmd
    assert f" {additional_switches} " in cmd

    assert f" -i .__tmp__.inp " not in cmd
    assert f" -o .__tmp__.out " not in cmd


@pytest.mark.parametrize(
    "mode, version, osname, context, res",
    [
        [None, None, None, NullContext(), "grpc"],  # default
        [
            "grpc",
            201,
            "nt",
            pytest.raises(
                VersionError, match="gRPC mode requires MAPDL 2020R2 or newer on Window"
            ),
            None,
        ],
        [
            "grpc",
            202,
            "posix",
            pytest.raises(
                VersionError, match="gRPC mode requires MAPDL 2021R1 or newer on Linux."
            ),
            None,
        ],
        ["grpc", 212, "nt", NullContext(), "grpc"],
        ["grpc", 221, "posix", NullContext(), "grpc"],
        ["grpc", 221, "nt", NullContext(), "grpc"],
        [
            "console",
            221,
            "nt",
            pytest.raises(ValueError, match="Console mode requires Linux."),
            None,
        ],
        [
            "console",
            221,
            "posix",
            pytest.warns(
                UserWarning,
                match="Console mode not recommended in MAPDL 2021R1 or newer.",
            ),
            "console",
        ],
        [
            "nomode",
            221,
            "posix",
            pytest.raises(ValueError, match=f'Invalid MAPDL server mode "nomode"'),
            None,
        ],
        [None, 211, "posix", NullContext(), "grpc"],
        [None, 211, "nt", NullContext(), "grpc"],
        [None, 202, "nt", NullContext(), "grpc"],
        [
            None,
            201,
            "nt",
            pytest.raises(VersionError, match="Running MAPDL as a service requires"),
            None,
        ],
        [None, 202, "posix", NullContext(), "console"],
        [None, 201, "posix", NullContext(), "console"],
        [
            None,
            110,
            "posix",
            pytest.warns(
                UserWarning,
                match="MAPDL as a service has not been tested on MAPDL < v13",
            ),
            "console",
        ],
        [
            None,
            110,
            "nt",
            pytest.raises(VersionError, match="Running MAPDL as a service requires"),
            None,
        ],
        [
            "anymode",
            None,
            "posix",
            pytest.warns(UserWarning, match="PyMAPDL couldn't detect MAPDL version"),
            "anymode",
        ],
    ],
)
def test_check_mode(mode, version, osname, context, res):
    with patch("os.name", osname):
        with context as cnt:
            assert res == check_mode(mode, version)


def test_env_injection():
    no_inject = update_env_vars(None, None)
    assert no_inject == os.environ.copy()  # return os.environ

    assert "myenvvar" in update_env_vars({"myenvvar": "True"}, None)

    _env_vars = update_env_vars(None, {"myenvvar": "True"})
    assert len(_env_vars) == 1
    assert "myenvvar" in _env_vars

    with pytest.raises(ValueError):
        update_env_vars({"myenvvar": "True"}, {"myenvvar": "True"})

    with pytest.raises(TypeError):
        update_env_vars("asdf", None)

    with pytest.raises(TypeError):
        update_env_vars(None, "asdf")


@pytest.mark.parametrize(
    "license_short,license_name",
    [[each_key, each_value] for each_key, each_value in LICENSES.items()],
)
def test_license_product_argument(license_short, license_name):
    additional_switches = set_license_switch(license_name, "qwer")
    assert f"qwer -p {license_short}" in additional_switches


@pytest.mark.parametrize("unvalid_type", [1, {}, ()])
def test_license_product_argument_type_error(unvalid_type):
    with pytest.raises(TypeError):
        set_license_switch(unvalid_type, "")


def test_license_product_argument_warning():
    with pytest.warns(UserWarning):
        assert "-p asdf" in set_license_switch("asdf", "qwer")


@pytest.mark.parametrize(
    "license_short,license_name",
    [[each_key, each_value] for each_key, each_value in LICENSES.items()],
)
def test_license_product_argument_p_arg(license_short, license_name):
    assert f"qw1234 -p {license_short}" == set_license_switch(
        None, f"qw1234 -p {license_short}"
    )


def test_license_product_argument_p_arg_warning():
    with pytest.warns(UserWarning):
        assert "qwer -p asdf" in set_license_switch(None, "qwer -p asdf")


def test_generate_start_parameters_console():
    args = {"mode": "console", "start_timeout": 90}

    new_args = generate_start_parameters(args)
    assert "start_timeout" in new_args
    assert "ram" not in new_args
    assert "override" not in new_args
    assert "timeout" not in new_args


@patch(
    "socket.gethostbyname",
    lambda *args, **kwargs: "123.45.67.89" if args[0] != LOCALHOST else LOCALHOST,
)
@pytest.mark.parametrize(
    "ip,ip_env",
    [[None, None], [None, "123.45.67.89"], ["123.45.67.89", "111.22.33.44"]],
)
def test_get_ip(monkeypatch, ip, ip_env):
    monkeypatch.delenv("PYMAPDL_IP", False)
    if ip_env:
        monkeypatch.setenv("PYMAPDL_IP", ip_env)
    args = {"ip": ip}

    get_ip(args)

    if ip:
        assert args["ip"] == ip
    else:
        if ip_env:
            assert args["ip"] == ip_env
        else:
            assert args["ip"] == LOCALHOST


@pytest.mark.parametrize(
    "port,port_envvar,start_instance,port_busy,result",
    (
        [None, None, True, False, 50052],  # Standard case
        [None, None, True, True, 50054],
        [None, 50053, True, True, 50053],
        [None, 50053, False, False, 50053],
        [50054, 50053, True, False, 50054],
        [50054, 50053, True, False, 50054],
        [50054, None, False, False, 50054],
    ),
)
def test_get_port(monkeypatch, port, port_envvar, start_instance, port_busy, result):
    # Settings
    pymapdl._LOCAL_PORTS = []  # Resetting

    monkeypatch.delenv("PYMAPDL_PORT", False)
    if port_envvar:
        monkeypatch.setenv("PYMAPDL_PORT", str(port_envvar))

    # Testing
    if port_busy:
        # Success after the second retry, it should go up to 2.
        # But for some reason, it goes up 3.
        side_effect = [True, True, False]
    else:
        side_effect = [False]

    context = patch(
        "ansys.mapdl.core.launcher.tools.port_in_use", side_effect=side_effect
    )

    with context:
        assert get_port(port, start_instance) == result


@requires("ansys-tools-path")
@patch("ansys.tools.path.path._mapdl_version_from_path", lambda *args, **kwargs: 201)
@patch("ansys.mapdl.core._HAS_ATP", True)
def test_get_version_version_error(monkeypatch):
    monkeypatch.delenv("PYMAPDL_MAPDL_VERSION", False)

    with pytest.raises(
        VersionError, match="The MAPDL gRPC interface requires MAPDL 20.2 or later"
    ):
        get_version(None, "/path/to/executable")


@pytest.mark.parametrize("version", [211, 221, 232])
def test_get_version_env_var(monkeypatch, version):
    monkeypatch.setenv("PYMAPDL_MAPDL_VERSION", str(version))

    assert version == get_version(None)
    assert version != get_version(241)


@requires("local")
def test_raise_exec_path_and_version_launcher(mapdl, cleared):
    with pytest.raises(ValueError):
        get_version("asdf", "asdf")


installed_mapdl_versions = []
installed_mapdl_versions.extend([int(each) for each in list(versions.keys())])
installed_mapdl_versions.extend([float(each / 10) for each in versions.keys()])
installed_mapdl_versions.extend([str(each) for each in list(versions.keys())])
installed_mapdl_versions.extend([str(each / 10) for each in versions.keys()])
installed_mapdl_versions.extend(list(versions.values()))
installed_mapdl_versions.extend([None])


@pytest.mark.parametrize("version", installed_mapdl_versions)
def test__verify_version_pass(version):
    ver = get_version(version)
    if version:
        assert isinstance(ver, int)
        assert min(versions.keys()) <= ver <= max(versions.keys())
    else:
        assert ver is None


def test__verify_version_latest():
    assert get_version("latest") is None


@patch("ansys.mapdl.core.launcher.tools._HAS_ATP", False)
def test_get_exec_file(monkeypatch):
    monkeypatch.delenv("PYMAPDL_MAPDL_EXEC", False)

    args = {"exec_file": None, "start_instance": True}

    with pytest.raises(ModuleNotFoundError):
        get_exec_file(args)


def test_get_exec_file_not_found(monkeypatch):
    monkeypatch.delenv("PYMAPDL_MAPDL_EXEC", False)

    args = {"exec_file": "my/fake/path", "start_instance": True}

    with pytest.raises(FileNotFoundError):
        get_exec_file(args)


def _get_application_path(*args, **kwargs):
    return None


@requires("ansys-tools-path")
@patch("ansys.tools.path.path._get_application_path", _get_application_path)
def test_get_exec_file_not_found_two(monkeypatch):
    monkeypatch.delenv("PYMAPDL_MAPDL_EXEC", False)
    args = {"exec_file": None, "start_instance": True}
    with pytest.raises(
        FileNotFoundError, match="Invalid exec_file path or cannot load cached "
    ):
        get_exec_file(args)


@pytest.mark.parametrize("run_location", [None, True])
@pytest.mark.parametrize("remove_temp_dir_on_exit", [None, False, True])
def test_get_run_location(tmpdir, remove_temp_dir_on_exit, run_location):
    if run_location:
        new_path = os.path.join(str(tmpdir), "my_new_path")
        assert not os.path.exists(new_path)
    else:
        new_path = None

    args = {
        "run_location": new_path,
        "remove_temp_dir_on_exit": remove_temp_dir_on_exit,
    }

    get_run_location(args)

    assert os.path.exists(args["run_location"])

    assert "remove_temp_dir_on_exit" in args

    if run_location:
        assert not args["remove_temp_dir_on_exit"]
    elif remove_temp_dir_on_exit:
        assert args["remove_temp_dir_on_exit"]
    else:
        assert not args["remove_temp_dir_on_exit"]


@patch("os.access", lambda *args, **kwargs: False)
def test_get_run_location_no_access(tmpdir):
    with pytest.raises(IOError, match="Unable to write to ``run_location``:"):
        get_run_location({"run_location": str(tmpdir)})


@pytest.mark.parametrize(
    "args,match",
    [
        [
            {"start_instance": True, "ip": True, "on_pool": False},
            "When providing a value for the argument 'ip', the argument",
        ],
        [
            {"exec_file": True, "version": True},
            "Cannot specify both ``exec_file`` and ``version``.",
        ],
        [
            {"scheduler_options": True},
            "PyMAPDL does not read the number of cores from the 'scheduler_options'.",
        ],
        [
            {"launch_on_hpc": True, "ip": "111.22.33.44"},
            "PyMAPDL cannot ensure a specific IP will be used when launching",
        ],
    ],
)
def test_pre_check_args(args, match):
    with pytest.raises(ValueError, match=match):
        pre_check_args(args)


@patch("psutil.cpu_count", lambda *args, **kwags: 5)
@pytest.mark.parametrize("arg", [None, 3, 10])
@pytest.mark.parametrize("env", [None, 3, 10])
def test_get_cpus(monkeypatch, arg, env):
    if env:
        monkeypatch.setenv("PYMAPDL_NPROC", str(env))

    context = NullContext()
    cores_machine = psutil.cpu_count(logical=False)  # it is patched

    if (arg and arg > cores_machine) or (arg is None and env and env > cores_machine):
        context = pytest.raises(NotEnoughResources)

    args = {"nproc": arg, "running_on_hpc": False}
    with context:
        get_cpus(args)

    if arg:
        assert args["nproc"] == arg
    elif env:
        assert args["nproc"] == env
    else:
        assert args["nproc"] == 2


@patch("psutil.cpu_count", lambda *args, **kwags: 1)
def test_get_cpus_min():
    args = {"nproc": None, "running_on_hpc": False}
    get_cpus(args)
    assert args["nproc"] == 1


def test_remove_err_files(tmpdir):
    run_location = str(tmpdir)
    jobname = "jobname"
    err_file = os.path.join(run_location, f"{jobname}.err")
    with open(err_file, "w") as fid:
        fid.write("Dummy")

    assert os.path.isfile(err_file)
    remove_err_files(run_location, jobname)
    assert not os.path.isfile(err_file)


def myosremove(*args, **kwargs):
    raise IOError("Generic error")


@patch("os.remove", myosremove)
def test_remove_err_files_fail(tmpdir):
    run_location = str(tmpdir)
    jobname = "jobname"
    err_file = os.path.join(run_location, f"{jobname}.err")
    with open(err_file, "w") as fid:
        fid.write("Dummy")

    assert os.path.isfile(err_file)
    with pytest.raises(IOError):
        remove_err_files(run_location, jobname)
    assert os.path.isfile(err_file)


def test__parse_ip_route():
    output = """default via 172.25.192.1 dev eth0 proto kernel <<<=== this
172.25.192.0/20 dev eth0 proto kernel scope link src 172.25.195.101 <<<=== not this"""

    assert "172.25.192.1" == _parse_ip_route(output)

    output = """
default via 172.23.112.1 dev eth0 proto kernel
172.23.112.0/20 dev eth0 proto kernel scope link src 172.23.121.145"""

    assert "172.23.112.1" == _parse_ip_route(output)


@requires("linux")
@requires("local")
def test_is_ubuntu():
    assert _is_ubuntu()
