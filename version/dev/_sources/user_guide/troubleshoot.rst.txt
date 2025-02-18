.. _ref_troubleshooting:


Troubleshooting PyMAPDL
=======================


To help you resolve any problems that you might have when using PyMAPDL,
some of the most common problems and frequently asked questions are posted here.

.. _ref_debug_pymapdl:

Debug in PyMAPDL
----------------

If you are having trouble with PyMAPDL, you can record some internal
logs into a file using a logger. 
This file can be examined to help to identify any issue. 

You can set the logger output file to be ``mylog.log`` by
running the following commands in a Python terminal or at the beginning of your
script:

.. code:: python

    from ansys.mapdl.core import LOG

    LOG.setLevel("DEBUG")
    LOG.log_to_file("mylog.log")

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl(loglevel="DEBUG")

You can attach this file to a bug report in the PyMAPDL GitHub repository for further investigation.
If you are not able to identify the issue, you can open a discussion on the
`PyMAPDL Discussions page <pymapdl_discussions_>`_.
If you believe you have found a bug, create an issue on the `PyMAPDL Issues page <pymapdl_issues_>`_.


.. _ref_launching_issue:

Launching issues
----------------

There are several issues that can cause MAPDL not to launch, including:

- `Connection timeout`_
- `Testing MAPDL launching`_
- `Licensing issues`_
- `Virtual private network (VPN) issues`_
- `Missing dependencies on Linux`_
- `Conflicts with student version`_
- `Incorrect environment variables`_
- `Using a proxy server`_
- `Firewall settings`_

If you cannot find your issue, see `More help needed?`_.


Connection timeout
~~~~~~~~~~~~~~~~~~

In some networks, MAPDL might take longer than expected to connect to the license server or to the remote instance.
In those cases, you might see this message:


.. code:: output

    PyMAPDL is taking longer than expected to connect to an MAPDL session. Checking if there are any available licenses...


First try increasing the starting timeout using this code:

.. code:: python

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl(start_timeout=60)

Or if you are connecting to a remote instance you can use:

.. code:: python

    from ansys.mapdl.core import Mapdl

    mapdl = Mapdl(timeout=60)


Testing MAPDL launching
~~~~~~~~~~~~~~~~~~~~~~~

In some cases, it may be necessary to run the launch command manually from the command line.


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        Open up a command prompt and run the version-dependent command:

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> "C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe"
        
        .. note:: PowerShell users can run the preceding command without quotes.

    .. tab-item:: Linux
        :sync: oskey
        
        Run the version-dependent command:

        .. code:: console

            (.venv) user@machine:~$ /usr/ansys_inc/v241/ansys/bin/ansys241


You should start MAPDL in a temporary working directory because MAPDL creates
several temporary files.

You can specify a directory by launching MAPDL from the temporary directory:


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> mkdir temporary_directory
            (.venv) PS C:\Users\user\pymapdl> cd temporary_directory
            (.venv) PS C:\Users\user\pymapdl> & 'C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe'

        Or, you can specify the directory using the ``-dir`` flag:

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> mkdir temporary_directory
            (.venv) PS C:\Users\user\pymapdl> & 'C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe' -dir "C:\ansys_job\mytest1"


    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: console

            (.venv) user@machine:~$ mkdir temporary_directory
            (.venv) user@machine:~$ cd temporary_directory
            (.venv) user@machine: temporary_directory $ /usr/ansys_inc/v241/ansys/bin/ansys241

        Or, you can specify the directory using the ``-dir`` flag:

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> mkdir /tmp/ansys_tmp/job1
            (.venv) PS C:\Users\user\pymapdl> /usr/ansys_inc/v241/ansys/bin/ansys241 -dir /tmp/ansys_tmp/job1


If this command doesn't launch MAPDL, look at the command output:

.. vale off

