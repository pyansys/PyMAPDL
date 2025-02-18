.. _ref_guide_wsl:

###########################
Windows Subsystem for Linux
###########################

This page explains how you use a PyAnsys library, more specifically PyMAPDL,
in the Windows Subsystem for Linux (WSL). WSL is a compatibility layer for
running Linux binary executables natively on Windows 10, Windows 11, and
Windows Server 2019. For more information, see:

- `Wikipedia WSL <WikipediaWSL_>`_
- Microsoft's `What is the Windows Subsystem for Linux <What_is_the_Windows_Subsystem_for_Linux_>`_.

This page walk you through the installation of WSL on Windows and then
show how to use it together with MAPDL, PyMAPDL, and `Docker <https://www.docker.com/>`_.


.. note::
   Because WSL is under constant development, keeping this guide updated is difficult. If you
   find any issues or have questions related to WSL, feel free to `open an issue in the GitHub repository <pymapdl_issues_>`_.


Install WSL
###########

There are two versions of WSL: WSL1 and WSL2. Because WSL2 provides many improvements
over WSL1, you should upgrade to and use WSL2.

Install WSL by following Microsoft's directions at 
`Microsoft: Install WSL <install_wsl_microsoft_>`_.

Install the CentOS7 WSL distribution
====================================

When working with PyAnsys libraries, you should use the CentOS7 WSL distribution.

You can install this distribution using an unofficial WSL distribution from
`CentOS-WSL <gh_centos_wsl_1_>`_ package or the
`CentOS WSL <gh_centos_wsl_2_>`_ package.


.. vale off

Using the Ubuntu WSL distribution
=================================

.. vale on

Ubuntu is a supported operative system for Ansys products. However it has not been
tested yet in the context of WSL. You should proceed with caution.


Install Ansys products in WSL
#############################

Prerequisites
=============
If you are using CentOS 7, before installing MAPDL, you must install some
required libraries:

.. code:: console
   
   sudo yum install openssl openssh-clients mesa-libGL mesa-libGLU motif libgfortran


If you are using Ubuntu, follow the instructions in `Run MAPDL: Ubuntu <pymapdl_run_ubuntu_>`_ .


.. _installing_ansys_in_wsl:

Install Ansys products
======================

To install Ansys products in WSL Linux, perform these steps:

1. Download the **Ansys Structures** image from the customer portal (`Current
   Release <ansys_current_release_>`_).
   
   If you are downloading the image on a Windows machine, you should later copy the image from
   your downloads folder to WSL.

2. Extract the compressed source code file (``tar.gz``) with this command:

   .. code:: console
   
       tar xvzf STRUCTURES_2021R2_LINX64.tgz


3. To install MAPDL, go into the folder where the files have been extracted and
   run this command:

   .. code:: console
   
      sudo ./INSTALL -silent -install_dir /usr/ansys_inc/ -mechapdl

   where: 

   - ``-silent`` : Initiates a silent installation, which means no GUI is shown.
   - ``-install_dir /path/`` : Specifies the directory to install the product or
     license manager to. If you want to install to the default location, you can
     omit the ``-install_dir`` argument. The default location is ``/ansys_inc``
     if the symbolic link is set. Otherwise, it defaults to ``/usr/ansys_inc``.
   - ``-<product_flag>`` : Specifies the one or more products to install.
     If you omit this argument, all products are installed. The *Ansys, Inc.
     Installation Guides* in the Ansys Help provides a list of valid
     values for the ``product_flags`` argument in `Chapter 6
     <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/corp/v241/en/installation/unix_silent.html>`_
     of the *Linux Installation Guide* and `Chapter 7
     <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/corp/v241/en/installation/win_silent.html>`_
     of the *Windows Installation Guide*.

     In the preceding example for MAPDL, you only need to specify the ``-mechapdl`` flag.

After installing MAPDL directly in ``/ansys_inc`` or in ``/usr/ansys_inc``,
you create a symbolic link with this command:

.. code:: console

   sudo ln -s /usr/ansys_inc /ansys_inc

