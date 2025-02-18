.. _mapdl_math_class_ref:

APDL Math overview
==================
APDL Math provides the ability to access and manipulate the large
sparse matrices and solve a variety of eigenproblems. PyMAPDL classes
and bindings present APDL Math in a similar manner to the popular
`numpy <numpy_docs_>`_ and `scipy <scipy_docs_>`_ libraries.
The APDL Math command set is based on tools for manipulating large mathematical
matrices and vectors that provide access to standard linear algebra
operations, access to the powerful sparse linear solvers of ANSYS
Mechanical APDL (MAPDL), and the ability to solve eigenproblems.

Python and MATLAB eigensolvers are based on the publicly available
LAPACK libraries and provides reasonable solve time for relatively
small degrees of freedom (dof) eigenproblems of perhaps 100,000.
However, Ansys solvers are designed for the scale of 100 s of
millions of dof, providing a variety of situations where you can
directly leverage Ansys high-performance solvers on a variety of
eigenproblems. Fortunately, you can leverage this without relearning
an entirely new language because APDL Math has been written in a similar manner
as the ``numpy`` and ``scipy`` libraries. For example, here is a comparison between
the NumPy and SciPy linear algebra solvers and the Ansys MAPDL Math solver:

.. table:: ``numpy`` vs PyMAPDL Math Implementation

   +--------------------------------------------+-----------------------------------+
   | ``numpy`` and ``scipy``                    | ``ansys.mapdl.math``              |
   +============================================+===================================+
   | .. code:: python                           | .. code:: python                  |
   |                                            |                                   |
   |   k_py = k + sparse.triu(k, 1).T           |   k = mm.matrix(k_py, triu=True)  |
   |   m_py = m + sparse.triu(m, 1).T           |   m = mm.matrix(m_py, triu=True)  |
   |   n = 10                                   |   n = 10                          |
   |   ev = linalg.eigsh(k_py, k=neqv, M=m_py)  |   ev = mm.eigs(n, k, m)           |
   |                                            |                                   |
   +--------------------------------------------+-----------------------------------+

What follows is a basic example and a detailed description of the
PyMAPDL Math API. For additional PyMAPDL Math examples, see
:ref:`ref_apdl_math_examples`.


MAPDL matrix example
~~~~~~~~~~~~~~~~~~~~
This example demonstrates how to send an MAPDL Math matrix from MAPDL
to Python and then send it back to be solved. While this example runs the
:func:`MapdlMath.eigs() <ansys.mapdl.core.math.MapdlMath.eigs>` method on mass
and stiffness matrices generated from MAPDL, you could instead use
mass and stiffness matrices generated from an external FEM tool or
even modify the mass and stiffness matrices within Python.

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
in the ``<jobname>.full`` file.  First, create an instance of the :class:`MapdlMath
<ansys.mapdl.core.math.MapdlMath>` class as ``mm``:

.. code:: python

    mm = mapdl.math

    # load by default from file.full
    k = mm.stiff()
    m = mm.mass()

    # convert to numpy
    k_py = k.asarray()
    m_py = m.asarray()
    mapdl.clear()
    print(k_py)

After running the :func:`Mapdl.clear() <ansys.mapdl.core.Mapdl.clear>` method,
these matrices are stored solely within Python.

.. code:: output

    (0, 0)	37019230769.223404
    (0, 1)	10283119658.117708
    (0, 2)	10283119658.117706
    :	:
    (240, 241)	11217948717.943113
    (241, 241)	50854700854.68495
    (242, 242)	95726495726.47179


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
:func:`MapdlMath.eigs() <ansys.mapdl.core.math.MapdlMath.eigs>` method is
identical to the result from the :func:`Mapdl.solve() <ansys.mapdl.core.Mapdl.solve>`
method within MAPDL.

.. code:: output

    [1475.1333421  1475.1333426  2018.83737064 2018.83737109 2018.83737237
     2024.78684466 2024.78684561 2024.7868466  2242.21532585 2274.82997741]

If you want to obtain the eigenvectors as well as the eigenvalues,
initialize a matrix ``eigvec`` and send that to the
:func:`MapdlMath.eigs() <ansys.mapdl.core.math.MapdlMath.eigs>` method:

.. code:: pycon

    >>> nmode = 10
    >>> eigvec = mm.zeros(my_stiff.nrow, nmode)  # for eigenvectors
    >>> val = mm.eigs(nmode, my_stiff, my_mass, fmin=1)

The MAPDL Math matrix ``eigvec`` now contains the eigenvectors for the
solution.

APDL Math reference
~~~~~~~~~~~~~~~~~~~
For more information, see :ref:`ref_math_api`.
