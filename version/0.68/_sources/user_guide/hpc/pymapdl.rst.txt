.. _ref_hpc_pymapdl:


=============================
PyMAPDL on SLURM HPC clusters
=============================

.. _ref_hpc_pymapdl_job:

Submit a PyMAPDL job
====================

To submit a PyMAPDL job, you must create two files:

- Python script with the PyMAPDL code
- Bash script that activates the virtual environment and calls the Python script

**Python script:** ``pymapdl_script.py``

.. code-block:: python

    from ansys.mapdl.core import launch_mapdl

    # Number of processors must be lower than the
    # number of CPUs allocated for the job.
    mapdl = launch_mapdl(nproc=10)

    mapdl.prep7()
    n_proc = mapdl.get_value("ACTIVE", 0, "NUMCPU")
    print(f"Number of CPUs: {n_proc}")

    mapdl.exit()


**Bash script:** ``job.sh``

.. code-block:: bash

    source /home/user/.venv/bin/activate
    python pymapdl_script.py

To start the simulation, you use this code:

.. code-block:: console

    user@machine:~$ srun job.sh


The bash script allows you to customize the environment before running the Python script.
This bash script performs such tasks as creating environment variables, moving to
different directories, and printing to ensure your configuration is correct. However,
this bash script is not mandatory.
You can avoid having the ``job.sh`` bash script if the virtual environment is activated
and you pass all the environment variables to the job:

.. code-block:: console

    user@machine:~$ source /home/user/.venv/bin/activate
    (.venv) user@machine:~$ srun python pymapdl_script.py --export=ALL


The ``--export=ALL`` argument might not be needed, depending on the cluster configuration.
Furthermore, you can omit the Python call in the preceding command if you include the
Python shebang (``#!/usr/bin/python3``) in the first line of the ``pymapdl_script.py`` script.

.. code-block:: console

    user@machine:~$ source /home/user/.venv/bin/activate
    (.venv) user@machine:~$ srun pymapdl_script.py --export=ALL

If you prefer to run the job in the background, you can use the ``sbatch``
command instead of the ``srun`` command. However, in this case, the Bash file is needed:

.. code-block:: console

    user@machine:~$ sbatch job.sh
    Submitted batch job 1

Here is the expected output of the job:

.. code-block:: text

    Number of CPUs: 10.0

