
.. _ref_hpc_slurm:

=====================
Introduction to SLURM
=====================


High performance computing (HPC) clusters are powerful systems designed to handle
computationally intensive tasks efficiently. SLURM (Simple Linux Utility for Resource
Management) is one of the most widely used job schedulers in HPC environments. This
page provides an overview of job submission using PyMAPDL and
SLURM on HPC clusters.


What is SLURM?
==============

SLURM is an open source workload manager and job scheduler designed for Linux
clusters of all sizes. It efficiently allocates resources (compute nodes, CPU
cores, memory, and GPUs) to jobs submitted by users.

For more information on SLURM, see the `SLURM documentation <slurm_docs_>`_.

Basic terms
===========

Descriptions follow of basic terms.

- **Nodes**: Individual computing servers within the cluster.
- **Compute node**: A type of node used only for running processes.
  It is not accessible from outside the cluster.
- **Login node**: A type of node used only for login and job submission.
  No computation should be performed on it. It is sometimes referred to as
  *virtual desktop infrastructure* (VDI).
- **Partition**: A logical grouping of nodes with similar characteristics (for 
  example, CPU architecture and memory size). 
- **Job**: A task submitted to SLURM for execution. 
- **Queue**: A waiting area where jobs are held until resources become available. 
- **Scheduler**: The component responsible for deciding which job gets 
  executed and when and where it gets executed.


Regular job submission workflow
===============================

.. _ref_hpc_login:

Log into the cluster
--------------------

You need access credentials and permissions to log in and submit jobs on the HPC cluster.
Depending on the login node configuration, you can log in using Virtual Network
Computing (VNC) applications or a terminal.

For example, you can log in to a login node using the terminal:

.. code-block:: console

    user@machine:~$ ssh username@login-node-hostname


Writing a SLURM batch script
----------------------------

A SLURM batch script is a shell script that specifies
job parameters and commands to execute. Here's a basic example:

**my_script.sh**

.. code-block:: bash
    
    #!/bin/bash
    #SBATCH --job-name=myjob
    #SBATCH --nodes=1
    #SBATCH --ntasks-per-node=4
    #SBATCH --time=01:00:00

    # Commands to run
    echo "Hello, SLURM!"
    srun my_executable


This script is run using ``srun`` and ``sbatch``.
Notice how comments in the file prefixed with ``#SBATCH`` describe the job configuration.
For more information on available ``srun`` and ``sbatch``
arguments, see `Slurm Workload Manager - srun <slurm_srun_>`_ and
`Slurm Workload Manager - sbatch <slurm_sbatch_>`_.

Submitting a job
----------------
To submit a job, use the ``srun`` command followed by the name of
the batch script:

.. code-block:: console
    
    user@machine:~$ srun my_script.sh

If you prefer to submit a batch job, you can use the ``sbatch`` command:

.. code-block:: console
    
    user@machine:~$ sbatch my_script.sh

You can specify each job setting using the command line. For example:

.. code-block:: console

    user@machine:~$ srun --nodes=2 my_script.sh

.. warning:: **Command line arguments versus in-file arguments**:
    Command line arguments do **NOT** overwrite the equivalent arguments
    written in the bash file. Hence, you must ensure that the argument that you 
    want to pass using the command line is not already present in the bash file.


Monitoring jobs
===============

View the job queue
------------------

The ``squeue`` command displays information about jobs that are currently queued or
running on the system.

**Basic usage:**

.. code-block:: bash

    squeue

**To see jobs from a specific user:**

.. code-block:: bash

    squeue -u username

**To filter jobs by partition:**

.. code-block:: bash

    squeue -p partition_name

**Common options:**

- ``-l`` or ``--long``: Displays detailed information about each job.
- ``--start``: Predicts and shows the start times for pending jobs.

Control the jobs and configuration
----------------------------------

The ``scontrol`` command provides a way to view and modify the SLURM configuration and state.
It's a versatile tool for managing jobs, nodes, partitions, and more.

**Show information about a job:**

.. code-block:: bash

    scontrol show job <jobID>

**Show information about a node:**

.. code-block:: bash

    scontrol show node nodename

**Hold and release jobs:**

- To hold a job (stop it from starting): ``scontrol hold <jobID>``
- To release a job on hold: ``scontrol release <jobID>``

Cancel jobs
-----------

The ``scancel`` command cancels a running or pending job.

**Cancel a specific job:**

.. code-block:: bash

    scancel <jobID>

**Cancel all jobs of a specific user:**

.. code-block:: bash

    scancel -u username

**Cancel jobs by partition:**

.. code-block:: bash

    scancel -p partition_name

**Common options:**

- ``--name=jobname``: Cancels all jobs with a specific name.
- ``--state=pending``: Cancels all jobs in a specific state,
  such as all pending jobs as shown.

Report accounting Information
-----------------------------

The ``sacct`` account reports job or job step accounting information
about active or completed jobs.

**Basic usage:**

.. code-block:: bash

    sacct

**To see information about jobs from a specific user:**

.. code-block:: bash

    sacct -u username

**To show information about a specific job or job range:**

.. code-block:: bash

    sacct -j <jobID>
    sacct -j <jobID_1>,<jobID_2>

**Common options:**

- ``--format``: Specifies which fields to display.
  For example, ``--format=JobID,JobName,State``.
- ``-S`` and ``-E``: Sets the start and end times for the report.
  For example, ``-S 2023-01-01 -E 2023-01-31``.

For more information, see the SLURM documentation
or use the ``man`` command (for example, ``man squeue``) to explore all available
options and their usage.



Best practices
==============
- Optimize resource usage to minimize job wait times and maximize cluster efficiency.
- Regularly monitor job queues and system resources to identify potential bottlenecks.
- Follow naming conventions for batch scripts and job names to maintain organization.
- Keep batch scripts and job submissions concise and well-documented 
  for reproducibility and troubleshooting.




Advanced configuration
======================

The following topics provide some advanced ideas for you to
explore when using PyMAPDL on HPC clusters.
In this section, these topics are just briefly described so
you can use online resources such as `SLURM documentation <slurm_docs_>`_.

Advanced job management
-----------------------

Job dependencies
~~~~~~~~~~~~~~~~
Specify dependencies between jobs using the ``--dependency`` flag.
Jobs can depend on completion, failure, or other criteria of previously submitted jobs.

Array jobs
~~~~~~~~~~

Submit multiple jobs as an array using the ``--array`` flag. Each array
element corresponds to a separate job, allowing for parallel execution of similar tasks.

Job arrays with dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Combine array jobs with dependencies for complex job
scheduling requirements. This allows for parallel execution while maintaining dependencies
between individual tasks.

Resource allocation and request
-------------------------------

Specify resources
~~~~~~~~~~~~~~~~~
Use SLURM directives in batch scripts to specify required
resources such as number of nodes, CPU cores, memory, and time limit.

Request resources
~~~~~~~~~~~~~~~~~
Use the ``--constraint`` flag to request specific hardware
configurations (for example, CPU architecture) or the ``--gres`` flag for requesting generic
resources like GPUs.

Resource Limits
~~~~~~~~~~~~~~~
Set resource limits for individual jobs using directives such as
``--cpus-per-task``, ``--mem``, and ``--time``.

