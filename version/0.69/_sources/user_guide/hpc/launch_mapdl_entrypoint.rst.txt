
Interactive MAPDL instance launched from the login node
=======================================================

Starting the instance
---------------------

If you are already logged in a login node, you can launch an MAPDL instance as a SLURM job and
connect to it.
To accomplish this, run these commands in your login node.

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl(launch_on_hpc=True)

PyMAPDL submits a job to the scheduler using the appropriate commands.
In case of SLURM, it uses the ``sbatch`` command with the ``--wrap`` argument
to pass the MAPDL command line to start.
Other scheduler arguments can be specified using the ``scheduler_options``
argument as a Python :class:`dict`:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> scheduler_options = {"nodes": 10, "ntasks-per-node": 2}
    >>> mapdl = launch_mapdl(launch_on_hpc=True, nproc=20, scheduler_options=scheduler_options)


.. note::
    PyMAPDL cannot infer the number of CPUs that you are requesting from the scheduler.
    Hence, you must specify this value using the ``nproc`` argument.

The double minus (``--``) common in the long version of some scheduler commands
are added automatically if PyMAPDL detects it is missing and the specified
command is long more than 1 character in length).
For instance, the ``ntasks-per-node`` argument is submitted as ``--ntasks-per-node``.

Or, a single Python string (:class:`str`) is submitted:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> scheduler_options = "-N 10"
    >>> mapdl = launch_mapdl(launch_on_hpc=True, scheduler_options=scheduler_options)

.. warning::
    Because PyMAPDL is already using the ``--wrap`` argument, this argument
    cannot be used again.

The values of each scheduler argument are wrapped in single quotes (`'`).
This might cause parsing issues that can cause the job to fail after successful
submission.

PyMAPDL passes all the environment variables of the
user to the new job and to the MAPDL instance.
This is usually convenient because many environmental variables are
needed to run the job or MAPDL command.
For instance, the license server is normally stored in the :envvar:`ANSYSLMD_LICENSE_FILE` environment variable.
If you prefer not to pass these environment variables to the job, use the SLURM argument
``--export`` to specify the desired environment variables.
For more information, see `SLURM documentation <slurm_docs_>`_.


Working with the instance
-------------------------

Once the :class:`Mapdl <ansys.mapdl.core.mapdl.MapdlBase>` object has been created,
it does not differ from a normal :class:`Mapdl <ansys.mapdl.core.mapdl.MapdlBase>`
instance.
You can retrieve the IP of the MAPDL instance as well as its hostname:

.. code:: pycon

    >>> mapdl.ip
    '123.45.67.89'
    >>> mapdl.hostname
    'node0'

You can also retrieve the SLURM job ID:

.. code:: pycon

    >>> mapdl.jobid
    10001

If you want to check whether the instance has been launched using a scheduler,
you can use the :attr:`mapdl_on_hpc <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.mapdl_on_hpc>`
attribute:

.. code:: pycon

    >>> mapdl.mapdl_on_hpc
    True


Sharing files
^^^^^^^^^^^^^

Most of the HPC clusters share the login node filesystem with the compute nodes,
which means that you do not need to do extra work to upload or download files to the MAPDL
instance. You only need to copy them to the location where MAPDL is running.
You can obtain this location with the
:attr:`directory <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.directory>` attribute.

