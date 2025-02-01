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
.. _ref_spotweld:

Running an input file - spotweld SHELL181 example
=================================================

This MAPDL example demonstrates how to model spot welding on three
thin sheets of metal. Here, the full input file is simply run using
the PyMAPDL interface.

Using the following commands, you can directly use an APDL
script within a PyMAPDL session with the following
commands:

"""

##############################################################################
# Script initialization
# ---------------------

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples.downloads import download_example_data

mapdl = launch_mapdl()

##############################################################################
# Download and run an MAPDL script
# --------------------------------

spotweld_data = download_example_data(
    filename="spotweld.inp", directory="pymapdl/spotweld"
)
mapdl.input(spotweld_data)

######################################################################
# Displacements
# -------------

# Enter post-processor
mapdl.post1()

# Plot the time step 1.
mapdl.set(1, 1)
mapdl.post_processing.plot_nodal_displacement(cmap="bwr")

# Plot the time step 3.
mapdl.set(1, 3)
mapdl.post_processing.plot_nodal_displacement(cmap="bwr")


######################################################################
# Stress
# ------

# Get the nodal and element component stress at time step 1.
mapdl.set(1, 1)
nodal_stress = mapdl.post_processing.nodal_stress_intensity()
print("Nodal stress : ", nodal_stress)

# Plot the element stress.
element_stress = mapdl.post_processing.element_stress("int")
print("Element stress : ", element_stress)

######################################################################
# The stress at the contact element simulating the spot weld.
#
# Plot the nodal stress in the Z direction.
mapdl.post_processing.plot_nodal_component_stress("z")


######################################################################
# Get the cumulative equivalent stress and plot the von Mises stress.

eqv_stress = mapdl.post_processing.nodal_eqv_stress()
print("Cumulative equivalent stress : ", eqv_stress)
mapdl.post_processing.plot_nodal_eqv_stress()

###############################################################################
# Stop MAPDL
#
mapdl.finish()
mapdl.exit()
