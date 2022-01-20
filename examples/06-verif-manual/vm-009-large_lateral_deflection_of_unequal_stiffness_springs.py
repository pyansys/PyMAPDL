r"""
.. _ref_vm9_example:

Large Lateral Deflection of Unequal Stiffness Springs
-----------------------------------------------------
Problem Description:
 - A two-spring system is subjected to a force ``F`` as shown below.
   Determine the strain energy of the system and
   the displacements :math:`\delta_x` and :math:`\delta_y`

Reference:
 - G. N. Vanderplaats, Numerical Optimization Techniques for Engineering Design
   with Applications, McGraw-Hill Book Co., Inc., New York, NY, 1984,
   pp. 72-73, ex. 3-1.

Analysis Type(s):
 - Nonlinear Transient Dynamic Analysis (ANTYPE = 4)

Element Type(s):
 - Spring-Damper Elements (COMBIN14)

.. image:: ../../_static/vm9_setup_1.png
   :width: 400
   :alt: COMBIN14 Geometry

 - Combination Elements (COMBIN40)

.. image:: ../../_static/vm9_setup_2.png
   :width: 400
   :alt: COMBIN40 Geometry

Material Properties
 - :math:`k_1 = 8\,N/cm`
 - :math:`k_2 = 1\,N/cm`
 - :math:`m = 1`

Geometric Properties:
 - :math:`l = 10\,cm`

Loading:
 - math:`F = 5\sqrt[2]{2}\,N`

.. image:: ../../_static/vm9_setup.png
   :width: 400
   :alt: VM9 Problem Sketch

Analysis Assumptions and Modeling Notes:
 - The solution to this problem is best obtained by adding mass and using
   the "slow dynamics" technique with approximately critical damping.
   Combination elements ``COMBIN40`` are used to provide damping in the ``X`` and
   ``Y`` directions. Approximate damping coefficients :math:`c_x` and :math:`c_y`, in the ``X`` and
   ``Y`` directions respectively, are determined from:

   * :math:`c_x = \sqrt[2]{k_xm}`
   * :math:`c_y = \sqrt[2]{k_ym}`
 where m is arbitrarily assumed to be unity.

 - :math:`k_x` and :math:`k_y` cannot be known before solving so are approximated
   by :math:`k_y = k_2 = 1\,N/cm` and :math:`k_x = k_y/2 = 0.5\,N/cm`, hence :math:`cx = 1.41` and :math:`cy = 2.0`.
   Large deflection analysis is performed due to the fact that the resistance to
   the load is a function of the deformed position. ``POST1`` is used to extract
   results from the solution phase.

"""

###############################################################################
# Start MAPDL
# ~~~~~~~~~~~
# Start MAPDL and import Numpy and Pandas libraries.

# sphinx_gallery_thumbnail_path = '_static/vm9_setup.png'
# sphinx_gallery_thumbnail_path = '_static/vm9_setup_1.png'
# sphinx_gallery_thumbnail_path = '_static/vm9_setup_2.png'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ansys.mapdl.core import launch_mapdl

# Start MAPDL.
mapdl = launch_mapdl()


###############################################################################
# Pre-Processing
# ~~~~~~~~~~~~~~
# Enter verification example mode and the pre-processing routine.

mapdl.clear()
mapdl.verify()
_ = mapdl.prep7()


###############################################################################
# Define Element Type
# ~~~~~~~~~~~~~~~~~~~
# Set up the element types.

# Element type COMBIN14.
mapdl.et(1, "COMBIN14")

# Special Features are defined by keyoptions of the element COMBIN14.
# KEYOPT(3)(2)
# Degree-of-freedom selection for 2-D and 3-D behavior:
# 2-D longitudinal spring-damper (2-D elements must lie in an X-Y plane)
mapdl.keyopt(1, 3, 2)

# Element type COMBIN40.
mapdl.et(3, "COMBIN40")

# Special Features are defined by keyoptions of the element COMBIN40.
# KEYOPT(3)(1)
# Element degrees of freedom:
# UX (Displacement along nodal X axes)
mapdl.keyopt(3, 3, 1)

# KEYOPT(6)(2)
# Mass location:
# Mass at node J
mapdl.keyopt(3, 6, 2)

# Element type COMBIN40.
mapdl.et(4, "COMBIN40")

# Special Features are defined by keyoptions of the element COMBIN40.
# KEYOPT(3)(2)
# Element degrees of freedom:
# UX (Displacement along nodal X axes)
mapdl.keyopt(4, 3, 2)

# KEYOPT(6)(2)
# Mass location:
# Mass at node J
mapdl.keyopt(4, 6, 2)

