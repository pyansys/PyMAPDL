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

"""
.. _ref_pyvista_mesh:

PyVista Mesh Integration
------------------------

Run a modal analysis on a mesh generated from pyvista within MAPDL.

"""
# sphinx_gallery_thumbnail_number = 2

import os
import tempfile

from ansys.mapdl.reader import save_as_archive
import pyvista as pv

from ansys.mapdl.core import launch_mapdl

# launch MAPDL as a service
mapdl = launch_mapdl(loglevel="ERROR")

# Create a simple plane mesh centered at (0, 0, 0) on the XY plane
mesh = pv.Plane(i_resolution=100, j_resolution=100)
mesh.plot(color="w", show_edges=True)

###############################################################################
# Write the mesh to a temporary file
archive_filename = os.path.join(tempfile.gettempdir(), "tmp.cdb")
save_as_archive(archive_filename, mesh)

# Read in the archive file
response = mapdl.cdread("db", archive_filename)
mapdl.prep7()
print(mapdl.shpp("SUMM"))

# specify shell thickness
mapdl.sectype(1, "shell")
mapdl.secdata(0.01)
mapdl.emodif("ALL", "SECNUM", 1)

# specify material properties
# using approximated values for AISI 5000 Series Steel
# http://www.matweb.com/search/datasheet.aspx?matguid=89d4b891eece40fbbe6b71f028b64e9e
mapdl.units("SI")  # not necessary, but helpful for book keeping
mapdl.mp("EX", 1, 200e9)  # Elastic moduli in Pa (kg/(m*s**2))
mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
mapdl.mp("NUXY", 1, 0.3)  # Poissons Ratio
mapdl.emodif("ALL", "MAT", 1)

# Run an unconstrained modal analysis
# for the first 20 modes above 1 Hz
mapdl.modal_analysis(nmode=20, freqb=1)

# you could have also run:
# mapdl.run('/SOLU')
# mapdl.antype('MODAL')  # default NEW
# mapdl.modopt('LANB', 20, 1)
# mapdl.solve()

###############################################################################
# Load the result file within ``pyansys`` and plot the 8th mode.
result = mapdl.result
print(result)

result.plot_nodal_displacement(7, show_displacement=True, displacement_factor=0.4)

###############################################################################
# plot the 1st mode using contours
result.plot_nodal_displacement(
    0, show_displacement=True, displacement_factor=0.4, n_colors=10
)

###############################################################################
# Animate a high frequency mode
#
# Get a smoother plot by disabling movie_filename and increasing ``n_frames``.
# Enable a continuous plot looping with ```loop=True```.

result.animate_nodal_displacement(
    18,
    loop=False,
    add_text=False,
    n_frames=30,
    displacement_factor=0.4,
    show_axes=False,
    background="w",
    movie_filename="plane_vib.gif",
)

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
