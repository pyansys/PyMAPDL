.. _user_guide_postprocessing:

Postprocessing
==============
In an active MAPDL session, you can postprocess using the
:class:`Mapdl.post_processing <ansys.mapdl.core.post.PostProcessing>` class,
an attribute of an instance of :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`. 
One advantage of this approach is that it integrates well with existing MAPDL
scripting or automation. This approach can also be used on result files generated
from other programs, including ANSYS Mechanical.

Perhaps one of the biggest advantages of gRPC-based postprocessing is
that it can be done remotely without any file exchange. Multi gigabyte
result files can remain remote, with only the necessary data being
streamed back to the client for review or visualization.

.. note::

   You are encouraged to use the Data Processing Framework (DPF)
   modules at `DPF-Core <dpf_core_gh_>`_ and
   `DPF-Post <dpf_post_gh_>`_ because they provide a
   modern interface to Ansys result files using a client-server
   interface. They use the same software that is used within Ansys Workbench
   but via a Python client.



Enriched command output
~~~~~~~~~~~~~~~~~~~~~~~
All :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class commands output
a string object that can be parsed to obtain specific data from it.

In certain :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class commands
the returned string contains some methods to process the output.
These commands are listed in Table-1_.

.. _Table-1:

**Table 1. Commands with extra processing methods in the output**

+----------------+---------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------+
| Category       | Extra methods available                                                                           | MAPDL commands                                                           |
+================+===================================================================================================+==========================================================================+
| **Listing**    | * :class:`cmd.to_list() <ansys.mapdl.core.commands.CommandListingOutput>`                         | **Results listing**                                                      |
|                | * :class:`cmd.to_array() <ansys.mapdl.core.commands.CommandListingOutput>`                        |                                                                          |
|                | * :class:`cmd.to_dataframe() <ansys.mapdl.core.commands.CommandListingOutput>`                    | * :func:`Mapdl.prcint() <ansys.mapdl.core.Mapdl.prcint>`                 |
|                |                                                                                                   | * :func:`Mapdl.prenergy() <ansys.mapdl.core.Mapdl.prenergy>`             |
|                |                                                                                                   | * :func:`Mapdl.prerr() <ansys.mapdl.core.Mapdl.prerr>`                   |
|                |                                                                                                   | * :func:`Mapdl.presol() <ansys.mapdl.core.Mapdl.presol>`                 |
|                |                                                                                                   | * :func:`Mapdl.pretab() <ansys.mapdl.core.Mapdl.pretab>`                 |
|                |                                                                                                   | * :func:`Mapdl.print() <ansys.mapdl.core.Mapdl.print>`                   |
|                |                                                                                                   | * :func:`Mapdl.priter() <ansys.mapdl.core.Mapdl.priter>`                 |
|                |                                                                                                   | * :func:`Mapdl.prjsol() <ansys.mapdl.core.Mapdl.prjsol>`                 |
|                |                                                                                                   | * :func:`Mapdl.prnld() <ansys.mapdl.core.Mapdl.prnld>`                   |
|                |                                                                                                   | * :func:`Mapdl.prnsol() <ansys.mapdl.core.Mapdl.prnsol>`                 |
|                |                                                                                                   | * :func:`Mapdl.prorb() <ansys.mapdl.core.Mapdl.prorb>`                   |
|                |                                                                                                   | * :func:`Mapdl.prpath() <ansys.mapdl.core.Mapdl.prpath>`                 |
|                |                                                                                                   | * :func:`Mapdl.prrfor() <ansys.mapdl.core.Mapdl.prrfor>`                 |
|                |                                                                                                   | * :func:`Mapdl.prrsol() <ansys.mapdl.core.Mapdl.prrsol>`                 |
|                |                                                                                                   | * :func:`Mapdl.prsect() <ansys.mapdl.core.Mapdl.prsect>`                 |
|                |                                                                                                   | * :func:`Mapdl.prvect() <ansys.mapdl.core.Mapdl.prvect>`                 |
|                |                                                                                                   | * :func:`Mapdl.swlist() <ansys.mapdl.core.Mapdl.swlist>`                 |
|                |                                                                                                   |                                                                          |
|                |                                                                                                   |  **Other Listing**                                                       |
|                |                                                                                                   |                                                                          |
|                |                                                                                                   | * :func:`Mapdl.set("LIST") <ansys.mapdl.core.Mapdl.set>`                 |
|                |                                                                                                   | * :func:`Mapdl.nlist() <ansys.mapdl.core.Mapdl.nlist>`                   |
|                |                                                                                                   |                                                                          |
+----------------+---------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------+  
| **Boundary**   | * :func:`cmd.to_list() <ansys.mapdl.core.commands.BoundaryConditionsListingOutput>`               | * :func:`Mapdl.dlist() <ansys.mapdl.core.Mapdl.dlist>`                   |
| **Conditions** | * :func:`cmd.to_dataframe() <ansys.mapdl.core.commands.BoundaryConditionsListingOutput>`          | * :func:`Mapdl.flist() <ansys.mapdl.core.Mapdl.flist>`                   |
| **Listing**    |                                                                                                   |                                                                          |
+----------------+---------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------+

.. warning:: If you use these methods, you might obtain a lower
   precision than using :class:`Mesh <ansys.mapdl.core.mesh_grpc.MeshGrpc>` methods.

Here's a simple example that demonstrates usage:

.. code:: pycon

    
    >>> from ansys.mapdl.core import launch_mapdl
    >>> from ansys.mapdl.core import examples

    >>> mapdl = launch_mapdl()
    >>> example = examples.vmfiles["vm10"]
    >>> mapdl.input(example)

    >>> mapdl.slashsolu()
    >>> mapdl.solve()

    >>> mapdl.post1()
    >>> cmd = mapdl.prnsol("U", "X")

    # Output as a list.

    >>> cmd.to_list()
    [['1', '0.0000'], ['2', '0.0000']]

    # Output as array.

    >>> cmd.to_array()
    array([[1., 0.],
           [2., 0.]])

    # Output as dataframe.

    >>> cmd.to_dataframe()
    NODE   UX
    0      1.0
    1      2.0

Examples
~~~~~~~~
You would typically request nodal results from MAPDL using the
``PRNSOL`` command:

.. code:: output

     POST1:
     PRNSOL, U, X
    
     PRINT U    NODAL SOLUTION PER NODE
    
      ***** POST1 NODAL DEGREE OF FREEDOM LISTING *****                            
     
      LOAD STEP=     1  SUBSTEP=     1                                             
       TIME=    1.0000      LOAD CASE=   0                                         
     
      THE FOLLOWING DEGREE OF FREEDOM RESULTS ARE IN THE GLOBAL COORDINATE SYSTEM  
     
        NODE       UX    
           1  0.10751E-003
           2  0.85914E-004
           3  0.57069E-004
           4  0.13913E-003
           5  0.35621E-004
           6  0.52186E-004
           7  0.30417E-004
           8  0.36139E-004
           9  0.15001E-003
     MORE (YES,NO OR CONTINUOUS)=


However, using an instance of the :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`
class, you can instead request the nodal displacement:

