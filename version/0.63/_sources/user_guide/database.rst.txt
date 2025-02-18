Accessing MAPDL Database
========================

.. warning:: This feature is still in beta. Please report any errors or suggestions to pyansys.support@ansys.com.


From PyMAPDL v0.61.2, you can access elements and nodes data from the MAPDL database using the DB module.


Usage
~~~~~

Getting the elems and nodes objects:

.. code:: py

    >>> from ansys.mapdl.core import launch_mapdl
    >>> from ansys.mapdl.core.examples import vmfiles
    
    >>> mapdl = launch_mapdl()
    >>> mapdl.input(vmfiles['vm271']

    >>> elems = mapdl.db.elems
    >>> elems
    MAPDL Database Elements
        Number of elements:          3459
        Number of selected elements: 3459
        Maximum element number:      3459

    >>> nodes = mapdl.db.nodes
    MAPDL Database Nodes
        Number of nodes:          3652
        Number of selected nodes: 3652
        Maximum node number:      3652

To obtain the first element:

.. code:: py
    
    >>> elems = mapdl.db.elems
    >>> elems.first()
    1


Check if the element is selected or not:

.. code:: py

    >>> from ansys.mapdl.core.database import DBDef
    >>> elems.info(1, DBDef.DB_SELECTED)

Return the element information of element 1.

.. code:: py

    >>> elems = mapdl.db.elems
    >>> elem_info = elems.get(1)
    >>> elem_info
    ielem: 1
    elmdat: 1
    elmdat: 1
    elmdat: 1
    elmdat: 1
    elmdat: 0
    elmdat: 0
    elmdat: 12
    elmdat: 0
    elmdat: 0
    elmdat: 0
    nnod: 2
    nodes: 1
    nodes: 3

Return the nodes belonging to the element.

.. code:: py

    >>> elem_info.nodes
    [1, 3]

Return the element data.

.. code:: py

    >>> elem_info.elmdat
    [1, 1, 1, 1, 0, 0, 12, 0, 0, 0]

Return the selection status and the coordinates of node 22.

.. code:: py

    >>> nodes = mapdl.db.nodes
    >>> sel, coord = nodes.coord(22)
    >>> coord
    (-0.0014423144202849985, 0.010955465718673852, 0.0, 0.0, 0.0, 0.0)

.. note:: The coordenates returned by the method ``coord`` contains the following: X, Y, Z, THXY, THYZ, and THZX.


Requirements
~~~~~~~~~~~~

To use ``DB`` feature, you need to meet the following requirements:

* ``ansys.api.mapdl`` package version should be 0.5.1 or higher.
* ANSYS MAPDL version should be 2021R1 or newer.

.. warning:: This feature does not work in the latest Ansys 2023R1.




