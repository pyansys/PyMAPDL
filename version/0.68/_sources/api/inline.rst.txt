.. _inline_functions_api:

Inline functions
================

.. currentmodule:: ansys.mapdl.core.inline_functions

These are wrapped versions of inline APDL functions that perform operations like finding the x-coordinate of a node
given its number (``Query.nx``).

.. autoclass:: ansys.mapdl.core.inline_functions.Query

.. autosummary::
   :toctree: _autosummary/

   Query.node
   Query.kp

   Query.centrx
   Query.centry
   Query.centrz

   Query.kx
   Query.ky
   Query.kz

   Query.nx
   Query.ny
   Query.nz

   Query.ux
   Query.uy
   Query.uz

   Query.rotx
   Query.roty
   Query.rotz

   Query.lx
   Query.ly
   Query.lz

   Query.lsx
   Query.lsy
   Query.lsz

   Query.nsel
   Query.ksel
   Query.lsel
   Query.asel
   Query.esel
   Query.vsel