.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> & 'C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe'
            *** ERROR ***
            Another Ansys job with the same job name (file) is already running in this
            directory or the file.lock file has not been deleted from an abnormally
            terminated Ansys run. To disable this check, set the ANSYS_LOCK environment
            variable to OFF.

    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: console

            (.venv) user@machine:~$ /usr/ansys_inc/v241/ansys/bin/ansys241
            *** ERROR ***
            Another Ansys job with the same job name (file) is already running in this
            directory or the file.lock file has not been deleted from an abnormally
            terminated Ansys run. To disable this check, set the ANSYS_LOCK environment
            variable to OFF.

.. vale on

Licensing issues
~~~~~~~~~~~~~~~~

Incorrect license server configuration can prevent MAPDL from being able to get a valid license.
In such cases, you might see output **similar** to:


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> & 'C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe'

            ANSYS LICENSE MANAGER ERROR:

            Maximum licensed number of demo users already reached.


            ANSYS LICENSE MANAGER ERROR:

            Request name mech_2 does not exist in the licensing pool.
            No such feature exists.
            Feature:          mech_2
            License path:  C:\Users\user\AppData\Local\Temp\\cb0400ba-6edb-4bb9-a333-41e7318c007d;
            FlexNet Licensing error:-5,357

    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: console

            (.venv) user@machine:~$ /usr/ansys_inc/v241/ansys/bin/ansys241

            ANSYS LICENSE MANAGER ERROR:

            Maximum licensed number of demo users already reached.


            ANSYS LICENSE MANAGER ERROR:

            Request name mech_2 does not exist in the licensing pool.
            No such feature exists.
            Feature:          mech_2
            FlexNet Licensing error:-5,357


PADT has a great blog regarding ANSYS issues, and licensing is always a common issue. For 
example, see `Changes to Licensing at ANSYS 2020R1 <padt_licensing_>`_. If you are responsible
for maintaining Ansys licensing or have a personal install of Ansys, see the online
`Ansys Installation and Licensing documentation <ansys_installation_and_licensing_>`_.

For more comprehensive information, download the :download:`ANSYS Licensing Guide <lic_guide.pdf>`.

Incorrect licensing environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The license server can be also specified using the environment variable :envvar:`ANSYSLMD_LICENSE_FILE`.
The following code examples show how you can see the value of this environment variable on
either Windows or Linux.


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> $env:ANSYSLMD_LICENSE_FILE
            1055@1.1.1.1

    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: console

            (.venv) user@machine:~$ printenv | grep ANSYSLMD_LICENSE_FILE
            1055@1.1.1.1


.. _vpn_issues_troubleshooting:

Virtual private network (VPN) issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From ANSYS 2022 R2 to ANSYS 2021 R1, MAPDL has issues launching when VPN software is running.
One issue stems from MPI communication and can be solved by either passing
the ``-smp`` option to set the execution mode to "Shared Memory
Parallel" which disables the default "Distributed Memory Parallel".
Or using a different MPI compilation, for example, if you are using Windows, you can pass
``-mpi msmpi`` to use the Microsoft MPI library instead of the default Intel MPI library.
This issue does not affect the Linux version of MAPDL.

.. note:: In you are using Windows in any of the versions from ANSYS 2022 R2 to ANSYS 2021 R1,
   the default compiler is Microsoft MPI when the MAPDL instance is launched by PyMAPDL.

.. code:: pycon

    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl(additional_switches="-smp")

While this approach has the disadvantage of using the potentially slower shared
memory parallel mode, you'll at least be able to run MAPDL.
For more information on shared versus distributed memory, see
`High-Performance Computing for Mechanical Simulations using ANSYS <ansys_parallel_computing_guide_>`_.


In addition, if your device is inside a VPN, MAPDL might not be able to correctly
resolve the IP of the license server. Verify that the hostname or IP address of the license server
is correct.

On Windows, you can find the license configuration file that points to the license server in ``C:\Program Files\ANSYS Inc\Shared Files\Licensing\ansyslmd.ini``.


.. _missing_dependencies_on_linux:

Missing dependencies on Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some Linux installations might be missing required dependencies. If
you get errors like ``libXp.so.6: cannot open shared object file: No
such file or directory``, you are likely missing some necessary
dependencies.