.. code:: pycon

    >>> mapdl.set(1, 1)
    >>> disp_x = mapdl.post_processing.nodal_displacement("X")
    array([1.07512979e-04, 8.59137773e-05, 5.70690047e-05, ...,
           5.70333124e-05, 8.58600402e-05, 1.07445726e-04])

You could also plot the nodal displacement with this code:

.. code:: pycon

    >>> mapdl.post_processing.plot_nodal_displacement("X")


.. figure:: ../images/post_norm_disp.png
    :width: 300pt

    Normalized Displacement of a Cylinder from MAPDL


Selecting entities
------------------
You can select entities such as nodes, or lines using the following methods:

* :func:`Mapdl.nsel() <ansys.mapdl.core.Mapdl.nsel>`
* :func:`Mapdl.esel() <ansys.mapdl.core.Mapdl.esel>`
* :func:`Mapdl.ksel() <ansys.mapdl.core.Mapdl.ksel>`
* :func:`Mapdl.lsel() <ansys.mapdl.core.Mapdl.lsel>`
* :func:`Mapdl.asel() <ansys.mapdl.core.Mapdl.asel>`
* :func:`Mapdl.vsel() <ansys.mapdl.core.Mapdl.vsel>`

These methods returns the ids of the selected entities. For example:

.. code:: pycon

    >>> selected_nodes = mapdl.nsel("S", "NODE", vmin=1, vmax=2000)
    >>> print(selected_nodes)
    array([   1    2    3 ... 1998 1999 2000])

.. code:: pycon

    >>> mapdl.ksel("all")
    array([1, 2, 3, ..., 1998, 1999, 2000])


Selected nodes
~~~~~~~~~~~~~~

The MAPDL database processes some results independently if nodes or
elements are selected. If you have subselected a certain component
and want to also limit the result of a certain output
(:func:`nodal_displacement() <ansys.mapdl.core.post.PostProcessing.nodal_displacement>`), 
use the :attr:`selected_nodes <ansys.mapdl.core.post.PostProcessing.selected_nodes>` attribute to get
a mask of the currently selected nodes:

.. code:: pycon

    >>> mapdl.nsel("S", "NODE", vmin=1, vmax=2000)
    >>> mapdl.esel("S", "ELEM", vmin=500, vmax=2000)
    >>> mask = mapdl.post_processing.selected_nodes


Postprocessing object methods
------------------------------
For a full list of all available postprocessing methods, see
:ref:`post_processing_api`.
