.. _pymapdl_docker:

****************
MAPDL and Docker
****************

You can run MAPDL within a Docker container on any OS and
connect to it via PyMAPDL.

There are several advantages to running MAPDL
in a containerized environment such as Docker (or Singularity):

- Consistent environment regardless of the host OS
- Portability and ease of install
- Large-scale cluster deployment using Kubernetes
- Genuine app isolation through containerization

When running MAPDL in a Docker container, you use your local Python installation to
connect to this instance.


Requirements
============

You must have access to a Docker image with MAPDL in it.
For more information on how to create your own Docker image,
see :ref:`ref_make_container`.

Once you have created and uploaded your Docker image to a registry,
you can start to pull and use the image on other devices.

.. warning::

   MAPDL Docker images are not allowed to be shared in
   public or free-to-access repositories or registries.
   Doing so violates Ansys policy.



Configure Docker to access a private GitHub registry
----------------------------------------------------

If you have created a Docker image and uploaded it to a GitHub
private repository, you must authorize your Docker installation
to access this private package by using a personal access
token.

For information on creating a GitHub personal access token with
``packages read`` permissions, see GitHub's `Creating a personal access token <gh_creating_pat_>`_.

Save that token to a file with this command:

.. code::

   echo MY_GITHUB_TOKEN_WITH_PACKAGE_READ_PERMISSION > GH_TOKEN.txt


This lets you send the token to Docker without leaving the token value
in your history. Next, authorize Docker to access this repository
with code like this:

.. code::

    GH_USERNAME=<my-github-username>
    cat GH_TOKEN.txt | docker login ghcr.io -u $GH_USERNAME --password-stdin


.. _run_an_mapdl_image:

Run an MAPDL Docker image
=========================

You can now launch MAPDL from Docker using the command line, a
`docker compose file <run_an_mapdl_image_using_docker_compose_>`_,
or a script that gather the commands given to the command line.

Your Docker image should have a valid MAPDL license configuration.
The easiest way is to have an environment variable, :envvar:`ANSYSLMD_LICENSE_FILE`,
pointing to a valid license server. This environment variable can be already
included in the Docker image. However, this is not recommended because it could
expose the license server if the Docker image is leaked.
The recommended approach is to set that environment variable when running the
container. 

To instantiate an MAPDL Docker container from an image hosted at ``ghcr.io/myuser/myrepo/mymapdldockerimage``,
use code like in the following examples.

**On Linux**

.. code:: bash

  ANSYSLMD_LICENSE_FILE=1055@MY_LICENSE_SERVER_IP
  LOCAL_MAPDL_PORT=50053
  MAPDL_DOCKER_REGISTRY_URL=ghcr.io/myuser/myrepo/mymapdldockerimage
  docker run -e ANSYSLMD_LICENSE_FILE=$ANSYSLMD_LICENSE_FILE --restart always --name mapdl -p $LOCAL_MAPDL_PORT:50052 $MAPDL_DOCKER_REGISTRY_URL -smp > log.txt

**On Windows**

