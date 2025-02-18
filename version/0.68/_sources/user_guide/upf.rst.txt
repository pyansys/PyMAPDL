.. _python_upf:


Using Python to code UPF subroutines
====================================

As an alternative to compiled languages like C and Fortran, you can use the
Python language to code user programmable subroutines. A subset of the
documented UPF subroutines support the Python UPF capability. For more information,
see `Supported UPF subroutines`_).

You must install a Python distribution before using this feature. Python 3.9
through Python 3.12 are supported.

Python UPFs are only supported on Linux.

You are strongly advised to start your code based on one of the examples in
`Python UPF examples`_.  In your Python code, you can make use of standard
Python libraries like NumPy.

These topics are available:

* `Supported UPF subroutines`_
* `Python UPF methodology`_
* `Accessing the database from the Python code`_
* `Python UPF limitations`_
* `Python UPF examples`_


Supported UPF subroutines
-------------------------

A subset of the entire set of available UPF subroutines supports Python coding. The following
table lists those that are supported.

**Table 1: Python support for subroutines** 


+---------------------------------------+-----------------------------------------------------------------------------+
| **Subroutine**                        | **Fortran description**                                                     |
+=======================================+=============================================================================+
|                              **Material behavior**                                                                  |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UserMat``                           | Subroutine ``UserMat`` (Creating Your Own Material Model)                   |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UserMatTh``                         | Subroutine ``UserMatTh`` (Creating Your Own Thermal Material Model)         |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UserHyper``                         | Subroutine ``UserHyper`` (Writing Your Own Isotropic Hyperelasticity Laws)  |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UserCreep``                         | Subroutine ``UserCreep`` (Defining Creep Material Behavior)                 |
+---------------------------------------+-----------------------------------------------------------------------------+
|                              **Modifying and Monitoring Elements**                                                  |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UsrShift``                          | Subroutine ``UsrShift`` (Calculating Pseudotime Time Increment)             |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UTimeInc``                          | Subroutine ``UTimeInc`` (Overriding the Program-Determined Time Step)       |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UCnvrg``                            | Subroutine ``UCnvrg`` (Overriding the Program-Determined Convergence)       |
+---------------------------------------+-----------------------------------------------------------------------------+
|                              **Customizing loads**                                                                  |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``usrefl``                            | Subroutine ``usrefl`` (Changing Scalar Fields to User-Defined Values)       |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``userpr``                            | Subroutine ``userpr`` (Changing Element Pressure Information)               |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``usercv``                            | Subroutine ``usercv`` (Changing Element Face Convection Surface Information)|
+---------------------------------------+-----------------------------------------------------------------------------+
| ``userfx``                            | Subroutine ``userfx`` (Changing Element Face Heat Flux Surface Information) |
+---------------------------------------+-----------------------------------------------------------------------------+
|                              **Accessing subroutines**                                                              |
+---------------------------------------+-----------------------------------------------------------------------------+
| ``UanBeg`` / ``UanFin``               | Access at the beginning and end of various operations                       |
|                                       |                                                                             |
| ``USolBeg`` / ``USolFin``             |                                                                             |
|                                       |                                                                             |
| ``ULdBeg`` / ``ULdFin``               |                                                                             |
|                                       |                                                                             |
| ``UItBeg`` / ``UItFin``               |                                                                             |
|                                       |                                                                             |
| ``USsBeg`` / ``USsFin``               |                                                                             |
+---------------------------------------+-----------------------------------------------------------------------------+


Python UPF methodology
----------------------

Coding a Python UPF is different from using a compiled language like C/C++ or Fortran,
mainly in terms of the API. Because the `gRPC technology <grpc_>`_ is used to handle
the communication and the exchange of data between the Python process and the Mechanical APDL
process, you need to understand the way this feature handles the serialization and
deserialization of data.

The main difference is in the subroutine arguments. Instead of having a full list of
arguments as described for each of the subroutines, there are only two: the request
object (for inputs), and the response object (for outputs). If an argument is both input
and output of the subroutine, it is part of both objects.

The description of the request object and the response object can be found in the
``MapdlUser.proto`` file stored in this installation directory:


.. code:: output

    Ansys Inc\vXXX\ansys\syslib\ansGRPC\User

Where ``XXX`` is the version of Mechanical APDL you are using.
For example ``222`` for Mechanical APDL 2022R2.

First, create a Python file starting from this template:


**my\_upf.py** 

.. code:: python

    import grpc
    import sys
    from mapdl import *


    class MapdlUserService(MapdlUser_pb2_grpc.MapdlUserServiceServicer):
        #   #################################################################
        def UAnBeg(self, request, context):
            print(" ======================================= ")
            print(" >> Inside the PYTHON UAnBeg routine  << ")
            print(" ======================================= \n")

            response = google_dot_protobuf_dot_empty__pb2._EMPTY()
            return response


    if __name__ == "__main__":
        upf.launch(sys.argv[0])