.. tab-set::

    .. tab-item:: CentOS 7 and Rocky 8

        On CentOS 7, you can install missing dependencies with:

        .. code:: console

            user@machine:~$  yum install openssl openssh-clients mesa-libGL mesa-libGLU motif libgfortran

    .. tab-item:: Ubuntu 22.04

        On Ubuntu 22.04, use this code to install the needed dependencies:

        .. code:: console

            user@machine:~$ apt-get update

            # Install dependencies
            user@machine:~$ apt-get install -y \
                openssh-client \
                libgl1 \
                libglu1 \
                libxm4 \
                libxi6

        The preceding code takes care of everything except for ``libxp6``, which you must install
        using this code:

        .. code:: console

            # This is a workaround
            # Source: https://bugs.launchpad.net/ubuntu/+source/libxp/+bug/1517884
            user@machine:~$ apt install -y software-properties-common
            user@machine:~$ add-apt-repository -y ppa:zeehio/libxp
            user@machine:~$ apt-get update
            user@machine:~$ apt-get install -y libxp6

    .. tab-item:: Ubuntu 20.04 through 18.04

        If you are using Ubuntu 20.04 through 18.04, you can install missing dependencies with:

        .. code:: console

            user@machine:~$ apt-get update

            # Install dependencies
            user@machine:~$ apt-get install -y \
                openssh-client \
                libgl1 \
                libglu1 \
                libxm4 \
                libxi6


        The preceding code takes care of everything except for ``libxp6``, which you must
        manually download and install.

        Because ``libxpl6`` pre-depends on ``multiarch-support``, which is
        also outdated, it must be removed. Otherwise you'll have a broken
        package configuration. The following code downloads and modifies the
        ``libxp6`` package to remove the ``multiarch-support`` dependency and
        then installs it via the ``dpkg`` package.

        .. code:: console

            cd /tmp
            wget http://ftp.br.debian.org/debian/pool/main/libx/libxp/libxp6_1.0.2-2_amd64.deb
            ar x libxp6_1.0.2-2_amd64.deb
            sudo tar xzf control.tar.gz
            sudo sed '/Pre-Depends/d' control -i
            sudo bash -c "tar c postinst postrm md5sums control | gzip -c > control.tar.gz"
            sudo ar rcs libxp6_1.0.2-2_amd64_mod.deb debian-binary control.tar.gz data.tar.xz
            sudo dpkg -i ./libxp6_1.0.2-2_amd64_mod.deb


    .. tab-item:: Ubuntu 16.04 and older

        If you are using Ubuntu 16.04, you can install missing dependencies with:

        .. code:: console

            user@machine:~$ apt-get update

            # Install dependencies
            user@machine:~$ apt-get install -y \
                openssh-client \
                libgl1 \
                libglu1 \
                libxm4 \
                libxi6 \
                libxp6


An useful resource is `HOW TO - Install Ansys' Required Linux Packages & Libraries <simutech_linux_dependencies_>`_.

.. _conflicts_student_version:

Conflicts with student version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although you can install Ansys together with other Ansys products or versions, on Windows, you
should not install a student version of an Ansys product together with its non-student version.
For example, installing both the Ansys MAPDL 2022 R2 Student Version and Ansys MAPDL 2022
R2 might cause license conflicts due to overwriting of environment variables. Having different
versions, for example the Ansys MAPDL 2022 R2 Student Version and Ansys MAPDL 2021 R1,
is fine.

If you experience issues, you should edit these environment variables to remove any
reference to the student version: ``ANSYSXXX_DIR``, ``AWP_ROOTXXX``, and
``CADOE_LIBDIRXXX``. 
Visit `Incorrect environment variables`_ for information on how to set these environment variables
to the correct location.

.. note::
   By default if a student version is detected, PyMAPDL launches the MAPDL instance in
   ``SMP`` mode, unless another MPI option is specified.

