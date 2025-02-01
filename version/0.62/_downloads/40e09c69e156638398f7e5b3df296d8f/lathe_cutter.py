"""
.. _ref_lathe_cutter_example:

=====================================
Structural Analysis of a Lathe Cutter
=====================================

**Summary**: Basic walk through PyMAPDL capabilities.

Objective
=========

The objective of this example is to highlight some regularly used
PyMAPDL features via a lathe cutter finite element model. Lathe
cutters have multiple avenues of wear and failure, and the analyses
supporting their design would most often be transient
thermal-structural. However, for simplicity, this simulation
example uses a non-uniform load.

.. figure:: ../../../_static/lathe_cutter_model.png
    :align: center
    :width: 600
    :alt:  Lathe cutter geometry and load description.
    :figclass: align-center

    **Figure 1: Lathe cutter geometry and load description.**



Contents
========

1. **Variables and launch**
   Define necessary variables and launch MAPDL.

2. **Geometry, mesh, and MAPDL parameters**
   Import geometry and inspect for MAPDL parameters. Define linear
   elastic material model with Python variables. Mesh and apply symmetry
   boundary conditions.

3. **Coordinate system and load**
   Create a local coordinate system for the applied load and verify with
   a plot.

4. **Pressure load**
   Define the pressure load as a sine function of the length of the
   application area using numpy arrays. Import the pressure array into
   MAPDL as a table array. Verify the applied load and solve.

5. **Plotting**
   Show result plotting, plotting with selection, and working with the
   plot legend.

6. **Postprocessing:**
   List a result two ways: use PyMAPDL and the Pythonic version of APDL.
   Demonstrate extended methods and writing a list to a file.

7. **Advanced plotting**
   Use of `mesh.grid <https://mapdldocs.pyansys.com/mapdl_commands/graphics/_autosummary/ansys.mapdl.core.Mapdl.grid.html>`_
   for additional postprocessing.


Step 1: Variables and launch
============================

Define variables and launch MAPDL.
"""

import os

import numpy as np

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples.downloads import download_example_data

# cwd = current working directory
path = os.getcwd()
PI = np.pi
EXX = 1.0e7
NU = 0.27

###############################################################################
# Often used MAPDL command line options are exposed as Pythonic parameter names in
# :func:`ansys.mapdl.core.launch_mapdl`. For example, ``-dir``
# has become ``run_location``.
# You could use ``run_location`` to specify the MAPDL run location. For example:
#
# ..code:: python3
#
#   mapdl = launch_mapdl(run_location=path)
#
# Otherwise, the MAPDL working directory is stored in ``mapdl.directory``. In this
# directory, MAPDL will create some of the images we will show later.
#
# Options without a Pythonic version can be accessed by the ``additional_switches``
# parameter.
# Here ``-smp`` is used only to keep the number of solver files to a minimum.

mapdl = launch_mapdl(additional_switches="-smp")

###############################################################################
# Step 2: Geometry, mesh, and MAPDL parameters
# ============================================
#
# - Import geometry and inspect for MAPDL parameters.
# - Define material and mesh, and then create boundary conditions.
#

# First, reset the MAPDL database.
mapdl.clear()

###############################################################################
# Import the geometry file and list any MAPDL parameters.
lathe_cutter_geo = download_example_data("LatheCutter.anf", "geometry")
mapdl.input(lathe_cutter_geo)
mapdl.finish()
print(mapdl.parameters)

###############################################################################
# Use pressure area per length in the load definition.
pressure_length = mapdl.parameters["PRESS_LENGTH"]

print(mapdl.parameters)

###############################################################################
# Change the units and title.
mapdl.units("Bin")
mapdl.title("Lathe Cutter")

###############################################################################
# Set material properties.
mapdl.prep7()
mapdl.mp("EX", 1, EXX)
mapdl.mp("NUXY", 1, NU)

###############################################################################
# The MAPDL element type ``SOLID285`` is used for demonstration purposes.
# Consider using an appropriate element type or mesh density for your actual
# application.

mapdl.et(1, 285)
mapdl.smrtsize(4)
mapdl.aesize(14, 0.0025)
mapdl.vmesh(1)

