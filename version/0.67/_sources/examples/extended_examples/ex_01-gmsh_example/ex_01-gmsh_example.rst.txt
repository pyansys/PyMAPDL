.. _extended_example01:


Gmsh example
============

Objective
---------
This example demonstrate the interoperability of PyAnsys with Gmsh, a very well known
open source Python meshing library. For more information, visit the Gmsh website: `Gmsh <gmsh_>`_.

Description
-----------
Gmsh is used to import an external geometry file in STL format. The `pymapdl-reader <legacy_reader_docs_>`_ library
is then used to import the geometry into PyMAPDL. 

This example makes use of these files: 

* ``gmsh_converter.py``: Loads a STEP file, meshes it, and saves it as a Gmsh file. 
* ``mesh_converter``: Converts the MSH file into an Ansys CDB database format file (archive file). 
* ``modal_analysis.py``: Imports the CDB database, sets up the modal analysis, and runs
  it. It also shows an animation of the first mode and saves it
  to a GIF file named ``animation.gif``. 


Requirements
------------
You must have Gmsh installed. You can install it using ``pip``:

.. code-block:: console

    pip install gmsh


Source code
-----------

``gmsh_generator.py`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: gmsh_generator.py
    :linenos:
    :language: python


``mesh_converter.py`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: mesh_converter.py
    :linenos:
    :language: python


``modal_analysis.py`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: modal_analysis.py
    :linenos:
    :language: python



Notes
-----

You should copy all the files in a separate directory to make running
the example easier. 
