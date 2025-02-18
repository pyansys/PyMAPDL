.. _faq:

**************************
Frequently asked questions
**************************

How do you report issues?
=========================

If you find an issue, the first place to visit for possible solutions is the :ref:`troubleshooting section <ref_troubleshooting>`.

If you do not find a solution there, you can search for your issue within the `GitHub repository <pymapdl_repo_>`_. You can use `the search box <pymapdl_search_issues_pr_>`_ to find related issues or pull requests.

To ask more open-ended questions or seek advice from the community,
use the `PyMAPDL discussions <pymapdl_discussions_>`_ page of the GitHub repository.

To report bugs and documentation errors and to make feature requests,
use the `PyMAPDL issues <pymapdl_issues_>`_ page of the GitHub repository.


What are the pros and cons of PyMAPDL versus Ansys ACT?
=======================================================

The pros and cons depend on your pipeline and software approach.
Ansys ACT is an Ansys Workbench-dependent approach, where extensions are
built from within the ACT App Builder and then run from within Ansys Mechanical.
If you intend to vary parameters, you must then use Ansys optiSLang to
vary them and batch your solutions.

The main advantages that PyMAPDL has over Ansys ACT are:

* PyMAPDL tightly integrates with Python tools and open source modules
  to run alongside Ansys software.
* Scripts are written in Python. ACT uses .NET, which means you can call
  only IronPython and potentially other tools within Ansys Mechanical.
* Being that PyMAPDL is outside of Ansys Mechanical, you can call your
  app workflow without opening up a GUI for user interaction.
  If you want a GUI, you can create your own with `PyQt <https://pythonpyqt.com/>`_.
  Or, you can output plots using `Matplotlib <https://matplotlib.org/>`_
  or `VTK <https://vtk.org/>`_.
* PyMAPDL is compatible with modern Python (3), whereas ACT is only
  compatible with IronPython (Python 2).

The best approach depends on your workflow needs and how you would
like to develop software.


Has APDL been "deprecated" by Ansys? If so, what does that mean for PyMAPDL?
============================================================================

APDL isn't going anywhere. In fact, whenever you call Mechanical Workbench, it's
generating an input file (``ds.dat``) that's fed into MAPDL. However, what's
changed over the past several years is where the geometry, meshing, and
postprocessing is occurring. Geometry generation can take place within
SpaceClaim or Design Modeler, and meshing is done using a variety of new and
powerful meshers within Workbench. While these tools are far superior to the
ones in MAPDL, their biggest limitation is that they're difficult to script
(especially externally). As a result, there are still users who choose to
generate the geometry and mesh within MAPDL.


What are the main reasons to use PyMAPDL over other Ansys products like Workbench?
==================================================================================
There are always tasks where it's better to use one over the
other. Workbench is great tool to rapidly prototype, mesh, set
boundary conditions, and solve. Because it is where a ton of development has
gone, there are many features that make it easy to run
analyses. However, it's limited by its IronPython scripting. Additionally, you're
unable to call multiple products at either a granular or high level or
use packages such as `NumPy <https://numpy.org/>`_, `SciPy <https://scipy.org/>`_,
`PyTorch <https://pytorch.org/>`_, and `TensorFlow <https://www.tensorflow.org/>`_.
PyMAPDL ties this in with MAPDL, allowing you to have a fully parametric workflow
that leverages these machine learning tools. It also allows you to generate 
advanced plots using `PyVista <pyvista_docs_>`_ or `Matplotlib <matplotlib_main_>`_.



How do you end a simulation and restart a script?
=================================================

Closing and reopening Python clears the solution within Python. To clear all previous
data such as the mesh, you can use this code:

.. code:: python

    import sys

    sys.modules[__name__].__dict__.clear()


However, a more efficient way is to clear MAPDL using the 
:meth:`clear() <ansys.mapdl.core.Mapdl.clear>`
method. You can also exit and restart MAPDL.


Why PyMAPDL results are different than the ones shown in the MAPDL GUI?
=======================================================================

Listing results
---------------

There might be several reasons why the results shown in the MAPDL GUI
differ from the results obtained using PyMAPDL. The most common
reason is that the MAPDL GUI is using a different graphics configuration
than the one used by PyMAPDL.

In the MAPDL GUI, the graphics configuration can change how the results are shown.
Each graphics configuration realizes entity selection and averaging differently.
By default, the graphics configuration is set to ``Power Graphics``.
However, PyMAPDL connects to an MAPDL instance running in batch mode, which by default
uses the ``Full Graphics`` configuration. This difference in the graphics configuration can
affect averaging as well.

You can change the graphics configuration in PyMAPDL using this command:

.. code:: python

    mapdl.graphics("POWER")

Or, you can change the graphics configuration in the MAPDL GUI using the 
``POWRGRPH`` button or this command:

.. code:: text

    /GRAPHICS,FULL

How the results are averaged on the nodes can also affect the
results. By default, MAPDL averages the results on the nodes except where
material type discontinuities exists. 
For more information, see :meth:`avres() <ansys.mapdl.core.Mapdl.avres>`.
Additionally, the command :meth:`efacet() <ansys.mapdl.core.Mapdl.efacet>`
can affect how the results are shown.

You should make sure that the values of the commands
:meth:`avres() <ansys.mapdl.core.Mapdl.avres>` and 
:meth:`efacet() <ansys.mapdl.core.Mapdl.efacet>` are the same in both
the MAPDL GUI and PyMAPDL.

Finally, depending on the results that you are trying to obtain, you
might be using a different MAPDL command. For example, the command
:meth:`post.element_displacement() <ansys.mapdl.core.post.PostProcessing.element_displacement>`
uses a combination of ``PRETAB`` and ``ETAB`` commands to obtain the results.
This MAPDL command then might show different results than the ones obtained
using the PyMAPDL :meth:`presol() <ansys.mapdl.core.Mapdl.presol>` method.
To make sure you are using the correct command, you should compare the
results obtained using both the MAPLD and PyMAPDL commands.

.. note:: Further reading on `this discussion <pymapdl_discussion_differences_mapdl_pymapdl_>`_

Plotting results
----------------

Even in cases where PyMAPDL and MAPDL agree on the result values, there may still be
display differences. For instance, interpolating scalar values at the nodes of a
quadrilateral facet across the whole facet is not deterministic.
