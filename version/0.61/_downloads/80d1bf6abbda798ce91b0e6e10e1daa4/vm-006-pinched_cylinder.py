r"""
.. _ref_vm6_example:

Pinched Cylinder
----------------
Problem Description:
 - A thin-walled cylinder is pinched by a force :math:`F` at the middle
   of the cylinder length. Determine the radial displacement :math:`\delta`
   at the point where the force :math:`F` is applied.
   The ends of the cylinder are free edges.

Reference:
 - R. D. Cook, Concepts and Applications of Finite Element Analysis, 2nd Edition,
   John Wiley and Sons, Inc., New York, NY, 1981, pp. 284-287.
   H. Takemoto, R. D. Cook, "Some Modifications of an Isoparametric Shell
   Element", International Journal for Numerical Methods in Engineering, Vol.7
   No. 3, 1973.

Analysis Type(s):
 - Static Analysis ``ANTYPE=0``

Element Type(s):
 - 4-Node Finite Strain Shell Elements (SHELL181)
 - 8-Node Finite Strain Shell Elements (SHELL281)

.. image:: ../../_static/vm6_setup.png
   :width: 400
   :alt: VM6 Pinched Cylinder Problem Sketch

Material Properties
 - :math:`E = 10.5 \cdot 10^6 psi`
 - :math:`\nu = 0.3125`

Geometric Properties:
 - :math:`l = 10.35  in`
 - :math:`r = 4.953  in`
 - :math:`t = 0.094  in`

Loading:
 - :math:`F = 100  lb`

Analysis Assumptions and Modeling Notes:
 - A one-eighth symmetry model is used. One-fourth of the load is applied
   due to symmetry.

"""
# sphinx_gallery_thumbnail_path = '_static/vm6_setup.png'

###############################################################################
# Start MAPDL
# ~~~~~~~~~~~

from ansys.mapdl.core import launch_mapdl

# Start mapdl.
mapdl = launch_mapdl()


###############################################################################
# Initiate Pre-Processing
# ~~~~~~~~~~~~~~~~~~~~~~~
# Enter verification example mode and the pre-processing routine.


def start_prep7():
    mapdl.clear()
    mapdl.verify()
    mapdl.prep7()


start_prep7()


###############################################################################
# Define Element Type
# ~~~~~~~~~~~~~~~~~~~
# Set up the element type (a shell-type).

# Define the element type number.
def define_element(elem_type):
    # Type of analysis: Static.
    mapdl.antype("STATIC")

    # Define the element type number.
    elem_num = 1

    if elem_type == "SHELL181":

        # Element type: SHELL181.
        mapdl.et(elem_num, elem_type)

        # Special Features are defined by keyoptions of shell element:

        # KEYOPT(3)
        # Integration option:
        # Full integration with incompatible modes.
        mapdl.keyopt(elem_num, 3, 2)  # Cubic shape function

    elif elem_type == "SHELL281":

        # Element type: SHELL181.
        mapdl.et(elem_num, "SHELL281")

    return elem_type, mapdl.etlist()


# Return the number of the element type.
elem_type, elem_type_list = define_element(elem_type="SHELL181")
print(
    f"Selected element type is: {elem_type},\n"
    f"Printout the element list with its own properties:\n {elem_type_list}"
)


###############################################################################
# Define Material
# ~~~~~~~~~~~~~~~
# Set up the material properties, where:
# Young Modulus is :math:`E = 10.5 \cdot 10^6 psi`,
# Poisson's ratio is :math:`\nu = 0.3125`.

# Define material number.
mat_num = 1

# Define material properties.
def define_material():
    # Define material properties.
    mapdl.mp("EX", mat_num, 10.5e6)
    mapdl.mp("NUXY", mat_num, 0.3125)
    return mapdl.mplist()


material_list = define_material()
print(material_list)


###############################################################################
# Define Section
# ~~~~~~~~~~~~~~
# Set up the cross-section properties for a shell element.

# Define cross-section number and thickness of the shell element.
sec_num = 1
t = 0.094

# Define shell cross-section.
def define_section():
    # Define shell cross-section.
    mapdl.sectype(secid=sec_num, type_="SHELL", name="shell181")
    mapdl.secdata(t, mat_num, 0, 5)
    return mapdl.slist()


section_list = define_section()
print(section_list)


###############################################################################
# Define Geometry
# ~~~~~~~~~~~~~~~
# Set up the keypoints and create the area through the keypoints.

# Define geometry of the simplified mathematical model.
def define_geometry():
    # Change active coordinate system
    # to the global cylindrical coordinate system.
    mapdl.csys(1)

    # Define keypoints by coordinates.
    mapdl.k(1, 4.953)
    mapdl.k(2, 4.953, "", 5.175)

    # Generate additional keypoints from a pattern of keypoints.
    mapdl.kgen(2, 1, 2, 1, "", 90)

    # Create an area through keypoints.
    mapdl.a(1, 2, 4, 3)

    if elem_type == "SHELL181":
        # Plot the lines.
        mapdl.lplot(color_lines=True, cpos="iso")

        # Plot the area using PyVista parameters.
        mapdl.aplot(
            title="Display the selected area",
            cpos="iso",
            vtk=True,
            color="#06C2AC",
            show_line_numbering=True,
            show_area_numbering=True,
            show_lines=True,
        )


define_geometry()


# Define the number of the keypoint where F is applied using inline function.
def keypoint_number(mapdl):
    keypoint_num = mapdl.queries.kp(4.953, 90, 0)
    return keypoint_num


# Call the function to get the number of keypoint.
top_keypoint = keypoint_number(mapdl)
print(f"The number of the keypoint where F is applied: {top_keypoint}")


