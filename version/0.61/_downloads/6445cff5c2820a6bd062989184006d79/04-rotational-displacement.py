"""
.. _ref_rotational_displacement_example:

Generating and Extracting Rotational Displacement
-------------------------------------------------

Not all element types have rotational degrees of freedom, but generally,
"shell" ones do. In this example we create a square shell with thickness
of 0.1 and bend it, creating rotational displacement.

We subsequently plot the cumulative principal stresses and use
:class:`ansys.mapdl.core.inline_functions.Query` to
extract the exact values of rotational displacement at the four corners
of our square.

"""

# start MAPDL and enter the pre-processing routine
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()
mapdl.prep7()

###############################################################################
# Mesh Setup
# ~~~~~~~~~~
# In this example we create a simple 2D square, 1 x 1 in dimension, and give it
# the `'SHELL181'` element type because this type has rotational degrees of
# freedom. Following this we:
#
# - Give the material an elastic modulus of 2e5 (EX)
# - Give the material a major poissons ratio of 0.3 (PRXY)
# - Set the section type to 'SHELL'
# - Set the thickness to 0.1
# - Set the element size to 0.2
# - Mesh the square
# - Plot the mesh

mapdl.et(1, "SHELL181")
mapdl.mp("EX", 1, 2e5)
mapdl.mp("PRXY", 1, 0.3)
mapdl.rectng(0, 1, 0, 1)
mapdl.sectype(1, "SHELL")
mapdl.secdata(0.1)
mapdl.esize(0.2)
mapdl.amesh("all")
mapdl.eplot()

###############################################################################
# Applying Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# - Enter solution mode
# - Set analysis type to `'STATIC'`
# - Remove all degrees of freedom for nodes at ``x = 0``
# - Apply a displacement of ``uz = -0.1`` at ``x = 1``
# - Select all nodes
# - Solve the model

mapdl.run("/SOLU")
mapdl.antype("STATIC")
mapdl.nsel("s", "loc", "x", 0)
mapdl.d("all", "all")
mapdl.nsel("s", "loc", "x", 1)
mapdl.d("all", "uz", -0.1)
mapdl.allsel("all")
mapdl.solve()

###############################################################################
# Plotting Stresses
# ~~~~~~~~~~~~~~~~~
# - Extract the results
# - Plot the cumulative (0) equivalent stress (SEQV)
#   - Set the colormap to 'plasma' because it is perceptually uniform
#   - Show displacement so that we can see any deformation

result = mapdl.result
result.plot_principal_nodal_stress(
    0, "SEQV", show_edges=True, cmap="plasma", show_displacement=True
)


###############################################################################
# Extracting Rotational Displacements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# - Get a :class:`ansys.mapdl.core.inline_functions.Query` instance from the
#   ``queries`` property
# - Locate the nodes at the four corners of the square
# - Extract all 3 rotational displacement components for each one
# - Print them all

q = mapdl.queries

node1 = q.node(0, 0, 0)
node2 = q.node(0, 1, 0)
node3 = q.node(1, 0, 0)
node4 = q.node(1, 1, 0)

nodes = [node1, node2, node3, node4]

rotations = [(q.rotx(n), q.roty(n), q.rotz(n)) for n in nodes]

message = f"""
(0,1) B _________ C (1,1)
       |         |
       |         |
       |         |
       |_________|
(0,0) A           D (1,0)

N | (x_rot_disp, y_rot_disp, z_rot_disp)
--|------------------------------------
A | {rotations[0][0]:11.6f},{rotations[0][1]:11.6f},{rotations[0][2]:11.6f}
B | {rotations[1][0]:11.6f},{rotations[1][1]:11.6f},{rotations[1][2]:11.6f}
C | {rotations[2][0]:11.6f},{rotations[2][1]:11.6f},{rotations[2][2]:11.6f}
D | {rotations[3][0]:11.6f},{rotations[3][1]:11.6f},{rotations[3][2]:11.6f}

"""

print(message)


###############################################################################
# stop mapdl
mapdl.exit()
