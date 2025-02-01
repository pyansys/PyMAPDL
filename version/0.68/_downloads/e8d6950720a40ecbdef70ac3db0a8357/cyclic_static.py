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
.. _ref_cyclic_static_analysis:

Static Cyclic Analysis
----------------------

Run a static cyclic analysis of an example rotor sector using the imperial unit
system at 1000 RPM.


"""
from ansys.mapdl.reader import examples

from ansys.mapdl.core import launch_mapdl

# launch mapdl
mapdl = launch_mapdl()


###############################################################################
# Load in the mesh
# ~~~~~~~~~~~~~~~~
# Load in the example sector and plot it.
mapdl.cdread("db", examples.sector_archive_file)
mapdl.eplot()


###############################################################################
# Make the rotor cyclic
# ~~~~~~~~~~~~~~~~~~~~~
# Enter the preprocessing routine and make the mesh cyclic.
mapdl.prep7()
mapdl.shpp("off")
mapdl.nummrg(label="NODE", toler=1e-3)

mapdl.cyclic()


###############################################################################
# Set material properties
# ~~~~~~~~~~~~~~~~~~~~~~~
# Units are in imperial units and the material is (approximately) structural
# steel.
mapdl.mp("NUXY", 1, 0.31)
mapdl.mp("DENS", 1, 4.1408e-04)
mapdl.mp("EX", 1, 16900000)


###############################################################################
# Apply boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply a cyclic rotation at 1000 RPM and constrain the rotor at the center.
mapdl.omega(0, 0, 1000)  # 1000 RPM

mapdl.csys(1)  # enter the cyclic coordinate system

mapdl.nsel("S", "loc", "x", 0, 0.71)  # radial between 0.69 - 0.71
mapdl.d("ALL", "ALL")  # all DOF for those 8 nodes

mapdl.allsel()
mapdl.csys(0)  # return to cartesian coordinate system

###############################################################################
# Run a static analysis
# ~~~~~~~~~~~~~~~~~~~~~
# Run the MAPDL solver and print the output of the solution.
mapdl.run("/SOLU")
mapdl.antype("STATIC")
output = mapdl.solve()
mapdl.finish()
print(output)


###############################################################################
# Plot the cyclic result
# ~~~~~~~~~~~~~~~~~~~~~~
# Plot the result using the legacy
mapdl.result.plot_nodal_displacement(0)


###############################################################################
# Exit MAPDL
# ~~~~~~~~~~
# Finally, exit MAPDL.
mapdl.exit()
