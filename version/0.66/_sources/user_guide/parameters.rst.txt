
.. _ref_parameters:

*********************************
Setting and retrieving parameters
*********************************
APDL parameters can be retrieved from and instance of :class:`Mapdl
<ansys.mapdl.core.mapdl._MapdlCore>` using the :attr:`Mapdl.parameters
<ansys.mapdl.core.Mapdl.parameters>`.  For example, if you want to use
MAPDL's :func:`Mapdl.get() <ansys.mapdl.core.Mapdl.get>` method to
populate a parameter, you can then access the parameter with code:

.. code:: pycon

   >>> from ansys.mapdl.core import launch_mapdl
   >>> mapdl = launch_mapdl()
   >>> mapdl.get("DEF_Y", "NODE", 2, "U", "Y")
   >>> mapdl.parameters["DEF_Y"]

You can also set both scalar and array parameters from Python objects
using :attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>`
with:

.. code:: pycon

   >>> mapdl.parameters["MY_ARRAY"] = np.arange(10000)
   >>> mapdl.parameters["MY_ARRAY"]
   array([0.00000e+00, 1.00000e+00, 2.00000e+00, ..., 9.99997e+05,
          9.99998e+05, 9.99999e+05])

   >>> mapdl.parameters["MY_STRING"] = "helloworld"
   >>> mapdl.parameters["MY_STRING"]
   "helloworld"

You can also access some built-in parameters normally accessed through
the :func:`Mapdl.get() <ansys.mapdl.core.Mapdl.get>` method. For example,
instead of getting the current routine with ``\*GET, ACTIVE, 0,
ROUT``, you can access it with this code:

.. code:: pycon

  >>> mapdl.parameters.routine
  'Begin level'


For a full list of the methods and attributes available to the
``Parameters`` class, see :ref:`ref_parameters_api`.

For additional information on PyMAPDL array limitations, see :ref:`ref_numpy_arrays_in_mapdl`.

.. _ref_special_named_param:

Specially named parameters
==========================

Parameters with leading underscores
-----------------------------------

Parameters starting with an underscore (``'_'``) are reserved parameters
for MAPDL macros and routines. Their use is discouraged, and in PyMAPDL
you cannot set them directly.

If you need to set one of these parameters, you can use the
:attr:`Mapdl._run <ansys.mapdl.core.Mapdl._run>`
attribute to avoid PyMAPDL parameter name checks:


.. code:: pycon

   >>> mapdl._run("_parameter=123")
   'PARAMETER _PARAMETER =     123.00000000'

By default, this type of parameter cannot be seen when issuing the
:attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>` attribute.
However, you can change this by setting the
:attr:`Mapdl.parameters.show_leading_underscore_parameters 
<ansys.mapdl.core.Mapdl.parameters.show_leading_underscore_parameters>`
to ``True``:

.. code:: pycon

   >>> mapdl.parameters.show_leading_underscore_parameters = True
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   PORT                             : 50053.0
   _RETURN                          : 0.0
   _STATUS                          : 0.0
   _UIQR                            : 17.0


Parameters with trailing underscores
------------------------------------

Parameters ending with an underscore are recommended for user routines
and macros. You can set this type of parameter in PyMAPDL, but by default,
they cannot be seen in the
:attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>` attribute unless
the :attr:`Mapdl.parameters.show_trailing_underscore_parameters 
<ansys.mapdl.core.Mapdl.parameters.show_trailing_underscore_parameters>` attribute
is set to ``True``:


.. code:: pycon

   >>> mapdl.parameters["param_"] = 1.0
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   >>> mapdl.parameters.show_trailing_underscore_parameters = True
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   PARAM_                           : 1.0


Parameters with leading and trailing underscores
------------------------------------------------

Parameters with both leading and trailing underscores are a special type. These parameters
**CANNOT** be seen in the :attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>` attribute
under any circumstances. Their use is not recommended.

You can still retrieve these special parameters using any of the normal methods
for retrieving parameters. However, you must know the parameter name:


.. code:: pycon

   >>> mapdl.parameters["_param_"] = 1.0
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   >>> print(mapdl.parameters["_param_"])
   1.0

