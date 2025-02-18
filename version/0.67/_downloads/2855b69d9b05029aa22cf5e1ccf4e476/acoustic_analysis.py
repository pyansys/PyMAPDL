"""
.. _acoustic_analysis_example:

====================
3D Acoustic Analysis
====================

This example shows how to perform an acoustic analysis using PyMAPDL and ``FLUID`` elements.
"""

###############################################################################
# Launch PyMAPDL
# ==============
# Launch PyMAPDL and load ``matplotlib``.
from matplotlib import pyplot as plt

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()

mapdl.clear()
mapdl.prep7()
mapdl.units("SI")  # SI - International system (m, kg, s, K).

###############################################################################
# Element and Material Properties
# ===============================
# Define the ``FLUID30`` and ``FLUID130`` element types.

mapdl.et(1, "FLUID30", kop1=2)


# Define the material properties
mapdl.mp("SONC", 1, 1500)  # sonc in m/s
mapdl.mp("DENS", 1, 1000)  # Density in kg/m3
print(mapdl.mplist())


# Define the real const
mapdl.r("1", "1e-6")  # Reference pressure for R set 1
print(mapdl.rlist())


###############################################################################
# Geometry Definition
# ===================
# Create a simple sphere.

vnum = mapdl.sphere(rad1=0.5, rad2=1.0)
mapdl.vsbw("all")
mapdl.vplot(show_area_numbering=True)

###############################################################################
# Geometry Meshing
# ================
# First select the material and elements.
#

mapdl.type(itype=1)
mapdl.real(nset=1)
mapdl.mat(mat=1)
mapdl.mshape(1, "3D")

###############################################################################
# Then choose the element size and perform the mesh.

mapdl.esize(0.25)
mapdl.vmesh("all")
mapdl.eplot(show_node_numbering=False)

###############################################################################
# Boundary Conditions
# ===================
# Add surface boundary condition to the nodes using :func:`Mapdl.sf() <ansys.mapdl.core.Mapdl.sf>`
# and the option ``SHLD`` for *Surface normal velocity or acceleration*.

mapdl.csys(2)
mapdl.asel("s", "loc", "x", 0.5)
mapdl.csys(0)
mapdl.nsla("S", 1)
mapdl.sf("all", "SHLD", 5)
mapdl.allsel()

###############################################################################
# Solve the model
# ===============
# Using :func:`Mapdl.solve() <ansys.mapdl.core.Mapdl.solve>`
#
mapdl.allsel()
mapdl.run("/SOLU")
mapdl.antype(3)
mapdl.harfrq(freqb=200, freqe=1000)
mapdl.autots("off")
mapdl.nsubst(40)
mapdl.kbc(0)

mapdl.outres("erase")  # Save less data in order to reduce the size of .rst file
mapdl.outres("all", "none")  # NOTE that other output like stresses is not saved
mapdl.outres("nsol", "all")  # Save pressure and displacement
mapdl.outres("fgrad", "all")  # Save velocities
mapdl.outres("misc", "all")  # For post processing calculations

mapdl.solve()

###############################################################################
# Post1: Time step results
# ========================
#
# Listing the results
mapdl.post1()
print(mapdl.set("LIST"))

###############################################################################
# Post26: Time dependent results
# ==============================
#
# Getting results for specific nodes

mapdl.post26()
freqs = mapdl.post_processing.time_values[::2]
node = 276

# Getting results
node_pressure = mapdl.nsol(3, node, "spl")
node_sound_pressure_level = mapdl.nsol(4, node, "SPLA")

# Plotting
fig, ax = plt.subplots(1, 2)

ax[0].plot(freqs, node_pressure)
ax[0].set_xlabel("Frequencies (Hz)")
ax[0].set_ylabel("Sound pressure level (Pa)")

ax[1].plot(freqs, node_sound_pressure_level, label="Nodal Sound Pressure")
ax[1].set_xlabel("Frequencies (Hz)")
ax[1].set_ylabel("A-weighted sound\npressure level (dBA)")

fig.suptitle(f"Node {node} Results")
fig.tight_layout()
fig.show()

###############################################################################
# Stop MAPDL
#
mapdl.exit()
