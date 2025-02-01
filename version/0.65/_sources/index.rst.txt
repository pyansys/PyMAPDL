PyMAPDL documentation |version|
===============================

.. toctree::
   :hidden:
   :maxdepth: 3

   getting_started/index
   user_guide/index
   mapdl_commands/index
   api/index
   examples/index



Introduction and purpose
------------------------
PyMAPDL is part of the larger `PyAnsys <pyansys_>`_
effort to facilitate the use of Ansys technologies directly from
Python. Its primary package, ``ansys-mapdl-core``, provides:

- Scripting of MAPDL through both Python and Ansys Parametric Design
  Language (APDL) syntax.
- Plotting of MAPDL geometry and meshes using `PyVista
  <pyvista_docs_>`_ from within a Python script or an
  interactive `Jupyter notebook <jupyter_>`_.
- Access to MAPDL arrays as Python objects (for example, nodes, elements,
  solution matrices, and results).

Thanks to an API that looks familiar to APDL and Python users alike, PyMAPDL
makes it is easier than ever to integrate the simulation capabilities 
of the Ansys MAPDL multi-physics solver directly into novel applications.
The package presents a Python-friendly interface to drive the software
that manages the submission of low-level APDL commands, while exchanging
data through high-performance gRPC interfaces.

Accelerate the preparation of your simulations using PyMAPDL. Combine the
expressiveness of general-purpose Python code to control the flow in your
input decks with methods that drive the solver. Explore proof of concept 
studies or capture knowledge using interactive Jupyter notebooks. Tap
the solver as the physics engine in your next AI app. PyMAPDL is now open source,
so enjoy it. Contributions are welcome.


Background
----------
PyMAPDL, based on `gRPC <grpc_>`_, represents an
improvement over its predecessor based on CORBA. These technologies
allow the MAPDL solver to function as a server, ready to respond to
connecting clients.

Google remote procedure calls, or gRPC, are used to establish secure 
connections so that a client app can directly call methods on 
a potentially remote MAPDL instance as if it were a local object. The 
use of HTTP/2 makes it friendly to modern internet infrastructures. 
This, along with the use of binary transmission formats, favors higher
performance. Using gRPC, PyMAPDL can convert Python statements into APDL 
commands that can then be transmitted to an MAPDL instance running anywhere, 
while producing network footprints that are compact and efficient.

The following diagram presents a simplified architecture of PyMAPDL.

.. figure:: ./images/architecture_diagram.png
    :width: 400pt

    PyMAPDL architecture diagram

Quick code
----------
Here's a brief example of how PyMAPDL works:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()
    >>> print(mapdl)

    Product:             ANSYS Mechanical Enterprise
    MAPDL Version:       RELEASE  2021 R1           BUILD 21.0
    PyMAPDL Version:     Version: 0.57.0

MAPDL is now active and you can send commands to it as a genuine
Python class. For example, if you wanted to create a surface using
key points, you could run:

.. code:: python

    mapdl.run("/PREP7")
    mapdl.run("K, 1, 0, 0, 0")
    mapdl.run("K, 2, 1, 0, 0")
    mapdl.run("K, 3, 1, 1, 0")
    mapdl.run("K, 4, 0, 1, 0")
    mapdl.run("L, 1, 2")
    mapdl.run("L, 2, 3")
    mapdl.run("L, 3, 4")
    mapdl.run("L, 4, 1")
    mapdl.run("AL, 1, 2, 3, 4")

MAPDL interactively returns the result of each command, which is
stored to the logging module. The ``print(mapdl.run)`` method can
also be used to immediately print out the result. Errors are caught
immediately and Pythonically.

Calling MAPDL Pythonically
~~~~~~~~~~~~~~~~~~~~~~~~~~
MAPDL functions can be called directly from a :class:`Mapdl
<ansys.mapdl.core.mapdl._MapdlCore>` instance in a Pythonic manner. This is to
simplify calling MAPDL, especially when inputs are variables within
Python. For example, the following two commands are equivalent:

.. code:: python

    mapdl.k(1, 0, 0, 0)
    mapdl.run("K, 1, 0, 0, 0")

This approach takes care of the string formatting for you. For
example, inputting points from a numpy array:

.. code:: python

   # make 10 random keypoints in MAPDL
   points = np.random.random((10, 3))
   for i, (x, y, z) in enumerate(points):
       mapdl.k(i + 1, x, y, z)


Advanced features
~~~~~~~~~~~~~~~~~
All features available to command line MAPDL can be used within
PyMAPDL, and there are a variety of new features available through
gRPC.

For example, view the current mesh status with:

.. code:: pycon

   >>> mapdl.mesh
    ANSYS Mesh
      Number of Nodes:              7217
      Number of Elements:           2080
      Number of Element Types:      2
      Number of Node Components:    0
      Number of Element Components: 0

Or save it as a VTK file with:

.. code:: pycon

    >>> mapdl.mesh.save("mymesh.vtk")

You can even plot directly from the Python environment with:

.. code:: pycon

    >>> mapdl.et(1, "SOLID186")
    >>> mapdl.vsweep("ALL")
    >>> mapdl.esize(0.1)
    >>> mapdl.eplot()

.. figure:: ./images/eplot_vtk.png
    :width: 400pt

    Element plot from MAPDL using ``PyMAPDL`` and ``vtk``

For a full listing of PyMAPDL features, see the
:ref:`ref_user_guide`.


Project index
*************

* :ref:`genindex`
