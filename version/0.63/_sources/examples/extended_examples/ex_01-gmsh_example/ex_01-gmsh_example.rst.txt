.. _extended_example01:


Gmsh Example
============

Objective
---------
Demonstrate the interoperability of PyAnsys with ``gmsh``, a very well known
open source Python meshing library.

For more information about ``gmsh`` please visit its website: `Gmsh <https://gmsh.info/>`_.

Description
-----------
In this example the interoperability of PyAnsys with the open source mesher ``gmsh`` is demonstrated.
Using ``gmsh`` we import an external geometry file in STL format and then the 
geometry is imported into PyMAPDL using the 
`pymapdl-reader <https://github.com/pyansys/pymapdl-reader>`_ library.

This example is composed of several files. 

* ``gmsh_converter.py``: Load a STEP file, mesh it, and save it as a gmsh file. 
* ``mesh_converter``: Convert the ``*.msh`` file into an Ansys CDB database format file (archive file). 
* ``modal_analysis.py``: Import CDB database, setup the modal analysis and run
  it. It also shows an animation of the first mode and save it
  to a gif file named ``animation.gif``. 


Requirements
------------
You need to have ``gmsh`` installed. You can install it using ``pip``:

.. code-block:: 

    pip install gmsh


Source code
-----------

``gmsh_generator.py``
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: gmsh_generator.py
    :linenos:
    :language: python


``mesh_converter.py``
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: mesh_converter.py
    :linenos:
    :language: python


``modal_analysis.py``
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: modal_analysis.py
    :linenos:
    :language: python



Notes
-----

It is recommended that you copy all the files in a separate directory to make it
easier to run the example. 
