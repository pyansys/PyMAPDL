.. _hpc_ml_ga_example:

==============================
Genetic algorithms and PyMAPDL
==============================

This example shows how to use PyMAPDL in an HPC cluster to 
take advantage of multiple MAPDL instances to calculate each of the
genetic algorithm population solutions.
To manage multiple MAPDL instances, you should use the
:class:`~ansys.mapdl.core.pool.MapdlPool` class, which allows you
to run multiple jobs in the background.

Introduction
============

Genetic algorithms are optimization techniques inspired by the principles of natural
selection and genetics. They are used to find solutions to complex problems by mimicking
the process of natural selection to evolve potential solutions over successive generations.
In a genetic algorithm, a population of candidate solutions (chromosomes) undergoes a
series of operations, including selection, crossover, and mutation, to produce new
generations of solutions. The fittest chromosomes, which best satisfy the problem
constraints and objectives, are more likely to be selected for reproduction, thus
gradually improving the overall quality of solutions over time. Genetic algorithms are
particularly useful for solving problems where traditional methods are impractical or
inefficient, such as optimization, search, and machine learning tasks. They find
applications in various fields, including engineering, economics, biology, and computer science.

Problem definition
==================

This example shows how to use a generic algorithm to calculate the force
required for a double-clamped beam to deform a specific amount in its
center.

The beam model is the same as :ref:`ref_mapdl_beam`.
It is made of ``BEAM188`` elements that span for 2.2 meters,
and it fully clamped at both ends.

The PyMAPDL beam model is defined in the ``calculate_beam()`` function as follows:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: def calculate_beam(mapdl, force):
    :end-at: return UZ_node_12

This function returns the control parameter for the model, which is the displacement at the Z-direction on the node 12 (``UZ_node_12``).


MAPDL pool setup
================

Genetic algorithms are expensive in regard to the amount of calculations needed to reach an optimal solution. As shown earlier, many simulations must be performed to select, cross over, and mutate
all the chromosomes across all the populations.
For this reason, to speed up the process, it is desirable to have as many MAPDL instances as possible so that each one can calculate one chromosome fit function.

To manage multiple MAPDL instances, the best approach is to use the :class:`~ansys.mapdl.core.pool.MapdlPool` class.

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: Importing packages
    :end-at: print(pool)


Deflection target
=================

Because this is a demonstration example, the target displacement is calculated 
using the beam function itself with a force of 22840 :math:`N/cm^2`.

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: ## Define deflection target
    :end-at: print(f"Setting target to {target_displacement} for force {force}")


Genetic algorithm model
=======================

Introduction
------------

You use the `PyGAD <pygad_docs_>`_ library to configure the genetic algorithm.

.. epigraph::

    PyGAD is an open source Python library for building the genetic algorithm and optimizing machine learning algorithms.

    PyGAD supports different types of crossover, mutation, and parent selection operators.
    PyGAD allows different types of problems to be optimized using the genetic algorithm
    by customizing the fitness function. It works with both single-objective and
    multi-objective optimization problems.

    From PyGAD - Python Genetic Algorithm - https://pygad.readthedocs.io/en/latest/


Configuration
-------------

To configure the genetic algorithm, the following code is used:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: Set GA model
    :end-at: mutation_probability = 0.5

In the preceding code, the most import parameters are:

* ``sol_per_pop``: Number of solutions (chromosomes) within the population.
* ``num_generations``:  Number of genes in the solution/chromosome.
  In this case, because only one parameter is simulated (deflection Z at node 12),
  this value is 1.
* ``num_parents_mating``: Number of solutions to select as parents.
* ``parent_selection_type``:  Parent selection type. This example uses the ``rws`` type
  (for roulette wheel selection). For more information on parent selection type,
  see `Genetic algorithms with PyGAD: selection, crossover, mutation <ga_article_>`_
  by Lucy Linder.