mapdl.da(11, "symm")
mapdl.da(16, "symm")
mapdl.da(9, "symm")
mapdl.da(10, "symm")

###############################################################################
# Step 3: Coordinate system and load
# ==============================================
#
# Create a local Coordinate System (CS) for the applied pressure as a function
# of local X.
#
# Local CS ID is 11

mapdl.cskp(11, 0, 2, 1, 13)
mapdl.csys(1)
mapdl.view(1, -1, 1, 1)
mapdl.psymb("CS", 1)
mapdl.vplot(
    color_areas=True,
    show_lines=True,
    cpos=[-1, 1, 1],
    smooth_shading=True,
)

###############################################################################
#
# VTK plots do not show MAPDL plot symbols.
# However, to use MAPDL plotting capabilities, you can set the keyword
# option ``vtk`` to ``False``.

mapdl.lplot(vtk=False)

###############################################################################
# Step 4: Pressure load
# =================================
#
# Create a pressure load, load it into MAPDL as a table array, verify the load,
# and solve.

# pressure_length = 0.055 inch

pts = 10
pts_1 = pts - 1

length_x = np.arange(0, pts, 1)
length_x = length_x * pressure_length / pts_1

press = 10000 * (np.sin(PI * length_x / pressure_length))

###############################################################################
# ``length_x`` and ``press`` are vectors. To combine them into the correct
# form needed to define the MAPDL table array, you can use
# `numpy.stack <https://numpy.org/doc/stable/reference/generated/numpy.stack.html>`_.

press = np.stack((length_x, press), axis=-1)
mapdl.load_table("MY_PRESS", press, "X", csysid=11)

mapdl.asel("S", "Area", "", 14)
mapdl.nsla("S", 1)
mapdl.sf("All", "Press", "%MY_PRESS%")
mapdl.allsel()

###############################################################################
# You can open the MAPDL GUI to check the model.
#
# .. code:: python
#
#     mapdl.open_gui()
#
#

###############################################################################
# Set up the solution.
mapdl.finish()
mapdl.slashsolu()
mapdl.nlgeom("On")
mapdl.psf("PRES", "NORM", 3, 0, 1)
mapdl.view(1, -1, 1, 1)
mapdl.eplot(vtk=False)

###############################################################################
# Solve the model.
mapdl.solve()
mapdl.finish()
if mapdl.solution.converged:
    print("The solution has converged.")

###############################################################################
# Step 5: Plotting
# ================
#

mapdl.post1()
mapdl.set("last")
mapdl.allsel()

mapdl.post_processing.plot_nodal_principal_stress("1", smooth_shading=False)

###############################################################################
# Plotting - Part of Model
# ------------------------
#

mapdl.csys(1)
mapdl.nsel("S", "LOC", "Z", -0.5, -0.141)
mapdl.esln()
mapdl.nsle()
mapdl.post_processing.plot_nodal_principal_stress(
    "1", edge_color="white", show_edges=True
)

###############################################################################
# Plotting - Legend Options
# -------------------------
#

mapdl.allsel()
sbar_kwargs = {
    "color": "black",
    "title": "1st Principal Stress (psi)",
    "vertical": False,
    "n_labels": 6,
}
mapdl.post_processing.plot_nodal_principal_stress(
    "1",
    cpos="xy",
    background="white",
    edge_color="black",
    show_edges=True,
    scalar_bar_args=sbar_kwargs,
    n_colors=9,
)

###############################################################################
# Let's try out some scalar bar options from the
# `PyVista documentation <https://docs.pyvista.org/>`_.
# For example, let's set black text on a beige background.
#
# The scalar bar keywords defined as a Python dictionary are an alternate
# method to using {key:value}'s.
# You can use the click-and drag method to reposition the scalar bar.
# Left-click it and hold down the left mouse button while moving the mouse.

sbar_kwargs = dict(
    title_font_size=20,
    label_font_size=16,
    shadow=True,
    n_labels=9,
    italic=True,
    bold=True,
    fmt="%.1f",
    font_family="arial",
    title="1st Principal Stress (psi)",
    color="black",
)