By default, PyMAPDL expects the MAPDL executable to be in
``/usr/ansys_inc``. Whether you install it there or not, you should
use a symbolic link to associate that directory with your Ansys installation
directory (``/*/ansys_inc``).


Post-installation setup
#######################

Open ports for license server communication
===========================================

**Theory:** You should open the ports ``1055`` and ``2325`` for license server
communication in the **Windows Control Panel**. For the steps to set advanced
Windows firewall options, see Microsoft's
`How to open port in Windows 10 Firewall <open_port_windows_10_>`_.

**Reality:** This works if you want to run a Docker image using WSL Linux image
to host that Docker image. The Docker image successfully communicates with the Windows
license server using these ports if you use the ``'-p'`` flag when running the
Docker image with these ports open.

If you want to run MAPDL in the CentOS 7 image and use the Windows license
server, opening the ports might not work properly because the Windows firewall
seems to block all traffic coming from WSL. For security purposes, you should
still try to open ports ``1055`` and ``2325`` in the firewall and verify that your
MAPDL installation can communicate with the Windows hosts. If you are having
problems after setting the firewall rules, you might have to turn off the Windows
firewall for the WSL ethernet virtual interface. This might pose some unknown
side effects and security risk so use it with caution. For more information, see
:ref:`Disable firewall on WSL ethernet <disable_firewall_on_wsl_ethernet_section>`.


Set up an environmental variable in WSL that points to Windows host license server
==================================================================================

The IP address for the Windows host is given in the WSL ``/etc/hosts`` file before the name
``host.docker.internal``.

.. note::
   This ``host.docker.internal`` definition might not be available if Docker is
   not installed.


Here is an example of the WSL ``/etc/hosts`` file:

.. vale off

.. code-block:: bash
   :emphasize-lines: 8

   # This file was automatically generated by WSL.
   # To stop automatic generation of this file, add the following entry to /etc/wsl.conf:
   # [network]
   # generateHosts = false
   127.0.0.1       localhost
   127.0.1.1       AAPDDqVK5WqNLve.win.ansys.com   AAPDDqVK5WqNLve

   192.168.0.12    host.docker.internal
   192.168.0.12    gateway.docker.internal
   127.0.0.1       kubernetes.docker.internal

   # The following lines are desirable for IPv6 capable hosts
   ::1     ip6-localhost ip6-loopback
   fe00::0 ip6-localnet
   ff00::0 ip6-mcastprefix
   ff02::1 ip6-allnodes
   ff02::2 ip6-allrouters


.. vale on

You can add the next lines to your WSL ``=/.bashrc`` file to create an
environment variable with this IP address:

.. vale off

.. _ref_bash_win_ip:

.. vale on

.. code:: console

    winhostIP=$(grep -m 1 host.docker.internal /etc/hosts | awk '{print $1}')
    export ANSYSLMD_LICENSE_FILE=1055@$winhostIP


Launch MAPDL in WSL
###################

To launch MAPDL in WSL, you must launch the MAPDL process.
An example follows.

.. code:: console

    /ansys_inc/v241/ansys/bin/ansys241 -grpc

This launches an MAPDL instance whose working directory is the current directory.
If you want to change the working directory, you can use the ``-dir`` flag.

.. code:: console

    /ansys_inc/v241/ansys/bin/ansys241 -grpc -dir /tmp/ansys_jobs/myjob


Launch MAPDL in the Windows host OS
###################################

You can launch an instance of MAPDL using the MAPDL installation from the
Windows host OS.
To do that, run this code:

.. code:: python

   from ansys.mapdl.core import launch_mapdl

   mapdl = launch_mapdl(
       exec_file="/mnt/c/Program Files/ANSYS Inc/v241/ANSYS/bin/winx64/ANSYS241.exe",
   )

As mentioned in `Open ports for license server communication`_, the Windows host OS
and WSL are connected with a virtual network where they both have different IP addresses.
PyMAPDL does its best to detect the IP address of the Windows host OS. For that, it parses
the output given by the command ``ip route`` in WSL. However, if you find that this IP
address is not correct, you can specify the IP address to connect to like this:

.. code:: python

   from ansys.mapdl.core import launch_mapdl

   mapdl = launch_mapdl(
       exec_file="/mnt/c/Program Files/ANSYS Inc/v241/ANSYS/bin/winx64/ANSYS241.exe",
       ip="172.23.112.1",
   )

You might need to turn off the Microsoft Firewall completely or at least
for the WSL network connection.
To do so, follow 
:ref:`Disable firewall on WSL ethernet <disable_firewall_on_wsl_ethernet_section>`.


For more information, see the issue `Launching MAPDL from WSL <wsl_launching_mapdl_>`_
or open a new issue in the `GitHub repository issues <pymapdl_issues_>`_.


Connect to an MAPDL instance running in WSL
###########################################

To connect to the WSL instance that is running the MAPDL instance,
you need to specify the IP address of the WSL instance:

.. code:: pycon

    >>> from ansys.mapdl.core import Mapdl
    >>> mapdl = Mapdl(ip="127.0.0.1", port=50053)



Additional information
######################

IP addresses in WSL and the Windows host
========================================

**Theory:** You should be able to access the Windows host using the IP address
specified in the WSL ``/etc/hosts`` file. This IP address is typically ``127.0.1.1``.
This means that the local WSL IP address is ``127.0.0.1``.

**Reality:** It is almost impossible to use the IP address ``127.0.1.1`` to
connect to the Windows host. However, it is possible to use the ``host.docker.internal``
hostname in the same WSL ``/etc/hosts`` file. This is an IP address that is
randomly allocated, which is an issue when you define the license server. However,
updating the ``.bashrc`` file as mentioned `in here <ref_bash_win_ip_>`_ resolves this issue.

The IP address ``127.0.0.1`` is the IP address of WSL CentOS from the WSL perspective, whereas the IP address
for the Windows host is typically ``127.0.1.1``.

Docker builds the PyMAPDL images using the WSL distribution as the base. Hence, PyMAPDL
is running on a Linux WSL distribution, which is running on a Windows host. Because the
Docker image shares resources with WSL, it also shares the internal IP address with the WSL
distribution.


Ansys installation flags
========================

Obtain help
~~~~~~~~~~~

To obtain license server information, use one of the following methods to access the ``INSTALL`` file
and then inspect the last few lines.

Method 1
--------

.. code:: console

    ./INSTALL --help

Method 2
--------

.. code:: console

    cat ./INSTALL


License server information for the client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``-licserverinfo`` argument specifies information that the client for the license server uses.
This argument is valid only in conjunction with a silent installation (INSTALL).

Single license server
---------------------

The format for a single license server is:

.. code:: console

   -licserverinfo LI_port_number:FLEXlm_port_number:hostname

Here is an example:

.. code:: console

   ./INSTALL -silent -install_dir /ansys_inc/ -mechapdl -licserverinfo 2325:1055:winhostIP

Three license servers
---------------------

The format for three license servers is:

.. code:: console

   -licserverinfo LI_port_number:FLEXlm_port_number:hostname1,hostname2,hostname3

Here is an example:

.. code:: console

   ./INSTALL -silent -install_dir /ansys_inc/ -mechapdl -licserverinfo 2325:1055:abc,def,xyz


Language for the installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``-lang`` argument specifies the language that the installation uses.


File specifying the products to install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can specify an ``options`` file that lists the products that you want to
install. When you do so, you must use the ``-productfile`` argument to specify the
full path to the ``options`` file.


.. _disable_firewall_on_wsl_ethernet_section:

Disable firewall on WSL ethernet
================================
There are two methods for disabling the firewall on the WSL ethernet.

Method 1
~~~~~~~~

This method shows a notification:

.. code:: pwsh-session

    Set-NetFirewallProfile -DisabledInterfaceAliases "vEthernet (WSL)"

Method 2
~~~~~~~~

This method does not show a notification:

.. code:: pwsh-session

    powershell.exe -Command "Set-NetFirewallProfile -DisabledInterfaceAliases \"vEthernet (WSL)\""


**Reference:** 
The information has been obtained from `WSL Windows Toolbar Launcher repository <WSL_Windows_Toolbar_Launcher_>`_.
More specifically from the *Troubleshooting* section `Firewall rules <disabling_firewall_on_wsl_>`_

Port forwarding on Windows 10
=============================

You can use Windows PowerShell commands for port forwarding on Windows 10.

Link ports between WSL and Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This command links ports between WSL and Windows:

.. code:: pwsh-session

    netsh interface portproxy add v4tov4 listenport=1055 listenaddress=0.0.0.0 connectport=1055 connectaddress=XXX.XX.XX.XX


View all forwards
~~~~~~~~~~~~~~~~~

This command allows you to view all forwards:

.. code:: pwsh-session

    netsh interface portproxy show v4tov4


Delete port forwarding
~~~~~~~~~~~~~~~~~~~~~~

This command allows you to delete port forwarding:

.. code:: pwsh-session

    netsh interface portproxy delete v4tov4 listenport=1055 listenaddres=0.0.0.0 protocol=tcp

Reset Windows network adapters
==============================

You can reset Windows network adapters with this code:

.. code:: pwsh-session

    netsh int ip reset all
    netsh winhttp reset proxy
    ipconfig /flushdns
    netsh winsock reset


Restart the WSL service
=======================

You can restart the WSL service with this command:

.. code:: pwsh-session

    Get-Service LxssManager | Restart-Service


Stop all processes with a given name
====================================

You can stop all processes with a given name with this command.

.. code:: pwsh-session

   Get-Process "ANSYS241" | Stop-Process


Install ``xvfb`` in CentOS 7
============================

If you want to replicate the CI/CD behavior, you must install the ``xvfb`` package
as shown in the following command. For more information, see the ``.ci`` folder.

.. code:: console

   yum install xorg-x11-server-Xvfb


.. note::
   If you want to replicate the CI/CD behavior or develop from inside a Docker container,
   you should use Ubuntu as your base operative system. You can find instructions
   to create your own MAPDL Ubuntu container in :ref:`ref_make_container` and how to use
   it to develop on containers in :ref:`ref_devcontainer`.

Notes
=====

- PyMAPDL only works for shared-memory parallel (SMP) when running on WSL. This
  is why the flag ``-smp`` should be included.

- Because there are some incompatibilities between VPN and INTEL MPI, use the
  flag ``-mpi msmpi`` when calling MAPDL. This WSL guidance has not been written for or tested
  on VPN. If you are experiencing issues connecting to the Windows host machine,
  your license server, or an MAPDL instance, disconnect the VPN and try again.

