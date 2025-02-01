.. _write_documentation:

===================
Write documentation
===================

Writing documentation is an excellent way to contribute to a project because it
plays a pivotal role in making the project more accessible and usable. Clear and
comprehensive documentation empowers users and developers to understand,
implement, and troubleshoot the project effectively. It minimizes barriers to
entry, making it easier for newcomers to get involved and for existing
contributors to be more productive.

Good documentation also reduces the burden on maintainers,
as it can answer common questions and help prevent issues. By
creating or improving documentation, you not only enhance the project's quality
but also facilitate knowledge sharing and community growth, making your
contribution invaluable for the project's long-term success.

Set up your environment
=======================

To be able to write and build the documentation, you must follow the same
steps described in :ref:`developing_pymapdl`, but in this case, you must install
documentation dependencies with this command:

.. code:: console

    pip install -e '.[doc]'


Build the documentation
=======================

PyMAPDL documentation is mainly written in reStructuredText
format, saved as RST files in the ``doc/source`` directory.
The tool used to  build the documentation from these reStructuredText files 
is `Sphinx <sphinx_>`_.

Sphinx also build API documentation from source code as well as manages the
cross-referencing between different files, classes, methods, and more.
Additionally, it builds an `examples gallery <pymapdl_examples_gallery_>`_,
where the capabilities of PyMAPDL can be showcased.

The documentation can be built as HTML files or a single PDF file.

To build the documentation as HTML files, you only need to run a single command.


.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> doc\make.bat html

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ make -C doc html
    

The HTML files for the documentation are written to the ``doc/_build/html`` directory.

If you want to build the PDF documentation, you must first install
a LaTeX distribution like `MikTeX <miktex_>`_. You can then run this command:

.. tab-set::

    .. tab-item:: Windows
        :sync: key1

        .. code:: pwsh-session

            (.venv) PS C:\Users\user\pymapdl> doc\make.bat pdf

    .. tab-item:: Linux
        :sync: key1
                
        .. code:: console

            (.venv) user@machine:~$ make -C doc pdf

Running the command to build either HTML files or a PDF file runs the Python files in ``./examples`` in the repository root directory to generate the `examples gallery <pymapdl_examples_gallery_>`_.
The result of running these examples is cached so that the only the changed files
are re-run the next time.

The Sphinx configuration is in the file 
`conf.py <https://github.com/ansys/pymapdl/blob/main/doc/source/conf.py>`_ in :file:`doc/source`.


Write documentation
===================

Writing good documentation for a GitHub repository is crucial to ensure that
users and contributors can understand, use, and contribute to PyMAPDL
effectively. 

Here's a short summary of how to write good documentation:

#. **Use a consistent structure**: Organize your documentation with a clear and
   consistent structure. Use headings, subheadings, and a table of contents if
   necessary to help users navigate your documentation easily.

#. **Use Sphinx properly**: Sphinx has multiple features and directives. Before
   starting to write documentation, you should get familiar with it. For guidance,
   see these Sphinx and DocUtils topics: `Directives <sphinx_directives_>`_,
   `reStructuredText Primer <sphinx_basics_>`_ and
   `reStructuredText Directives <docutils_directives_>`_.

#. **Explain configuration changes**: If you require configuration changes, provide
   clear instructions on how to use this new configuration, along with examples and explanations
   of why they are needed.

#. **Usage Examples**: Include real-world usage examples, code snippets, and
   explanations to demonstrate how users can make the most of PyMAPDL.

#. **Document the API and code**: Thoroughly document each function, class, and method. Include
   parameter descriptions, return values, and usage examples. Follow the
   `numpydoc <numpydoc_>`_ convention for documenting code.

#. **Tutorials and guides**: Create tutorials or guides to help users achieve
   specific tasks or workflows with PyMAPDL. These can be especially
   helpful for complex projects.

#. **Troubleshooting and FAQs**: Anticipate common issues and provide solutions
   in a troubleshooting section. Frequently asked questions (FAQs) can also be
   helpful for addressing common queries.

#. **Maintain and update**: Keep your documentation up to date as the project
   evolves. New features, changes, and bug fixes should be reflected in the
   documentation.

