.. _ref_building_example:


===================
Building an example
===================

.. currentmodule:: ansys.mapdl.core.building_example

To run the documentation, you need to have the correct versions of each tool. To do so, execute the
following instruction.

.. code:: console

    pip install -r requirements/requirements_docs.txt


The Sphinx configuration is in the file 
`conf.py <https://github.com/ansys/pymapdl/blob/main/doc/source/conf.py>`_ in :file:`doc/source`.


To run the sphinx tool:

.. code:: pwsh-session

    doc\make.bat html


There are three types of examples: dynamic, static, and semi-static.

* `Dynamic examples`_
* `Static examples`_
* `Semi-dynamic examples`_


Dynamic examples
----------------

The dynamic examples are based on Python files and must be able to run in under three minutes.

They are in the `examples <pymapdl_examples_>`_ directory in this repository.

.. vale off

Example: `2d_plate_with_a_hole.py <pymapdl_2d_plate_with_a_hole_>`_
.. vale on

Here is a link to this dynamic example: 
`MAPDL 2D Plane Stress Concentration Analysis <pymapdl_doc_2d_plate_with_a_hole_>`_

When an example is executed, **Total running time of the script** appears at the end of
the document.


Static examples
---------------

Static examples are based on RST files and are not executed. 

They are in the `doc\source <pymapdl_doc_source_>`_ directory.
.. vale off

Example: `krylov_example.rst <pymapdl_doc_krylov_example_rst_>`_
.. vale on

Here is a link to this static example: `Harmonic analysis using the frequency-sweep Krylov method <pymapdl_doc_krylov_example_>`_


Semi-dynamic examples
---------------------

Semi-dynamic examples are RST files that execute Python code using this RST directive:

.. code:: rst

    .. jupyter-execute::
    :hide-code:


.. vale off

Example: `tecfricstir.rst <pymapdl_techdemo_28_rst_>`_
.. vale on

Here is a link to this semi-dynamic example: `Friction Stir Welding (FSW) Simulation <pymapdl_techdemo_28_>`_


Recommendations
---------------

As dynamic examples must run each time documentation is built, make sure that they are very short.
To get around the problem of execution time, feel free to use static or semi-static examples.