# Print the list of the elements and their attributes.
print(mapdl.etlist())


###############################################################################
# Define Real Constants
# ~~~~~~~~~~~~~~~~~~~~~
# Define damping coefficients :math:`c_x`, :math:`c_y` and
# stiffness values :math:`k_1`, :math:`k_2` for the spring elements.

mapdl.r(1, 1)  # SPRING STIFFNESS = 1
mapdl.r(2, 8)  # SPRING STIFFNESS = 8
mapdl.r(3, "", 1.41, 1)  # C = 1.41, M = 1
mapdl.r(4, "", 2, 1)  # C = 2, M = 1


###############################################################################
# Define Nodes
# ~~~~~~~~~~~~
# Set up the nodes coordinates using ``Numpy`` and create them
# using python ``for-loop``.

mapdl.n(1)
mapdl.n(2, "", 10)
mapdl.n(3, "", 20)
mapdl.n(4, -1, 10)
mapdl.n(5, "", 9)


###############################################################################
# Create Elements
# ~~~~~~~~~~~~~~~
# Create the elements through the nodes using python `for-loop``.

mapdl.e(1, 2)  # ELEMENT 1 IS SPRING ELEMENT WITH STIFFNESS 1

mapdl.real(2)
mapdl.e(2, 3)  # ELEMENT 2 IS SPRING ELEMENT WITH STIFFNESS 8

mapdl.type(3)
mapdl.real(3)
mapdl.e(4, 2)  # ELEMENT 3 IS COMBINATION ELEMENT WITH C = 1.41

mapdl.type(4)
mapdl.real(4)
mapdl.e(5, 2)  # ELEMENT 4 IS COMBINATION ELEMENT WITH C = 2


###############################################################################
# Define Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application of boundary conditions (BC) for the spring model.

mapdl.nsel("U", "NODE", "", 2)
mapdl.d("ALL", "ALL")
mapdl.nsel("ALL")
mapdl.finish()


###############################################################################
# Solution settings
# ~~~~~~~~~~~~~~~~~
# Enter solution mode and apply settings for ``Transient Dynamic Analysis".

mapdl.slashsolu()

mapdl.antype("TRANS")  # FULL TRANSIENT DYNAMIC ANALYSIS
mapdl.nlgeom("ON")  # LARGE DEFLECTION
mapdl.kbc(1)  # STEP BOUNDARY CONDITION
mapdl.f(2, "FX", 5)
mapdl.f(2, "FY", 5)
mapdl.autots("ON")
mapdl.nsubst(30)
mapdl.outpr("", "LAST")
mapdl.outpr("VENG", "LAST")
mapdl.time(15)  # ARBITRARY TIME FOR SLOW DYNAMICS


###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system , using ``_ =`` avoiding the printing output.

# Enter to the pre-processing mode.
mapdl.slashsolu()

# Run the simulation.
mapdl.solve()
_ = mapdl.finish()


###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing, using ``_ =`` avoiding the printing output.

# Enter the post-processing mode.
_ = mapdl.post1()


###############################################################################
# Getting Results
# ~~~~~~~~~~~~~~~

mapdl.set("", "", "", "", 15)  # USE ITERATION WHEN TIME = 15

mapdl.etable("SENE", "SENE")  # STORE STRAIN ENERGY

mapdl.ssum()  # SUM ALL ACTIVE ENTRIES IN ELEMENT STRESS TABLE

mapdl.run("*GET,ST_EN,SSUM,,ITEM,SENE")

mapdl.prnsol("U", "COMP")  # PRINT DISPLACEMENTS IN GLOBAL COORDINATE SYSTEM

mapdl.run("*GET,DEF_X,NODE,2,U,X")

mapdl.run("*GET,DEF_Y,NODE,2,U,Y")

mapdl.run("*DIM,LABEL,CHAR,3,2")

mapdl.run("*DIM,VALUE,,3,3")

mapdl.run("LABEL(1,1) = 'STRAIN E','DEF_X (C','DEF_Y (C'")
mapdl.run("LABEL(1,2) = ', N-cm  ','m)      ','m)      '")

mapdl.run("*VFILL,VALUE(1,1),DATA,24.01,8.631,4.533")
mapdl.run("*VFILL,VALUE(1,2),DATA,ST_EN ,DEF_X,DEF_Y")
mapdl.run("*VFILL,VALUE(1,3),DATA,ABS(ST_EN/24.01), ABS(8.631/DEF_X), ABS(DEF_Y/4.533 )")


###############################################################################
# Check Results
# ~~~~~~~~~~~~~
# Print output results using pandas dataframe.
