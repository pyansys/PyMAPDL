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
.. _ref_contact_example:

Contact Element Example
~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates how to create contact elements for general
contact.

Begin by launching MAPDL.

"""
from ansys.mapdl import core as pymapdl

mapdl = pymapdl.launch_mapdl()

###############################################################################
# Enter the pre-processor, create a block and mesh it with tetrahedral
# elements.
#
mapdl.prep7()

vnum0 = mapdl.block(0, 1, 0, 1, 0, 0.5)

mapdl.et(1, 187)
mapdl.esize(0.1)

mapdl.vmesh(vnum0)
mapdl.eplot()

###############################################################################
# Second a volume block above the existing block and mesh it with
# quadratic hexahedral elements.  Ensure that these blocks do not
# touch by starting it slightly higher than the existing block.
#
# Note how these two blocks do not touch and the mesh is non-conformal.

mapdl.esize(0.09)
mapdl.et(2, 186)
mapdl.type(2)
vnum1 = mapdl.block(0, 1, 0, 1, 0.50001, 1)
mapdl.vmesh(vnum1)
mapdl.eplot()


###############################################################################
# Select all the elements at the intersection between the two blocks
# and generate contact elements.

mapdl.nsel("s", "loc", "z", 0.5, 0.50001)
mapdl.esln("s")
output = mapdl.gcgen("NEW", splitkey="SPLIT", selopt="SELECT")
print(output)

###############################################################################
# Plot the contact element pairs.  Note from the command output above
# that the section IDs are 5 and 6.
#
# Here, we plot the element mesh as a wire-frame to show that the
# contact pairs overlap.

mapdl.esel("S", "SEC", vmin=3, vmax=4)
mapdl.eplot(style="wireframe", line_width=3)

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