* ``parallel_processing``: Number of parallel workers for the genetic
  algorithm and how these workers are created. They can be created as a ``"thread"``
  or ``"process"``. The example creates the workers as threads, and the amount is
  equal to the number of instances.


Helper functions
----------------

Additionally, for printing purposes, several helper functions are defined:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: import numpy as np
    :end-at: print("=============")


Fitness function
----------------

After all helper functions are defined, the fitness function can be defined:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: def fitness_func(ga_instance, solution, solution_idx):
    :end-at: return fitness_criteria

`PyMAPDL <pymapdl_main_>`_ and `PyGAD <pygad_docs_>`_ evaluate each chromosome using this function to
evaluate how fit is it and assign survival probability.


Mutation function
-----------------

To further demonstrate `PyGAD <pygad_docs_>`_ capabilities, this example uses a custom mutation
function.

This custom mutation function does two things:

* **To each chromosomes**, it adds a random value between the maximum and minimum of the population.
* **To two random chromosomes**, it additionally adds a random percentage of the mean across all the
  population between -10% and 10%. The random chromosomes are selected independently.
  This is to reduce the possibility of the function converging to a local minimal.

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: def mutation_func(offspring, ga_instance):
    :end-at: return offspring


Model assembly
--------------

Use the GA class to assemble all the parameters and functions
created to run the simulation:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: import pygad
    :end-at: To count the number of generations


Simulation
==========

Once the model is set, use the ``run()`` method to start the simulation:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: import time
    :end-at: print(f"Time spent (minutes): {(t1-t0)/60}")


Plot fitness and genes values
=============================

You can plot the solution fitness across generations and the evolution of gene
values using the following code:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: import os
    :end-at: print(f"Fitness value of the best solution = {solution_fitness}")


.. figure:: fitness_plot.png

   Fitness at each generation plot


.. figure:: genes.png

   Evolution of genes values


Model storage
==============

You can store the model in a file for later reuse:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: # To save the model data:
    :end-at: ga_instance.save(filename=filename)

Load the model:

.. literalinclude:: ml_ga_beam.py
    :language: python
    :start-at: # Load the saved GA instance
    :end-at: loaded_ga_instance.plot_fitness()


Simulation on an HPC cluster using SLURM
========================================

The previous steps create the PyMAPDL script.
To see the file, you can click this link
:download:`ml_ga_beam.py <ml_ga_beam.py>`.

To run the preceding script in an HPC environment, you must
create a Python environment, install the packages, and then run
this script.

1. Log into your HPC cluster.
   For more information, see :ref:`ref_hpc_login`

2. Create a virtual environment that is accessible from
   the compute nodes.

   .. code-block:: console

      user@machine:~$ python3 -m venv /home/user/.venv

   If you have problems when creating the virtual environment
   or accessing it from the compute nodes,
   see :ref:`ref_hpc_pymapdl_job`.

3. Install the requirements for this example from the
   :download:`requirements.txt <requirements.txt>` file.

4. Create the bash script ``job.sh``:

   .. code-block:: bash

      #!/bin/bash
      #SBATCH --job-name=ml_ga_beam
      #SBATCH --time=01:00:00
      #SBATCH --time=1:00:00
      #SBATCH --partition=%your_partition_name%
      #SBATCH --output=output_%j.txt
      #SBATCH --error=error_%j.txt

      # Commands to run
      echo "Running simulation..."
      source /home/user/.venv/bin/activate  # Activate venv
      python ml_ga_beam.py
      echo "Done"

   Remember to replace ``%your_partition_name%`` with your cluster
   partition.

5. Run the bash script using the `sbatch <slurm_sbatch_>`_ command:

   .. code-block:: console
    
      sbatch --nodes=1 --ntasks-per-node=10 job.sh

   The preceding command allocates 10 cores for the job.
   For optimal performance, this value should be higher than the number
   of MAPDL instances that the
   :class:`~ansys.mapdl.core.pool.MapdlPool` instance is creating.

