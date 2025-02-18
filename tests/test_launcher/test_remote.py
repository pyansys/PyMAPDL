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

from ansys.mapdl.core.launcher.remote import _NON_VALID_ARGS, connect_to_mapdl


def test_connect_to_mapdl(mapdl):
    mapdl_2 = connect_to_mapdl(port=mapdl.port)

    assert "PREP7" in mapdl_2.prep7()

    assert not mapdl_2._start_instance
    assert not mapdl_2._launched


@pytest.mark.parametrize("arg", _NON_VALID_ARGS)
def test_connect_to_mapdl_exceptions(arg):
    with pytest.raises(
        ValueError, match=f"'connect_to_mapdl' does not accept '{arg}' argument."
    ):
        connect_to_mapdl(**{arg: True})


_IP_TEST = "my_ip"


@pytest.mark.parametrize(
    "arg,value",
    (
        ("ip", _IP_TEST),
        ("port", 50053),
        ("loglevel", "DEBUG"),
        ("loglevel", "ERROR"),
        ("start_timeout", 12),
        ("start_timeout", 15),
        ("cleanup_on_exit", True),
        ("cleanup_on_exit", False),
        ("clear_on_connect", True),
        ("clear_on_connect", False),
        ("log_apdl", True),
        ("log_apdl", False),
        ("log_apdl", "log.out"),
        ("print_com", False),
    ),
)
@patch("socket.gethostbyname", lambda *args, **kwargs: _IP_TEST)
@patch("socket.inet_aton", lambda *args, **kwargs: _IP_TEST)
def test_connect_to_mapdl_kwargs(arg, value):
    with patch("ansys.mapdl.core.launcher.remote.MapdlGrpc") as mock_mg:
        args = {arg: value}
        mapdl = connect_to_mapdl(**args)

        mock_mg.assert_called_once()
        kw = mock_mg.call_args_list[0].kwargs
        assert "ip" in kw and kw["ip"] == _IP_TEST
        assert arg in kw and kw[arg] == value