###############################################################################
# Meshing
# ~~~~~~~
# Define line division of the lines, then mesh the area with shell elements.

# Define mesh properties and create the mesh with shell elements.
def meshing():
    # Specify the default number of line divisions.
    mapdl.esize(size="", ndiv=8)

    # Mesh the area.
    mapdl.amesh(1)

    # Define global cartesian coordinate system.
    mapdl.csys(0)

    if elem_type == "SHELL181":
        # Plot the mesh.
        mapdl.eplot(
            title="Plot of the currently selected elements",
            vtk=True,
            cpos="iso",
            show_edges=True,
            edge_color="white",
            show_node_numbering=True,
            color="purple",
        )

    # Print the list of elements.
    print(mapdl.elist())

    # Plot the nodes using VTK.
    mapdl.nplot(
        vtk=True, nnum=True, background="", cpos="iso", show_bounds=True, point_size=10
    )

    # Print the list of nodes.
    print(mapdl.nlist())


meshing()


###############################################################################
# Define Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application of symmetric boundary conditions for simplified model.

# Select nodes by location and apply BC.
def define_bc():
    # Select nodes by location and apply BC.
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.dsym("SYMM", "X", 0)
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.dsym("SYMM", "Y", 0)
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.dsym("SYMM", "Z", 0)
    mapdl.nsel("ALL")


define_bc()


###############################################################################
# Define Distributed Loads
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Apply the force of :math:`F = (100/4) lb` in the y-direction.

# Define loads.
def define_loads():
    # Parametrization of the :math:`F` load for the quarter of the model.
    force = 100 / 4

    # Application of the load to the model.
    mapdl.fk(top_keypoint, "FY", -force)
    mapdl.finish()


define_loads()


###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system. Print the solver output.


def solve_procedure():
    mapdl.run("/solu")
    out = mapdl.solve()
    mapdl.finish()
    return out


simulation_info = solve_procedure()
print(simulation_info)

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing for the model with elements ``shell181``.
# Plotting nodal displacement.
# Get the the radial displacement at the node where force F is applied.

# Start post-processing mode.
def post_processing():
    mapdl.post1()
    mapdl.set(1)


post_processing()


###############################################################################
# Plotting
# ~~~~~~~~
# Plot nodal displacement using PyVista.


def plot_nodal_disp():
    mapdl.post_processing.plot_nodal_displacement(
        title="Nodal Displacements",
        component="Y",
        cpos="zx",
        scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        show_node_numbering=True,
        show_axes=True,
        show_edges=True,
    )


plot_nodal_disp()


###############################################################################
# Getting the radial displacements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To determine the radial displacement :math:`\delta` at the point
# where F is applied, we can use :meth:`Mapdl.get_value <ansys.mapdl.core.Mapdl.get_value>`.


def get_displacements():
    # Select keypoint by its number ``top_keypoint``.
    mapdl.ksel("S", vmin="top_keypoint")

    # Select the node associated with the selected keypoint.
    mapdl.nslk()

    # Get the number of the selected node by :meth:`Mapdl.get <ansys.mapdl.core.Mapdl.get>`
    top_node = int(mapdl.get("_", "node", 0, "num", "max"))

    # Define radial displacement at the node where F is applied.
    deflect_shell = mapdl.get_value(
        entity="node", entnum=top_node, item1="u", it1num="y"
    )

    return top_node, deflect_shell


# Call the function and get the value of the deflection.
top_node_181, deflect_shell_181 = get_displacements()
print(
    f"Number of the node attached to the top keypoint: {top_node_181},\n"
    f"Radial displacement: {(round(deflect_shell_181, 4))}"
)


###############################################################################
# Rerun Model with SHELL281
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the simulation again using the element type SHELL281.

# Restart pre-processing routine.
start_prep7()
elem_type = define_element(elem_type="SHELL281")
define_material()
define_section()
define_geometry()
meshing()
define_bc()
define_loads()


###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system. Print the solver output.

solve_procedure()


###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing for the model with elements ``shell281``.
# Plotting nodal displacement.
# Get the the radial displacement at the node where force F is applied.

post_processing()
plot_nodal_disp()
top_node_281, deflect_shell_281 = get_displacements()


###############################################################################
# Check Results
# ~~~~~~~~~~~~~
# Now we have the deflections, we can compare them to the expected values
# of radial deflection at the node where force :math:`F` was applied
# for both simulations. The expected value for :math:`\delta_{\mathrm{shell181}}` is 0.1139,
# and :math:`\delta_{\mathrm{shell281}}` is 0.1139.

# Results obtained by hand-calculations.
deflect_target_181 = 0.1139
deflect_target_281 = 0.1139

# Calculate the deviation.
deflect_ratio_shell_181 = abs(deflect_shell_181) / deflect_target_181
deflect_ratio_shell_281 = abs(deflect_shell_281) / deflect_target_281

# Print output results.
output = f"""
----------------------------------------------------------------------------
------------------------- VM3 RESULTS COMPARISON ---------------------------
----------------------------------------------------------------------------
                            |   TARGET   |   Mechanical APDL   |   RATIO   |
----------------------------------------------------------------------------
    Deflection, in SHELL181{deflect_target_181:11.4f} {abs(deflect_shell_181):17.4f} {deflect_ratio_shell_181:15.3f}
    Deflection, in SHELL281{deflect_target_281:11.4f} {abs(deflect_shell_281):17.4f} {deflect_ratio_shell_281:15.3f}
----------------------------------------------------------------------------
"""
print(output)

###############################################################################
# stop mapdl
mapdl.exit()
