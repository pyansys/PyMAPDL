.. _ref_macro_files_commands_api:

***********
Macro files
***********

.. currentmodule:: ansys.mapdl.core

These APDL commands are used to build and execute command macros.

.. note::
   Most of the commands here should be replaced with Python
   alternatives. For example, instead of using macros, use Python
   functions. Instead of ``/MKDIR`` use ``os.mkdir``.

.. warning::
   Many of the commands here must be run in ``mapdl.non_interactive``

.. autosummary::
   :toctree: _autosummary/

   Mapdl.cfclos
   Mapdl.cfopen
   Mapdl.cfwrite
   Mapdl.create
   Mapdl.dflab
   Mapdl.end
   Mapdl.mkdir
   Mapdl.msg
   Mapdl.pmacro
   Mapdl.psearch
   Mapdl.rmdir
   Mapdl.tee
   Mapdl.ulib
   Mapdl.use
