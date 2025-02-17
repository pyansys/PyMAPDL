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

"""Test the DPF implementation"""
import pytest

from conftest import HAS_DPF, ON_CI, has_dependency, requires

if not has_dependency("ansys-dpf-core") or not HAS_DPF:
    pytest.skip(allow_module_level=True)

from ansys.dpf import core as dpf
from ansys.dpf.core import server as server_module


@pytest.fixture()
def skip_dpf(mapdl):
    mapdl_version = str(mapdl.version)
    if mapdl_version in ["25.2"] and ON_CI:
        pytest.skip(
            f"This MAPDL version ({mapdl_version}) docker image seems to not support DPF on CICD.",
            allow_module_level=True,
        )
    return


@requires("dpf")
@requires("ansys-dpf-core")
def test_dpf_connection(skip_dpf):
    # uses 127.0.0.1 and port 50054 by default
    try:
        grpc_con = dpf.connect_to_server()
        assert grpc_con.live
        assert True
    except OSError:
        assert False


@requires("dpf")
@requires("ansys-dpf-core")
def test_upload(skip_dpf, mapdl, solved_box, tmpdir):
    # Download RST file
    rst_path = mapdl.download_result(str(tmpdir.mkdir("tmpdir")))

    # Establishing connection
    grpc_con = dpf.connect_to_server()

    server = server.DPFServer()
    server = server_module.get_or_create_server(server)
    if not server.local_server and not server.docker_config.use_docker:
        return upload_file_in_tmp_folder(local_path, server=server)

    assert grpc_con.live

    # Upload RST
    server_file_path = dpf.upload_file_in_tmp_folder(rst_path)

    # Creating model
    model = dpf.Model(server_file_path)
    assert model.results is not None

    # Checks
    mapdl.allsel()
    assert mapdl.mesh.n_node == model.metadata.meshed_region.nodes.n_nodes
    assert mapdl.mesh.n_elem == model.metadata.meshed_region.elements.n_elements
