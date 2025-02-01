# Copyright (C) 2016 - 2024 ANSYS, Inc. and/or its affiliates.
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
.. _ref_mapdl_beam:

MAPDL 2D Beam Example
---------------------

This is an example from the book *"Finite element analysis using ansys 11.0"*
by Paletikrishna Chaitanya, Sambanarajesh Kumar, and Datti Srinivas.
PHI Learning Pvt. Ltd., 1 Jan 2010.

"""

###############################################################################
# Launch MAPDL with interactive plotting
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()
mapdl.fcomp("rst", 0)  # specify compression level
###############################################################################
# Define an I-beam
mapdl.prep7()
mapdl.et(1, "BEAM188")
mapdl.keyopt(1, 4, 1)  # transverse shear stress output

# material properties
mapdl.mp("EX", 1, 2e7)  # N/cm2
mapdl.mp("PRXY", 1, 0.27)  #  Poisson's ratio

# beam properties in centimeters
sec_num = 1
mapdl.sectype(sec_num, "BEAM", "I", "ISection", 3)
mapdl.secoffset("CENT")
beam_info = mapdl.secdata(15, 15, 29, 2, 2, 1)  # dimensions are in centimeters

###############################################################################
# Create nodes within MAPDL
mapdl.n(1, 0, 0, 0)
mapdl.n(12, 110, 0, 0)
mapdl.n(23, 220, 0, 0)
mapdl.fill(1, 12, 10)
mapdl.fill(12, 23, 10)

# list the node coordinates
print(mapdl.mesh.nodes)

# list the node numbers
print(mapdl.mesh.nnum)

# plot the nodes using VTK
mapdl.nplot(vtk=True, nnum=True, cpos="xy", show_bounds=True, point_size=10)

###############################################################################
# create elements between the nodes
# we can just manually create elements since we know that the elements
# are sequential
for node in mapdl.mesh.nnum[:-1]:
    mapdl.e(node, node + 1)

# print the elements from MAPDL
print(mapdl.elist())

###############################################################################
# Access them as a list of arrays
# See the documentation on ``mapdl.mesh.elem`` for interpreting the
# individual elements
for elem in mapdl.mesh.elem:
    print(elem)

###############################################################################
# Define the boundary conditions

# Allow movement only in the X and Z direction
for const in ["UX", "UY", "ROTX", "ROTZ"]:
    mapdl.d("all", const)

# constrain just nodes 1 and 23 in the Z direction
mapdl.d(1, "UZ")
mapdl.d(23, "UZ")

# apply a -Z force at node 12
mapdl.f(12, "FZ", -22840)


###############################################################################
# run the static analysis
mapdl.run("/solu")
mapdl.antype("static")
print(mapdl.solve())

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
