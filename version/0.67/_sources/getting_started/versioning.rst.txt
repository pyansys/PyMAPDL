.. _versions_and_interfaces:

=======================
Versions and interfaces
=======================

The PyMAPDL project attempts to maintain compatibility with legacy
versions of MAPDL while allowing for support of faster and better
interfaces with the latest versions of MAPDL.

There are three interfaces PyMAPDL can use to connect to MAPDL.
You can see a table with the MAPDL version and the supported interfaces
in `Table of supported versions <table_versions_>`_


gRPC interface
==============

This is the default and preferred interface to connect to MAPDL.
Ansys 2020 R1 and later support the latest `gRPC interface <grpc_>`_, allowing
for remote management of MAPDL with rapid streaming of mesh, results,
and files from the MAPDL service.

This interface also works with a Docker image.
If you have the applicable license, you can install and use 
MAPDL within Docker, enabling you
to run and solve even on officially unsupported platforms like Mac
OS. For more information, see :ref:`pymapdl_docker`.


Legacy interfaces
=================

CORBA interface
---------------

.. vale off

Ansys 17.0 supports the legacy CORBA interface, enabled with the
`ansys.mapdl.corba <https://github.com/ansys/pymapdl-corba>`_ module.

.. vale on

This interface allows you to send only
text to and from the MAPDL service, relying on file IO for all other
operations. While not as performant as gRPC, this interface still
allows you to control a local instance of MAPDL. These versions of
MAPDL support specific versions of Windows and Linux.
For more information on supported platforms, see 
`Ansys Platform Support <ansys_platform_support_>`_.
    
The CORBA interface is likely to be phased out from MAPDL at some
point. The gRPC interface is faster, more stable, and can run in
both local and remote connection configurations.

Deprecation of CORBA Interface in PyMAPDL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from version v0.67 of PyMAPDL library, the CORBA interface
is set to be deprecated and eventually removed.
This decision is driven by the CORBA library's lack of support
for Python versions superior to 3.8.

**Action Required:** If you currently rely on the CORBA interface,
it is recommend planning for its replacement as you migrate to
PyMAPDL v0.67 or later versions. Specifying a different mode when
launching MAPDL should suffice. PyMAPDL maintainers understand that
this change may impact some users, and apologize for any inconvenience it
may cause.

**Why is this happening?** As the Python ecosystem evolves,
maintaining compatibility with outdated libraries becomes
increasingly challenging. By removing the CORBA interface,
PyMAPDL remains compatible with modern Python
environments, enabling the maintainers to provide better
features and support in the future.

**When this happen?** The deprecation process is set to start
with version v0.66 and it should be completed with version v0.67.
While the exact timeline for the removal is yet to be determined,
it is essential to prepare for its eventual deprecation.

**Alternative Solutions:** For users requiring a similar feature,
it is recommended exploring alternative interfaces available in PyMAPDL.

PyMAPDL maintainers greatly appreciate your support and understanding
during this transition.
If you have any questions or concerns regarding this change,
email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_ or
post them on the `PyMAPDL Discussions <https://github.com/ansys/pymapdl>`_ page.

Console interface
-----------------

PyMAPDL project supports Ansys versions as early as 13.0 on Linux using a
console interface. Like CORBA, the console interface allows for the exchange of text to
and from the Ansys instance.

Because console-specific support is to be depreciated at some point, you should
shift to a modern version of Ansys to continue to use PyMAPDL.


Compatibility between MAPDL and interfaces
==========================================

The following table shows the supported versions of Ansys and the recommended interface for each one of them in PyMAPDL.


**Table of supported versions**

.. _table_versions:

+---------------------------+------------------------+-----------------------------------------------------------------------+
| Ansys Version             | Recommended interface  | Support                                                               |
|                           |                        +-----------------------+-----------------------+-----------------------+
|                           |                        | gRPC                  | CORBA                 | Console (Only Linux)  |
+===========================+========================+=======================+=======================+=======================+
| Ansys 2023 R1             | gRPC                   | |:heavy_check_mark:|  | |:heavy_minus_sign:|  | |:heavy_minus_sign:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2022 R2             | gRPC                   | |:heavy_check_mark:|  | |:heavy_minus_sign:|  | |:heavy_minus_sign:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2022 R1             | gRPC                   | |:heavy_check_mark:|  | |:heavy_minus_sign:|  | |:heavy_minus_sign:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2021 R2             | gRPC                   | |:heavy_check_mark:|  | |:heavy_check_mark:|  | |:heavy_minus_sign:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2021 R1             | gRPC                   | |:heavy_check_mark:|  | |:heavy_check_mark:|  | |:heavy_minus_sign:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2020 R2             | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2020 R1             | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2019 R3             | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2019 R2             | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 2019 R1             | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 19.2                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 19.1                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 19.0                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 18.2                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 18.1                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 18.0                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 17.2                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 17.1                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 17.0                | CORBA                  | |:x:|                 | |:heavy_check_mark:|  | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Ansys 16.2                | Console                | |:x:|                 | |:x:|                 | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+
| Older up to Ansys 13.0    | Console                | |:x:|                 | |:x:|                 | |:heavy_check_mark:|  |
+---------------------------+------------------------+-----------------------+-----------------------+-----------------------+

Where:

* |:heavy_check_mark:| means that the interface is supported and recommended.
* |:heavy_minus_sign:| means that the interface is supported, but not recommended. Their support might be dropped in the future.
* |:x:| means that the interface is not supported.


MAPDL-supported operative systems
=================================

You can obtain the list of MAPDL-supported operative systems on the
`Platform Support <ansys_platform_support_>`_ page of the Ansys website.

Or, you can `download <ansys_current_supported_os_>`_ the list for the current release. 