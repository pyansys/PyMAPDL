.. _ref_user_guide:

==========
User guide
==========
This section provides a general overview of PyMAPDL and how you use it.


..
   This toctreemust be a top level index to get it to show up in
   pydata_sphinx_theme

.. toctree::
   :maxdepth: 1
   :hidden:

   launcher
   mapdl
   mapdl_examples
   plotting
   mesh_geometry
   post
   parameters
   database
   convert
   math
   pool
   xpl
   upf
   krylov
   troubleshoot


PyMAPDL overview
================
The :func:`launch_mapdl() <ansys.mapdl.core.launch_mapdl>` function
within the ``ansys-mapdl-core`` library creates an instance of the
:class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class in the background and sends
commands to that service. Errors and warnings are processed
Pythonically, letting you develop a script in real time, without
worrying about it functioning correctly when deployed in batch
mode.

MAPDL can be started from Python in gRPC mode using the
:func:`launch_mapdl() <ansys.mapdl.core.launch_mapdl>` method. This starts
MAPDL in a temporary directory by default. You can change this to
your current directory with:

.. code:: python

    import os
    from ansys.mapdl.core import launch_mapdl

    path = os.getcwd()
    mapdl = launch_mapdl(run_location=path)

MAPDL is now active, and you can send commands to it as a genuine a
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
stored to the logging module. Errors are caught immediately. For
example, if you input an invalid command:

.. code:: pycon

   >>> mapdl.run("AL, 1, 2, 3")

   apdlRuntimeError: 
   L, 1, 2, 3

   EFINE AREA BY LIST OF LINES
   INE LIST =     1    2    3
   TRAVERSED IN SAME DIRECTION AS LINE     1)

   ** ERROR ***                           CP =       0.338   TIME= 09:45:36
   eypoint 1 is referenced by only one line.  Improperly connected line   
   et for AL command.                                                     

This ``MapdlRuntimeError`` was caught immediately. This means that
you can write your MAPDL scripts in Python, run them interactively, and
then run them as a batch without worrying if the script would run correctly if
you had instead outputted it to a script file.

The :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class supports much more
than just sending text to MAPDL. It includes higher-level wrapping,
allowing for better scripting and interaction with MAPDL. For an overview of the
various advanced methods to visualize, script, and interact with MAPDL, see
:ref:`ref_examples`.


Calling MAPDL Pythonically
~~~~~~~~~~~~~~~~~~~~~~~~~~
MAPDL functions can be called directly from an instance of
:class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` in a Pythonic manner. This is
to simplify calling Ansys, especially when inputs are variables within
Python. For example, the following two commands are equivalent:

.. code:: python

    mapdl.k(1, 0, 0, 0)
    mapdl.run("K, 1, 0, 0, 0")

This approach has some obvious advantages. Chiefly, it's easier
to script because ``ansys-mapdl-core`` takes care of the string formatting for you.
For example, you can input points from a numpy array with:

.. code:: python

   # make 10 random keypoints in Ansys
   points = np.random.random((10, 3))
   for i, (x, y, z) in enumerate(points):
       mapdl.k(i + 1, x, y, z)

Additionally, exceptions are caught and handled within Python.

.. code:: pycon

   >>> mapdl.run("AL, 1, 2, 3")

   xception: 
   L, 1, 2, 3

   EFINE AREA BY LIST OF LINES
   INE LIST =     1    2    3
   TRAVERSED IN SAME DIRECTION AS LINE     1)

   ** ERROR ***                           CP =       0.338   TIME= 09:45:36
   eypoint 1 is referenced by only one line.  Improperly connected line   
   et for AL command.                                                     


For longer scripts, instead of sending commands to MAPDL as in the
area creation example, you can instead run:

.. code:: python

    # clear existing geometry
    mapdl.finish()
    mapdl.clear()

    # create a square area using keypoints
    mapdl.prep7()
    mapdl.k(1, 0, 0, 0)
    mapdl.k(2, 1, 0, 0)
    mapdl.k(3, 1, 1, 0)
    mapdl.k(4, 0, 1, 0)
    mapdl.l(1, 2)
    mapdl.l(2, 3)
    mapdl.l(3, 4)
    mapdl.l(4, 1)
    mapdl.al(1, 2, 3, 4)

This approach has some obvious advantages, chiefly that it's a bit
easier to script as :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`
takes care of the string formatting for you. For example, inputting
points from a numpy array:

.. code:: python

   import numpy as np

   # make 10 random keypoints in MAPDL
   points = np.random.random((10, 3))
   for i, (x, y, z) in enumerate(points):
       mapdl.k(i + 1, x, y, z)

Additionally, each function with the MAPDL class has help associated
with it. For example:

.. code:: pycon

    >>> help(mapdl.k)

    Help on method K in module ansys.mapdl.core.mapdl_grpc.MapdlGrpc:

    k(npt='', x='', y='', z='') method of ansys.mapdl.core.mapdl_grpc.MapdlGrpc
    instance

        Defines a keypoint.

        APDL Command: K

        Parameters
        ----------
        npt
            Reference number for keypoint. If zero, the lowest
            available number is assigned [NUMSTR].

        x, y, z
            Keypoint location in the active coordinate system (may be
            R, θ, Z or R, θ, Φ). If X = P, graphical picking is
            enabled and all other fields (including NPT) are ignored
            (valid only in the GUI).

        Examples
        --------
        Create a keypoint at (1, 1, 2)

    >>> mapdl.k(1, 1, 1, 2)

        Notes
        -----
        Defines a keypoint in the active coordinate system [CSYS] for
        line, area, and volume descriptions. A previously defined
        keypoint of the same number is then redefined. A keypoint may
        be redefined only if it is not yet attached to a line or is
        not yet meshed. Solid modeling in a toroidal system is not
        recommended.


For stability considerations, see :ref:`ref_pymapdl_stability`.
