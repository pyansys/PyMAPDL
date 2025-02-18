.. _ref_mapdl_commands:

==============
MAPDL commands
==============
This section gives an overview of the classic MAPDL commands that have
been wrapped pythonically via PyMAPDL. Most commands have been
wrapped, but there are a few commands that are not supported natively
or only have partial support within PyMAPDL.  See
:ref:`ref_unsupported_commands` for more details.

*******
Session
*******
These commands provide general control to the session. The commands
are grouped by capability.

.. toctree::
   :maxdepth: 1

   session/run_controls
   session/processor_entry
   session/files
   session/list_controls


********
Database
********
These commands are used to operate on the database globally.

.. toctree::
   :maxdepth: 1

   database/setup
   database/selecting
   database/components
   database/working_plane
   database/coord_sys
   database/picking

********
Graphics
********
These commands are used to control the graphics of the program.

.. toctree::
   :maxdepth: 1

   graphics/setup
   graphics/views
   graphics/scaling
   graphics/style
   graphics/labeling
   graphics/graphs
   graphics/annotation


****
APDL
****
These commands make up the ANSYS Parametric Design Language
(APDL).

.. toctree::
   :maxdepth: 1

   apdl/parameter_definition
   apdl/macro_files
   apdl/abbreviations
   apdl/array_parm
   apdl/matrix_op
   apdl/process_controls

.. _ref_prep_commands:

*************
Preprocessing
*************

These commands are used to create and set up the model.


.. toctree::
   :maxdepth: 1

   prep7/database
   prep7/element_type
   prep7/real_constants
   prep7/materials
   prep7/material_data_tables
   prep7/primitives
   prep7/keypoints
   prep7/hard_points
   prep7/lines
   prep7/areas
   prep7/volumes
   prep7/booleans
   prep7/meshing
   prep7/nodes
   prep7/elements
   prep7/superelements
   prep7/digitizing
   prep7/coupled_dof
   prep7/constraint_equations
   prep7/status
   prep7/explicit_dynamics
   prep7/sections
   prep7/morphing
   prep7/artificially_matched_layers
   prep7/special_purpose


********
Solution
********
These commands are used to load and solve the model.

.. toctree::
   :maxdepth: 1

   solution/analysis_options
   solution/nonlinear_options
   solution/dynamic_options
   solution/spectrum_options
   solution/load_step_options
   solution/solid_constraints
   solution/solid_forces
   solution/solid_surface_loads
   solution/solid_body_loads
   solution/inertia
   solution/miscellaneous_loads
   solution/load_step_operations
   solution/master_dof
   solution/gap_conditions
   solution/rezoning
   solution/2d_to_3d_analysis
   solution/birth_and_death
   solution/fe_constraints
   solution/fe_forces
   solution/fe_surface_loads
   solution/fe_body_loads
   solution/ocean
   solution/solution_status
   solution/radiosity
   solution/multi_field_solver_definition_commands
   solution/multi_field_solver_global_controls
   solution/multi_field_solver_time_controls
   solution/multi_field_solver_load_transfer
   solution/multi_field_solver_convergence_controls
   solution/multi_field_solver_interface_mapping
   
*****
POST1
*****
These commands are used to postprocess the results with the database
processor.

.. toctree::
   :maxdepth: 1

   post1/setup
   post1/controls
   post1/results
   post1/element_table
   post1/listing
   post1/animation
   post1/path_operations
   post1/surface_operations
   post1/load_case
   post1/magnetics_calc
   post1/trace_points
   post1/special
   post1/status
   post1/failure_criteria

******
POST26
******
These commands are used to postprocess the results with the
time-history processor.

.. toctree::
   :maxdepth: 1

   post26/setup
   post26/controls
   post26/operations
   post26/display
   post26/listing
   post26/special
   post26/status


****
AUX2
****
These commands are used to examine or manipulate the contents of
binary files produced by the program.

.. toctree::
   :maxdepth: 1

   aux2/bin_dump
   aux2/bin_manip


****
AUX3
****
The auxiliary processor ``/AUX3`` allows you to operate on results
files by deleting sets or by changing values.

.. toctree::
   :maxdepth: 1

   aux3


*****
AUX12
*****
These commands are used to define radiation options for use in thermal
analyses.

.. toctree::
   :maxdepth: 1

   aux12/general_radiation
   aux12/radiation_mat
   aux12/radiosity_solver


*****
AUX15
*****
These commands are used to read in an IGES file for analysis in ANSYS.

.. toctree::
   :maxdepth: 1

   aux15


*****************
Mapping processor
*****************
The ``/MAP`` processor allows you to map data from an external file
onto the existing geometry.

.. toctree::
   :maxdepth: 1

   map


***************
DISPLAY program
***************
These commands are used for the DISPLAY program. The DISPLAY program
is a companion program to ANSYS, used for recovering graphics displays
produced within ANSYS.

.. note::
   Many of these commands are not applicable when using PyMAPDL.

.. toctree::
   :maxdepth: 1

   display/setup


**********************
REDUCED order modeling
**********************
These commands are used for the DISPLAY program. The DISPLAY program
is a companion program to ANSYS, used for recovering graphics displays
produced within ANSYS.

.. toctree::
   :maxdepth: 1

   reduced/setup
   reduced/preparation
   reduced/generation
   reduced/use_pass

*******************
Connection commands
*******************

These commands read in external CAD files into MAPDL.

.. toctree::
   :maxdepth: 1

   conn


**********************
Miscellaneous commands
**********************

Undocumented miscellaneous commands.

.. toctree::
   :maxdepth: 1

   misc



*****************************
Undocumented inquire commands
*****************************

Undocumented inquire commands.

.. warning:: **DISCLAIMER**: This function is un-documented in the official ANSYS Command Reference Guide.
                   Hence its support is limited and it use is not encouraged.
                   **Please use it with caution.**


.. toctree::
   :maxdepth: 1

   inqfun