mapdl.post_processing.plot_nodal_principal_stress(
    "1",
    cpos="xy",
    edge_color="black",
    background="beige",
    show_edges=True,
    scalar_bar_args=sbar_kwargs,
    n_colors=256,
    cmap="jet",
)

# cmap names *_r usually reverses values.  Try cmap='jet_r'


###############################################################################
# Step 6: Postprocessing
# =======================
#
# Results List
# ------------
#
# Get all principal nodal stresses.
mapdl.post_processing.nodal_principal_stress("1")

###############################################################################
# Get the principal nodal stresses of the node subset.
mapdl.nsel("S", "S", 1, 6700, 7720)
mapdl.esln()
mapdl.nsle()

print("The node numbers are:")
print(mapdl.mesh.nnum)  # get node numbers

print("The principal nodal stresses are:")
mapdl.post_processing.nodal_principal_stress("1")

###############################################################################
# Results as lists, arrays, and DataFrames
# -----------------------------------------
# Using `mapdl.prnsol <https://mapdldocs.pyansys.com/mapdl_commands/post1/_autosummary/ansys.mapdl.core.Mapdl.prnsol.html>`_
# to check
print(mapdl.prnsol("S", "PRIN"))

###############################################################################
# Use this command to obtain the data as a list.
mapdl_s_1_list = mapdl.prnsol("S", "PRIN").to_list()
print(mapdl_s_1_list)

###############################################################################
# Use this command to obtain the data as an array:
mapdl_s_1_array = mapdl.prnsol("S", "PRIN").to_array()
print(mapdl_s_1_array)

###############################################################################
# or as a DataFrame:
mapdl_s_1_df = mapdl.prnsol("S", "PRIN").to_dataframe()
mapdl_s_1_df.head()

###############################################################################
# Use this command to obtain the data as a DataFrame, which is a.
# `Pandas data type <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_.
# Because the Pandas module is imported, you can use its functions.
# For example, you can write principal stresses to a file.

# mapdl_s_1_df.to_csv(path + '\prin-stresses.csv')
# mapdl_s_1_df.to_json(path + '\prin-stresses.json')
mapdl_s_1_df.to_html(path + "\prin-stresses.html")

###############################################################################
# Step 7: Advanced plotting
# =========================
#

mapdl.allsel()
principal_1 = mapdl.post_processing.nodal_principal_stress("1")

###############################################################################
# Load this result into the VTK grid.
grid = mapdl.mesh.grid
grid["p1"] = principal_1

sbar_kwargs = {
    "color": "black",
    "title": "1st Principal Stress (psi)",
    "vertical": False,
    "n_labels": 6,
}

###############################################################################
# Generate a single horizontal slice along the XY plane.
#
# .. note::
#    We're using ``eye_dome_lighting`` here to enhance the plots of our slices.
#    Read more about it at `Eye Dome Lighting
#    <https://docs.pyvista.org/examples/02-plot/edl.html>`_

single_slice = grid.slice(normal=[0, 0, 1], origin=[0, 0, 0])
single_slice.plot(
    scalars="p1",
    background="white",
    lighting=False,
    eye_dome_lighting=True,
    show_edges=False,
    cmap="jet",
    n_colors=9,
    scalar_bar_args=sbar_kwargs,
)

###############################################################################
# Generate a plot with three slice planes.
slices = grid.slice_orthogonal()
slices.plot(
    scalars="p1",
    background="white",
    lighting=False,
    eye_dome_lighting=True,
    show_edges=False,
    cmap="jet",
    n_colors=9,
    scalar_bar_args=sbar_kwargs,
)

###############################################################################
# Generate a grid with multiple slices in the same plane.
#
slices = grid.slice_along_axis(12, "x")
slices.plot(
    scalars="p1",
    background="white",
    show_edges=False,
    lighting=False,
    eye_dome_lighting=True,
    cmap="jet",
    n_colors=9,
    scalar_bar_args=sbar_kwargs,
)

###############################################################################
# Finally, exit MAPDL.
mapdl.exit()
