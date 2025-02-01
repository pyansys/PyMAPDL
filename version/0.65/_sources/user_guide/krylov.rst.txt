=========================================
Harmonic analysis using the Krylov method
=========================================

Introduction
============
You can use the frequency-sweep Krylov method for a high-performance
solution of forced-frequency simulations in acoustic or single-field
structural analyses.

Similar to the full harmonic analysis, the frequency-sweep Krylov method
uses full system matrices to compute the harmonic response. While the full
method solves at every frequency point in the frequency range, the 
frequency-sweep Krylov method performs the following steps to approximate
the response across the frequency range:

* Builds a Krylov subspace set of vectors at the frequency value in the
  middle of the requested frequency range
* Reduces the system matrices and loading on the entire frequency range
* Solves the reduced system
* Expands the results back to compute the harmonic response 

Mechanical APDL provides the following ways to implement a harmonic analysis
using the Krylov method:

#. Mechanical APDL commands
#. APDL macros as described in `Frequency-Sweep Harmonic Analysis via the Krylov Method
   <ansys_krylov_sweep_harmonic_analysis_>`_ in the *Structural Analysis* guide
   for Mechanical APDL

PyMAPDL also provides a way to implement a harmonic analysis using the Krylov method.
Subsequent sections describe how to use the Krylov method in PyMAPDL.


**Assumptions**
---------------
The following assumptions are made when using the Krylov PyMAPDL method
to obtain the solution:

* The stiffness, mass, and damping matrices are assumed to be constant
  (independent of frequency).

* The external load vector is linearly ramped over frequency. Ramping
  assumes that the frequency at which the Krylov subspace is built is
  in the middle of the frequency range. If you want to apply stepped loading,
  there is an option to specify that in the inputs for the 
  :func:`KrylovSolver.solve() <ansys.mapdl.core.krylov.KrylovSolver.solve>`
  method.


Krylov method implementation in PyMAPDL
=======================================
The PyMAPDL implementation of the Krylov method gives you customization
and flexibility because you can access subspace vectors and reduced
solutions using the Python programming language for user-defined routines.

If you do not require customization, you can use the Mechanical APDL
commands to solve a harmonic analysis with the Krylov method. For more
information, including the theory behind this method, see
`Frequency-Sweep Harmonic Analysis via the Krylov Method 
<ansys_krylov_sweep_harmonic_analysis_>`_ in the *Structural Analysis* guide
for Mechanical APDL. 

For additional theory information and equations for
the Krylov method, see the works of Puri [1]_ and Eser [2]_.

The exposure in PyMAPDL follows the same theory as the Mechanical APDL macros and
has the following methods:

* :func:`KrylovSolver.gensubspace() <ansys.mapdl.core.krylov.KrylovSolver.gensubspace>`:
  Creates the Krylov subspace. 
* :func:`KrylovSolver.solve() <ansys.mapdl.core.krylov.KrylovSolver.solve>`: 
  Solves the reduced system of equations.
* :func:`KrylovSolver.expand() <ansys.mapdl.core.krylov.KrylovSolver.expand>`:
  Expands the Krylov subspace.

.. warning:: These methods must be run consecutively.

Usage
=====
This section shows how to implement an analysis identical to that 
defined by the Mechanical APDL macros.

Generate the FULL file and FEA model
------------------------------------
Generate the FULL file for the Krylov method and the FEA model
using Mechanical APDL:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl

    >>> mapdl = launch_mapdl()
    >>> mapdl.prep7()

	# Generate the FEA model (mesh, constraints, loads)
  # ...

    >>> mapdl.run("/SOLU")
    >>> mapdl.antype("HARMIC")  # HARMONIC ANALYSIS
    >>> mapdl.hropt("KRYLOV")
    >>> mapdl.eqslv("SPARSE")
    >>> mapdl.harfrq(0,1000)  # Set beginning and ending frequency
    >>> mapdl.nsubst(100)  # Set the number of frequency increments
    >>> mapdl.wrfull(1)  # GENERATE .FULL FILE AND STOP
    >>> mapdl.solve()
    >>> mapdl.finish()

Create an instance of the Krylov class
--------------------------------------

.. code:: pycon
    
    >>> mk = mapdl.krylov

Call the 
:func:`gensubspace <ansys.mapdl.core.krylov.KrylovSolver.gensubspace>`
method to create the Krylov subspace and build a subspace of
size/dimension 10 at a frequency of 500 Hz:

.. code:: pycon

    >>> Qz = mk.gensubspace(10, 500, True)

Return the Krylov subspace
--------------------------

Call the :func:`solve <ansys.mapdl.core.krylov.KrylovSolver.solve>` method to
reduce the system of equations and solve at each frequency. This code
solves from 0 Hz to 1000 Hz with 100 intervals in between, with stepped loading:

.. code:: pycon

    >>> Yz = mk.solve(0, 1000, 100, ramped_load=True)


Return the reduced solution over the frequency range
----------------------------------------------------
            
Call the :func:`expand <ansys.mapdl.core.krylov.KrylovSolver.expand>` method
to expand the reduced solution back to the FE space, output the expanded
solution, and calculate the residual:   

.. code:: pycon

    >>> result = mk.expand(
    ...     residual_computation=True, "L-inf", compute_solution_vectors=True, True
    ... )

The preceding code returns a :class:`numpy array<numpy.ndarray>` if the kwarg ``out_key``
is set to ``True``. Solution vectors are mapped to user order.

.. note:: The :class:`numpy array<numpy.ndarray>` class returned by the
   :func:`expand <ansys.mapdl.core.krylov.KrylovSolver.expand>` method contains
   the node number along with the degrees of freedom (dof) solution for each of
   the calculated frequencies.

Get the dof solution at a specific frequency
--------------------------------------------
This code shows how to get the nodal solution at a specific frequency
or step:

.. code:: pycon

   # Get the nodal solution at freq number 3``````
   >>> freq = 3
   >>> nodal_sol = result[freq - 1]  # Get the nodal solution for each node

Example
=======

Examples of using the Krylov method in PyMAPDL are available in :ref:`krylov_example`.

Requirements
============

To use the Krylov method in PyMAPDL, you must use Mechanical APDL version 2022 R2 or later.

.. warning:: This feature does not support Distributed Ansys. 
    However, you can still run Mechanical APDL Math commands without
    specifying the ``-smp`` flag when launching Mechanical APDL.

Reference
=========
For more information on the Krylov method, see `Frequency-Sweep Harmonic Analysis via the Krylov Method 
<ansys_krylov_sweep_harmonic_analysis_>`_ in the *Structural Analysis* guide for Mechanical APDL
and these resources:

.. [1] Puri, S. R. (2009). Krylov Subspace Based Direct Projection Techniques for Low Frequency,
   Fully Coupled, Structural Acoustic Analysis and Optimization. PhD Thesis. Oxford Brookes University,
   Mechanical Engineering Department. Oxford, UK.

.. [2] Eser, M. C. (2019) Efficient Evaluation of Sound Radiation of an Electric Motor using Model Order
   Reduction. MSc Thesis. Technical University of Munich, Mechanical Engineering Department. Munich, DE.
