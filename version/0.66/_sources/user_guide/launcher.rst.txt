Initial setup and launch of MAPDL locally
-----------------------------------------
To run, ``ansys.mapdl.core`` must know the location of the MAPDL
binary. Most of the time this can be automatically determined, but
the location of MAPDL must be provided for non-standard installations.
When running for the first time, ``ansys-mapdl-core`` requests the
location of the MAPDL executable if it cannot automatically find it.
You can test your installation of PyMAPDL and set it up by running
the :func:`launch_mapdl() <ansys.mapdl.core.launch_mapdl>` function:

.. code:: python

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl()

Python automatically attempts to detect your MAPDL binary based on
environmental variables. If it is unable to find a copy of MAPDL, you
are prompted for the location of the MAPDL executable.

Here is a sample input for Linux:

.. code:: output

    Enter location of MAPDL executable: /usr/ansys_inc/v222/ansys/bin/ansys222

Here is a sample input for Windows:

.. code:: output

    Enter location of MAPDL executable: C:\Program Files\ANSYS Inc\v222\ANSYS\bin\winx64\ansys222.exe

The settings file is stored locally, which means that you are not prompted
to enter the path again. If you must change the default Ansys path
(meaning change the default version of MAPDL), run the following:

.. code:: python

    from ansys.mapdl import core as pymapdl

    new_path = "C:\\Program Files\\ANSYS Inc\\v212\\ANSYS\\bin\\winx64\\ansys222.exe"
    pymapdl.change_default_ansys_path(new_path)

Also see the :func:`change_default_ansys_path() <ansys.mapdl.core.change_default_ansys_path>` method and
the :func:`find_ansys() <ansys.mapdl.core.find_ansys>` method.

Additionally, it is possible to specify the executable using the keyword argument ``exec_file``. 

In Linux:

.. code:: python

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl(exec_file="/usr/ansys_inc/v212/ansys/bin/ansys212")


In Windows:

.. code:: python

    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl(
        exec_file="C://Program Files//ANSYS Inc//v212//ANSYS//bin//winx64//ansys212.exe"
    )

You could also specify a custom executable by adding the correspondent flag (``-custom``) to the ``additional_switches``
keyword argument:

.. code:: python

    from ansys.mapdl.core import launch_mapdl

    custom_exec = "/usr/ansys_inc/v212/ansys/bin/ansys212t"
    add_switch = f" -custom {custom_exec}"
    mapdl = launch_mapdl(additional_switches=add_switch)



API reference
~~~~~~~~~~~~~
For more information on controlling how MAPDL launches locally, see the
description of the :func:`launch_mapdl() <ansys.mapdl.core.launch_mapdl>` function.
