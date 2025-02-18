.. _mapdl_math_class_ref:

PyAnsys Math overview
=====================
`PyAnsys Math <pyansys_math_>`_ provides the ability to access and manipulate
large sparse matrices and solve a variety of eigenproblems in a similar
manner to the popular `numpy <numpy_docs_>`_ and `scipy <scipy_docs_>`_ libraries.


PyMAPDL and PyAnsys Math
~~~~~~~~~~~~~~~~~~~~~~~~
This example demonstrates how to take advantage of the `ansys-math-core` package
with PyMAPDL.

It illustrates how to send an MAPDL Math matrix from MAPDL to Python and then send
it back to be solved. While this example runs the 
:func:`mm.eigs() <ansys.math.core.math.AnsMath.eigs>` method on mass and stiffness
matrices generated from MAPDL, you could instead use mass and stiffness matrices
generated from an external FEM tool or even modify the mass and stiffness matrices
within Python.

First, solve the first 10 modes of a ``1 x 1 x 1`` steel meter cube
in MAPDL.

.. code:: python

    import re
    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl()

    # setup the full file
    mapdl.prep7()
    mapdl.block(0, 1, 0, 1, 0, 1)
    mapdl.et(1, 186)
    mapdl.esize(0.5)
    mapdl.vmesh("all")

    # Define a material (nominal steel in SI)
    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

    # solve first 10 non-trivial modes
    out = mapdl.modal_analysis(nmode=10, freqb=1)

    # store the first 10 natural frequencies
    mapdl.post1()
    resp = mapdl.set("LIST")
    w_n = np.array(re.findall(r"\s\d*\.\d\s", resp), np.float32)
    print(w_n)

You now have solved for the first 10 modes of the cube:

.. code:: output

    [1475.1 1475.1 2018.8 2018.8 2018.8 2024.8 2024.8 2024.8 2242.2 2274.8]

Next, load the mass and stiffness matrices that are stored by default
in the :file:`<jobname>.full` file. First, create an instance of the 
:class:`MapdlMath <ansys.math.core.math.AnsMath>` class as ``mm``:

.. code:: python

    from ansys.math.core.math import AnsMath

    # Importing and connecting PyAnsys Math to PyMAPDL
    mm = AnsMath(mapdl)

    # load by default from file.full
    k = mm.stiff()
    m = mm.mass()

    # convert to numpy
    k_py = k.asarray()
    m_py = m.asarray()
    mapdl.clear()
    print(k_py)

After running the :func:`mapdl.clear() <ansys.mapdl.core.Mapdl.clear>` method,
these matrices are stored solely within Python.

.. code:: output

    (0, 0)	37019230769.223404
    (0, 1)	10283119658.117708
    (0, 2)	10283119658.117706
    :	:
    (240, 241)	11217948717.943113
    (241, 241)	50854700854.68495
    (242, 242)	95726495726.47179

To call PyAnsys Math directly from PyMAPDL, you can run this command:

.. code:: python

    # Launching PyAnsys Math directly with PyMAPDL
    mm = mapdl.math


The final step is to send these matrices back to MAPDL to be solved.
While you have cleared MAPDL, you could have shut down MAPDL or even
transferred the matrices to a different MAPDL session to be solved:

.. code:: python

    my_stiff = mm.matrix(k_py, triu=True)
    my_mass = mm.matrix(m_py, triu=True)

    # solve for the first 10 modes above 1 Hz
    nmode = 10
    mapdl_vec = mm.eigs(nmode, my_stiff, my_mass, fmin=1)
    eigval = mapdl_vec.asarray()
    print(eigval)

As expected, the natural frequencies obtained from the
:func:`mm.eigs() <ansys.math.core.math.AnsMath.eigs>` method is
identical to the result from the :func:`mapdl.solve() <ansys.mapdl.core.Mapdl.solve>`
method within MAPDL.

.. code:: output

    [1475.1333421  1475.1333426  2018.83737064 2018.83737109 2018.83737237
     2024.78684466 2024.78684561 2024.7868466  2242.21532585 2274.82997741]

If you want to obtain the eigenvectors as well as the eigenvalues,
initialize a matrix ``eigvec`` and send that to the
:func:`mm.eigs() <ansys.math.core.math.AnsMath.eigs>` method:

.. code:: pycon

    >>> nmode = 10
    >>> eigvec = mm.zeros(my_stiff.nrow, nmode)  # for eigenvectors
    >>> val = mm.eigs(nmode, my_stiff, my_mass, fmin=1)

The AnsMath matrix ``eigvec`` now contains the eigenvectors for the
solution.

PyAnsys Math reference
~~~~~~~~~~~~~~~~~~~~~~
For more information, see the `PyAnsys Math API reference <pyansys_math_api_>`_.
