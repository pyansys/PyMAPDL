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

from ansys.mapdl.core.hpc import SshSession, launch_on_remote_hpc
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc
from conftest import TESTING_MINIMAL, has_dependency

if not has_dependency("paramiko") or TESTING_MINIMAL:
    pytest.skip(allow_module_level=True)


def test_launch_on_remote_hpc():
    import io

    with (
        patch("paramiko.client.SSHClient.connect") as mck_connect,
        patch("paramiko.client.SSHClient.exec_command") as mck_exec_command,
        patch("ansys.mapdl.core.launcher.get_hostname_host_cluster") as mock_ghhc,
        patch("socket.gethostbyname") as mck_ghn,
        patch("ansys.mapdl.core.mapdl_grpc.MapdlGrpc.__init__") as mock_mapdl,
    ):

        mck_connect.return_value = None
        mock_ghhc.return_value = "myhost", "123.45.67.89"
        mck_ghn.return_value = "123.45.67.89"
        mock_mapdl.return_value = None
        str_0 = [io.BytesIO(i) for i in [b"stdint", b"Directory created", b""]]
        str_1 = [io.BytesIO(i) for i in [b"stdint", b"Submitted batch job 1001", b""]]
        mck_exec_command.side_effect = (str_0, str_1)

        hostname = "myhost"
        username = "myuser"
        password = "mypass"  # nosec B105
        exec_file = "my/path/to/ansys"
        port = 50054

        mapdl = launch_on_remote_hpc(
            hostname=hostname,
            username=username,
            password=password,
            exec_file=exec_file,
            port=port,
        )

        assert isinstance(mapdl, MapdlGrpc)

        mck_connect.assert_called()
        kwargs = mck_connect.call_args_list[0].kwargs
        assert kwargs["hostname"] == hostname
        assert kwargs["username"] == username
        assert kwargs["password"] == password
        assert kwargs["port"] == 22

        mck_exec_command.assert_called()
        assert len(mck_exec_command.call_args_list) == 2
        kwargs = mck_exec_command.call_args_list[1].kwargs
        assert "sbatch" in kwargs["command"]
        assert exec_file in kwargs["command"]
        assert str(port) in kwargs["command"]

        kwargs = mck_exec_command.call_args_list[0].kwargs
        assert f"/home/{username}/pymapdl/simulations" in kwargs["command"]

        kwargs = mock_mapdl.call_args_list[0].kwargs
        assert kwargs["ip"] == "123.45.67.89"
        assert kwargs["hostname"] == hostname
        assert kwargs["jobid"] == 1001
        assert kwargs["port"] == 50054


@pytest.mark.parametrize(
    "args, match",
    [
        (
            {"exec_file": "path/to/exec", "ip": "123.45.67"},
            "Argument IP is not allowed for launching MAPDL on HPC",
        ),
        (
            {"exec_file": "path/to/exec", "mode": "console"},
            "Only gRPC mode is allowed for launching MAPDL on an SLURM HPC",
        ),
        ({}, "The 'exec_file' argument must be provided."),
    ],
)
def test_non_valid_args(args, match):
    with pytest.raises(ValueError, match=match):
        launch_on_remote_hpc(**args)


def test_failed_to_launch_mapdl_no_jobid():
    with (
        patch("ansys.mapdl.core.hpc.launch_grpc") as mock_launch_grpc,
        patch("ansys.mapdl.core.hpc.kill_job") as mock_kill_job,
    ):
        mock_launch_grpc.side_effect = RuntimeError("Failed to launch MAPDL on HPC")

        with pytest.raises(RuntimeError, match="Failed to launch MAPDL on HPC"):
            launch_on_remote_hpc(exec_file="path/to/exec")

        mock_kill_job.assert_not_called()


def test_failed_to_launch_mapdl_jobid():
    import io

    with (
        patch("paramiko.client.SSHClient.connect") as mck_connect,
        patch("paramiko.client.SSHClient.exec_command") as mck_exec_command,
        patch("ansys.mapdl.core.launcher.get_hostname_host_cluster") as mock_ghhc,
        patch("socket.gethostbyname") as mck_ghn,
        patch("ansys.mapdl.core.mapdl_grpc.MapdlGrpc.__init__") as mock_mapdl,
        patch("ansys.mapdl.core.hpc.get_job_info") as mock_get_job_info,
        patch("ansys.mapdl.core.hpc.kill_job") as mock_kill_job,
    ):

        mck_connect.return_value = None
        mock_ghhc.return_value = "myhost", "123.45.67.89"
        mck_ghn.return_value = "123.45.67.89"
        mock_mapdl.return_value = None
        str_0 = [io.BytesIO(i) for i in [b"stdint", b"Directory created", b""]]
        str_1 = [io.BytesIO(i) for i in [b"stdint", b"Submitted batch job 1001", b""]]
        mck_exec_command.side_effect = (str_0, str_1)
        mock_get_job_info.side_effect = RuntimeError("Failed to launch MAPDL on HPC")

        hostname = "myhost"
        username = "myuser"
        password = "mypass"  # nosec B105
        exec_file = "my/path/to/ansys"
        port = 50054

        with pytest.raises(RuntimeError, match="Failed to launch MAPDL on HPC"):
            launch_on_remote_hpc(
                hostname=hostname,
                username=username,
                password=password,
                exec_file=exec_file,
                port=port,
            )

        mock_kill_job.assert_called()
        assert mock_kill_job.call_args_list[0].args[0] == 1001


