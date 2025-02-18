Mesh and Geometry
=================
The :class:`Mapdl <ansys.mapdl.core.Mapdl>` class allows you to access
the mesh and geometry without writing to an intermediate file or
interpreting the text output from various MAPDL commands.  For
example, to access the nodes and elements of a model, normally one
would list the nodes within MAPDL :func:`Mapdl.nlist()
<ansys.mapdl.core.Mapdl.nlist`, but this generates a string and array
access either requires cumbersome MAPDL GET commands, or requires the
nodes be written to a archive file and then read in within other
software.  For example:

.. code::

    NLIST

 LIST ALL SELECTED NODES.   DSYS=      0

    NODE        X             Y             Z           THXY     THYZ     THZX
        1   0.0000        0.0000        0.0000          0.00     0.00     0.00
        2   1.0000        0.0000        0.0000          0.00     0.00     0.00
        3   0.2500        0.0000        0.0000          0.00     0.00     0.00


However, with :class:`Mapdl.mesh <ansys.mapdl.core.mesh_grpc.Mesh>`
possible to interface with a current instance of :class:`Mapdl
<ansys.mapdl.core.Mapdl>` and access the current nodes coordinates
with:

.. code:: python

   >>> mapdl.mesh.nodes
   [[0.   0.   0.  ]
    [1.   0.   0.  ]
    [0.25 0.   0.  ]
    ...,
    [0.75 0.5  3.5 ]
    [0.75 0.5  4.  ]
    [0.75 0.5  4.5 ]]


Both the :attr:`Mapdl.geometry <ansys.mapdl.core.Mapdl.geometry` and
:attr:`Mapdl.mesh <ansys.mapdl.core.Mapdl.mesh` attributes support
additional, lower level access to MAPDL data.  Access them with:

.. code:: python

    >>> mapdl.mesh
    >>> mapdl.geometry

View the current mesh status with:

.. code::

   >>> mapdl.mesh
    ANSYS Mesh
      Number of Nodes:              7217
      Number of Elements:           2080
      Number of Element Types:      2
      Number of Node Components:    0
      Number of Element Components: 0


Geometry Commands
~~~~~~~~~~~~~~~~~
See the :ref:`ref_prep_commands` commands for additional MAPDL
commands for creating geometries.


API Reference
~~~~~~~~~~~~~
For a full description of the ``Mesh`` and ``Geometry`` classes, please
see :ref:`ref_mesh_api` and :ref:`ref_geometry_api`.
