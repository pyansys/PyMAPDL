********************
Interactive plotting
********************
When generating geometry from scratch within MAPDL, it is often
necessary to plot the geometry, such as key points, lines, areas,
and volumes. PyMAPDL supports plotting basic CAD using VTK. The
:class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class leverages the
existing MAPDL commands by providing the following functions, which
transfer the geometry to Python to visualize it:

- :func:`Mapdl.kplot() <ansys.mapdl.core.Mapdl.kplot>`
- :func:`Mapdl.vplot() <ansys.mapdl.core.Mapdl.vplot>`
- :func:`Mapdl.eplot() <ansys.mapdl.core.Mapdl.eplot>`). 

These methods rely on the :func:`ansys.mapdl.core.plotting.general_plotter`
method. Combined with the MAPDL geometry commands, you can
generate and visualize geometry from scratch without opening the GUI
using the :func:`open_gui() <ansys.mapdl.core.Mapdl.open_gui>` method.


Line plotting
~~~~~~~~~~~~~
You plot lines within Python using the :func:`Mapdl.lplot() <ansys.mapdl.core.Mapdl.lplot>` method:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()

    Create a rectangle with a few holes

    >>> mapdl.prep7()
    >>> rect_anum = mapdl.blc4(width=1, height=0.2)

    Create several circles in the middle in the rectangle

    >>> for x in np.linspace(0.1, 0.9, 8):
    ...     mapdl.cyl4(x, 0.1, 0.025)
    ...

    Generate a line plot

    >>> mapdl.lplot(color_lines=True, cpos="xy")


.. figure:: ../images/lplot_vtk.png
    :width: 400pt

    Line plot from MAPDL using PyMAPDL and `PyVista <pyvista_docs_>`__


Area and volume plotting
~~~~~~~~~~~~~~~~~~~~~~~~
You can using Boolean operations to obtain more complex geometry and
visualize them using the :func:`Mapdl.vplot()
<ansys.mapdl.core.Mapdl.vplot>` method. This example cuts the initial
area with the eight circles and then extrudes it.

.. code:: pycon

    >>> plate_holes = mapdl.asba(rect_anum, "all")

    Extrude this area

    >>> mapdl.vext(plate_holes, dz=0.1)
    >>> mapdl.vplot()


.. figure:: ../images/vplot_vtk.png
    :width: 400pt

    Volume Plot from MAPDL using PyMAPDL and `PyVista <pyvista_docs_>`__


Node and element plotting
~~~~~~~~~~~~~~~~~~~~~~~~~
You can plot nodes and elements directly from the instance of the
:class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` class. This code defines
some element types, performs meshing, and then displays the mesh:

.. code:: pycon

    >>> mapdl.et(1, "SOLID186")
    >>> mapdl.vsweep("ALL")
    >>> mapdl.esize(0.1)
    >>> mapdl.eplot()

.. figure:: ../images/eplot_vtk.png
    :width: 400pt

    Element Plot from MAPDL using PyMAPDL and `Pyvista <pyvista_docs_>`_


Plotting non-interactively using MAPDL
--------------------------------------
You can also plot using MAPDL's native plotting tools. To use the
native tools, pass ``vtk=False`` when running plotting commands such
as the :func:`Mapdl.aplot <ansys.mapdl.core.Mapdl.aplot>` and
:func:`Mapdl.eplot <ansys.mapdl.core.Mapdl.eplot>` methods. Plots are
generated within MAPDL and then shown using 
`Matplotlib <matplotlib_main_>`_.


Start PyMAPDL

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()

Create a square area using key points

.. code:: pycon

    >>> mapdl.prep7()
    >>> mapdl.k(1, 0, 0, 0)
    >>> mapdl.k(2, 1, 0, 0)
    >>> mapdl.k(3, 1, 1, 0)
    >>> mapdl.k(4, 0, 1, 0)
    >>> mapdl.l(1, 2)
    >>> mapdl.l(2, 3)
    >>> mapdl.l(3, 4)
    >>> mapdl.l(4, 1)
    >>> mapdl.al(1, 2, 3, 4)

Set the view to "isometric"

.. code:: pycon

    >>> mapdl.view(1, 1, 1, 1)
    >>> mapdl.pnum("kp", 1)  # enable keypoint numbering
    >>> mapdl.pnum("line", 1)  # enable line numbering

Each of these creates a Matplotlib figure and pause execution.

.. code:: pycon

    >>> mapdl.aplot(vtk=False)
    >>> mapdl.lplot(vtk=False)
    >>> mapdl.kplot(vtk=False)


.. figure:: ../images/aplot.png
    :width: 400pt

    Area Plot from MAPDL displayed using 
    `Matplotlib <matplotlib_main_>`_


For more information on plotting functions, see :ref:`ref_plotting_api`.


Plotting keyword options
~~~~~~~~~~~~~~~~~~~~~~~~
When ``vtk=True``, which is the default, all MAPDL plotting
methods allow you to enter in additional keyword arguments to better
control the plot. For example, you can automatically generate a
screenshot of an area plot or element plot with this code:

.. code:: pycon

    >>> mapdl.aplot(savefig="aplot.png")
    >>> mapdl.eplot(savefig="eplot.png")

You can also control the camera position with ``cpos`` when you
want to view from a standard viewing direction. This code shows how
to view the XY plane with ``cpos='xy'``.

.. code:: pycon

    >>> mapdl.eplot(cpos="xy")

For all general plotting options, see the
:func:`ansys.mapdl.core.plotting.general_plotter` method.


Plotting boundary conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   This feature is beta so its functionalities and stability are
   limited. See the documentation regarding the allowed boundary
   conditions and targets.

It is possible to plot the boundary conditions applied on the model by
specifying ``plot_bc=True`` in plotting functions. For example, this code
specifies ``plot_bc=True`` for the :func:`Mapdl.nplot() <ansys.mapdl.core.Mapdl.nplot>`
method:

.. code:: pycon

    >>> mapdl.nplot(
    ...     plot_bc=True, plot_labels=True, savefig=f"bc_plot.png", bc_labels="mechanical"
    ... )


.. figure:: ../images/bc_plot.png
    :width: 500pt

    **Mechanical boundary conditions**
    Forces (arrows) and displacements (cones)

.. note::
    Because boundary conditions can only target nodes, you can
    only use ``plot_bc`` as an argument in the :func:`Mapdl.nplot()
    <ansys.mapdl.core.Mapdl.nplot>` method.



.. figure:: ../images/bc_plot_2.png
    :width: 500pt

    **Boundary conditions demonstration**
