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
.. _ref_modal_beam:

=================================
MAPDL modal beam analysis example
=================================

This example demonstrates how to perform a simple modal analysis
and animate its results.


Objective
~~~~~~~~~
This example models a simple 3D elastic beam made of BEAM188 elements.
These beams elements are made of a linear elastic material similar to steel,
and have a rectangular section.


Procedure
~~~~~~~~~

* Launch MAPDL instance
* Material properties
* Geometry
* Finite element model
* Boundary conditions
* Solving the model
* Post-processing
* Stop MAPDL

"""

###############################################################################
# Launch MAPDL instance
# =====================
#
# Launch MAPDL with interactive plotting
from ansys.mapdl.core import launch_mapdl

nmodes = 10
# start MAPDL
mapdl = launch_mapdl()
print(mapdl)


###############################################################################
# Define material
# ===============
#
# Define material
mapdl.prep7()
mapdl.mp("EX", 1, 2.1e11)
mapdl.mp("PRXY", 1, 0.3)
mapdl.mp("DENS", 1, 7800)

###############################################################################
# Create geometry
# ===============
#
# Create keypoints and line
mapdl.k(1)
mapdl.k(2, 10)
mapdl.l(1, 2)
mapdl.lplot()

###############################################################################
# Define finite element model
# ===========================
#
# Define element type/section type - Rectangular beam section.
mapdl.et(1, "BEAM188")
mapdl.sectype(1, "BEAM", "RECT")
mapdl.secoffset("CENT")
mapdl.secdata(2, 1)

# Mesh the line
mapdl.type(1)
mapdl.esize(1)
mapdl.lesize("ALL")
mapdl.lmesh("ALL")
mapdl.eplot()
mapdl.finish()

###############################################################################
# Specify boundary conditions
# ===========================
#
# Fully fixed (clamped) end.
mapdl.solution()  # Entering the solution processor.
mapdl.nsel("S", "LOC", "X", "0")
mapdl.d("ALL", "ALL")
mapdl.allsel()
mapdl.nplot(plot_bc=True, nnum=True)

###############################################################################
# Solve the model
# ===============
#
# Setting modal analysis
mapdl.antype("MODAL")
mapdl.modopt("LANB", nmodes, 0, 200)
mapdl.solve()
mapdl.finish()

###############################################################################
# Postprocess
# ===========
#
# Enter the post processor (post1)
mapdl.post1()
output = mapdl.set("LIST")
print(output)

result = mapdl.result

###############################################################################
# Animate results

mode2plot = 2
normalizeDisplacement = 1 / result.nodal_displacement(mode2plot - 1)[1].max()

result.plot_nodal_displacement(
    mode2plot,
    show_displacement=True,
    displacement_factor=normalizeDisplacement,
    n_colors=10,
)

result.animate_nodal_displacement(
    mode2plot,
    loop=False,
    add_text=False,
    n_frames=100,
    displacement_factor=normalizeDisplacement,
    show_axes=False,
    background="w",
    movie_filename="animation.gif",
    off_screen=True,
)

###############################################################################
# Stop MAPDL
# ==========
#
mapdl.finish()
mapdl.exit()
