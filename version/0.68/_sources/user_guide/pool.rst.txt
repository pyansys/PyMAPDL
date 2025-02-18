.. _ref_pymapdl_pool:

Create a pool of MAPDL instances
================================

PyMAPDL contains the :class:`MapdlPool <ansys.mapdl.core.pool.MapdlPool>`
class to simplify creating multiple local instances of the 
:class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`
class for batch processing. This can be used for the batch processing of a
set of input files, convergence analysis, or other batch related
processes.

This code creates a pool:

.. code:: pycon

    >>> from ansys.mapdl.core import MapdlPool
    >>> pool = MapdlPool(10)
    'MAPDL Pool with 10 active instances'
    >>> pool.exit(block=True)

You can supply additional keyword arguments when creating the
pool. This code creates several instances with one CPU each running
at the current directory within their own isolated directories:

.. code:: pycon

    >>> import os
    >>> my_path = os.getcmd()
    >>> pool = MapdlPool(10, nproc=1, run_location=my_path)
    Creating Pool: 100%|########| 10/10 [00:01<00:00,  1.43it/s]

Additionally, you can group already running MAPDL instances into an
:class:`MapdlPool <ansys.mapdl.core.pool.MapdlPool>` instance by specifying
their ports when creating the pool.

.. code:: pycon

    >>> from ansys.mapdl.core import MapdlPool
    >>> pool = MapdlPool(port=[50082, 50083, 50084, 50085, 50086])
    'MAPDL Pool with 5 active instances'
    >>> pool.exit(block=True)

You can also specify a list of IP addresses to connect to: 

.. code:: pycon

    >>> pool = MapdlPool(ip=["127.0.0.2", "127.0.0.3", "127.0.0.4"])
    Creating Pool: 100%|########| 3/3 [00:01<00:00,  1.43it/s]

You can access each individual MAPDL instance with this code:

.. code:: pycon

    >>> pool[0]
    <ansys.mapdl.core.mapdl.MapdlGrpc object at 0x7f66270cc8d0>

Note that this is a self-healing pool. If an instance of MAPDL dies
during a batch process, that instance is automatically restarted.
You can turn off this behavior by setting ``restart_failed=False`` when
creating the pool.

Run a set of input files
------------------------

You can use the pool to run a set of pre-generated input files using the
:meth:`MapdlPool.run_batch <ansys.mapdl.core.MapdlPool.run_batch>` method. For
example, this code would run the first set of 20 verification files:

.. code:: pycon

    >>> from ansys.mapdl.core import examples
    >>> files = [examples.vmfiles["vm%d" % i] for i in range(1, 21)]
    >>> outputs = pool.run_batch(files)
    >>> len(outputs)
    20


Run an user function
--------------------

You can use the pool to run a custom user function on each MAPDL
instance over a set of inputs. As in the example for the
:meth:`MapdlPool.run_batch <ansys.mapdl.core.MapdlPool.run_batch>` method,
the following code uses a set of verification files. However, it implements
it as a function and outputs the final routine instead of the text
output from MAPDL.

.. code:: python

    completed_indices = []


    def func(mapdl, input_file, index):
        # input_file, index = args
        mapdl.clear()
        output = mapdl.input(input_file)
        completed_indices.append(index)
        return mapdl.parameters.routine


    inputs = [(examples.vmfiles["vm%d" % i], i) for i in range(1, 10)]
    output = pool.map(func, inputs, progress_bar=True, wait=True)
    [
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
        "Begin level",
    ]

    # Close the PyMAPDL pool.
    pool.exit()


Using next available instances
------------------------------

When working with many multiple instances, it might be more convenient to use
the :class:`MapdlPool <ansys.mapdl.core.pool.MapdlPool>` class within a context manager.
This can be accomplished using the :meth:`MapdlPool.next() <ansys.mapdl.core.MapdlPool.next>` method
as follows:

.. code:: python

    with pool.next() as mapdl:
        mapdl.prep7()
        ...

This context manager makes sure to set the instance as busy or locked while code
is executing the block.
Once the execution exits the context manager, the instance is set free or unlocked.
This context manager is particularly interesting when using it with threads.

.. code:: python

    from ansys.mapdl.core import MapdlPool
    from threading import Thread

    loads = [1e6, 2e6, 3e6]
    solutions = {each_load: None for each_load in loads}

    pool = MapdlPool(2)


    def calculate_model(mapdl, load):
        mapdl.prep7()
        mapdl.et(1, "SOLID5")
        mapdl.block(0, 10, 0, 20, 0, 30)
        mapdl.esize(10)
        mapdl.vmesh("ALL")
        mapdl.units("SI")  # SI - International system (m, kg, s, K).

        # Define a material (nominal steel in SI)
        mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
        mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
        mapdl.mp("PRXY", 1, 0.3)  # Poisson's Ratio

        # Fix the left-hand side.
        mapdl.nsel("S", "LOC", "Z", 0)
        mapdl.d("ALL", "UX")
        mapdl.d("ALL", "UY")
        mapdl.d("ALL", "UZ")

        mapdl.nsel("S", "LOC", "Z", 30)
        mapdl.f("ALL", "FX", load)

        mapdl.allsel()
        mapdl.solu()
        mapdl.antype("STATIC")
        mapdl.solve()
        mapdl.finish()

        # Get maximum displacement in the X direction on the top surface.
        mapdl.nsel("S", "LOC", "Z", 30)
        solutions[load] = mapdl.post_processing.nodal_displacement("X").max()


    def threaded_function(load):
        with pool.next() as mapdl:
            value = calculate_model(mapdl, load)


    if __name__ == "__main__":
        threads = []
        for load in loads:
            t = Thread(target=threaded_function, args=[load])
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        for k, v in solutions.items():
            print(f"Load: {k:5.2f}\tDisplacement: {v:8.6f}")


You can also use the :meth:`MapdlPool.next_available() <ansys.mapdl.core.MapdlPool.next_available>` method
to obtain an available :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>` instance, but in that case,
you must manage the lock with the :meth:`Mapdl.locked <ansys.mapdl.core.mapdl._MapdlCore.locked>` method.

.. code:: python

    pool = MapdlPool(4)

    mapdl, i = pool.next_available(return_index=True)

    mapdl.locked = True

    mapdl.prep7()
    # More code...
    # ...
    #
    mapdl.locked = False  # Important for the instance to be seen as available.


Close the PyMAPDL pool
----------------------

You can close the PyMAPDL pool with the
:meth:`MapdlPool.exit() <ansys.mapdl.core.MapdlPool.exit>` command.

.. code:: pycon
    
    >>> pool.exit()


API description
---------------

For a comprehensive description, see :ref:`ref_pool_api`.
