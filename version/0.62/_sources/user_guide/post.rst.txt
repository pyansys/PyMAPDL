Post-Processing
===============
You can post process using an active MAPDL session using the
:class:`Mapdl.post_processing <ansys.mapdl.core.post.PostProcessing>`
an attribute of an instance of :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`. 
One advantage of this approach
is it integrates well with existing MAPDL scripting or automation, but
can also be carried out on result files generated from other programs,
including ANSYS Mechanical.

Perhaps on of the biggest advantages of gRPC based post-processing is
it can be done remotely without any file exchange.  Multi gigabyte
result files can remain remote and only the necessary data needs to be
streamed back to the client for review or visualization.

.. note::

   You are encouraged to use the new Data Processing Framework (DPF)
   modules at `DPF-Core <https://github.com/pyansys/DPF-Core>`_ and
   `DPF-Post <https://github.com/pyansys/DPF-Post>`_ as they provide a
   modern interface to ANSYS result files using a client/server
   interface using the same software used within Ansys Workbench, but
   via a Python client.



Enriched Command Output
~~~~~~~~~~~~~~~~~~~~~~~
All :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` commands output
a string object which can be parsed to obtain specific data from it.

In certain :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` commands
the returned string contains some methods to process the output.
These commands are listed in Table-1_.

.. _Table-1:

**Table 1. Commands with extra processing methods in the output.**

+----------------+---------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| Category       | Extra Methods Available                                                                           | Mapdl Commands                                           |
+================+===================================================================================================+==========================================================+
| **Listing**    | * :func:`to_list() <ansys.mapdl.core.commands.CommandListingOutput.to_list>`                      | * :func:`prcint() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                | * :func:`to_array() <ansys.mapdl.core.commands.CommandListingOutput.to_array>`                    | * :func:`prenergy() <ansys.mapdl.core.mapdl._MapdlCore>` |
|                | * :func:`to_dataframe() <ansys.mapdl.core.commands.CommandListingOutput.to_dataframe>`            | * :func:`prerr() <ansys.mapdl.core.mapdl._MapdlCore>`    |
|                |                                                                                                   | * :func:`presol() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`pretab() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`print() <ansys.mapdl.core.mapdl._MapdlCore>`    |
|                |                                                                                                   | * :func:`priter() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prjsol() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prnld() <ansys.mapdl.core.mapdl._MapdlCore>`    |
|                |                                                                                                   | * :func:`prnsol() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prorb() <ansys.mapdl.core.mapdl._MapdlCore>`    |
|                |                                                                                                   | * :func:`prpath() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prrfor() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prrsol() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prsect() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`prvect() <ansys.mapdl.core.mapdl._MapdlCore>`   |
|                |                                                                                                   | * :func:`stat() <ansys.mapdl.core.mapdl._MapdlCore>`     |
|                |                                                                                                   | * :func:`swlist() <ansys.mapdl.core.mapdl._MapdlCore>`   |
+----------------+---------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| **Boundary**   | * :func:`to_list() <ansys.mapdl.core.commands.BoundaryConditionsListingOutput.to_list>`           | * :func:`dlist() <ansys.mapdl.core.mapdl._MapdlCore>`    |
| **Conditions** | * :func:`to_dataframe() <ansys.mapdl.core.commands.BoundaryConditionsListingOutput.to_dataframe>` | * :func:`flist() <ansys.mapdl.core.mapdl._MapdlCore>`    |
| **Listing**    |                                                                                                   |                                                          |
+----------------+---------------------------------------------------------------------------------------------------+----------------------------------------------------------+

Here's a simple example demonstrating the the usage:

.. code:: python

    
    >>> from ansys.mapdl.core import launch_mapdl
    >>> from ansys.mapdl.core import examples

    >>> mapdl = launch_mapdl()
    >>> example = examples.vmfiles['vm10']
    >>> mapdl.input(example)

    >>> mapdl.slashsolu()
    >>> mapdl.solve()

    >>> mapdl.post1()
    >>> cmd = mapdl.prnsol('U', 'X')

    Output as a list.

    >>> cmd.to_list()
    [['1', '0.0000'], ['2', '0.0000']]

    Output as array.

    >>> cmd.to_array()
    array([[1., 0.],
           [2., 0.]])

    Output as dataframe.

    >>> cmd.to_dataframe()
    NODE   UX
    0      1.0
    1      2.0

Examples
~~~~~~~~
Classically, one would request nodal results from MAPDL using the
``PRNSOL`` command.  For example:

.. code::

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


However, using an instance of :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`, 
you can instead request the
nodal displacement with:

.. code:: python

    >>> mapdl.set(1, 1)
    >>> disp_x = mapdl.post_processing.nodal_displacement('X')
    array([1.07512979e-04, 8.59137773e-05, 5.70690047e-05, ...,
           5.70333124e-05, 8.58600402e-05, 1.07445726e-04])

You could also plot the nodal displacement with:

    >>> mapdl.post_processing.plot_nodal_displacement('X')


.. figure:: ../images/post_norm_disp.png
    :width: 300pt

    Normalized Displacement of a Cylinder from MAPDL


Selected Nodes
~~~~~~~~~~~~~~
The MAPDL database processes some results independently of if nodes or
elements are selected.  If you have subselected a certain component
and wish to also limit the result of a certain output
(i.e. :func:`nodal_displacement() <ansys.mapdl.core.post.PostProcessing.nodal_displacement>`), 
use the :attr:`selected_nodes <ansys.mapdl.core.post.PostProcessing.selected_nodes>` attribute to get
a mask of the currently selected nodes.

.. code::

    >>> mapdl.nsel('S', 'NODE', vmin=1, vmax=2000)
    >>> mapdl.esel('S', 'ELEM', vmin=500, vmax=2000)
    >>> mask = mapdl.post_processing.selected_nodes


Post Processing Object Methods
------------------------------
For a full list of all available post-processing methods, see
:ref:`post_processing_api`.
