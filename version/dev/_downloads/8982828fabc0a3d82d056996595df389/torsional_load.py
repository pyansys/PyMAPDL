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
.. _ref_tors_load:

Torsional load on a bar using SURF154 elements
==============================================

This Ansys PyMAPDL script builds a bar and applies torque to it using
SURF154 elements. This is a static analysis example.
"""

##############################################################################
# Script initialization
# ---------------------

import os

import numpy as np

from ansys.mapdl.core import launch_mapdl

# start Ansys in the current working directory with default jobname "file"
mapdl = launch_mapdl(run_location=os.getcwd(), version=23.1)


##############################################################################
# Define cylinder and mesh parameters

torque = 100
radius = 2
h_tip = 2
height = 20
elemsize = 0.5
pi = np.arccos(-1)
force = 100 / radius
pressure = force / (h_tip * 2 * np.pi * radius)

##############################################################################
# Model creation
# --------------

# Define higher-order SOLID186
# Define surface effect elements SURF154 to apply torque
# as a tangential pressure
mapdl.prep7()
mapdl.et(1, 186)
mapdl.et(2, 154)
mapdl.r(1)
mapdl.r(2)

##############################################################################
# Aluminum properties (or something)
mapdl.mp("ex", 1, 10e6)
mapdl.mp("nuxy", 1, 0.3)
mapdl.mp("dens", 1, 0.1 / 386.1)
mapdl.mp("dens", 2, 0)

# Simple cylinder
for i in range(4):
    mapdl.cylind(radius, "", "", height, 90 * (i - 1), 90 * i)

mapdl.nummrg("kp")

# interactive volume plot (optional)
mapdl.vplot()


##############################################################################
# Mesh cylinder
mapdl.lsel("s", "loc", "x", 0)
mapdl.lsel("r", "loc", "y", 0)
mapdl.lsel("r", "loc", "z", 0, height - h_tip)
mapdl.lesize("all", elemsize * 2)
mapdl.mshape(0)
mapdl.mshkey(1)
mapdl.esize(elemsize)
mapdl.allsel("all")
mapdl.vsweep("ALL")
mapdl.csys(1)
mapdl.asel("s", "loc", "z", "", height - h_tip + 0.0001)
mapdl.asel("r", "loc", "x", radius)
mapdl.local(11, 1)
mapdl.csys(0)
mapdl.aatt(2, 2, 2, 11)
mapdl.amesh("all")
mapdl.finish()

# plot elements
mapdl.eplot()

##############################################################################
# Solution
# --------

mapdl.slashsolu()  # Using Slash instead of / due to duplicate SOLU command
mapdl.antype("static", "new")
mapdl.eqslv("pcg", 1e-8)

# Apply tangential pressure
mapdl.esel("s", "type", "", 2)
mapdl.sfe("all", 2, "pres", "", pressure)

# Constrain bottom of cylinder/rod
mapdl.asel("s", "loc", "z", 0)
mapdl.nsla("s", 1)

mapdl.d("all", "all")
mapdl.allsel()
mapdl.psf("pres", "", 2)
mapdl.pbc("u", 1)
mapdl.solve()


##############################################################################
# Post-processing
# ---------------

# Enter post-processor
mapdl.post1()
# Select the step you want to analyse
mapdl.set(1, 1)


##############################################################################
# Access element results as arrays
nodal_stress = mapdl.post_processing.nodal_stress_intensity()
elem_stress = mapdl.post_processing.element_stress("int")

print("Nodal stress : ", nodal_stress)
print("Element stress : ", elem_stress)

##############################################################################
# Plot interactively
# ~~~~~~~~~~~~~~~~~~~

mapdl.post_processing.plot_nodal_displacement(cmap="bwr")
mapdl.post_processing.plot_nodal_component_stress("x", cmap="bwr")
mapdl.post_processing.plot_nodal_eqv_stress(cmap="bwr")


##############################################################################
# Plot non-interactively
# ~~~~~~~~~~~~~~~~~~~~~~

# Setting up the correct camera angle
cpos = [
    (20.992831318277517, 9.78629316586435, 31.905115108541928),
    (0.35955395443745797, -1.4198191001571547, 10.346158032932495),
    (-0.10547549888485548, 0.9200673323892437, -0.377294345312956),
]

mapdl.post_processing.plot_nodal_displacement(
    cmap="bwr", cpos=cpos, savefig="cylinder_disp.png"
)
mapdl.post_processing.plot_nodal_component_stress(
    "x", cmap="bwr", cpos=cpos, savefig="cylinder_comp_stx.png"
)
mapdl.post_processing.plot_nodal_eqv_stress(
    cmap="bwr", cpos=cpos, savefig="cylinder_eqv_st.png"
)

###############################################################################
# Stop MAPDL
#
mapdl.finish()
mapdl.exit()
