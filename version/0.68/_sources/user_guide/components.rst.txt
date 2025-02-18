
.. _ref_components:

*******************
Managing components
*******************

MAPDL components can be retrieved and set using
:attr:`Mapdl.components <ansys.mapdl.core.component.ComponentManager>`.


There are several ways to create a component in MAPDL.

You can use the :meth:`Mapdl.cm <ansys.mapdl.core.Mapdl.cm>` method:

.. code:: pycon

   >>> from ansys.mapdl.core import launch_mapdl
   >>> mapdl = launch_mapdl()
   >>> mapdl.prep7()
   >>> mapdl.block(0, 1, 0, 1, 0, 1)
   >>> mapdl.vsel("s", "", "", 1)
   >>> mapdl.cm("my_comp", "volu")

Or use higher level syntax. For instance, to set a component
specifying the type and items:

.. code:: pycon

    >>> mapdl.components["mycomp3"] = "KP", [1, 2, 3]

Set a component without specifying the type, by default it is ``NODE``:

.. code:: pycon

   >>> mapdl.components["mycomp4"] = (1, 2, 3)
   /Users/german.ayuso/pymapdl/src/ansys/mapdl/core/component.py:347: UserWarning: Assuming   a KP selection.
   It is recommended you use the following notation to avoid this warning:
   > mapdl.components['mycomp4'] = 'KP' (1, 2, 3)
   Alternatively, you disable this warning using:
   > mapdl.components.default_entity_warning=False
   warnings.warn(

You can change the default type by changing
:attr:`Mapdl.components.default_entity <ansys.mapdl.core.component.ComponentManager.default_entity>`

.. code:: pycon

    >>> mapdl.components.default_entity = "KP"
    >>> mapdl.components["mycomp"] = [1, 2, 3]
    >>> mapdl.components["mycomp"].type
    'KP'

You can also create a component from already selected entities:

.. code:: pycon

    >>> mapdl.lsel("S", 1, 2)
    >>> mapdl.components["mylinecomp"] = "LINE"
    >>> mapdl.components["mylinecomp"]
    (1, 2)


Selecting a component and retrieving it:

.. code:: pycon

    >>> mapdl.cmsel("s", "mycomp3")
    >>> mapdl.components["mycomp3"]
    Component(type='KP', items=(1, 2, 3))


.. note:: Component selection
    To being able to access a component through :attr:`Mapdl.components <ansys.mapdl.core.Mapdl.components>`,
    the component needs to be selected using :meth:`Mapdl.cmsel() <ansys.mapdl.core.Mapdl.cmsel>`.


Component object
================

The :class:`Component object <ansys.mapdl.core.component.Component>` is the object returned by 
:attr:`Mapdl.components <ansys.mapdl.core.Mapdl.components>` when you query it with a component name.
This object has two main attributes: :attr:`type <Component.type>` and :attr:`items <Component.items>`.
The former returns the component type (``"ELEM"``, ``"NODE"``, ``"KP"``, etc) and the later returns
a tuple with the index of the entities which belong to that component.

.. code:: pycon

    >>> comp = mapdl.components["mycomp3"]
    >>> comp.type
    'KP'
    >>> comp.items
    (1, 2, 3)

It should be noticed that the component object is not linked to the MAPDL component, so any change on it
is not reflected in the MAPDL counterpart.

