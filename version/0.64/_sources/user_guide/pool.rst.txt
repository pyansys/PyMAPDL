Create a pool of MAPDL instances
================================
PyMAPDL contains the :class:`MapdlLocalPool
<ansys.mapdl.core.MapdlLocalPool>` class to simplify creating multiple
local instances of the :class:`Mapdl <ansys.mapdl.core.mapdl._MapdlCore>`
class for batch processing. This can be used for the batch processing of a
set of input files, convergence analysis, or other batch related
processes.

This code creates a pool:

.. code:: pycon

    >>> from ansys.mapdl.core import LocalMapdlPool
    >>> pool = LocalMapdlPool(10)
    'MAPDL Pool with 10 active instances'

You can supply additional keyword arguments when creating the
pool. This code creates several instances with one CPU each running
at the current directory within their own isolated directories:

.. code:: pycon

    >>> import os
    >>> my_path = os.getcmd()
    >>> pool = LocalMapdlPool(10, nproc=1, run_location=my_path)
    Creating Pool: 100%|########| 10/10 [00:01<00:00,  1.43it/s]

You can access each individual MAPDL instance with this code:

.. code:: pycon

    >>> pool[0]
    <ansys.mapdl.core.mapdl.MapdlGrpc object at 0x7f66270cc8d0>

Note that this is a self-healing pool. If an instance of MAPDL dies
during a batch process, that instance is automatically restarted.
You can turn off this behavior by setting ``restart_failed=False`` when
creating the pool.


Run a set of input files
~~~~~~~~~~~~~~~~~~~~~~~~
You can use the pool to run a set of pre-generated input files using the
:func:`run_batch <ansys.mapdl.core.MapdlLocalPool.run_batch>` method. For
example, this code would run the first set of 20 verification files:

.. code:: pycon

    >>> from ansys.mapdl.core import examples
    >>> files = [examples.vmfiles["vm%d" % i] for i in range(1, 21)]
    >>> outputs = pool.run_batch(files)
    >>> len(outputs)
    20


Run a user function
~~~~~~~~~~~~~~~~~~~
You can use the pool to run a custom user function on each MAPDL
instance over a set of inputs. As in the example for the
:func:`run_batch <ansys.mapdl.core.MapdlLocalPool.run_batch>` function,
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


API description
~~~~~~~~~~~~~~~
For a comprehensive description, see :ref:`ref_pool_api`.
