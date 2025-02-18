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
import re
import subprocess  # nosec B404
from unittest.mock import MagicMock, patch

import numpy as np
import psutil
import pytest

from conftest import VALID_PORTS, requires

if VALID_PORTS:
    PORT1 = max(VALID_PORTS) + 1
else:
    PORT1 = 50090


def make_fake_process(pid, name, port=PORT1, ansys_process=False, n_children=0):
    mock_process = MagicMock(spec=psutil.Process)
    mock_process.pid = pid
    mock_process.name.return_value = name
    mock_process.status.return_value = psutil.STATUS_RUNNING
    mock_process.children.side_effect = lambda *arg, **kwargs: [
        i for i in range(n_children)
    ]
    mock_process.cwd.return_value = f"/cwd/of/{name}"

    if ansys_process:
        mock_process.cmdline.return_value = (
            f"/ansys_inc/v251/ansys/bin/ansys251 -grpc -port {port}".split(" ")
        )
    else:
        mock_process.cmdline.return_value = f"/path/to/process".split(" ")

    return mock_process


@pytest.fixture
@requires("click")
@requires("nostudent")
def run_cli():
    def do_run(arguments=""):
        from click.testing import CliRunner

        from ansys.mapdl.core.cli import main

        if arguments:
            args = list(arguments.strip().split(" "))
        else:
            args = []

        runner = CliRunner()
        result = runner.invoke(main, args)

        assert result.exit_code == 0
        return result.output

    return do_run


@requires("click")
@pytest.mark.parametrize("start_instance", [None, True, False])
def test_launch_mapdl_cli(monkeypatch, run_cli, start_instance):
    if start_instance is not None:
        monkeypatch.setenv("PYMAPDL_START_INSTANCE", str(start_instance))
    else:
        monkeypatch.delenv("PYMAPDL_START_INSTANCE", raising=False)

    with (
        patch("ansys.mapdl.core.launcher.launch_mapdl") as mock_launch,
        patch("ansys.mapdl.core.launcher.submitter") as mock_submitter,
    ):  # test we are not calling Popen

        mock_launch.side_effect = lambda *args, **kwargs: (
            "123.45.67.89",
            str(PORT1),
            "123245",
        )

        # Setting a port so it does not collide with the already running instance for testing
        output = run_cli(f"start --port {PORT1}")

    assert "Success: Launched an MAPDL instance " in output
    assert str(PORT1) in output

    # grab ips and port
    pid = re.search(r"\(PID=(\d+)\)", output)
    assert pid
    pid = int(re.search(r"\(PID=(\d+)\)", output).groups()[0])
    assert pid != 0


@requires("click")
@pytest.mark.parametrize(
    "mapping",
    ((False, True), (False, True, False), (False, False, False), (True, True, False)),
)
def test_pymapdl_stop_instances(run_cli, mapping):

    fake_process_ = [
        {
            "pid": np.random.randint(10000, 100000),
            "name": f"ansys251_{ind}" if each else "process",
            "port": str(50052 + ind),
            "ansys_process": each,
        }
        for ind, each in enumerate(mapping)
    ]

    fake_processes = [make_fake_process(**each) for each in fake_process_]

    with (
        patch("ansys.mapdl.core.cli.stop._kill_process") as mock_kill,
        patch("psutil.pid_exists") as mock_pid,
        patch("psutil.process_iter", return_value=iter(fake_processes)),
    ):

        mock_pid.return_value = lambda *args, **kwargs: True  # All process exists
        mock_kill.side_effect = lambda *args, **kwargs: None  # avoid kill nothing

        if sum(mapping) == 0:
            output = run_cli(f"stop --port {PORT1}")
            assert (
                f"error: no ansys instances running on port {PORT1}" in output.lower()
            )
            mock_kill.assert_not_called()

            output = run_cli(f"stop --all")
            assert f"error: no ansys instances have been found." in output.lower()
            mock_kill.assert_not_called()

        elif sum(mapping) == 1:
            # Port
            process, process_mock = [
                (each, each_mock)
                for each, each_mock in zip(fake_process_, fake_processes)
                if "ansys251" in each["name"]
            ][0]
            port = process["port"]

            output = run_cli(f"stop --port {port}")
            assert (
                f"success: ansys instances running on port {port} have been stopped"
                in output.lower()
            )

            # PID
            pid = process["pid"]
            with patch("psutil.Process") as mock_process:
                mock_process.return_value = process_mock

                output = run_cli(f"stop --pid {pid}")
                assert (
                    f"the process with pid {pid} and its children have been stopped."
                    in output.lower()
                )

            mock_kill.assert_called()
            assert mock_kill.call_count == 2

        else:
            output = run_cli(f"stop --all")
            assert "success: ansys instances have been stopped." in output.lower()
            assert mock_kill.call_count == sum(mapping)


