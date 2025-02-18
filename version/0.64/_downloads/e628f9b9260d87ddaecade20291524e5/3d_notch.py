"""
.. _ref_3d_plane_stress_concentration:

3D Stress Concentration Analysis for a Notched Plate
----------------------------------------------------

This tutorial is the 3D corollary to the 2D plane example
:ref:`ref_plane_stress_concentration`, but This example verifies the
stress concentration factor :math:`K-t` when modeling opposite single
notches in a finite width thin plate

First, start MAPDL as a service and disable all but error messages.
"""
from matplotlib import pyplot as plt

# sphinx_gallery_thumbnail_number = 3
import numpy as np
import pyvista as pv

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(loglevel="ERROR")


###############################################################################
# Geometry
# ~~~~~~~~
# Create a rectangular area with two notches at the top and bottom.

length = 0.4
width = 0.1

notch_depth = 0.04
notch_radius = 0.01

# create the half arcs
mapdl.prep7()

circ0_kp = mapdl.k(x=length / 2, y=width + notch_radius)
circ_line_num = mapdl.circle(circ0_kp, notch_radius)
circ_line_num = circ_line_num[2:]  # only concerned with the bottom arcs

# create a line and drag the top circle downward
circ0_kp = mapdl.k(x=0, y=0)
k1 = mapdl.k(x=0, y=-notch_depth)
l0 = mapdl.l(circ0_kp, k1)
mapdl.adrag(*circ_line_num, nlp1=l0)

# same thing for the bottom notch (except upwards
circ1_kp = mapdl.k(x=length / 2, y=-notch_radius)
circ_line_num = mapdl.circle(circ1_kp, notch_radius)
circ_line_num = circ_line_num[:2]  # only concerned with the top arcs

# create a line whereby the top circle will be dragged up
k0 = mapdl.k(x=0, y=0)
k1 = mapdl.k(x=0, y=notch_depth)
l0 = mapdl.l(k0, k1)
mapdl.adrag(*circ_line_num, nlp1=l0)

rect_anum = mapdl.blc4(width=length, height=width)

# Note how pyansys parses the output and returns the area numbers
# created by each command.  This can be used to execute a boolean
# operation on these areas to cut the circle out of the rectangle.
# plate_with_hole_anum = mapdl.asba(rect_anum, circ_anum)
cut_area = mapdl.asba(rect_anum, "ALL")  # cut all areas except the plate

plotter = pv.Plotter(shape=(1, 3))

plotter.subplot(0, 0)
mapdl.lsla("S")
mapdl.lplot(vtk=True, show_keypoint_numbering=True, plotter=plotter)
mapdl.lsel("all")

# plot the area using vtk/pyvista
plotter.subplot(0, 1)
mapdl.aplot(
    vtk=True, show_area_numbering=True, show_lines=True, cpos="xy", plotter=plotter
)

# Next, extrude the area to create volume
thickness = 0.01
mapdl.vext(cut_area, dz=thickness)

# Checking volume plot
plotter.subplot(0, 2)
mapdl.vplot(
    vtk=True, show_lines=True, show_axes=True, smooth_shading=True, plotter=plotter
)

plotter.show()

###############################################################################
# Meshing
# ~~~~~~~
# This example will use PLANE183 elements as a thin plate can be
# modeled with plane elements provided that KEYOPTION 3 is set to 3
# and a thickness is provided.
#
# Mesh the plate using a higher density near the hole and a lower
# density for the remainder of the plate by setting ``LESIZE`` for the
# lines nearby the hole and ``ESIZE`` for the mesh global size.
#
# Line numbers can be identified through inspection using ``lplot``

# define a PLANE183 element type with thickness

# ensure there are at 25 elements around the hole
notch_esize = np.pi * notch_radius * 2 / 50
plate_esize = 0.01

# increased the density of the mesh at the notch
# line and area numbers identified using aplot

mapdl.asel("S", "AREA", vmin=1, vmax=1)
mapdl.aplot(vtk=True, show_line_numbering=True)


mapdl.lsel("NONE")
for line in [7, 8, 20, 21]:
    mapdl.lsel("A", "LINE", vmin=line, vmax=line)
mapdl.lesize("ALL", notch_esize, kforc=1)
mapdl.lsel("ALL")

