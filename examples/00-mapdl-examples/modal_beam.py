"""
.. _ref_modal_beam:

=================================
MAPDL Modal Beam Analysis Example
=================================

This example demonstrate how to performa a simple modal analysis
and animate its results.


Objective
~~~~~~~~~
In this example, we model a simple 3D elastic beam made of BEAM188 elements.
These beams elements are made of a linear elastic material similar to steel,
and have a rectangular section.


Procedure
~~~~~~~~~

* Launch MAPDL instance
* Material properties
* Geometry
* Finite element model
* Boundary conditions
* Solving the model
* Post-processing
* Stop MAPDL

"""

###############################################################################
# Launch MAPDL instance
# =====================
#
# Launch MAPDL with interactive plotting
from ansys.mapdl.core import launch_mapdl

nmodes = 10
# start MAPDL
mapdl = launch_mapdl()
print(mapdl)


###############################################################################
# Material properties
# ===================
#
# Define material
mapdl.prep7()
mapdl.mp("EX", 1, 2.1e11)
mapdl.mp("PRXY", 1, 0.3)
mapdl.mp("DENS", 1, 7800)

###############################################################################
# Geometry
# ========
#
# Create keypoints and line
mapdl.k(1)
mapdl.k(2, 10)
mapdl.l(1, 2)
mapdl.lplot()

###############################################################################
# Finite element model
# ====================
#
# Define element type/section type - Rectangular beam section
mapdl.et(1, "BEAM188")
mapdl.sectype(1, "BEAM", "RECT")
mapdl.secoffset("CENT")
mapdl.secdata(2, 1)

# Mesh the line
mapdl.type(1)
mapdl.esize(1)
mapdl.lesize("ALL")
mapdl.lmesh("ALL")
mapdl.eplot()
mapdl.finish()

###############################################################################
# Boundary conditions
# ===================
#
# Fully fixed (clamped) end.
mapdl.nsel("S", "LOC", "X", "0")
mapdl.d("ALL", "ALL")
mapdl.allsel()
mapdl.nplot(plot_bc=True, nnum=True)

###############################################################################
# Solving the model
# =================
#
# Setting modal analysis
mapdl.solution()  # Entering the solution processor.
mapdl.antype("MODAL")
mapdl.modopt("LANB", nmodes, 0, 200)
mapdl.solve()
mapdl.finish()

###############################################################################
# Post-processing
# ===============
#
# Enter the post processor (post1)
mapdl.post1()
output = mapdl.set("LIST")
print(output)

result = mapdl.result

## animate result
mode2plot = 2
normalizeDisplacement = 1 / result.nodal_displacement(mode2plot - 1)[1].max()
result.plot_nodal_displacement(
    mode2plot,
    show_displacement=True,
    displacement_factor=normalizeDisplacement,
    n_colors=10,
)

result.animate_nodal_displacement(
    mode2plot,
    loop=True,
    add_text=False,
    n_frames=100,
    displacement_factor=normalizeDisplacement,
    show_axes=False,
    background="w",
)

###############################################################################
# Stop MAPDL
# ==========
#
mapdl.finish()
mapdl.exit()
