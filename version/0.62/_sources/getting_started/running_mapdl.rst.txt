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


Debugging Launching MAPDL
-------------------------
For any number of reasons, Python may fail to launch MAPDL.  Here's
some approaches to debug the start:


Manually Set the Executable Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you have a non-standard install, ``pymapdl`` may be unable find
your installation.  If that's the case, provide the location of MAPDL
as the first parameter to ``launch_mapdl``.  For example, on Windows,
this will be:

.. code:: python

    >>> from ansys.mapdl.core import launch_mapdl
    >>> exec_loc = 'C:/Program Files/ANSYS Inc/v211/ansys/bin/winx64/ANSYS211.exe'
    >>> mapdl = launch_mapdl(exec_loc)

For Linux:

.. code:: python

    >>> from ansys.mapdl.core import launch_mapdl
    >>> exec_loc = '/usr/ansys_inc/v211/ansys/bin/ansys211'
    >>> mapdl = launch_mapdl(exec_loc)

Should this fail to launch or hang while launching, pass
``verbose_mapdl=True`` when using ``launch_mapdl``.  This will print
the output of MAPDL within Python and can be used to debug why MAPDL
isn't launching.  Output will be limited on Windows due to the way
MAPDL launches on Windows.


Debug Launch Issues
~~~~~~~~~~~~~~~~~~~
In some cases, it may be necessary to debug why MAPDL isn't launching
by running the launch command manually from the command line.  In
Windows, open up a command prompt and run the following (version
dependent) command:

.. code::

    "C:\Program Files\ANSYS Inc\v211\ansys\bin\winx64\ANSYS211.exe"

.. note::
   Powershell users can run the above without quotes.


For Linux:

.. code::

    /usr/ansys_inc/v211/ansys/bin/ansys211

Note that you should probably startup MAPDL in a temporary working
directory as MAPDL creates a several temporary files.

If this command doesn't launch, you could have a variety of issues, including:

  - License server setup
  - Running behind a VPN
  - Missing dependencies


Licensing Issues
----------------

PADT generally has a great blog regarding ANSYS issues, and licensing is always a common issue (for example `Changes to Licensing at ANSYS 2020R1 <https://www.padtinc.com/blog/15271-2/>`_).  Should you be responsible for maintaining Ansys licensing or have a personal install of Ansys, please check the online Ansys licensing documentation at `Installation and Licensing <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/prod_page.html?pn=Installation%20and%20Licensing&pid=InstallationAndLicensing&lang=en>`_.

For an in-depth explanation, please see the :download:`ANSYS Licensing Guide <ANSYS_Inc._Licensing_Guide.pdf>`.


VPN Issues
----------
Sometimes, MAPDL has issues starting when VPN software is running.  One
issue stems from MPI communication and can be solved by passing
the ``-smp`` option that sets the execution mode to "Shared Memory
Parallel", rather than the default "Distributed Memory Parallel" mode.

.. code::

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl(additional_switches='-smp')

While this approach has the disadvantage of using the potentially slower shared memory parallel mode, you'll at least be able to run MAPDL.  For more details on shared vs distributed memory, see `High-Performance Computing for Mechanical Simulations using ANSYS <https://www.ansys.com/-/media/Ansys/corporate/resourcelibrary/presentation/hpc-for-mechanical-ansys.pdf>`_.


Missing Dependencies on Linux
-----------------------------
Some Linux installations may be missing required dependencies.  Should
you get errors like ``libXp.so.6: cannot open shared object file: No
such file or directory``, you may be missing some necessary
dependencies.

CentOS
~~~~~~
On CentOS 7, you can install these with:

.. code::

    yum install openssl openssh-clients mesa-libGL mesa-libGLU motif libgfortran


Ubuntu
~~~~~~
Since MAPDL isn't officially supported on Ubuntu, it's a bit more
difficult to setup, but it's still possible.  On Ubuntu 20.04 with
Ansys 2021R1, install the following:

.. code::

    sudo apt-get install libx11-6 libgl1 libxm4 libxt6 libxext6 libxi6 libx11-6 libsm6 libice6 libxxf86vm1 libglu1

This takes care of everything except for ``libxp6``.  Should you be
using Ubuntu 16.04, you can install that simply with ``sudo apt
install libxp6``.  However, on Ubuntu 18.04+, you must manually
download and install the package.

Since ``libxpl6`` also pre-depends on ``multiarch-support``, which is
also outdated, it must be removed, otherwise you'll have a broken
package configuration.  The following step downloads and modifies the
``libxp6`` package to remove the ``multiarch-support`` dependency, and
then installs it via ``dpkg``.

.. code::

    cd /tmp
    wget http://ftp.br.debian.org/debian/pool/main/libx/libxp/libxp6_1.0.2-2_amd64.deb
    ar x libxp6_1.0.2-2_amd64.deb
    sudo tar xzf control.tar.gz
    sudo sed '/Pre-Depends/d' control -i
    sudo bash -c "tar c postinst postrm md5sums control | gzip -c > control.tar.gz"
    sudo ar rcs libxp6_1.0.2-2_amd64_mod.deb debian-binary control.tar.gz data.tar.xz
    sudo dpkg -i ./libxp6_1.0.2-2_amd64_mod.deb