@requires("click")
@pytest.mark.parametrize(
    "arg,check",
    (
        ("", {}),  # default
        ("-i", {"Is Instance": False}),
        ("-c", {"Command line": True}),
        ("-l", {"Command line": True, "Working directory": True}),
        ("-cwd", {"Working directory": True}),
        ("--instances", {"Is Instance": False}),
        ("--cmd", {"Command line": True}),
        ("--long", {"Command line": True, "Working directory": True}),
        ("--location", {"Working directory": True}),
    ),
)
@patch("psutil.pid_exists", lambda *args, **kwargs: True)
def test_launch_mapdl_cli_list(run_cli, arg, check):

    mapping = (False, True, False, True, False, False)
    is_instance = (False, False, False, True, False, False)

    fake_process_ = [
        {
            "pid": np.random.randint(10000, 100000),
            "name": f"ansys251_{ind}" if each else "process",
            "port": str(50052 + ind),
            "ansys_process": each,
            "n_children": 4 if each_ins else 1,
        }
        for ind, (each, each_ins) in enumerate(zip(mapping, is_instance))
    ]

    fake_processes = [make_fake_process(**each) for each in fake_process_]

    checks_defaults = {
        "Is Instance": True,
        "Command line": False,
        "Working directory": False,
    }

    with patch("psutil.process_iter", return_value=iter(fake_processes)):
        output = run_cli(" ".join(["list", arg]))

        assert "running" in output or "sleeping" in output
        checks_defaults.update(check)

        for each, value in checks_defaults.items():
            if value:
                assert each in output
            else:
                assert each not in output

        assert len(output.splitlines()) > 2

        if arg in ["-c", "--cmd"]:
            assert "/ansys_inc/v251/ansys/bin/ansys251" in output

        if arg in ["-cwd", "--location"]:
            assert "/cwd/of/ansys251" in output

        if arg in ["-i", "--instances"]:
            assert len(output.splitlines()) == sum(is_instance) + 2
        else:
            assert len(output.splitlines()) == sum(mapping) + 2

        if arg in ["-l", "--long"]:
            assert "/ansys_inc/v251/ansys/bin/ansys251" in output.lower()

        for ind, (each, each_ins) in enumerate(zip(mapping, is_instance)):
            proc_options = fake_process_[ind]
            # is ansys
            if not each or (not each_ins and arg in ["-i", "--instances"]):
                assert proc_options["name"] not in output
                assert str(proc_options["pid"]) not in output
                assert proc_options["port"] not in output
            else:
                assert proc_options["name"] in output
                assert str(proc_options["pid"]) in output
                assert proc_options["port"] in output


@requires("click")
@pytest.mark.parametrize(
    "arg",
    [
        "ip",
        "license_server_check",
        "mode",
        "loglevel",
        "cleanup_on_exit",
        "start_instance",
        "clear_on_connect",
        "log_apdl",
        "remove_temp_dir_on_exit",
        "print_com",
        "add_env_vars",
        "replace_env_vars",
    ],
)
def test_launch_mapdl_cli_config(run_cli, arg):
    cmd = " ".join(["start", f"--port {PORT1}", "--jobname myjob", f"--{arg} True"])

    with (
        patch("ansys.mapdl.core.launcher.launch_mapdl") as mock_launch,
        patch("ansys.mapdl.core.launcher.submitter") as mock_submitter,
    ):  # test we are not calling Popen
        mock_launch.side_effect = lambda *args, **kwargs: (
            "123.45.67.89",
            str(PORT1),
            "123245",
        )

        output = run_cli(cmd)

        mock_submitter.assert_not_called()
        kwargs = mock_launch.call_args_list[0].kwargs
        assert str(kwargs["port"]) == str(PORT1)

        assert "Launched an MAPDL instance" in output
        assert str(PORT1) in output

        # assert warnings
        assert arg not in kwargs
        assert (
            f"The following argument is not allowed in CLI: '{arg}'" in output
        ), f"Warning about '{arg}' not printed"