Incorrect environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using a non-standard install, you might need to manually set the
environment variables ``ANSYSXXX_DIR``, ``AWP_ROOTXXX``, and
``CADOE_LIBDIRXXX`` to the correct location. 
The three-digit MAPDL version appears where ``XXX`` is
shown. For Ansys MAPDL 2024 R2, ``242`` appears where ``XXX`` is shown.


.. vale off


.. tab-set::

    .. tab-item:: AWP_ROOT242
        :sync: envvarskey

        .. code:: pwsh-session

           PS echo $env:AWP_ROOT242
           C:\Program Files\ANSYS Inc\ANSYS Student\v242

    .. tab-item:: ANSYS242_DIR
        :sync: envvarskey

        .. code:: pwsh-session

           PS echo $env:ANSYS242_DIR
           C:\Program Files\ANSYS Inc\ANSYS Student\v242\ANSYS

    .. tab-item:: CADOE_LIBDIR242
        :sync: envvarskey

        .. code:: pwsh-session

           PS echo $env:CADOE_LIBDIR242
           C:\Program Files\ANSYS Inc\ANSYS Student\v242\CommonFiles\Language\en-us


Set these environment variables to custom values for the terminal session:

.. tab-set::

    .. tab-item:: AWP_ROOT242
        :sync: envvarskey

        .. code:: pwsh-session

           PS $env:AWP_ROOT242 = "C:\Program Files\ANSYS Inc\v242"
           PS echo $env:AWP_ROOT242
           C:\Program Files\ANSYS Inc\v242

    .. tab-item:: ANSYS242_DIR
        :sync: envvarskey

        .. code:: pwsh-session

           PS $env:ANSYS242_DIR = "C:\Program Files\ANSYS Inc\v242\ANSYS"
           PS echo $env:ANSYS242_DIR
           C:\Program Files\ANSYS Inc\v242\ANSYS

    .. tab-item:: CADOE_LIBDIR242
        :sync: envvarskey

        .. code:: pwsh-session

           PS $env:CADOE_LIBDIR242 = "C:\Program Files\ANSYS Inc\v242\CommonFiles\Language\en-us"
           PS echo $env:CADOE_LIBDIR242
           C:\Program Files\ANSYS Inc\v242\CommonFiles\Language\en-us


If you want these changes to be permanent then:


.. tab-set::

    .. tab-item:: AWP_ROOT242
        :sync: envvarskey

        .. code:: pwsh-session

           PS [System.Environment]::SetEnvironmentVariable('AWP_ROOT242','C:\Program Files\ANSYS Inc\v242',[System.EnvironmentVariableTarget]::User)
           PS echo $env:AWP_ROOT242
           C:\Program Files\ANSYS Inc\v242

    .. tab-item:: ANSYS242_DIR
        :sync: envvarskey

        .. code:: pwsh-session

           PS [System.Environment]::SetEnvironmentVariable('ANSYS242_DIR','C:\Program Files\ANSYS Inc\v242\ANSYS',[System.EnvironmentVariableTarget]::User)
           PS echo $env:ANSYS242_DIR
           C:\Program Files\ANSYS Inc\v242\ANSYS

    .. tab-item:: CADOE_LIBDIR242
        :sync: envvarskey

        .. code:: pwsh-session

           PS [System.Environment]::SetEnvironmentVariable('CADOE_LIBDIR242','C:\Program Files\ANSYS Inc\v242\CommonFiles\Language\en-us',[System.EnvironmentVariableTarget]::User)
           PS echo $env:CADOE_LIBDIR242
           C:\Program Files\ANSYS Inc\v242\CommonFiles\Language\en-us

.. vale on

Using a proxy server
~~~~~~~~~~~~~~~~~~~~

