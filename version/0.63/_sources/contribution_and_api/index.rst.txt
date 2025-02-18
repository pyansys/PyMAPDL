.. _ref_contributing:

====================
Contributing and API
====================

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/overview/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `Guidelines and Best Practices
<https://dev.docs.pyansys.com/guidelines/index.html>`_ before attempting to
contribute to PyMAPDL.
 
The following contribution information is specific to PyMAPDL.


Cloning the PyMAPDL Repository
==============================

Run this code to clone and install the latest version of PyMAPDL in development mode:

.. code::

    git clone https://github.com/pyansys/pymapdl
    cd pymapdl
    pip install pip -U
    pip install -e .


Posting Issues
==============

Use the `PyMAPDL Issues <https://github.com/pyansys/pymapdl/issues>`_
page to submit questions, report bugs, and request new features. When possible, we
recommend that you use these issue templates:

* Bug report template
* Feature request template

If your issue does not fit into one of these categories, create your own issue.

To reach the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Viewing PyMAPDL Documentation
=============================

Documentation for the latest stable release of PyMAPDL is hosted at
`PyMAPDL Documentation <https://mapdldocs.pyansys.com>`_.

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at  `Development PyMAPDL Documentation <https://dev.mapdldocs.pyansys.com/>`_.
This version is automatically kept up to date via GitHub actions.

Testing MAPDL
=============

If you do not have MAPDL installed locally but still want to run the
unit testing, you must set up the following environment variables.

In Windows, use:

.. code::

    SET PYMAPDL_START_INSTANCE=False
    SET PYMAPDL_PORT=<MAPDL Port> (default 50052)
    SET PYMAPDL_IP=<MAPDL IP> (default 127.0.0.1)

In Linux, use:

.. code::

    export PYMAPDL_START_INSTANCE=False
    export PYMAPDL_PORT=<MAPDL Port> (default 50052)
    export PYMAPDL_IP=<MAPDL IP> (default 127.0.0.1)

This tells ``ansys.mapdl.core`` to attempt to connect to the existing
MAPDL service by default when the ``launch_mapdl`` function is used.


Code Style
==========

PyMAPDL follows PEP8 standard as outlined in the `PyAnsys Development Guide
<https://dev.docs.pyansys.com>`_ and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks. For example::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed


.. _ref_index_api:

API Reference
=============
This section gives an overview of the API of several public PyMAPDL
classes, functions, and attributes.

These methods may include some MAPDL commands but are generally
specific to pymapdl specific methods and classes (i.e. methods that
extend existing MAPDL methods in a pythonic manner).  For classic
MAPDL commands mapped to PyMAPDL, see :ref:`ref_mapdl_commands`.


.. toctree::
   :maxdepth: 2
   :hidden:

   commands
   database
   geometry
   helper
   inline
   logging
   mapdl
   math
   mesh
   parameters
   plotting
   pool
   post
   solution
   xpl
   