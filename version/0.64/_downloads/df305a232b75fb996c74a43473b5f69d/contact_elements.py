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

mapdl.esel("S", "SEC", vmin=5, vmax=6)
mapdl.eplot(style="wireframe", line_width=3)

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
