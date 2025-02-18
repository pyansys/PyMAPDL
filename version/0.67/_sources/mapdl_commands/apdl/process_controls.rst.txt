.. _ref_process_controls_api:

****************
Process controls
****************

.. currentmodule:: ansys.mapdl.core

These APDL commands can be used to control the order in which other
commands are processed.

.. note::
   The following commands are not directly mapped to PyMAPDL.  Use
   `non-interactive` if you must use these commands, but ideally they
   should be replaced by Python statements.

   * ``*CYCLE``
   * ``*DO``
   * ``*DOWHILE``
   * ``*ELSE``
   * ``*ELSEIF``
   * ``*ENDDO``
   * ``*ENDIF``
   * ``*EXIT``
   * ``*GO``
   * ``*IF``
   * ``*REPEAT``
   * ``*RETURN``


.. autosummary::
   :toctree: _autosummary/

   Mapdl.wait
