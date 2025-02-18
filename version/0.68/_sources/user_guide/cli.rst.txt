
.. _ref_cli:

==============================
PyMAPDL command line interface
==============================

For your convenience, PyMAPDL package includes a command line interface
which allows you to launch, stop and list local MAPDL instances.


Launch MAPDL instances
======================

To start MAPDL, just type on your activated virtual environment:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl start
            Success: Launched an MAPDL instance (PID=23644) at 127.0.0.1:50052

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl start
            Success: Launched an MAPDL instance (PID=23644) at 127.0.0.1:50052

If you want to specify an argument, for instance the port, then you need to call
`launch_mapdl start`:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl start --port 50054
            Success: Launched an MAPDL instance (PID=18238) at 127.0.0.1:50054

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl start --port 50054
            Success: Launched an MAPDL instance (PID=18238) at 127.0.0.1:50054


This ``pymapdl start`` command aims to replicate the function
:func:`ansys.mapdl.core.launcher.launch_mapdl`. Hence, you can use
some of the arguments which this function allows.
For instance, you could specify the working directory:

.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl start --run_location C:\Users\user\temp\    
            Success: Launched an MAPDL instance (PID=32612) at 127.0.0.1:50052

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl start --run_location /home/user/tmp    
            Success: Launched an MAPDL instance (PID=32612) at 127.0.0.1:50052


For more information, see :func:`ansys.mapdl.core.launcher.launch_mapdl`.


Stop MAPDL instances
====================
You can use the ``pymapdl stop`` command to stop MAPDL instances like this:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl stop
            Success: Ansys instances running on port 50052 have been stopped.

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl stop
            Success: Ansys instances running on port 50052 have been stopped.


By default, the instance running on the port `50052` is stopped.

You can specify the instance running on a different port using `--port` argument:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl stop --port 50053
            Success: Ansys instances running on port 50053 have been stopped.

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl stop --port 50053
            Success: Ansys instances running on port 50053 have been stopped.


Or an instance with a given process id (PID):


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl stop --pid 40952
            Success: The process with PID 40952 and its children have been stopped.

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl stop --pid 40952
            Success: The process with PID 40952 and its children has been stopped.


Alternatively, you can stop all the running instances by using:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl stop --all      
            Success: Ansys instances have been stopped.

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl stop --all      
            Success: Ansys instances have been stopped.


List MAPDL instances and processes
==================================

You can also list MAPDL instances and processes.
If you want to list MAPDL process, just use the following command:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl list
            Name          Is Instance    Status      gRPC port    PID
            ------------  -------------  --------  -----------  -----
            ANSYS.exe     False          running         50052  35360
            ANSYS.exe     False          running         50052  37116
            ANSYS241.exe  True           running         50052  41644

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl list
            Name          Is Instance    Status      gRPC port    PID
            ------------  -------------  --------  -----------  -----
            ANSYS.exe     False          running         50052  35360
            ANSYS.exe     False          running         50052  37116
            ANSYS241.exe  True           running         50052  41644


If you want, to just list the instances (avoiding listing children MAPDL
processes), just type:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl list -i
            Name          Status      gRPC port    PID
            ------------  --------  -----------  -----
            ANSYS241.exe  running         50052  41644

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl list -i
            Name          Status      gRPC port    PID
            ------------  --------  -----------  -----
            ANSYS241.exe  running         50052  41644


You can also print other fields like the working directory (using `--cwd`)
or the command line (using `-c`).
Additionally, you can also print all the available information by using the
argument `--long` or `-l`:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl list -l
            Name          Is Instance    Status      gRPC port    PID  Command line                                                                                                                      Working directory
            ------------  -------------  --------  -----------  -----  --------------------------------------------------------------------------------------------------------------------------------  ---------------------------------------------------
            ANSYS.exe     False          running         50052  35360  C:\Program Files\ANSYS Inc\v241\ANSYS\bin\winx64\ANSYS.EXE -j file -b -i .__tmp__.inp -o .__tmp__.out -port 50052 -grpc           C:\Users\User\AppData\Local\Temp\ansys_ahmfaliakp
            ANSYS.exe     False          running         50052  37116  C:\Program Files\ANSYS Inc\v241\ANSYS\bin\winx64\ANSYS.EXE -j file -b -i .__tmp__.inp -o .__tmp__.out -port 50052 -grpc           C:\Users\User\AppData\Local\Temp\ansys_ahmfaliakp
            ANSYS241.exe  True           running         50052  41644  C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ansys241.exe -j file -np 2 -b -i .__tmp__.inp -o .__tmp__.out -port 50052 -grpc  C:\Users\User\AppData\Local\Temp\ansys_ahmfaliakp

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl list -l
            Name          Is Instance    Status      gRPC port    PID  Command line                                                               Working directory
            ------------  -------------  --------  -----------  -----  -------------------------------------------------------------------------  --------------------------------
            ANSYS         False          running         50052  35360  /ansys_inc/v241/ansys/bin/linx64/ansys -j file -port 50052 -grpc           /home/user/temp/ansys_ahmfaliakp
            ANSYS         False          running         50052  37116  /ansys_inc/v241/ansys/bin/linx64/ansys -j file -port 50052 -grpc           /home/user/temp/ansys_ahmfaliakp
            ANSYS241      True           running         50052  41644  /ansys_inc/v241/ansys/bin/linx64/ansys241 -j file -np 2 -port 50052 -grpc  /home/user/temp/ansys_ahmfaliakp


The converter module has its own command line interface to convert
MAPDL files to PyMAPDL. For more information, see 
:ref:`ref_cli_converter`.



.. _ref_cli_converter:

Convert APDL code
=================

After you have activated and installed the package as described
in :ref:`installation`, you can use the converter from your terminal.
Here is how you use the ``pymapdl convert`` command:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl convert mapdl.dat -o python.py
            
            The ``mapdl.dat`` file is successfully converted to the ``python.py`` file.


    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl convert mapdl.dat -o python.py
            
            File mapdl.dat successfully converted to python.py.

To obtain help on converter usage, options, and examples, type this command:


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> pymapdl convert --help
            
            
            Usage: pymapdl convert [OPTIONS] FILENAME_IN

            PyMAPDL CLI tool for converting MAPDL scripts to PyMAPDL scripts.

            USAGE:

            ...


    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ pymapdl convert --help
            
            Usage: pymapdl convert [OPTIONS] FILENAME_IN

            PyMAPDL CLI tool for converting MAPDL scripts to PyMAPDL scripts.

            USAGE:

            ...


The ``pymapdl convert`` command uses the
:func:`convert_script() <ansys.mapdl.core.convert_script>` function.
Hence, this command accepts most of this function's arguments.
