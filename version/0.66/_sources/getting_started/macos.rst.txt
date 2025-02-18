.. _ref_pymapdl_and_macos:

=================
PyMAPDL and MacOS
=================

Install PyMAPDL
===============

You can install PyMAPDL normally on a MacOS that fulfill PyMAPDL
requirements using this command:

.. code:: zsh

    pip install ansys-mapdl-core


While PyMAPDL requires a connection to an MAPDL live instance to function,
MAPDL is not compatible with a MacOS.

There are two options:

* **Connect to a remote instance**: You can connect to a remote instance running
  on a Windows or Linux machine as indicated in :ref:`connect_grpc_madpl_session`.

* **Launch MAPDL locally using Docker**: You can run MAPDL on a MacOS machine as
  indicated in :ref:`launch_mapdl_on_macos`.


.. _launch_mapdl_on_macos:

Launch MAPDL on MacOS
=====================

If you do not have an MAPDL Docker image, you can create one on a Linux
machine as indicated in :ref:`ref_make_container`.


If you already have an MAPDL Docker image, you can launch MAPDL as
indicated in :ref:`run_an_mapdl_image`.

Apple Silicon compatibility
---------------------------

If you are using an Apple Silicon device (for instance M1 or M2), you might see the following
warning:

.. code::  output

    WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested

This is because the Docker image has not been built to run on the Apple Silicon architecture (arm64).
You must add the ``--platform linux/amd64`` argument to the `docker run <docker_run_>`_ command
as shown in this code example:

.. code:: zsh

    ANSYSLMD_LICENSE_FILE=1055@MY_LICENSE_SERVER_IP
    LOCAL_MAPDL_PORT=50053
    MAPDL_DOCKER_REGISTRY_URL=ghcr.io/myuser/myrepo/mymapdldockerimage
    docker run -e ANSYSLMD_LICENSE_FILE=$ANSYSLMD_LICENSE_FILE --restart always --name mapdl -p $LOCAL_MAPDL_PORT:50052 --platform linux/amd64 $MAPDL_DOCKER_REGISTRY_URL -smp > log.txt


Connect to an MAPDL container
=============================

You can connect to an MAPDL instance as indicated in :ref:`connect_grpc_madpl_session`.


