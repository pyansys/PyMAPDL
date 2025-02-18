Mesh and geometry
=================
The :class:`Mapdl <ansys.mapdl.core.Mapdl>` class allows you to access
the mesh and geometry without writing to an intermediate file or
interpreting the text output from various MAPDL commands. For
example, to access the nodes and elements of a model, normally you
would list the nodes within MAPDL using the :func:`Mapdl.nlist()
<ansys.mapdl.core.Mapdl.nlist` method. However, this generates a string.
Array access requires either cumbersome MAPDL GET commands or that the
nodes be written to an archive file and then read in with other
software:

.. code:: output

    NLIST

    LIST ALL SELECTED NODES.   DSYS=      0

    NODE        X             Y             Z           THXY     THYZ     THZX
        1   0.0000        0.0000        0.0000          0.00     0.00     0.00
        2   1.0000        0.0000        0.0000          0.00     0.00     0.00
        3   0.2500        0.0000        0.0000          0.00     0.00     0.00


However, with the :class:`Mapdl.mesh <ansys.mapdl.core.mesh_grpc.Mesh>` class,
you can interface with a current instance of the 
:class:`Mapdl <ansys.mapdl.core.Mapdl>` class and access the current nodes coordinates
with this code:

.. code:: pycon

   >>> mapdl.mesh.nodes
   [[0.0, 0.0, 0.0],
     [1.0, 0.0, 0.0],
     [0.25, 0.0, 0.0],
     [0.75, 0.5, 3.5],
     [0.75, 0.5, 4.0],
     [0.75, 0.5, 4.5]]


Both the :attr:`Mapdl.geometry <ansys.mapdl.core.Mapdl.geometry>` and
:attr:`Mapdl.mesh <ansys.mapdl.core.Mapdl.mesh>` attributes support
additional, lower-level access to MAPDL data. You can use this code
to access them:

.. code:: pycon

    >>> mapdl.mesh
    >>> mapdl.geometry

To view the current mesh status, you can use this code:

.. code:: pycon

   >>> mapdl.mesh
    ANSYS Mesh
      Number of Nodes:              7217
      Number of Elements:           2080
      Number of Element Types:      2
      Number of Node Components:    0
      Number of Element Components: 0


Geometry commands
~~~~~~~~~~~~~~~~~
For additional MAPDLcommands for creating geometries, see the
:ref:`ref_prep_commands` commands.


API reference
~~~~~~~~~~~~~
For a full description of the ``Mesh`` and ``Geometry`` classes,
see :ref:`ref_mesh_api` and :ref:`ref_geometry_api`.