#. **Solicit Feedback**: Invite users and contributors to provide feedback on
   the documentation and be responsive to their suggestions and questions.


Vale linting tool
=================

On the GitHub repository, the CI/CD runs `Vale <vale_>`_, a powerful and extensible linting tool for
checking the writing of each pull request.
If you want to verify locally as well, you must install Vale locally:

Installation
------------

#. **Install Vale**: Follow the instructions in `Installation <vale_installation_>`_
#. **Verify installation**: To confirm that Vale is installed correctly, run this command:

   .. code:: console
    
      vale --version

   You should see the installed Vale version displayed in the terminal.

Usage
-----

Vale is a versatile tool for linting and style checking your documents,
supporting various file formats and providing a wide range of style guides.
Here's a basic example of how to use Vale in PyMAPDL:

#. **Sync styles**: The first time you run Vale in a repository, you must
   sync the styles specified in the :file:`.vale.ini` file by running this command:

   .. code:: console

      vale sync


#. **Lint Your Document**: To verify a document, run Vale from the command line,
   specifying the file or directory you want to lint. For example:

   .. code:: console

       vale --config="./doc/.vale.ini" path/to/your_document.rst

   Vale analyzes your document, and if there are any style guide violations
   or linting issues, it provides feedback in the terminal.

Make sure you have no errors or warnings before opening your pull request.


.. _ref_building_example:

Create an example
=================

Creating an example is also a good way to get familiar with the tool and
contribute to its improvement.
`PyMAPDL gallery <pymapdl_examples_gallery_>`_ contain dozens of examples
that demonstrate PyMAPDL capabilities and features.
You can expand this gallery by creating and sharing your
own example.

This `example template <pymapdl_examples_template_>`_ shows how to
write and structure an example.

There are three types of examples: dynamic, static, and semi-static.

* `Dynamic examples`_
* `Static examples`_
* `Semi-dynamic examples`_


Dynamic examples
----------------

Dynamic examples are based on Python files and must be able to run in under three minutes.
In the PyMAPDL repository, they are in the `examples <pymapdl_examples_>`_ directory.


.. vale off

One dynamic example is the `MAPDL 2D Plane Stress Concentration Analysis <pymapdl_2d_plate_with_a_hole_>`_.
example.
The source code can be found in this GitHub `2d_plate_with_a_hole.py <pymapdl_2d_plate_with_a_hole_>`_. 
This code is then rendered on the 
`MAPDL 2D Plane Stress Concentration Analysis <pymapdl_doc_2d_plate_with_a_hole_>`_ page.
.. vale on

Because dynamic examples must run each time the documentation is built, make sure that they are
short.
If you need longer runtime or big files for your example, feel free to use static or semi-static
examples.


Static examples
---------------

Static examples are based on reStructuredText files and do not have to
be executed or run using Python.
In the PyMAPDL repository, they are in the `doc\source <pymapdl_doc_source_>`_ directory.

One static example is the `Harmonic analysis using the frequency-sweep Krylov method <pymapdl_doc_krylov_example_>`_ example. 
This example shows how to do an harmonic analysis using the Krylov method.
The source code can be found in the GitHub `krylov_example.rst <pymapdl_doc_krylov_example_rst_>`_, and it
is rendered as HTML on the `Harmonic analysis using the frequency-sweep Krylov method <pymapdl_doc_krylov_example_>`_ page.


Semi-dynamic examples
---------------------

Semi-dynamic examples are static RST files that execute Python code using this RST directive:

.. code:: rst

    .. jupyter-execute::
       :hide-code:


These examples are also located in `doc\source <pymapdl_doc_source_>`_ directory.
These type of examples allow you to view and interact with the model.

One semi-dynamic example is the
`Friction stir welding (FSW) simulation <pymapdl_techdemo_28_>`_ example.
In this example, you can interactively explore some of the plots.

The source code can be found in this GitHub `ex_28-tecfricstir.rst <pymapdl_techdemo_28_rst_>`_, which
is then rendered on the `Friction Stir Welding (FSW) Simulation <pymapdl_techdemo_28_>`_ page.


