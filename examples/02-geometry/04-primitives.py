"""
.. _ref_basic-geometry-volumes:

Primitives
----------
This example shows how you can use PyMAPDL to create basic geometry
using Pythonic PREP7 volume commands.

"""

import numpy as np
from ansys.mapdl.core import launch_mapdl

# start MAPDL and enter the pre-processing routine
mapdl = launch_mapdl()
mapdl.clear()
mapdl.prep7()
print(mapdl)


###############################################################################
# APDL Command: BLC4
# ~~~~~~~~~~~~~~~~~~
# Create a rectangular area or block volume by corner points.
#
# Create a ``0.5 x 0.5`` rectangle starting at ``(0.25, 0.25)``
mapdl.clear(); mapdl.prep7()

anum1 = mapdl.blc4(0.25, 0.25, 0.5, 0.5)
mapdl.aplot(show_lines=True, line_width=5, show_bounds=True, cpos='xy')


###############################################################################
# Create a block with dimensions ``1 x 4 x 9`` with one corner of
# the block at ``(0, 0)`` of the current working plane.
#
# This method returns the volume number.
mapdl.clear(); mapdl.prep7()

vnum = mapdl.blc4(width=1, height=4, depth=9)
mapdl.vplot(show_lines=True)


###############################################################################
# APDL Command: CYL4
# ~~~~~~~~~~~~~~~~~~
# Creates a circular area or cylindrical volume anywhere on the working plane.
#
# Create a half arc centered at the origin with an outer radius
# of 2 and an inner radius of 1.
#
# Note that the ``depth`` keyword argument is unset, which will
# generate an area rather than a volume.  Setting depth to a value
# greater than 0 will generate a volume.
mapdl.clear(); mapdl.prep7()

anum = mapdl.cyl4(xcenter=0, ycenter=0, rad1=1, theta1=0, rad2=2, theta2=180)
mapdl.aplot(show_lines=True, line_width=5, show_bounds=True, cpos='xy')


###############################################################################
# Create a volumetric half arc centered at the origin with an outer
# radius of 2 and an inner radius of 1, and a thickness of 0.55.
mapdl.clear(); mapdl.prep7()

anum = mapdl.cyl4(xcenter=0, ycenter=0, rad1=1, theta1=0, rad2=2, theta2=180,
                  depth=0.55)
mapdl.vplot(show_bounds=True)


###############################################################################
# APDL Command: BLC5
# ~~~~~~~~~~~~~~~~~~
# Create a rectangular area or block volume by center and corner points.
#
# This differs from BLC4 since this describes the center rather than
# the corner points.
#
# Create a square centered at ``(0, 0)`` with a width of 0.5 and a
# height of 0.5

mapdl.clear(); mapdl.prep7()

anum1 = mapdl.blc5(width=0.5, height=0.5)
mapdl.aplot(show_lines=True, line_width=5, show_bounds=True, cpos='xy')


###############################################################################
# Create a block with dimensions ``1 x 4 x 9`` with the cetner at
# ``(0, 0)`` of the current working plane.
#
# This method returns the volume number.
mapdl.clear(); mapdl.prep7()

vnum = mapdl.blc5(width=1, height=4, depth=9)
mapdl.vplot(show_lines=True, show_bounds=True)


###############################################################################
# APDL Command: BLOCK
# ~~~~~~~~~~~~~~~~~~~
# Create a block volume based on working plane coordinates with the
# size ``(1 x 2 x 3)``
mapdl.clear(); mapdl.prep7()

vnum = mapdl.block(0, 1, 0, 2, 1, 4)
mapdl.vplot(show_lines=False, show_bounds=True,
            color=(0.5, 0.5, 0.5),
            background=(0.8, 0.8, 0.8))


###############################################################################
# APDL Command: CON4
# ~~~~~~~~~~~~~~~~~~
# Create a conical volume anywhere on the working plane.
#
# Create a cone with a bottom radius of 3 and a height of 10.
mapdl.clear(); mapdl.prep7()

vnum = mapdl.con4(rad1=3, rad2=0, depth=10)
mapdl.vplot(show_lines=False, quality=6, show_bounds=True)


###############################################################################
# APDL Command: CONE
# ~~~~~~~~~~~~~~~~~~
# Create a conical volume centered about the working plane origin.
#
# Create a quarter cone with a bottom radius of 3, top radius of 1 and
# a height of 10 centered at ``(0, 0)``.
mapdl.clear(); mapdl.prep7()

vnum = mapdl.cone(rbot=5, rtop=1, z1=0, z2=10, theta1=180, theta2=90)
mapdl.vplot(show_lines=False, quality=6, show_bounds=True)