In some rare cases, you might experience some problems to connect to the MAPDL instance if you are
using a proxy.
When `gRPC <grpc_>`_ is used in a proxy environment, if a local address is specified (that is ``127.0.0.1``)
as the connection destination, the gRPC implementation refers automatically to the proxy address.
In this case, the local address cannot be referred, resulting in a connection error.
As a workaround, you can set the environment variable ``NO_PROXY`` to your local address ``127.0.0.1``,
and then run :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>`
to connect to MAPDL instance.


Firewall settings
~~~~~~~~~~~~~~~~~

MAPDL and Python should have the correct firewall settings to allow communication between the two.
If you are using a firewall, you should allow MAPDL to receive inbound connections to the following ports:

* ``50052`` (TCP) for gRPC connection.
* ``50053+`` (TCP) for extra gRPC connection.
* ``50055`` (TCP) for gRPC connection to the MAPDL database.

Python process must be allowed to connect to the mentioned ports (outbound connections).

Normally most of the firewall rules focus on the inbound connections, so you should not need to
configure the outbound connections. However, if you are experiencing problems, you should make sure
that the firewall is not blocking the outbound connections on the following ports:

* ``5005X`` (TCP) for gRPC connections.
* ``50055`` (TCP) for gRPC connection to the MAPDL database.
* ``1055`` (TCP) for licensing connections.
* ``2325`` (TCP) for licensing connections.

For more information on how to **configure your firewall on Windows**, please refer to the following
link in `Ansys forum-Licensing 2022 R2 Linux Ubuntu (and also Windows) <af_licensing_windows_ubuntu_>`_.

For more information on how to **configure your firewall on Ubuntu Linux**, please refer to the following
link `Security-Firewall | Ubuntu <ubuntu_firewall_>`_.


Location of the executable file
-------------------------------

Manually set the location of the executable file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a non-standard install, PyMAPDL might be unable find
your MAPDL installation. If this is the case, provide the location of MAPDL
as the first parameter to the :func:`launch_mapdl() <ansys.mapdl.core.launcher.launch_mapdl>`
method.


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: pycon

            >>> from ansys.mapdl.core import launch_mapdl
            >>> exec_loc = "C:/Program Files/ANSYS Inc/v241/ansys/bin/winx64/ANSYS241.exe"
            >>> mapdl = launch_mapdl(exec_loc)

    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: pycon

            >>> from ansys.mapdl.core import launch_mapdl
            >>> exec_loc = "/usr/ansys_inc/v241/ansys/bin/ansys241"
            >>> mapdl = launch_mapdl(exec_loc)


Default location of the executable file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first time that you run PyMAPDL, it detects the
available Ansys installations.

**On Windows**

Ansys installations are normally under:


.. tab-set::

    .. tab-item:: Windows
        :sync: oskey

        .. code:: text

            C:/Program Files/ANSYS Inc/vXXX

    .. tab-item:: Linux
        :sync: oskey
                
        .. code:: text

            /usr/ansys_inc/vXXX
            
        Or under:

        .. code:: text

            /ansys_inc/vXXX


By default, Ansys installer uses the former one (``/usr/ansys_inc``) but also creates a symbolic to later one (``/ansys_inc``).

If PyMAPDL finds a valid Ansys installation, it caches its
path in the configuration file, ``config.txt``. The path for this file
is shown in this code:

.. code:: pycon

    >>> from ansys.mapdl.core.launcher import CONFIG_FILE
    >>> print(CONFIG_FILE)
    'C:\\Users\\user\\AppData\\Local\\ansys_mapdl_core\\ansys_mapdl_core\\config.txt'


In certain cases, this configuration file might become obsolete. For example, when a new
Ansys version is installed and an earlier installation is removed.

To update this configuration file with the latest path, use:

.. code:: pycon

    >>> from ansys.mapdl.core import save_ansys_path
    >>> save_ansys_path(r"C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ansys241.exe")
    'C:\\Program Files\\ANSYS Inc\\v241\\ansys\\bin\\winx64\\ansys241.exe'

If you want to see which Ansys installations PyMAPDL has detected, use:

.. code:: pycon

    >>> from ansys.mapdl.core import get_available_ansys_installations
    >>> get_available_ansys_installations()
    {242: 'C:\\Program Files\\ANSYS Inc\\v242',
    241: 'C:\\Program Files\\ANSYS Inc\\v241',
    -242: 'C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v242'}

Student versions are provided as **negative** versions because the Python dictionary
does not accept two equal keys. The result of the
:func:`get_available_ansys_installations() <ansys.tools.path.get_available_ansys_installations>`
method lists higher versions first and student versions last.

.. warning::
    You should not have the same Ansys product version and student version installed. For more
    information, see :ref:`conflicts_student_version`.


PyMAPDL usage issues
--------------------

.. _ref_issues_np_mapdl:

Issues when importing and exporting NumPy arrays in MAPDL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because of the way MAPDL is designed, there is no way to store an
array where one or more dimensions are zero.
This can happens in NumPy arrays, where its first dimension can be
set to zero. For example:

.. code:: pycon

   >>> import numpy
   >>> from ansys.mapdl.core import launch_mapdl
   >>> mapdl = launch_mapdl()
   >>> my_array = np.reshape([1, 2, 3, 4], (4,))
   >>> my_array
   array([1, 2, 3, 4])


These types of array dimensions are always converted to ``1``.

For example:

.. code:: pycon

   >>> mapdl.parameters["mapdlarray"] = my_array
   >>> mapdl.parameters["mapdlarray"]
   array([[1.],
      [2.],
      [3.],
      [4.]])
   >>> mapdl.parameters["mapdlarray"].shape
   (4, 1)

This means that when you pass two arrays, one with the second axis equal
to zero (for example, ``my_array``) and another one with the second axis equal
to one, have the same shape if later retrieved.

.. code:: pycon

   >>> my_other_array = np.reshape([1, 2, 3, 4], (4, 1))
   >>> my_other_array
   array([[1],
      [2],
      [3],
      [4]])
   >>> mapdl.parameters["mapdlarray_b"] = my_other_array
   >>> mapdl.parameters["mapdlarray_b"]
   array([[1.],
      [2.],
      [3.],
      [4.]])
   >>> np.allclose(mapdl.parameters["mapdlarray"], mapdl.parameters["mapdlarray_b"])
   True


.. _ref_pymapdl_stability:

PyMAPDL stability
-----------------

Recommendations
~~~~~~~~~~~~~~~

When connecting to an instance of MAPDL using gRPC (default), there are some cases
where the MAPDL server might exit unexpectedly. There
are several ways to improve MADPL performance and stability:

Use ``mute`` to improve stability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When possible, pass ``mute=True`` to individual MAPDL commands or
set it globally with the :func:`Mapdl.mute <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.mute>`
method. This disables streaming back the response from MAPDL for each command
and marginally improves performance and stability. Consider having a debug flag in
your program or script so that you can turn on and off logging and
verbosity as needed.


Known Issues
~~~~~~~~~~~~

* MAPDL 2021 R1 has a stability issue with the :
  :func:`Mapdl.input() <ansys.mapdl.core.Mapdl.input>`
  method. Avoid using input files if possible. Attempt to use the
  :func:`Mapdl.upload() <ansys.mapdl.core.mapdl_grpc.MapdlGrpc.upload>` method to upload
  nodes and elements and read them in via the
  :func:`Mapdl.nread() <ansys.mapdl.core.Mapdl.nread>` and
  :func:`Mapdl.eread() <ansys.mapdl.core.Mapdl.eread>` methods.



More help needed?
-----------------

.. vale off

.. epigraph::

   *"What do I do if an issue is not listed here?"*  

.. vale on

To see if your issue is already posted, search the `PyMAPDL Issues <pymapdl_issues_>`_ page. If not, do one of the following:

* If you are not sure of the cause or would like some explanation about the
  usage of the function or its documentation, create a discussion on the
  `PyMAPDL Discussions <pymapdl_discussions_>`_ page.

* If you believe you have found a bug or want to create a feature request,
  create an issue on the `PyMAPDL Issues <pymapdl_issues_>`_ page.

For more complex issues or queries, contact the `PyAnsys Core team <pyansys_core_>`_.

