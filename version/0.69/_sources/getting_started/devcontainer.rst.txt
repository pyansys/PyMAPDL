.. _ref_devcontainer:

=====================
Develop on containers
=====================

This guide describes how to develop PyMAPDL features or fix bugs using
a `remote container <vscode_devcontainers_containers_>`_.
The files for setting up the container can be found in the 
`.devcontainer directory <pymapdl_devcontainer_directory_>`_.


About the MAPDL container
=========================

Because MAPDL software is not open source, the GPL license does not allow to
distribute a docker container to users.
Having a docker container with MAPDL installed is a requirement to use
any of the development methods mentioned on this section.
If you want to build your own docker image, visit the following link
:ref:`ref_make_container`.


License
-------

As mentioned before, you must have a valid license to run MAPDL.
When you launch the container, the file :file:`script.sh` automatically
checks if the environment variable :envvar:`ANSYSLMD_LICENSE_FILE` exists.
This environment variable sets the port and IP address of the license server.
If you do not have set this environment variable before launching the
container, you are prompt to enter your license server port and address.

You can set the :envvar:`ANSYSLMD_LICENSE_FILE` environment variable 
from the terminal before launching VS Code.
For example, if you have a license server at the address ``123.45.67.89``,
you can set the license using:

.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> $env:ANSYSLMD_LICENSE_FILE = '1055@123.45.65.89'
            (.venv) PS C:\Users\user\pymapdl> code . # launch VS Code

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ export ANSYSLMD_LICENSE_FILE =1055@123.45.65.89
            (.venv) user@machine:~$code . # launch VS Code


And then open the folder in the container using the `Command palette`.


.. _develop_on_remote_containers:

Develop on a remote container
=============================

.. note:: This approach requires you have a Docker image with MAPDL installed.
   The Docker image listed in the 
   `repository development container configuration files <pymapdl_devcontainer_configuration_>`_ 
   is not for public use due to licensing issues.
   However, you can `create your own Docker image <ref_make_container_>`
   and use this file as a template for setting your own local development container.

To use a `remote container <vscode_devcontainers_containers_>`_, you must install this software:

* `Visual Studio Code <vscode_>`_
* `Docker software <docker_main_>`_ or equivalent.
  To run Linux Docker containers, you should use the Windows Subsystem Linux (WSL) backend. For
  more information, see `Developing inside a Container - Getting started
  <vscode_devcontainers_containers_getting_started_>`_.
* `Remove Development VS Code extension pack <vscode_devcontainers_remote_extension_>`_

As mentioned before, you must have your own Docker image with MAPDL installed
locally available or hosted in an online registry, such as GitHub `ghcr.io <ghcr_>`_.
For the purpose of this document, assume your image is hosted at
``ghcr.io/myaccount/mapdlimage:mytag``.

You must then modify the
`docker-compose.yml <pymapdl_build_docker_compose_>`_ file with your custom image:

.. code-block:: yaml
   :emphasize-lines: 4

   ports:
      - '50052:50052'
      - '50055:50055'
   image: 'ghcr.io/myaccount/mapdlimage:mytag'
   user: "0:0"


.. warning:: You might also need to change some environment variables or Docker
   options to adjust to your image configuration.
   For example, you might need to change the :envvar:`AWP_ROOT222` environment
   variable if your MAPDL container does not have the installation in the default directory.
   Be careful that you do not commit those changes in your PRs.

You can now open the current folder (or PyMAPDL repository) using
:kbd:`ctr/cmd` + :kbd:`shift` + :kbd:`p` to open the Visual Studio Code **Command palette**.
Then select **Dev Containers: Open Folder in Container**.
When you are prompted to select one of the multiple devcontainer configurations,
select **PyMAPDL-DevContainer (Local)**.
Because the configuration is available in the :file:`.devcontainer/devcontainer-local` directory,
Visual Studio Code automatically launches the MAPDL container with the desired configuration.

.. note:: The first time that you launch the devcontainer, it might take a long time before it is ready,
   This is because the container image must be pulled from the registry.

You can now work normally, but you would be, in fact, working from
inside the container.
Because Visual Studio Code mount the local directory into the Docker container,
you don't lose your changes if you accidentally delete your container.
However, this mounting process might have a significant impact on
the container performance, especially noticeable if you are using MacOS.
You can avoid this by cloning the repository inside the container.
For more information, see `Quick start: Open a Git repository or GitHub PR in an isolated container volume <vscode_open_a_repository_in_container_>`_.