def test_launch_on_remote_hpc_failed():
    import io

    with (
        patch("paramiko.client.SSHClient.connect") as mck_connect,
        patch("paramiko.client.SSHClient.exec_command") as mck_exec_command,
        patch("ansys.mapdl.core.launcher.get_hostname_host_cluster") as mock_ghhc,
        patch("socket.gethostbyname") as mck_ghn,
        patch("ansys.mapdl.core.mapdl_grpc.MapdlGrpc.__init__") as mock_mapdl,
    ):

        mck_connect.return_value = None
        mock_ghhc.return_value = "myhost", "123.45.67.89"
        mck_ghn.return_value = "123.45.67.89"
        mock_mapdl.side_effect = RuntimeError("Failed to launch MAPDL on HPC")
        str_0 = [io.BytesIO(i) for i in [b"stdint", b"Directory created", b""]]
        str_1 = [io.BytesIO(i) for i in [b"stdint", b"Submitted batch job 1001", b""]]
        mck_exec_command.side_effect = (str_0, str_1)

        hostname = "myhost"
        username = "myuser"
        password = "mypass"  # nosec B105
        exec_file = "my/path/to/ansys"
        port = 50054

        with pytest.raises(RuntimeError, match="Failed to launch MAPDL on HPC"):
            launch_on_remote_hpc(
                hostname=hostname,
                username=username,
                password=password,
                exec_file=exec_file,
                port=port,
            )

        mck_connect.assert_called()
        kwargs = mck_connect.call_args_list[0].kwargs
        assert kwargs["hostname"] == hostname
        assert kwargs["username"] == username
        assert kwargs["password"] == password
        assert kwargs["port"] == 22

        mck_exec_command.assert_called()
        assert len(mck_exec_command.call_args_list) == 2
        kwargs = mck_exec_command.call_args_list[1].kwargs
        assert "sbatch" in kwargs["command"]
        assert exec_file in kwargs["command"]
        assert str(port) in kwargs["command"]

        kwargs = mck_exec_command.call_args_list[0].kwargs
        assert f"/home/{username}/pymapdl/simulations" in kwargs["command"]

        kwargs = mock_mapdl.call_args_list[0].kwargs
        assert kwargs["ip"] == "123.45.67.89"
        assert kwargs["hostname"] == hostname
        assert kwargs["jobid"] == 1001
        assert kwargs["port"] == 50054


class Test_SshSession:

    @pytest.mark.parametrize("cmd", ["exec_command", "run"])
    def test_failed_not_connected_after_started(self, cmd):
        with patch("paramiko.client.SSHClient.connect") as mck_connect:
            mck_connect.return_value = None
            with pytest.raises(Exception, match="ssh session is not connected"):
                with SshSession("myhost", "myuser", "mypass") as ssh:
                    ssh._connected = False
                    cmd = getattr(ssh, cmd)
                    cmd("ls")

    def test_failed_exec_command(self):
        import io

        str_0 = [io.BytesIO(i) for i in [b"", b"", b"We couldn't start MAPDL"]]
        with (
            patch("paramiko.client.SSHClient.connect") as mck_connect,
            patch("paramiko.client.SSHClient.exec_command") as mck_exec_command,
        ):
            mck_exec_command.return_value = str_0
            mck_connect.return_value = None

            with pytest.raises(Exception, match=f"ERROR: We couldn't start MAPDL"):
                with SshSession("myhost", "myuser", "mypass") as ssh:
                    ssh.run(["cmd1", "cmd2"])

            mck_exec_command.assert_called()
            kwargs = mck_exec_command.call_args_list[0].kwargs
            assert kwargs["command"] == "cmd1 cmd2"

    def test_submit(self):
        import io

        str_0 = [io.BytesIO(i) for i in [b"", b"", b"We couldn't start MAPDL"]]
        with (
            patch("paramiko.client.SSHClient.connect") as mck_connect,
            patch("paramiko.client.SSHClient.exec_command") as mck_exec_command,
            patch("ansys.mapdl.core.hpc.SshSession.run") as mck_run,
        ):
            mck_exec_command.return_value = str_0
            mck_connect.return_value = None

            cmd = "cmd1"
            cwd = "mydir"
            env = {"MYVAR": "myval"}

            with SshSession(
                "myhost", "myuser", "mypass", allow_missing_host_key=True
            ) as ssh:
                ssh.submit(cmd, cwd=cwd, environment=env)

            mck_run.assert_called()

            assert mck_run.call_args_list[0].args[0] == f"mkdir -p {cwd}"
            assert mck_run.call_args_list[1].args[0] == f"cd {cwd};{cmd}"
            assert mck_run.call_args_list[1].kwargs["environment"] == env

    def test_submit_fail(self):
        with (
            patch("paramiko.client.SSHClient.connect") as mck_connect,
            patch("paramiko.client.SSHClient.close") as mck_close,
            patch("ansys.mapdl.core.hpc.SshSession.run") as mck_run,
        ):
            cmd = "cmd1"
            cwd = "mydir"
            env = {"MYVAR": "myval"}
            error = "Failed to run command"

            mck_run.side_effect = Exception(error)
            mck_connect.return_value = None

            with pytest.raises(Exception, match=f"Unexpected error occurred: {error}"):
                with SshSession("myhost", "myuser", "mypass") as ssh:
                    ssh.submit(cmd, cwd=cwd, environment=env)

            mck_close.assert_called()
