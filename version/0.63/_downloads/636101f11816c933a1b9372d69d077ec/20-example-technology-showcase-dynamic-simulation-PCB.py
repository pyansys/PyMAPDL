""".. _ref_dynamic_simulation_printed_circuit_board:

Dynamic simulation of a printed circuit board assembly
======================================================

This examples shows how to use PyMAPDL to import an existing FE model and to
run a modal and PSD analysis. PyDPF modules are also used for post-processing.

This example is inspired from the model and analysis defined in Chapter 20 of
the Mechanical APDL Technology Showcase Manual.

Additional Packages Used
------------------------

* `Matplotlib <https://matplotlib.org>`_ is used for plotting purposes.

"""

###############################################################################
# Setting up model
# ----------------
#
# The original FE model is given in the Ansys Mechanical APDL Technology
# Showcase Manual.  The .cdb contains a FE model of a single circuit board. The
# model is meshed with SOLID186, SHELL181 and BEAM188 elements. All components
# of the PCB model is assigned with linear elastic isotropic materials. Bonded
# and flexible surface-to-surface contact pairs are used to define the contact
# between the IC packages and the circuit board.
#
# Starting MAPDL as a service and importing an external model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

import matplotlib.pyplot as plt

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples import download_tech_demo_data

# start MAPDL as a service
mapdl = launch_mapdl()
print(mapdl)

# read model of single circuit board
# download the cdb file
pcb_mesh_file = download_tech_demo_data("td-20", "pcb_mesh_file.cdb")

# enter preprocessor and read in cdb
mapdl.prep7()
mapdl.cdread("COMB", pcb_mesh_file)
mapdl.allsel()
mapdl.eplot(background="w")
mapdl.cmsel("all")

###############################################################################
# Creating the complete layered model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The original model will be duplicated to create a layered PCB of three layers
# that are binded together.

# duplicate single PCB to get three layers
# get the maximum node number for the single layers PCB in the input file
max_nodenum = mapdl.get("max_nodenum", "node", "", "num", "max")

# generate additional PCBs offset by 20 mm in the -y direction
mapdl.egen(3, max_nodenum, "all", dy=-20)


# bind the three layers together
# select components of interest
mapdl.cmsel("s", "N_JOINT_BOARD")
mapdl.cmsel("a", "N_JOINT_LEGS")
mapdl.cmsel("a", "N_BASE")

# get number of currently selected nodes
nb_selected_nodes = mapdl.mesh.n_node
current_node = 0
queries = mapdl.queries

# also select similar nodes for copies of the single PCB
# and couple all dofs at the interface
for node_id in range(1, nb_selected_nodes + 1):
    current_node = queries.ndnext(current_node)
    mapdl.nsel("a", "node", "", current_node + max_nodenum)
    mapdl.nsel("a", "node", "", current_node + 2 * max_nodenum)
mapdl.cpintf("all")

# define fixed support boundary condition
# get max coupled set number
cp_max = mapdl.get("cp_max", "cp", 0, "max")

# unselect nodes scoped in CP equations
mapdl.nsel("u", "cp", "", 1, "cp_max")

# create named selection for base excitation
mapdl.cm("n_base_excite", "node")

# fix displacement for base excitation nodes
mapdl.d("all", "all")

# select all and plot the model using MAPDL's plotter and VTK's
mapdl.allsel("all")
mapdl.cmsel("all")
mapdl.graphics("power")
mapdl.rgb("index", 100, 100, 100, 0)
mapdl.rgb("index", 80, 80, 80, 13)
mapdl.rgb("index", 60, 60, 60, 14)
mapdl.rgb("index", 0, 0, 0, 15)
mapdl.triad("rbot")
mapdl.pnum("type", 1)
mapdl.number(1)
mapdl.hbc(1, "on")
mapdl.pbc("all", "", 1)
mapdl.view(1, 1, 1, 1)
# mapdl.eplot(vtk=False)
mapdl.eplot(vtk=True)

###############################################################################
# Modal Analysis
# --------------
#
# Run modal analysis
# ~~~~~~~~~~~~~~~~~~
#
# A modal analysis is run using Block Lanzos.
# Only 10 modes are extracted for the sake of run times, but using a higher
# number of nodes is recommended (suggestion: 300 modes).
#

# enter solution processor and define analysis settings
mapdl.slashsolu()
mapdl.antype("modal")
# set number of modes to extract
# using a higher number of modes is recommended
nb_modes = 10
# use Block Lanzos to extract specified number of modes
mapdl.modopt("lanb", nb_modes)
mapdl.mxpand(nb_modes)
output = mapdl.solve()
print(output)


###############################################################################
# Post-processing the modal results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This sections illustrates different methods to post-process the results of the
# modal analysis : PyMAPDL method, PyMAPDL result reader, PyDPF-Post
# and PyDPF-Core. All methods lead to the same result and are just given as an
# example of how each module can be used.

