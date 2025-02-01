.. _api_logging:

Logging
=======
To make the logging of events consistent, PyMAPDL has a specific
logging architecture with global and local logging instances.

For these two types of loggers, the default log message format is:

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()
    >>> mapdl._log.info("This is an useful message")
      LEVEL - INSTANCE NAME - MODULE - FUNCTION - MESSAGE
      INFO - GRPC_127.0.0.1:50052 -  test - <module> - This is an useful message

The ``instance_name`` field depends on the name of the MAPDL instance,
which might not be set yet when the log record is created (for
example, during the initialization of the library).  If an MAPDL
instance is not yet created, this field might be empty.

Because both types of loggers are based in the Python module
``logging``, you can use any of the tools provided in this module to
extend or modify these loggers.


Logging API
-----------
.. currentmodule:: ansys.mapdl.core.logging

.. autosummary::
   :toctree: _autosummary

   Logger