.. code:: pwsh-session

    $env:ANSYSLMD_LICENSE_FILE="1055@MY_LICENSE_SERVER_IP"
    $env:LOCAL_MAPDL_PORT=50053
    $env:MAPDL_DOCKER_REGISTRY_URL="ghcr.io/myuser/myrepo/mymapdldockerimage"

    docker run -e ANSYSLMD_LICENSE_FILE=$env:ANSYSLMD_LICENSE_FILE --restart always --name mapdl -p $env:LOCAL_MAPDL_PORT`:50052   $env:MAPDL_DOCKER_REGISTRY_URL -smp


The first time you instantiate the container, Docker logins into the registry and
pulls the required image. This can take some time, depending on the size of the image.

To rerun it, you should restart the container with this command:

.. code:: bash

   docker start mapdl

Or you can delete the container and run it again using these commands:

.. code:: bash

    docker rm -f mapdl

    docker run -e ANSYSLMD_LICENSE_FILE=$ANSYSLMD_LICENSE_FILE --restart always --name mapdl -p $LOCAL_MAPDL_PORT:50052   $MAPDL_DOCKER_REGISTRY_URL -smp > log.txt


You can append the Docker flag ``--rm`` to automatically clean up the container
when it exits.

The preceding commands create a log file (``log.txt``) in your current directory location.
However, you can remove ``> log.txt`` if you don't want to create this file. In this case,
the command output is redirected to the console, which is kept blocked until the Docker
image exits. You can detach the console from the Docker container output by appending
``-d`` to the `docker run <docker_run_>`_ command. (Always add this before the Docker
image URL.)

If you don't want to block the console, the best approach is to pipe the output to a file
as mentioned earlier so that you can inspect the output of that file.

Notice that the MAPDL Docker image gRPC port (``50052``) is being mapped to a
different host port (``50053``) to avoid port conflicts with local
MAPDL instances running on the host or other Docker images.
You could additionally launch more Docker containers in different ports if
you want to run multiple simulations at the same time.

The :ref:`ref_pymapdl_pool` module does not
work when you are connecting to a remote MAPDL Docker image.
It also does not work when connected to Docker containers. 
If you decide to launch multiple MAPDL instances, you must manage these
instances yourself.

.. note:: Ensure that port ``50053`` is open in your local firewall.

You can provide additional MAPDL command line parameters to MAPDL by simply
appending them to the end of the command.

For example, you can increase the number of processors (up to the
number available on the host machine) with the ``-np`` switch:

.. code:: bash

  docker run -e ANSYSLMD_LICENSE_FILE=$ANSYSLMD_LICENSE_FILE --restart always -d --name mapdl -p $LOCAL_MAPDL_PORT:50052 $MAPDL_DOCKER_REGISTRY_URL -smp -np 8 > log.txt


For additional command line arguments, see the *Notes* section in the
description for the :func:`launch_mapdl() <ansys.mapdl.core.launch_mapdl>`
function.

You can use a script file (batch ``'.bat'`` or PowerShell ``'.ps'``)
to run the preceding commands all at once.

Once you have launched MAPDL, you should see the following content
in your console (or the output file):

.. code::

    Start GRPC Server

    ##############################
    ### START GRPC SERVER      ###
    ##############################

    Server Executable   : MapdlGrpc Server
    Server listening on : 0.0.0.0:50052


.. note:: 
  
   Notice that the port specified in the console is the internal Docker container port.
   This port has been mapped to the value specified for the :envvar:`LOCAL_MAPDL_PORT`
   environment variable.


.. _run_an_mapdl_image_using_docker_compose:

Using ``docker-compose`` to launch MAPDL
----------------------------------------

You can also use the ``docker-compose`` command to launch MAPDL configured in
a ``docker-compose`` file.
This is useful if you want to load an already configured environment, or
if you want to launch multiple instances of MAPDL or services.

For your convenience, the `docker <pymapdl_docker_dir_>`_ directory 
contains configured ``docker-compose`` files that you can
use.

Using the `docker-compose.yml <pymapdl_docker_compose_base_>`_ file is recommended.
This is the *base* configuration file for launching an instance of MAPDL that you can connect
to remotely.


.. _pymapdl_connect_to_MAPDL_container:

Connect to the MAPDL container from Python
==========================================

You can connect to an MAPDL instance as indicated in :ref:`connect_grpc_madpl_session`.
You do not need to specify an IP address because Docker maps the ports to the local host.


Additional considerations
=========================

Use ``--restart`` policy with MAPDL products
--------------------------------------------

By default, MAPDL creates a ``LOCK`` file in the working directory when it starts,
and it deletes this file if it exits normally. The file is used to avoid overwriting files
such as database (DB) files or result (RST) files when starting MAPDL after an
abnormal termination.

Because of this behavior, when using the Docker ``--restart`` flag in the `docker run <docker_run_>`_ 
command, you might enter into an infinite loop after crashing if you specify the Docker image to
reboot after an abnormal termination.
When there is an abnormal termination (MAPDL crashes), the :file:`LOCK` file is kept on the
working directory. Since MAPDL has exited, the container also exits.

This triggers the Docker ``restart`` policy, which attempts to restart MAPDL container and
the MAPDL process with it.
But because of the presence of the ``LOCK`` file, MAPDL exits in an attempt to not overwrite
the files from the previous crash. 
This is the start of an infinite loop, where Docker keeps restarting the MAPDL container and
MAPDL keeps exiting to avoid overwrite the previous files.

In such cases, you should not use the ``--restart`` option. If you really need to use
this option, you can avoid MAPDL checks and create the ``LOCK`` file by starting
the process with the ``ANSYS_LOCK`` environment variable set to ``"OFF"``. 

This code shows how to do this in your `docker run <docker_run_>`_ command:

.. code:: bash

  docker run \
      --restart always \
      -e ANSYSLMD_LICENSE_FILE=1055@$LICENSE_SERVER \
      -e ANSYS_LOCK="OFF" \
      -p 50052:50052 \
      $IMAGE


Get useful files after abnormal termination
-------------------------------------------

In some cases, the MAPDL container might crash after the MAPDL process experiences an
abnormal termination. In these cases, you can retrieve log files and output files using the
tools that Docker provides.

First, get the Docker container name:

.. code:: pwsh-session

  PS docker ps -a
  CONTAINER ID   IMAGE                                   COMMAND                  CREATED          STATUS          PORTS                      NAMES
  c14560bff70f   my.registry/myuser/mypackage/mapdl   "/ansys_inc/ansys/bi…"   9 seconds ago    Exited(137)    0.0.0.0:50053->50052/tcp   mapdl


Then use the ``name`` in this command:

.. code:: pwsh-session

  PS docker exec -it mapdl /bin/bash

This command executes the command shell (``/bin/bash``) of the container and attaches your current terminal to it (interactive ``-it``).

.. code:: pwsh-session

  PS C:\Users\user> docker exec -it mapdl /bin/bash
  [root@c14560bff70f /]#

Now you can enter commands inside the Docker container and navigate inside it.

.. code:: pwsh-session

  PS C:\Users\user> docker exec -it mapdl /bin/bash
  [root@c14560bff70f /]# ls
  anaconda-post.log  cleanup-ansys-c14560bff70f-709.sh  file0.err   file1.err  file1.page  file2.out   file3.log   home   media  proc  sbin  tmp
  ansys_inc          dev                                file0.log   file1.log  file2.err   file2.page  file3.out   lib    mnt    root  srv   usr
  bin                etc                                file0.page  file1.out  file2.log   file3.err   file3.page  lib64  opt    run   sys   var

You can then take note of the files you want to retrieve. For example, you would likely want to retrieve the error and output files (``file*.err`` and ``file*.out``).

Exit the container terminal using the ``exit`` command:

.. code:: pwsh-session

  [root@c14560bff70f /]# exit
  exit
  (base) PS C:\Users\user>

You can then copy the noted files using the `docker cp <docker_cp_>`_ command:

.. code:: pwsh-session

  docker cp mapdl:/file0.err .

This command copies the files in the current directory. You can specify a different destination using
the second argument.

If you want to retrieve multiple files, the most efficient approach is to get back inside the Docker container:

.. code:: pwsh-session

  PS C:\Users\user> docker exec -it mapdl /bin/bash
  [root@c14560bff70f /]#

Create a folder where you are going to copy all the desired files:

.. code:: pwsh-session

  [root@c14560bff70f /]# mkdir -p /mapdl_logs
  [root@c14560bff70f /]# cp -f /file*.out /mapdl_logs
  [root@c14560bff70f /]# cp -f /file*.err /mapdl_logs
  [root@c14560bff70f /]# ls mapdl_logs/
  file0.err  file1.err  file1.out  file2.err  file2.out  file3.err  file3.out

Then copy the entire folder content at once:

.. code:: pwsh-session

  docker cp mapdl:/mapdl_logs/. .