If no location is specified in the :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>`
function, then a temporal location is selected.
It is a good idea to set the ``run_location`` argument to a directory that is accessible
from all the compute nodes.
Normally anything under ``/home/user`` is available to all compute nodes.
If you are unsure where you should launch MAPDL, contact your cluster administrator.

Additionally, you can use methods like the :meth:`upload <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.upload>`
and :meth:`download <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.download>` to
upload and download files to and from the MAPDL instance respectively.
You do not need ``ssh`` or another similar connection.
However, for large files, you might want to consider alternatives.


Exiting MAPDL
-------------

Exiting MAPDL, either intentionally or unintentionally, stops the job.
This behavior occurs because MAPDL is the main process at the job. Thus, when finished,
the scheduler considers the job done.

To exit MAPDL, you can use the :meth:`exit() <ansys.mapdl.core.Mapdl.exit>` method.
This method exits MAPDL and sends a signal to the scheduler to cancel the job.

.. code-block:: python

    mapdl.exit()

When the Python process you are running PyMAPDL on finishes without errors, and you have not
issued the :meth:`exit() <ansys.mapdl.core.Mapdl.exit>` method, the garbage collector
kills the MAPDL instance and its job. This is intended to save resources.

If you prefer that the job is not killed, set the following attribute in the
:class:`Mapdl <ansys.mapdl.core.mapdl.MapdlBase>` class:

.. code-block:: python

    mapdl.finish_job_on_exit = False


In this case, you should set a timeout in your job to avoid having the job
running longer than needed.


Handling crashes on an HPC
^^^^^^^^^^^^^^^^^^^^^^^^^^

If MAPDL crashes while running on an HPC, the job finishes right away.
In this case, MAPDL disconnects from MAPDL.
PyMAPDL retries to reconnect to the MAPDL instance up to 5 times, waiting
for up to 5 seconds.
If unsuccessful, you might get an error like this:

.. code-block:: text

    MAPDL server connection terminated unexpectedly while running:
    /INQUIRE,,DIRECTORY,,
    called by:
    _send_command

    Suggestions:
    MAPDL *might* have died because it executed a not-allowed command or ran out of memory.
    Check the MAPDL command output for more details.
    Open an issue on GitHub if you need assistance: https://github.com/ansys/pymapdl/issues
    Error:
    failed to connect to all addresses; last error: UNKNOWN: ipv4:127.0.0.1:50052: Failed to connect to remote host: connect: Connection refused (111)
    Full error:
    <_InactiveRpcError of RPC that terminated with:
    status = StatusCode.UNAVAILABLE
    details = "failed to connect to all addresses; last error: UNKNOWN: ipv4:127.0.0.1:50052: Failed to connect to remote host: connect: Connection refused (111)"
    debug_error_string = "UNKNOWN:Error received from peer  {created_time:"2024-10-24T08:25:04.054559811+00:00", grpc_status:14, grpc_message:"failed to connect to all addresses; last error: UNKNOWN: ipv4:127.0.0.1:50052: Failed to connect to remote host: connect: Connection refused (111)"}"
    >

The data of that job is available at :attr:`directory <ansys.mapdl.core.Mapdl.directory>`.
You should set the run location using the ``run_location`` argument.

While handling this exception, PyMAPDL also cancels the job to avoid resources leaking.
Therefore, the only option is to start a new instance by launching a new job using
the :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>` function.

User case on a SLURM cluster
----------------------------

Assume a user wants to start a remote MAPDL instance in an HPC cluster
to interact with it.
The user would like to request 10 nodes, and 1 task per node (to avoid clashes
between MAPDL instances). 
The user would like to also request 64 GB of RAM.
Because of administration logistics, the user must use the machines in
the ``supercluster01`` partition.
To make PyMAPDL launch an instance like that on SLURM, run the following code:

.. code-block:: python

    from ansys.mapdl.core import launch_mapdl
    from ansys.mapdl.core.examples import vmfiles

    scheduler_options = {
        "nodes": 10,
        "ntasks-per-node": 1,
        "partition": "supercluster01",
        "memory": 64,
    }
    mapdl = launch_mapdl(launch_on_hpc=True, nproc=10, scheduler_options=scheduler_options)

    num_cpu = mapdl.get_value("ACTIVE", 0, "NUMCPU")  # It should be equal to 10

    mapdl.clear()  # Not strictly needed.
    mapdl.prep7()

    # Run an MAPDL script
    mapdl.input(vmfiles["vm1"])

    # Let's solve again to get the solve printout
    mapdl.solution()
    output = mapdl.solve()
    print(output)

    mapdl.exit()  # Kill the MAPDL instance


PyMAPDL automatically sets MAPDL to read the job configuration (including machines,
number of CPUs, and memory), which allows MAPDL to use all the resources allocated
to that job.
