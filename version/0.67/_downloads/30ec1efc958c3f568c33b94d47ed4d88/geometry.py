"""
.. _ref_3d_bracket_example:

Plotting and Mesh Access
------------------------

PyMAPDL can load basic IGES geometry for analysis.

This example demonstrates loading basic geometry into MAPDL for
analysis and demonstrates how to use the built-in Python specific
plotting functionality.

This example also demonstrates some of the more advanced features of
PyMAPDL including direct mesh access through VTK.

"""
# sphinx_gallery_thumbnail_number = 3

import numpy as np

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import examples

mapdl = pymapdl.launch_mapdl()


###############################################################################
# Load Geometry
# ~~~~~~~~~~~~~
# Here we download a simple example bracket IGES file and load it into
# MAPDL.  Since ``igesin`` must be in the AUX15 process

# note that this method just returns a file path
bracket_file = examples.download_bracket()

# load the bracket and then print out the geometry
mapdl.aux15()
mapdl.igesin(bracket_file)
print(mapdl.geometry)


###############################################################################
# Plotting
# ~~~~~~~~
# PyMAPDL uses VTK and pyvista as a plotting backend to enable
# remotable (with 2021R1 and newer) interactive plotting.  The common
# plotting methods (``kplot``, ``lplot``, ``aplot``, ``eplot``, etc.)
# all have compatible commands that use the
# :func:`ansys.mapdl.core.plotting.general_plotter` function.  You can
# configure this method with a variety of keyword arguments.  For example:

mapdl.lplot(
    show_line_numbering=False,
    background="k",
    line_width=3,
    color="w",
    show_axes=False,
    show_bounds=True,
    title="",
    cpos="xz",
)


###############################################################################
# You can also configure a theme to enable consistent plotting across
# multiple plots.  These theme parameters override any unset keyword
# arguments.  For example:

my_theme = pymapdl.MapdlTheme()
my_theme.background = "white"
my_theme.cmap = "jet"  # colormap
my_theme.axes.show = False
my_theme.show_scalar_bar = False

mapdl.aplot(theme=my_theme, quality=8)


###############################################################################
# Accessesing Element and Nodes Pythonically
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PyMAPDL also supports element and nodal plotting using ``eplot`` and
# ``nplot``.  First, mesh the bracket using SOLID187 elements.  These
# are well suited to this geometry and the static structural analyses.

# set the preprocessor, element type and size, and mesh the volume
mapdl.prep7()
mapdl.et(1, "SOLID187")
mapdl.esize(0.075)
mapdl.vmesh("all")

# print out the mesh characteristics
print(mapdl.mesh)


###############################################################################
# You can access the underlying finite element mesh as a VTK grid
# through the ``mesh.grid`` attribute.

grid = mapdl.mesh.grid
grid


###############################################################################
# This UnstructuredGrid contains a powerful API, including the ability
# to access the nodes, elements, original node numbers, all with the
# ability to plot the mesh and add new attributes and data to the
# grid.

grid.points  # same as mapdl.mesh.nodes


###############################################################################
# cell representation in VTK format

grid.cells


###############################################################################
# Obtain node numbers of the grid

grid.point_data["ansys_node_num"]


###############################################################################
# Save arbitrary data to the grid

# must be sized to the number of points
grid.point_data["my_data"] = np.arange(grid.n_points)
grid.point_data


###############################################################################
# Plot this mesh with scalars of your choosing.  You can apply the
# same MapdlTheme when plotting as it's compatible with the grid plotter.

# make interesting scalars
scalars = grid.points[:, 2]  # z coordinates

sbar_kwargs = {"color": "black", "title": "Z Coord"}
grid.plot(
    scalars=scalars,
    show_scalar_bar=True,
    scalar_bar_args=sbar_kwargs,
    show_edges=True,
    theme=my_theme,
)


###############################################################################
# This grid can be also saved to disk in the compact cross-platform VTK
# format and loaded again with ``pyvista`` or ParaView.
#
# ..code:: pycon
#
#     >>> grid.save('my_mesh.vtk')
#     >>> import pyvista
#     >>> imported_mesh = pyvista.read('my_mesh.vtk')

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
