
.. _ref_hpc_pymapdl_job:

=======================
PyMAPDL on HPC clusters
=======================


Introduction
============

PyMAPDL communicates with MAPDL using the gRPC protocol.
This protocol offers the many advantages and features described in
:ref:`ref_project_page`.
One of these features is that it is not required to have both
PyMAPDL and MAPDL processes running on the same machine.
This possibility opens the door to many configurations, depending
on whether or not you run them both on the HPC compute nodes.
Additionally, you might be able interact with them (``interactive`` mode)
or not (``batch`` mode).

PyMAPDL takes advantage of HPC clusters to launch MAPDL instances
with increased resources.
PyMAPDL automatically sets these MAPDL instances to read the
scheduler job configuration (which includes machines, number
of CPUs, and memory), which allows MAPDL to use all the resources
allocated to that job.
For more information, see :ref:`ref_tight_integration_hpc`.

The following configurations are supported:

* :ref:`ref_pymapdl_batch_in_cluster_hpc`.
* :ref:`ref_pymapdl_interactive_in_cluster_hpc_from_login`


.. _ref_pymapdl_batch_in_cluster_hpc:

Batch job submission from the login node
========================================

Many HPC clusters allow their users to log into a machine using
``ssh``, ``vnc``, ``rdp``, or similar technologies and then submit a job
to the cluster from there.
This login machine, sometimes known as the *head node* or *entrypoint node*,
might be a virtual machine (VDI/VM).

In such cases, once the Python virtual environment with PyMAPDL is already
set and is accessible to all the compute nodes, launching a
PyMAPDL job from the login node is very easy to do using the ``sbatch`` command.
When the ``sbatch`` command is used, PyMAPDL runs and launches an MAPDL instance in
the compute nodes.
No changes are needed on a PyMAPDL script to run it on an SLURM cluster.

First the virtual environment must be activated in the current terminal.

.. code-block:: console

    user@entrypoint-machine:~$ export VENV_PATH=/my/path/to/the/venv
    user@entrypoint-machine:~$ source $VENV_PATH/bin/activate

Once the virtual environment is activated, you can launch any Python
script that has the proper Python shebang (``#!/usr/bin/env python3``).

For instance, assume that you want to launch the following ``main.py`` Python script:

.. code-block:: python
    :caption: main.py

    #!/usr/bin/env python3

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl(run_location="/home/ubuntu/tmp/tmp/mapdl", loglevel="debug")

    print(mapdl.prep7())
    print(f'Number of CPU: {mapdl.get_value("ACTIVE", 0, "NUMCPU")}')

    mapdl.exit()

You can run this command in your console:

.. code-block:: console

    (venv) user@entrypoint-machine:~$ sbatch main.py

Alternatively, you can remove the shebang from the Python file and use a
Python executable call:

.. code-block:: console

    (venv) user@entrypoint-machine:~$ sbatch python main.py

Additionally, you can change the number of cores used in your
job by setting the :envvar:`PYMAPDL_NPROC` environment variable to the desired value.

.. code-block:: console

    (venv) user@entrypoint-machine:~$ PYMAPDL_NPROC=4 sbatch main.py

For more applicable environment variables, see :ref:`ref_environment_variables`.

You can also add ``sbatch`` options to the command:

.. code-block:: console

    (venv) user@entrypoint-machine:~$ PYMAPDL_NPROC=4 sbatch  main.py


For instance, to launch a PyMAPDL job that starts a four-core MAPDL instance
on a 10-CPU SLURM job, you can run this command:

.. code-block:: console

    (venv) user@entrypoint-machine:~$ PYMAPDL_NPROC=4 sbatch --partition=qsmall --nodes=10 --ntasks-per-node=1 main.py


Using a submission script
-------------------------

If you need to customize your PyMAPDL job further, you can create a SLURM
submission script for submitting it. 
In this case, you must create two files:

- Python script with the PyMAPDL code
- Bash script that activates the virtual environment and calls the
  Python script

.. code-block:: python
    :caption: main.py

    from ansys.mapdl.core import launch_mapdl

    # Number of processors must be lower than the
    # number of CPU allocated for the job.
    mapdl = launch_mapdl(nproc=10)

    mapdl.prep7()
    n_proc = mapdl.get_value("ACTIVE", 0, "NUMCPU")
    print(f"Number of CPU: {n_proc}")

    mapdl.exit()


.. code-block:: bash
   :caption: job.sh

   #!/bin/bash
   # Set SLURM options
   #SBATCH --job-name=ansys_job            # Job name
   #SBATCH --partition=qsmall              # Specify the queue/partition name                  
   #SBATCH --nodes=5                       # Number of nodes
   #SBATCH --ntasks-per-node=2             # Number of tasks (cores) per node
   #SBATCH --time=04:00:00                 # Set a time limit for the job (optional but recommended)

   # Set env vars
   export MY_ENV_VAR=VALUE

   # Activate Python virtual environment
   source /home/user/.venv/bin/activate
   # Call Python script
   python main.py

To start the simulation, you use this code:

.. code-block:: console

    user@machine:~$ sbatch job.sh

In this case, the Python virtual environment does not need to be activated
before submission since it is activated later in the script.

The expected output of the job follows:

.. code-block:: text

    Number of CPU: 10.0


The bash script allows you to customize the environment before running the
Python script.
This bash script performs tasks such as creating environment variables,
moving files to different directories, and printing to ensure your
configuration is correct.


.. _ref_pymapdl_interactive_in_cluster_hpc:


.. _ref_pymapdl_interactive_in_cluster_hpc_from_login:

.. include:: launch_mapdl_entrypoint.rst


.. _ref_tight_integration_hpc:

Tight integration between MAPDL and the HPC scheduler
=====================================================

Since v0.68.5, PyMAPDL can take advantage of the tight integration
between the scheduler and MAPDL to read the job configuration and
launch an MAPDL instance that can use all the resources allocated
to that job.
For instance, if a SLURM job has allocated 8 nodes with 4 cores each,
then PyMAPDL launches an MAPDL instance that uses 32 cores
spawning across those 8 nodes.

This behavior can turn off by passing the
:envvar:`PYMAPDL_RUNNING_ON_HPC` environment variable
with a ``'false'`` value or passing the ``detect_hpc=False`` argument
to the :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>` function.

Alternatively, you can override these settings by either specifying
custom settings in the :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>`
function's arguments or using specific environment variables. 
For more information, see :ref:`ref_environment_variables`.
