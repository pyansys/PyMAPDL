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
.. _ref_3d_plate_thermal:

Basic Thermal Analysis with PyMAPDL
-----------------------------------

This example demonstrates how you can use MAPDL to create a plate,
impose thermal boundary conditions, solve, and plot it all within
PyMAPDL.

First, start MAPDL as a service and disable all but error messages.
"""

# sphinx_gallery_thumbnail_number = 2

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()

###############################################################################
# Geometry and Material Properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a simple beam, specify the material properties, and mesh it.
mapdl.prep7()
mapdl.mp("kxx", 1, 45)
mapdl.et(1, 90)
mapdl.block(-0.3, 0.3, -0.46, 1.34, -0.2, -0.2 + 0.02)
mapdl.vsweep(1)
mapdl.eplot()


###############################################################################
# Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~
# Set the thermal boundary conditions
mapdl.asel("S", vmin=3)
mapdl.nsla()
mapdl.d("all", "temp", 5)
mapdl.asel("S", vmin=4)
mapdl.nsla()
mapdl.d("all", "temp", 100)
out = mapdl.allsel()


###############################################################################
# Solve
# ~~~~~
# Solve the thermal static analysis and print the results
mapdl.vsweep(1)
mapdl.run("/SOLU")
print(mapdl.solve())
out = mapdl.finish()


###############################################################################
# Post-Processing using MAPDL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# View the thermal solution of the beam by getting the results
# directly through MAPDL.
mapdl.post1()
mapdl.set(1, 1)
mapdl.post_processing.plot_nodal_temperature()


###############################################################################
# Alternatively you could also use the result object that reads in the
# result file using pyansys

result = mapdl.result
nnum, temp = result.nodal_temperature(0)
# this is the same as pyansys.read_binary(mapdl._result_file)
print(nnum, temp)

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
