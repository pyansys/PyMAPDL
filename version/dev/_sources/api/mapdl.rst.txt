.. _ref_mapdl_api:

``Mapdl`` module
================

``Mapdl`` methods and attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: ansys.mapdl.core

.. autoclass:: ansys.mapdl.core.mapdl.MapdlBase

.. autosummary::
   :toctree: _autosummary

   Mapdl.add_file_handler
   Mapdl.allow_ignore
   Mapdl.busy
   Mapdl.chain_commands
   Mapdl.check_parameter_names
   Mapdl.default_file_type_for_plots
   Mapdl.directory
   Mapdl.exited
   Mapdl.exiting
   Mapdl.file_type_for_plots
   Mapdl.finish_job_on_exit
   Mapdl.force_output
   Mapdl.get
   Mapdl.get_array
   Mapdl.get_esol
   Mapdl.get_nodal_constrains
   Mapdl.get_nodal_loads
   Mapdl.get_nsol
   Mapdl.get_value
   Mapdl.get_variable
   Mapdl.hostname
   Mapdl.ignore_errors
   Mapdl.info
   Mapdl.input_strings
   Mapdl.is_alive
   Mapdl.is_console
   Mapdl.is_corba
   Mapdl.is_grpc
   Mapdl.jobid
   Mapdl.jobname
   Mapdl.kill_job
   Mapdl.last_response
   Mapdl.launched
   Mapdl.list_error_file
   Mapdl.list_files
   Mapdl.load_array
   Mapdl.load_table
   Mapdl.locked
   Mapdl.logger
   Mapdl.mapdl_on_hpc
   Mapdl.mute
   Mapdl.name
   Mapdl.non_interactive
   Mapdl.on_docker
   Mapdl.open_apdl_log
   Mapdl.open_gui
   Mapdl.platform
   Mapdl.print_com
   Mapdl.process_is_alive
   Mapdl.remove_file_handler
   Mapdl.remove_temp_dir_on_exit
   Mapdl.result
   Mapdl.result_file
   Mapdl.run
   Mapdl.run_as_routine
   Mapdl.run_multiline
   Mapdl.save_selection
   Mapdl.scalar_param
   Mapdl.screenshot
   Mapdl.set_log_level
   Mapdl.thermal_result
   Mapdl.use_vtk
   Mapdl.version


Constants
~~~~~~~~~
.. autosummary::
   :toctree: _autosummary

   plotting.ALLOWED_TARGETS
   plotting.BCS


``mapdl_grpc.MapdlGrpc`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.mapdl.core.mapdl_grpc.MapdlGrpc

.. autosummary::
   :toctree: _autosummary

   mapdl_grpc.MapdlGrpc.channel_state
   mapdl_grpc.MapdlGrpc.check_status
   mapdl_grpc.MapdlGrpc.connection
   mapdl_grpc.MapdlGrpc.download
   mapdl_grpc.MapdlGrpc.download_project
   mapdl_grpc.MapdlGrpc.download_result
   mapdl_grpc.MapdlGrpc.file
   mapdl_grpc.MapdlGrpc.ip
   mapdl_grpc.MapdlGrpc.is_local
   mapdl_grpc.MapdlGrpc.list_error_file
   mapdl_grpc.MapdlGrpc.list_files
   mapdl_grpc.MapdlGrpc.mute
   mapdl_grpc.MapdlGrpc.port
   mapdl_grpc.MapdlGrpc.upload