# using MAPDL methods
mapdl.post1()
mapdl.set(1, 1)
mapdl.plnsol("u", "sum")


###############################################################################
# Using PyMAPDL result reader
# ***************************
#
# *Not recommended* - PyMAPDL reader library is in process to being deprecated.
# It is recommended to use `DPF Post <https://postdocs.pyansys.com/>`_.
#

mapdl_result = mapdl.result
mapdl_result.plot_nodal_displacement(0)

###############################################################################
# Using DPF-Post
# **************
#

from ansys.dpf import post

solution_path = mapdl.result_file
solution = post.load_solution(solution_path)
print(solution)
displacement = solution.displacement(time_scoping=1)
total_deformation = displacement.norm
total_deformation.plot_contour(show_edges=True, background="w")

###############################################################################
# Using DPF-Core
# **************
#

from ansys.dpf import core

model = core.Model(solution_path)
results = model.results
print(results)
displacements = results.displacement()
total_def = core.operators.math.norm_fc(displacements)
total_def_container = total_def.outputs.fields_container()
mesh = model.metadata.meshed_region
mesh.plot(total_def_container.get_field_by_time_id(1))

###############################################################################
# Run PSD analysis
# ----------------
# The response spectrum analysis is defined, solved and post-processed.

# define PSD analysis with input spectrum
mapdl.slashsolu()
mapdl.antype("spectr")

# power spectral density
mapdl.spopt("psd")

# use input table 1 with acceleration spectrum in terms of acceleration due to gravity
mapdl.psdunit(1, "accg", 9.81 * 1000)

# define the frequency points in the input table 1
mapdl.psdfrq(1, "", 1, 40, 50, 70.71678, 100, 700, 900)

# define the PSD values in the input table 1
mapdl.psdval(1, 0.01, 0.01, 0.1, 1, 10, 10, 1)

# set the damping ratio as 5%
mapdl.dmprat(0.05)

# apply base excitation on the set of nodes N_BASE_EXCITE in the y-direction from table 1
mapdl.d("N_BASE_EXCITE", "uy", 1)

# calculate the participation factor for PSD with base excitation from input table 1
mapdl.pfact(1, "base")

# write the displacent solution relative to the base excitation to the results file from the PSD analysis
mapdl.psdres("disp", "rel")

# write the absolute velocity solution to the results file from the PSD analysis
mapdl.psdres("velo", "abs")

# write the absolute acceleration solution to the results file from the PSD analysis
mapdl.psdres("acel", "abs")

# combine only those modes whose significance level exceeds 0.0001
mapdl.psdcom()
output = mapdl.solve()
print(output)

###############################################################################
# Post-process PSD analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# The response spectrum analysis is post-processed. First, the standard
# MAPDL POST1 postprocessor is used. Then, the MAPDL time-history
# POST26 postprocessor is used to generate the response power spectral
# density.
#
# .. note::
#    The graph generated through POST26 is exported as a picture in the working
#    directory. Finally, the results from POST26 are saved to Python variables
#    to be plotted in the Python environment with the use of Matplotlib
#    library.


###############################################################################
# Post-process PSD analysis in POST1
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mapdl.post1()
mapdl.set(1, 1)
mapdl.plnsol("u", "sum")
mapdl.set("last")
mapdl.plnsol("u", "sum")

###############################################################################
# Post-process PSD analysis in POST26 (time-history post-processing)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mapdl.post26()

# allow storage for 200 variables
mapdl.numvar(200)
mapdl.cmsel("s", "MY_MONITOR")
monitored_node = mapdl.queries.ndnext(0)
mapdl.store("psd")

# store the psd analysis u_y data for the node MYMONITOR as the reference no 2
mapdl.nsol(2, monitored_node, "u", "y")

# compute the response power spectral density for displacement associated with variable 2
mapdl.rpsd(3, 2)
mapdl.show("png")

# plot the variable 3
mapdl.plvar(3)

# print the variable 3
mapdl.prvar(3)

# x-axis is set for Log X scale
mapdl.gropt("logx", 1)

# y-axis is set for Log X scale
mapdl.gropt("logy", 1)

# plot the variable 3
mapdl.plvar(3)
mapdl.show("close")

###############################################################################
# Post-process PSD analysis using Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# store MAPDL results to python variables
mapdl.dim("frequencies", "array", 4000, 1)
mapdl.dim("response", "array", 4000, 1)
mapdl.vget("frequencies(1)", 1)
mapdl.vget("response(1)", 3)
frequencies = mapdl.parameters["frequencies"]
response = mapdl.parameters["response"]

# use Matplotlib to create graph
fig = plt.figure()
ax = fig.add_subplot(111)
plt.xscale("log")
plt.yscale("log")
ax.plot(frequencies, response)
ax.set_xlabel("Frequencies")
ax.set_ylabel("Response power spectral density")

###############################################################################
# Exit MAPDL
mapdl.exit()