# Decrease the area mesh expansion.  This ensures that the mesh
# remains fine nearby the hole
mapdl.mopt("EXPND", 0.7)  # default 1

# mesh several elements through the plate
esize = notch_esize * 5
if esize > thickness / 2:
    esize = thickness / 2  # minimum of two elements through

mapdl.esize()  # this is tough to automate
mapdl.et(1, "SOLID186")
mapdl.vsweep("all")
mapdl.eplot(vtk=True, show_edges=True, show_axes=False, line_width=2, background="w")


###############################################################################
# Material Properties and Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix the left-hand side of the plate in the X direction and set a
# force of 1 kN in the positive X direction.
#

# This example will use SI units.
mapdl.units("SI")  # SI - International system (m, kg, s, K).

# Define a material (nominal steel in SI)
mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

# Fix the left-hand side.
mapdl.nsel("S", "LOC", "X", 0)
mapdl.d("ALL", "UX")

# Fix a few nodes on the left-hand side of the plate in the Y and Z
# direction.  Otherwise, the mesh would be allowed to move in the y
# direction and would be an improperly constrained mesh.
mapdl.nsel("R", "LOC", "Y", width / 2)
mapdl.d("ALL", "UY")
mapdl.d("ALL", "UZ")

# Apply a force on the right-hand side of the plate.  For this
# example, we select the nodes at the right-most side of the plate.
mapdl.nsel("S", "LOC", "X", length)

# Verify that only the nodes at length have been selected:
# assert np.unique(mapdl.mesh.nodes[:, 0]) == length

# Next, couple the DOF for these nodes.  This lets us provide a force
# to one node that will be spread throughout all nodes in this coupled
# set.
mapdl.cp(5, "UX", "ALL")

# Select a single node in this set and apply a force to it
# We use "R" to re-select from the current node group
mapdl.nsel("R", "LOC", "Y", width / 2)  # selects more than one
single_node = mapdl.mesh.nnum[0]
mapdl.nsel("S", "NODE", vmin=single_node, vmax=single_node)
mapdl.f("ALL", "FX", 1000)

# finally, be sure to select all nodes again to solve the entire solution
mapdl.allsel(mute=True)


###############################################################################
# Solve the Static Problem
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Solve the static analysis
mapdl.run("/SOLU")
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish(mute=True)


###############################################################################
# Post-Processing
# ~~~~~~~~~~~~~~~
# The static result can be post-processed both within MAPDL and
# outside of MAPDL using ``pyansys``.  This example shows how to
# extract the von Mises stress and plot it using the ``pyansys``
# result reader.

# grab the result from the ``mapdl`` instance
result = mapdl.result
result.plot_principal_nodal_stress(
    0,
    "SEQV",
    lighting=False,
    background="w",
    show_edges=True,
    text_color="k",
    add_text=False,
)

nnum, stress = result.principal_nodal_stress(0)
von_mises = stress[:, -1]  # von-Mises stress is the right most column

# Must use nanmax as stress is not computed at mid-side nodes
max_stress = np.nanmax(von_mises)


###############################################################################
# Compute the Stress Concentration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The stress concentration :math:`K_t` is the ratio of the maximum
# stress at the hole to the far-field stress, or the mean cross
# sectional stress at a point far from the hole.  Analytically, this
# can be computed with:
#
# :math:`\sigma_{nom} = \frac{F}{wt}`
#
# Where
#
# - :math:`F` is the force
# - :math:`w` is the width of the plate
# - :math:`t` is the thickness of the plate.
#
# Experimentally, this is computed by taking the mean of the nodes at
# the right-most side of the plate.

# We use nanmean here because mid-side nodes have no stress
mask = result.mesh.nodes[:, 0] == length
far_field_stress = np.nanmean(von_mises[mask])
print("Far field von mises stress: %e" % far_field_stress)
# Which almost exactly equals the analytical value of 10000000.0 Pa


###############################################################################
# Since the expected nominal stress across the cross section of the
# hole will increase as the size of the hole increases, regardless of
# the stress concentration, the stress must be adjusted to arrive at
# the correct stress.  This stress is adjusted by the ratio of the
# width over the modified cross section width.
adj = width / (width - notch_depth * 2)
stress_adj = far_field_stress * adj

