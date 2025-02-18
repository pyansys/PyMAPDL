r"""
.. _ref_vm2_example:

Beam Stresses and Deflections
-----------------------------
**Problem Description**

A standard 30 inch WF beam, with a cross-sectional area :math:`A`,
is supported as shown below and loaded on the overhangs by a
uniformly distributed load :math:`w`. Determine the maximum bending
stress, :math:`\sigma_max`, in the middle portion of the beam and
the deflection, :math:`\delta`, at the middle of the beam.

**Reference**

S. Timoshenko, Strength of Material, Part I, Elementary Theory and
Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1955,
pg. 98, problem 4.

**Analysis Type(s)**

Static Analysis ``ANTYPE=0``

**Element Type(s):**

3-D 2 Node Beam (BEAM188)

.. image:: ../../../_static/vm2_setup.png
   :width: 400
   :alt: VM2 Problem Sketch

**Material Properties**

:math:`E = 30 \cdot 10^6 psi`

**Geometric Properties**

:math:`a = 120 in`
:math:`l = 240 in`
:math:`h = 30 in`
:math:`A = 50.65 in^2`
:math:`I_z = 7892 in^4`

**Loading**

:math:`w = (10000/12) lb/in`

**Analytical Equations**

- :math:`M` is the bending moment for the middle portion of the beam:
  :math:`M = 10000 \cdot 10 \cdot 60 = 6 \cdot 10^6 lb \cdot in`
- Determination of the maximum stress in the middle portion of the beam is
  :math:`\sigma_max = \frac{M h}{2 I_z}`
- The deflection, :math:`\delta`, at the middle of the beam can be defined
  by the formulas of the transversally loaded beam:
  :math:`\delta = 0.182 in`

"""

###############################################################################
# Start MAPDL
# ~~~~~~~~~~~

# sphinx_gallery_thumbnail_path = '_static/vm2_setup.png'

from ansys.mapdl.core import launch_mapdl

# Start mapdl and clear it.
mapdl = launch_mapdl()
mapdl.clear()

# Enter verification example mode and the pre-processing routine.
mapdl.verify()
mapdl.prep7()


###############################################################################
# Define Element Type
# ~~~~~~~~~~~~~~~~~~~
# Set up the element type (a beam-type).

# Type of analysis: Static.
mapdl.antype("STATIC")

# Element type: BEAM188.
mapdl.et(1, "BEAM188")

# Special Features are defined by keyoptions of beam element:

# KEYOPT(3)
# Shape functions along the length:
# Cubic
mapdl.keyopt(1, 3, 3)  # Cubic shape function

# KEYOPT(9)
# Output control for values extrapolated to the element
# and section nodes:
# Same as KEYOPT(9) = 1 plus stresses and strains at all section nodes
mapdl.keyopt(1, 9, 3, mute=True)


###############################################################################
# Define Material
# ~~~~~~~~~~~~~~~
# Set up the material.

mapdl.mp("EX", 1, 30e6)
mapdl.mp("PRXY", 1, 0.3)
print(mapdl.mplist())


###############################################################################
# Define Section
# ~~~~~~~~~~~~~~
# Set up the cross-section properties for a beam element.

w_f = 1.048394965
w_w = 0.6856481
sec_num = 1
mapdl.sectype(sec_num, "BEAM", "I", "ISection")
mapdl.secdata(15, 15, 28 + (2 * w_f), w_f, w_f, w_w)


###############################################################################
# Define Geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. Create nodes then create elements
# between nodes.

# Define nodes
for node_num in range(1, 6):
    mapdl.n(node_num, (node_num - 1) * 120, 0, 0)

# Define one node for the orientation of the beam cross-section.
orient_node = mapdl.n(6, 60, 1)

# Print the list of the created nodes.
print(mapdl.nlist())

###############################################################################
# Define elements

for elem_num in range(1, 5):
    mapdl.e(elem_num, elem_num + 1, orient_node)

# Print the list of the created elements.
print(mapdl.elist())

# Display elements with their nodes numbers.
mapdl.eplot(show_node_numbering=True, line_width=5, cpos="xy", font_size=40)


###############################################################################
# Define Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application of boundary conditions (BC).

# BC for the beams seats
mapdl.d(2, "UX", lab2="UY")
mapdl.d(4, "UY")

# BC for all nodes of the beam
mapdl.nsel("S", "LOC", "Y", 0)
mapdl.d("ALL", "UZ")
mapdl.d("ALL", "ROTX")
mapdl.d("ALL", "ROTY")
mapdl.nsel("ALL")

###############################################################################
# Define Distributed Loads
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Apply a distributed force of :math:`w = (10000/12) lb/in`
# in the y-direction.

# Parametrization of the distributed load.
w = 10000 / 12

# Application of the surface load to the beam element.
mapdl.sfbeam(1, 1, "PRES", w)
mapdl.sfbeam(4, 1, "PRES", w)
mapdl.finish()


###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system. Print the solver output.

mapdl.run("/SOLU")
out = mapdl.solve()
mapdl.finish()
print(out)


###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. To get the stress and deflection results
# from the middle node and cross-section of the beam we can use
# :meth:`Mapdl.get_value <ansys.mapdl.core.Mapdl.get_value>`.

# Enter the post-processing routine and select the first load step.
mapdl.post1()
mapdl.set(1)

# Get the maximum stress at the middle of the beam.
s_eqv_max = mapdl.get_value("secr", 2, "s", "eqv", "max")

# Get the deflection at the middle of the beam.
mid_node_uy = mapdl.get_value(entity="NODE", entnum=3, item1="u", it1num="y")


###############################################################################
# Check Results
# ~~~~~~~~~~~~~
# Now that we have the results we can compare the nodal displacement and stress
# experienced by middle node of the beam to the known stresses -11,400 psi and
# 0.182 inches of the deflection.

# Results obtained by hand-calculations.
stress_target = 11400.0
deflection_target = 0.182

# Calculate the deviation.
stress_ratio = s_eqv_max / stress_target
deflection_ratio = mid_node_uy / deflection_target

# Print output results.
output = f"""
----------------------------- VM3 RESULTS COMPARISON -----------------------------
                |   TARGET   |   Mechanical APDL   |   RATIO   |
----------------------------------------------------------------------------------
    Stress{stress_target:18.3f} {s_eqv_max:16.3f} {stress_ratio:14.3f}
    Deflection{deflection_target:14.3f} {mid_node_uy:16.3f} {deflection_ratio:14.3f}
----------------------------------------------------------------------------------
"""
print(output)


###############################################################################
# stop mapdl
mapdl.exit()
