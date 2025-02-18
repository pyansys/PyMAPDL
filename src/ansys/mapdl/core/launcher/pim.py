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

from typing import Optional

from ansys.mapdl.core import _HAS_PIM, LOG
from ansys.mapdl.core.mapdl_grpc import MAX_MESSAGE_LENGTH, MapdlGrpc

if _HAS_PIM:
    import ansys.platform.instancemanagement as pypim


def is_ready_for_pypim(exec_file):
    return _HAS_PIM and exec_file is None and pypim.is_configured()


def launch_remote_mapdl(
    version: Optional[str] = None,
    cleanup_on_exit: bool = True,
) -> MapdlGrpc:
    """Start MAPDL remotely using the product instance management API.

    When calling this method, you need to ensure that you are in an environment where PyPIM is configured.
    This can be verified with :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`.

    Parameters
    ----------
    version : str, optional
        The MAPDL version to run, in the 3 digits format, such as "212".

        If unspecified, the version will be chosen by the server.

    cleanup_on_exit : bool, optional
        Exit MAPDL when python exits or the mapdl Python instance is
        garbage collected.

        If unspecified, it will be cleaned up.

    Returns
    -------
    ansys.mapdl.core.mapdl.MapdlBase
        An instance of Mapdl.
    """
    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    LOG.debug("Connecting using PyPIM.")
    pim = pypim.connect()
    instance = pim.create_instance(product_name="mapdl", product_version=version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )

    LOG.debug("Channel created and passing it to the Mapdl object")
    return MapdlGrpc(
        channel=channel,
        cleanup_on_exit=cleanup_on_exit,
        remote_instance=instance,
    )