Note that Mechanical APDL automatically installs a Mechanical APDL Python package (a
set of Python functions) to handle the connection between Mechanical APDL and the Python
environment. Each Python UPF must be imported:


.. code:: python

    from mapdl import *


The preceding example redefines the `UAnBeg` routine and prints a
customized banner. This file must be in the same directory as the input file.

To use this Python UPF, you must add the Mechanical APDL ``/UPF`` command to your
input file (``my\_inp.dat``).

.. code:: apdl

    /UPF,'my_upf.py'

    ! The UAnBeg UPF must be activated by using the USRCAL APDL command

    USRCAL,UANBEG


This command is trapped by the Mechanical APDL Launcher so that a Python gRPC server is up
and running when the Mechanical APDL process starts.

When launching Mechanical APDL using this input file, you see the following printout to
indicate Mechanical APDL detected the Python UPF instructions and has launched a Python
server:


.. code:: output

    Processing "/upf" found in input file "my_inp.dat"

    Python UPF Detected

    PYTHON VERSION : 3.10
    >>
    >> START PYTHON GRPC SERVER
    >>
    >> User Functions Python File :  my_upf.py
    >>
    >> Server started on port [50054]


During the Mechanical APDL process, you see this Python printout:


.. code:: output

    RUN SETUP PROCEDURE FROM FILE= /ansys_inc/v241/ansys/apdl/start.ans
    =======================================
    >> Inside the PYTHON UAnBeg routine  <<
    =======================================


At the very end of the process, the Python server is automatically shut
down:


.. code:: output
    
    |-----------------------------------------------------------------|
    |                                                                 |
    |   CP Time      (sec) =          0.326       Time  =  10:40:24   |
    |   Elapsed Time (sec) =          2.000       Date  =  03/11/2021 |
    |                                                                 |
    *-----------------------------------------------------------------*

    >> We shutdown Python Server(s)



Accessing the database from the Python code
-------------------------------------------

Within your UPF routine, you might need to access the Mechanical APDL database in read/write
mode. 

In the Python code, you can create a connection with the DB server. This command must
be called only once, so that you can protect the call based on the value of a static
variable:


.. code:: python

    import grpc
    import sys
    from mapdl import *

    firstcall = 1


    class MapdlUserService(MapdlUser_pb2_grpc.MapdlUserServiceServicer):
        #   ###############################################################
        def UserMat(self, request, context):
            global firstcall

            if firstcall == 1:
                print(">> Connection to the MAPDL DB Server\n")
                db.start()
                firstcall = 0

            # continuation of the python function
            # ...


Once the DB connection has been initialized, you can access the database of the
Mechanical APDL instance in read/write mode. 

Of the functions documented in accessing the Mechanical APDL Database, a
subset has been exposed so that they can be called from the Python code.
The following table describes the exposed functions.

**Table 2. Supported database access functions**

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Supported database access functions**                                                                                                                                                                                                              |
+==========================================================+===========================================================================================================================================================================================+
| ``db.start()``                                           | Initializes the connection with a running Mechanical APDL instance. The DB Server is automatically started in Mechanical APDL if a **/UPF** command with a Python file has been detected. |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.stop()``                                            | Closes the connection with the DB Server.                                                                                                                                                 |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.ndnext(next)``                                      | Equivalent to the function described in function ``ndnext`` (Getting the Next Node Number)                                                                                                |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.ndinqr(ind, key)``                                  | Equivalent to the function described in function ``ndinqr`` (Getting Information About a Node)                                                                                            |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.getnod(inod)``                                      | Equivalent to the function described in function ``getnod`` (Getting a Nodal Point)                                                                                                       |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.putnod(inod, x, y, z)``                             | Equivalent to the function described in function ``putnod`` (Storing a Node)                                                                                                              |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.elnext(ielm)``                                      | Equivalent to the function described in function ``elnext`` (Getting the Number of the Next Element)                                                                                      |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.getelem(ielm)``                                     | Equivalent to the function described in function ``elmget`` (Getting an Element's Attributes and Nodes)                                                                                   |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.get_ElmInfo(inquire)``                              | Equivalent to the function ``get\_ElmInfo`` described in accessing Solution and Material Data                                                                                             |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.get_ElmData(kchar, elemId, kMatRecPt, ncomp, vect)``| Equivalent to the function ``get\_ElmData`` described in accessing Solution and Material Data                                                                                             |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``db.putElmData(inquire, elemId, kIntg, nvect, vect)``   | Equivalent to the function ``put\_ElmData`` described in accessing Solution and Material Data                                                                                             |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Python UPF limitations
----------------------

The Python UPF capability has these limitations:

* Currently, Distributed Ansys is not supported. You must specify the ``-smp`` option on the command line to make sure Mechanical APDL is running in shared-memory processing mode.
* Python UPFs are only available on Linux platforms.



Python UPF examples
-------------------

The following Python UPF examples are available in :ref:`python_upf_examples`:

* Python `UserMat` subroutine
* Python `UsrShift` subroutine
* Python `UserHyper` subroutine