@requires("click")
def test_convert(run_cli, tmpdir):
    from ansys.mapdl.core._version import __version__

    input_file = str(tmpdir.join("input.apdl"))
    output_file = str(tmpdir.join("output.pymapdl"))

    with open(input_file, "w") as fid:
        fid.write(
            """/prep7
BLOCK,0,1,0,1,0,1
"""
        )

    run_cli(f"convert -f {input_file} -o {output_file}")

    with open(output_file, "r") as fid:
        converted = fid.read()

    assert "Script generated by ansys-mapdl-core version" in converted
    assert str(__version__) in converted
    assert "from ansys.mapdl.core import launch_mapdl" in converted

    assert (
        """
mapdl.prep7()
mapdl.block(0, 1, 0, 1, 0, 1)"""
        in converted
    )


@requires("click")
@pytest.mark.skipif(os.name != "posix", reason="Piping only works on Linux")
@pytest.mark.parametrize("output", [True, False])
def test_convert_pipe(output):
    cmd = ["echo", "/prep7"]
    cmd2 = ["pymapdl", "convert"]
    if output:
        out_file = "my_output.out"
        cmd2.extend(["-o", out_file])

    process_echo = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process_pymapdl = subprocess.Popen(
        cmd2, stdin=process_echo.stdout, stdout=subprocess.PIPE
    )

    process_echo.stdout.close()

    stdout = process_pymapdl.stdout.read().decode()

    if output:
        assert os.path.exists(out_file)
        with open(out_file, "r") as fid:
            stdout = fid.read()

    assert "mapdl.prep7" in stdout
    assert "Script generated by ansys-mapdl-core version" in stdout
    assert "mapdl.exit()" in stdout


DEFAULT_ARGS = {
    "apdl_strings": "/prep7\nBLOCK,0,1,0,1,0,1",
    "loglevel": "WARNING",
    "auto_exit": True,
    "line_ending": None,
    "exec_file": None,
    "macros_as_functions": True,
    "use_function_names": True,
    "show_log": False,
    "add_imports": True,
    "comment_solve": False,
    "cleanup_output": True,
    "header": True,
    "print_com": True,
    "only_commands": False,
    "use_vtk": None,
    "clear_at_start": False,
    "check_parameter_names": False,
}


@requires("click")
@pytest.mark.parametrize(
    "arg, value",
    (
        ("output", "specific_output"),
        ("loglevel", "specific_output"),
        ("auto_exit", False),
        ("line_ending", "specific_output"),
        ("exec_file", "specific_output"),
        ("macros_as_functions", False),
        ("use_function_names", False),
        ("show_log", True),
        ("add_imports", False),
        ("comment_solve", True),
        ("cleanup_output", False),
        ("header", False),
        ("print_com", False),
        ("only_commands", True),
        ("use_vtk", True),
        ("clear_at_start", True),
        ("check_parameter_names", True),
    ),
)
@patch("ansys.mapdl.core.convert.convert_apdl_block")
def test_convert_passing(mock_conv, run_cli, tmpdir, arg, value):
    mock_conv.return_value = None

    input_file = str(tmpdir.join("input.apdl"))
    with open(input_file, "w") as fid:
        fid.write("/prep7\nBLOCK,0,1,0,1,0,1")

    default_ = DEFAULT_ARGS.copy()
    default_[arg] = value

    if arg not in ["only_commands"]:
        run_cli(f"convert -f {input_file} --{arg} {value}")

    else:
        run_cli(f"convert -f {input_file} --{arg}")

    mock_conv.assert_called()
    kwargs = mock_conv.call_args.kwargs

    for key in DEFAULT_ARGS:
        assert kwargs[key] == default_[key]