# The stress concentration is then simply the maximum stress divided
# by the adjusted far-field stress.
stress_con = max_stress / stress_adj
print("Stress Concentration: %.2f" % stress_con)


###############################################################################
# Batch Analysis
# ~~~~~~~~~~~~~~
# The above script can be placed within a function to compute the
# stress concentration for a variety of hole diameters.  For each
# batch, MAPDL is reset and the geometry is generated from scratch.
#
# .. note::
#    This section has been disabled to reduce the execution time of
#    this example. Enable it by setting ``RUN_BATCH = TRUE``

RUN_BATCH = False

# The function to compute the batch analysis is the following:


def compute_stress_con(ratio):
    notch_depth = ratio * width / 2

    mapdl.clear()
    mapdl.prep7()

    # Notch circle.
    circ0_kp = mapdl.k(x=length / 2, y=width + notch_radius)
    circ_line_num = mapdl.circle(circ0_kp, notch_radius)
    circ_line_num = circ_line_num[2:]  # only concerned with the bottom arcs

    circ0_kp = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=-notch_depth)
    l0 = mapdl.l(circ0_kp, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    circ1_kp = mapdl.k(x=length / 2, y=-notch_radius)
    circ_line_num = mapdl.circle(circ1_kp, notch_radius)
    circ_line_num = circ_line_num[:2]  # only concerned with the top arcs

    k0 = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=notch_depth)
    l0 = mapdl.l(k0, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    rect_anum = mapdl.blc4(width=length, height=width)
    cut_area = mapdl.asba(rect_anum, "ALL")  # cut all areas except the plate

    mapdl.allsel()
    mapdl.vext(cut_area, dz=thickness)

    notch_esize = np.pi * notch_radius * 2 / 50
    plate_esize = 0.01

    mapdl.asel("S", "AREA", vmin=1, vmax=1)

    mapdl.lsel("NONE")
    for line in [7, 8, 20, 21]:
        mapdl.lsel("A", "LINE", vmin=line, vmax=line)

    mapdl.ksel("NONE")
    mapdl.ksel(
        "S",
        "LOC",
        "X",
        length / 2 - notch_radius * 1.1,
        length / 2 + notch_radius * 1.1,
    )
    mapdl.lslk("S", 1)
    mapdl.lesize("ALL", notch_esize, kforc=1)
    mapdl.lsel("ALL")

    mapdl.mopt("EXPND", 0.7)  # default 1

    esize = notch_esize * 5
    if esize > thickness / 2:
        esize = thickness / 2  # minimum of two elements through

    mapdl.esize()  # this is tough to automate
    mapdl.et(1, "SOLID186")
    mapdl.vsweep("all")

    mapdl.allsel()

    # Uncomment if you want to print geometry and mesh plots.
    # mapdl.vplot(savefig=f'vplot-{ratio}.png', off_screen=True)
    # mapdl.eplot(savefig=f'eplot-{ratio}.png', off_screen=True)

    mapdl.units("SI")  # SI - International system (m, kg, s, K).

    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX")

    mapdl.nsel("R", "LOC", "Y", width / 2)
    mapdl.d("ALL", "UY")
    mapdl.d("ALL", "UZ")

    mapdl.nsel("S", "LOC", "X", length)
    mapdl.cp(5, "UX", "ALL")

    mapdl.nsel("R", "LOC", "Y", width / 2)  # selects more than one
    single_node = mapdl.mesh.nnum[0]
    mapdl.nsel("S", "NODE", vmin=single_node, vmax=single_node)
    mapdl.f("ALL", "FX", 1000)

    mapdl.allsel(mute=True)

    mapdl.run("/SOLU")
    mapdl.antype("STATIC")
    mapdl.solve()
    mapdl.finish()

    result = mapdl.result
    _, stress = result.principal_nodal_stress(0)
    von_mises = stress[:, -1]  # von-Mises stress is the right most column
    max_stress = np.nanmax(von_mises)

    mask = result.mesh.nodes[:, 0] == length
    far_field_stress = np.nanmean(von_mises[mask])

    adj = width / (width - notch_depth * 2)
    stress_adj = far_field_stress * adj

    return max_stress / stress_adj


###############################################################################
# Run the batch and record the stress concentration

if RUN_BATCH:
    k_t_exp = []
    ratios = np.linspace(0.05, 0.75, 9)
    print("    Ratio  : Stress Concentration (K_t)")
    for ratio in ratios:
        stress_con = compute_stress_con(ratio)
        print("%10.4f : %10.4f" % (ratio, stress_con))
        k_t_exp.append(stress_con)


###############################################################################
# Analytical Solution
# ~~~~~~~~~~~~~~~~~~~
# Stress concentrations are often obtained by referencing tabular
# results or polynominal fits for a variety of geometries.  According
# to *Roark’s Formulas for Stress and Strain* (Warren C. Young and
# Richard G. Budynas, Seventh Edition, McGraw-Hill) the analytical
# equation for two U notches in a thin plate in uniaxial tension:
#
# .. math::
#
#    K_t = C_1 + C_2 \left(\dfrac{2h}{D}\right) + C_3 \left(\dfrac{2h}{D}\right)^2 + C_4 \left(\dfrac{2h}{D}\right)^3
#
# where:
#
# .. math::
#    \begin{array}{c|c|c}
#        & 0.1 \leq h/r \leq 2.0                 & 2.0 \leq h/r \leq 50.0 \\ \hline
#    C_1 & 0.85 + 2.628 \sqrt{h/r} - 0.413 h/r   & 0.833 + 2.069 \sqrt{h/r} - 0.009 h/r \\
#    C_2 & -1.119 - 4.826 \sqrt{h/r} + 2.575 h/r & 2.732 - 4.157   \sqrt{h/r} + 0.176 h/r \\
#    C_3 & 3.563 - 0.514 \sqrt{h/r} - 2.402 h/r  & -8.859 + 5.327 \sqrt{h/r} - 0.32 h/r \\
#    C_4 & -2.294 + 2.713 \sqrt{h/r} + 0.240 h/r & 6.294 - 3.239 \sqrt{h/r} + 0.154 h/r
#    \end{array}
#
# Where:
#
# - :math:`K_t` is the stress concentration
# - :math:`r` is the radius of the notch
# - :math:`h` is the notch depth
# - :math:`D` is the width of the plate
#
# In this example the ratio is given as :math:`2h/D`.
#
# These formulas are converted in the following function:


def calc_teor_notch(ratio):
    notch_depth = ratio * width / 2
    h = notch_depth
    r = notch_radius
    D = width

    if 0.1 <= h / r <= 2.0:
        c1 = 0.85 + 2.628 * (h / r) ** 0.5 - 0.413 * h / r
        c2 = -1.119 - 4.826 * (h / r) ** 0.5 + 2.575 * h / r
        c3 = 3.563 - 0.514 * (h / r) ** 0.5 - 2.402 * h / r
        c4 = -2.294 + 2.713 * (h / r) ** 0.5 + 0.240 * h / r
    elif 2.0 <= h / r <= 50.0:
        c1 = 0.833 + 2.069 * (h / r) ** 0.5 - 0.009 * h / r
        c2 = 2.732 - 4.157 * (h / r) ** 0.5 + 0.176 * h / r
        c3 = -8.859 + 5.327 * (h / r) ** 0.5 - 0.32 * h / r
        c4 = 6.294 - 3.239 * (h / r) ** 0.5 + 0.154 * h / r

    return c1 + c2 * (2 * h / D) + c3 * (2 * h / D) ** 2 + c4 * (2 * h / D) ** 3


###############################################################################
# which is used later to calculate the concentration factor for the given ratios:

if RUN_BATCH:
    print("    Ratio  : Stress Concentration (K_t)")
    k_t_anl = []
    for ratio in ratios:
        stress_con = calc_teor_notch(ratio)
        print("%10.4f : %10.4f" % (ratio, stress_con))
        k_t_anl.append(stress_con)


###############################################################################
# Analytical Comparison
# ~~~~~~~~~~~~~~~~~~~~~
#
# As shown in the following plot, MAPDL matches the known tabular
# result for this geometry remarkably well using PLANE183 elements.
# The fit to the results may vary depending on the ratio between the
# height and width of the plate.

if RUN_BATCH:
    plt.plot(ratios, k_t_anl, label=r"$K_t$ Analytical")
    plt.plot(ratios, k_t_exp, label=r"$K_t$ ANSYS")
    plt.legend()
    plt.show()

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
