

.. _ref_using_standard_install: install_mapdl_

.. _install_mapdl:

*************
Install MAPDL
*************


The PyAnsys ``ansys-mapdl-core`` package (PyMAPDL) requires either a local or
remote instance of MAPDL to communicate with it. This section covers
launching and interfacing with MAPDL from a local instance by
launching it from Python.

MAPDL is installed by default from the Ansys standard installer. When
installing Ansys, verify that the **Mechanical Products** checkbox is
selected under the **Structural Mechanics** option. While the standard
installer options can change, see the following figure for reference.

.. figure:: ../images/unified_install_2019R1.jpg
    :width: 400pt


If you want to avoid having to install MAPDL locally, you can use Docker.
This is especially convenient if you are using a non-supported platform such
as MacOS.
For more information, see :ref:`ref_pymapdl_and_macos`.

You can also download and try the `Ansys Student Version <ansys_student_version_>`_.
A Student Version is valid during a calendar year with limited capabilities. For
example, there is a limit on the number of nodes and elements.

If you experience problems installing MAPDL on Linux, see
:ref:`missing_dependencies_on_linux`.


Ansys software requirements
---------------------------

For the latest features, you must have a copy of Ansys 2021 R1 or later
installed locally. However, PyMAPDL is compatible with Ansys 17.0 and later
on Windows and with Ansys 13.0 on Linux. However, its usage with these older
versions is discouraged.

.. note::

    The latest versions of Ansys provide significantly better support
    and features. Certain features are not supported on earlier
    Ansys versions.

For more information, see :ref:`versions_and_interfaces`.


For information on installing PyMAPDL, see :ref:`ref_pymapdl_installation`.