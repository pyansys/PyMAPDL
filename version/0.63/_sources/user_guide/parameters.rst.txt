
.. _ref_parameters:

*********************************
Setting and Retrieving Parameters
*********************************
APDL parameters can be retrieved from and instance of :class:`Mapdl
<ansys.mapdl.core.mapdl._MapdlCore>` using the :attr:`Mapdl.parameters
<ansys.mapdl.core.Mapdl.parameters>`.  For example, if you wish to use
the MAPDL's :func:`Mapdl.get() <ansys.mapdl.core.Mapdl.get>` to
populate a parameter, you can then access the parameter with:

.. code:: python

   >>> from ansys.mapdl.core import launch_mapdl
   >>> mapdl = launch_mapdl()
   >>> mapdl.get('DEF_Y', 'NODE' , 2, 'U' ,'Y')
   >>> mapdl.parameters['DEF_Y']

You can also set both scalar and array parameters from python objects
using :attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>`
with:

.. code:: python

   >>> mapdl.parameters['MY_ARRAY'] = np.arange(10000)
   >>> mapdl.parameters['MY_ARRAY']
   array([0.00000e+00, 1.00000e+00, 2.00000e+00, ..., 9.99997e+05,
          9.99998e+05, 9.99999e+05])

   >>> mapdl.parameters['MY_STRING'] = "helloworld"
   >>> mapdl.parameters['MY_STRING']
   "helloworld"

You can also access some built-in parameters normally accessed through
the :func:`Mapdl.get() <ansys.mapdl.core.Mapdl.get>`.  For example,
instead of getting the current routine with ``\*GET, ACTIVE, 0,
ROUT``, you can access it with:

.. code:: python

  >>> mapdl.parameters.routine
  'Begin level'


For a full listing of the methods and attributes available to the
``Parameters`` class, please reference the :ref:`ref_parameters_api`.

Please visit :ref:`ref_numpy_arrays_in_mapdl` for further information about 
PyMAPDL array limitations.

.. _ref_special_named_param:

Specially Named Parameters
==========================

Leading Underscored Parameters
------------------------------

The parameters starting with underscore (``'_'``) are reserved parameters
for MAPDL macros and routines. Their use is discouraged, and in PyMAPDL
you cannot set them directly.

If you need to set one of these parameters, you can use
:attr:`Mapdl._run <ansys.mapdl.core.Mapdl._run>`
to avoid PyMAPDL parameter name checks. For example


.. code:: python

   >>> mapdl._run('_parameter=123')
   'PARAMETER _PARAMETER =     123.00000000'

By default, this type of parameter cannot be seen when issuing
:attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>`.
However, you can change this by setting
:attr:`Mapdl.parameters.show_leading_underscore_parameters 
<ansys.mapdl.core.Mapdl.parameters.show_leading_underscore_parameters>`
equal to ``True``.
For example:


.. code:: python

   >>> mapdl.parameters.show_leading_underscore_parameters=True
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   PORT                             : 50053.0
   _RETURN                          : 0.0
   _STATUS                          : 0.0
   _UIQR                            : 17.0


Trailing Underscored Parameters
-------------------------------

Parameters ending with an underscore are recommended for user routines
and macros.
You can set this type of parameter in PyMAPDL, but by default,
they cannot be seen in
:attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>`, unless
:attr:`Mapdl.parameters.show_trailing_underscore_parameters 
<ansys.mapdl.core.Mapdl.parameters.show_trailing_underscore_parameters>`
is set to ``True``.


.. code:: python

   >>> mapdl.parameters['param_'] = 1.0
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   >>> mapdl.parameters.show_trailing_underscore_parameters=True
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   PARAM_                           : 1.0


Parameters with Leading and Trailing Underscore
-----------------------------------------------

These are a special type of parameter. They **CANNOT** be seen in :attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>` under any circumstances. Their use is not recommended.

You can still retrieve them using any of the normal methods
to retrieve parameters. But you need to know the parameter name.
For example:


.. code:: python

   >>> mapdl.parameters["_param_"] = 1.0
   >>> mapdl.parameters
   MAPDL Parameters
   ----------------
   >>> print(mapdl.parameters['_param_'])
   1.0

