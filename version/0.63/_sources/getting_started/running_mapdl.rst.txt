.. _using_standard_install:

***************************************
Using PyMAPDL from the Standard Install
***************************************

The pyansys ``ansys-mapdl-core`` package requires either a local or
remote instance of MAPDL to communicate with it.  This section covers
launching and interfacing with MAPDL from a local instance by
launching it from Python.

Installing MAPDL
----------------

MAPDL is installed by default from the standard installer.  When
installing ANSYS, verify that the "Mechanical Products" option is
checked under the "Structural Mechanics" option.  The standard
installer options may change, but for reference see the following
figure.

.. figure:: ../images/unified_install_2019R1.jpg
    :width: 400pt


Launching MAPDL
---------------

Launching MAPDL locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``launch_mapdl`` function to have Python startup MAPDL and
automatically connect to it:

.. code:: python

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()
    >>> print(mapdl)

    Product:             ANSYS Mechanical Enterprise
    MAPDL Version:       RELEASE  2021 R1           BUILD 21.0
    PyMAPDL Version:     Version: 0.57.0


This is the easiest and fastest way to get PyMAPDL up and running. 
But you need to have an ANSYS license server installed locally. 

Launching a gRPC MAPDL session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can start MAPDL from the command line and then connect to it.
To launch MAPDL on Windows (assuming a ``C:/Program Files/ANSYS Inc/v211`` installation) use:

.. code::

    C:/Program Files/ANSYS Inc/v211/ansys/bin/winx64/ANSYS211.exe -grpc

Or on Linux (assuming a ``/usr/ansys_inc`` installation):

.. code::

    /usr/ansys_inc/v211/ansys/bin/ansys211 -grpc

This starts up MAPDL in gRPC mode, and MAPDL should output:

.. code::

     Start GRPC Server

     ##############################
     ### START GRPC SERVER      ###
     ##############################

     Server Executable   : MapdlGrpc Server
     Server listening on : 0.0.0.0:50052

You can configure the port MAPDL starts on with the ``-port`` argument.  For
example, you can startup the server to listen for connections at 
port 50005 with:

.. code::

    /usr/ansys_inc/v211/ansys/bin/ansys211 -port 50005 -grpc

You can also configure the IP. 
However because of an ANSYS limitation to receive
strings from command line, the IP needs to be read from an external file 
called ``mylocal.ip``. This file is read automatically from the directory where 
MAPDL is running.

You can then setup the IP in Windows (Powershell and CMD) with:

.. code::
    
    echo "127.0.0.1" > mylocal.ip
    C:/Program Files/ANSYS Inc/v211/ansys/bin/winx64/ANSYS211.exe -grpc


or in Linux with:

.. code::
    
    echo "127.0.0.1" > mylocal.ip
    /usr/ansys_inc/v211/ansys/bin/ansys211 -grpc


Connecting to a gRPC MAPDL session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A MAPDL gRPC server can be connected to either from the same host, or from an
external host.  For example, you can connect to a MAPDL service
running **locally** with:

.. code::

    >>> from ansys.mapdl.core import Mapdl
    >>> mapdl = Mapdl()


This assumes that your MAPDL service is running locally on the default ip 
(127.0.0.1) and on the default port (50052).  

If you want to connect to a **remote** instance of MAPDL and you know the IP 
address of that instance, you can connect to it.
For example, if on your local network at IP ``192.168.0.1`` there is a
computer running MAPDL on the port 50052, you can connect to it with

.. code::

    >>> mapdl = Mapdl('192.168.0.1', port=50052)

Alternatively you can use a hostname:

.. code:: python

    >>> mapdl = Mapdl('myremotemachine', port=50052)

Please note that you must have started MAPDL in gRPC mode in the PC with
the mentioned IP/hostname for this to work.
If you have MAPDL installed on your local host, you
can use ``launch_mapdl`` to both start and connect to MAPDL.

If you find any problem launching PyMAPDL, please check :ref:`debugging_launch_mapdl`
