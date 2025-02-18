.. _ref_setting_pymapdl_on_hpc:

===============
Setting PyMAPDL
===============

Requirements
============

Using PyMAPDL in an HPC environment managed by SLURM scheduler has certain
requirements:

* **An Ansys installation must be accessible from all the compute nodes.**
  This normally implies that the ``ANSYS`` installation directory is in a
  shared drive or directory. Your HPC cluster administrator
  should provide you with the path to the ``ANSYS`` directory.

* **A compatible Python installation must be accessible from all the compute
  nodes.**
  For compatible Python versions, see :ref:`ref_pymapdl_installation`.

Additionally, you must perform a few key steps to ensure efficient job
execution and resource utilization. Subsequent topics describe these steps.

Check the Python installation
=============================

The PyMAPDL Python package (``ansys-mapdl-core``) must be installed in
a virtual environment that is accessible from the compute nodes.

To see where your Python distribution is installed, use this code:

.. code-block:: console

    user@machine:~$ which python3
    /usr/bin/python3

To print the version of Python you have available, use this code:

.. code-block:: console

    user@machine:~$ python3 --version
    Python 3.10.15

You should be aware that your machine might have other Python versions
installed.
To find out if those installations are already in the ``PATH`` environment
variable, you can press the **Tab** key to use autocomplete:

.. code-block:: console

    user@machine:~$ which python3[TAB]
    python3             python3-intel64     python3.10-config   python3.11          python3.12          python3.8           python3.8-intel64   python3.9-config  
    python3-config      python3.10          python3.10-intel64  python3.11-config   python3.12-config   python3.8-config    python3.9 
    $ which python3.10
    /usr/bin/python3.10

You should use a Python version that is compatible with PyMAPDL.
For more information, see :ref:`ref_pymapdl_installation`.

.. warning::
    
    Contact your cluster administrator if you cannot find a Python version
    compatible with PyMAPDL.


The ``which`` command returns the path where the Python executable is
installed.
You can use that executable to create your own Python virtual environment
in a directory that is accessible from all the compute nodes.
For most HPC clusters, the ``/home/$user`` directory is generally available
to all nodes.
You can then create the virtual environment in the ``/home/user/.venv``
directory:

.. code-block:: console

    user@machine:~$ python3 -m venv /home/user/.venv

After activating the virtual environment, you can install PyMAPDL.

.. _ref_install_pymapdl_on_hpc:

Install PyMAPDL
===============

To install PyMAPDL on the activated virtual environment, run the following
commands:

.. code-block:: console

    user@machine:~$ source /home/user/.venv/bin/activate
    (.venv) user@machine:~$ pip install ansys-mapdl-core
    Collecting ansys-mapdl-core
    Downloading ansys_mapdl_core-0.68.1-py3-none-any.whl (26.9 MB)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 26.9/26.9 MB 37.3 MB/s eta 0:00:00
    Collecting pexpect>=4.8.0
    Using cached pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
    Collecting click>=8.1.3
    ...

To test if this virtual environment is accessible from the compute nodes,
run this ``test.sh`` bash script:

.. code-block:: bash

    #!/bin/bash
    #SBATCH --job-name=myjob
    #SBATCH --nodes=1
    #SBATCH --ntasks-per-node=4
    #SBATCH --time=01:00:00

    # Commands to run
    echo "Testing Python!"
    source /home/user/.venv/bin/activate
    python -c "from ansys.mapdl import core;print(f'PyMAPDL version {core.__version__} was successfully imported.')"

then you can run that script using: 

.. code-block:: console

    user@machine:~$ srun test.sh

This command might take a minute or two to complete, depending on the amount of
free resources available in the cluster.

On the console, you should see this output:

.. code-block:: text

    Testing Python!
    PyMAPDL version 0.68.1 was successfully imported.

If you see an error in the output, see :ref:`ref_hpc_troubleshooting`,
especially :ref:`ref_python_venv_not_accesible`.
