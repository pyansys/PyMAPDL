.. _ref_mapdl_api:

Mapdl
=====

Mapdl Class Specific Classes or Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. currentmodule:: ansys.mapdl.core

.. autoclass:: ansys.mapdl.core.mapdl._MapdlCore

.. autosummary::
   :toctree: _autosummary

   Mapdl.add_file_handler
   Mapdl.allow_ignore
   Mapdl.chain_commands
   Mapdl.directory
   Mapdl.get
   Mapdl.get_array
   Mapdl.get_value
   Mapdl.ignore_errors
   Mapdl.jobname
   Mapdl.last_response
   Mapdl.load_table
   Mapdl.mesh
   Mapdl.modal_analysis
   Mapdl.non_interactive
   Mapdl.open_apdl_log
   Mapdl.open_gui
   Mapdl.parameters
   Mapdl.result
   Mapdl.run
   Mapdl.run_multiline
   Mapdl.input_strings
   Mapdl.set_log_level
   Mapdl.version


Latest 2021R1 and newer features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.mapdl.core.mapdl_grpc.MapdlGrpc

.. autosummary::
   :toctree: _autosummary

   mapdl_grpc.MapdlGrpc.download
   mapdl_grpc.MapdlGrpc.list_error_file
   mapdl_grpc.MapdlGrpc.list_files
   mapdl_grpc.MapdlGrpc.math
   mapdl_grpc.MapdlGrpc.mute
   mapdl_grpc.MapdlGrpc.upload


Mapdl Information Class
~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: ansys.mapdl.core.misc

.. autoclass:: ansys.mapdl.core.misc.Information

.. autosummary::
   :toctree: _autosummary

   Information.product
   Information.mapdl_version
   Information.pymapdl_version
   Information.products
   Information.preprocessing_capabilities
   Information.aux_capabilities
   Information.solution_options
   Information.post_capabilities
   Information.title
   Information.titles
   Information.stitles
   Information.units
   Information.scratch_memory_status
   Information.database_status
   Information.config_values
   Information.global_status
   Information.job_information
   Information.model_information
   Information.boundary_condition_information
   Information.routine_information
   Information.solution_options_configuration
   Information.load_step_options
