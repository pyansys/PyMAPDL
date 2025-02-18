"""
.. _ref_how_to_add_an_example_reference_key:

Adding a New Gallery Example
----------------------------
This example demonstrates how to add new examples as well as being a template that can
be used in their creation.

This block comment should be included at the top of any new example. Each example
should have a reference tag/key in the form:

``.. _ref_my_example:``

The ``.. _ref_`` is necessary. Everything that follows is your reference tag. As
convention, we keep all references all in ``snake_case``.

This section should give a brief overview of what the example is about and/or demonstrates.
The title should be changed to reflect the topic your example covers.

New examples should be added as python scripts to:

``PyMAPDL/examples/XY-example-folder-name/``

.. note::
   Avoid creating new folders unless absolutely necessary. If in doubt put the example
   in the folder closest to what it is doing and its precise location can be advised
   on in the pull request. If you *must* create a new folder, make sure to add a
   ``README.txt`` containing a reference, a title and a single sentence description of the folder.
   Otherwise the new folder will be ignored by Sphinx.

Example file names should be in the format:

``XY-example-name.py``

Where ``XY`` is the number of the example. If there are already three examples numbered
``00``, ``01``, and ``02``, then your example must subsequently use the prefix ``03``.

After this preamble is complete, the first code block begins.
"""

# Your code goes here...
from ansys.mapdl.core import launch_mapdl

# start MAPDL and enter the pre-processing routine
mapdl = launch_mapdl()
mapdl

###############################################################################
# Section Title
# ~~~~~~~~~~~~~
# Code blocks can be broken up with text "sections" which are interpreted as
# restructured text.
#
# This will also be translated into a markdown cell in the generated jupyter notebook.
# Sections can contain any information you may have regarding the example
# such as step-by-step comments or notes regarding motivations etc.
#
# As in jupyter notebooks, if code is left unassigned at the end of a code block
# (as with ``mapdl`` in the previous block) the output will be generated and
# printed to the screen according to its ``__repr__``.  Otherwise, you can use ``print()`` to output the ``__str__``.

# more code...
mapdl.clear()
mapdl.prep7()
print(mapdl)
mapdl

###############################################################################
# Plots and images
# ~~~~~~~~~~~~~~~~
# If you use an mapdl plotting command the result will be auto-generated and
# rendered in the page. Like so:

mapdl.block(0, 1, 0, 1, 0, 1)
mapdl.vplot()

###############################################################################
# Further Plots and images
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Matplotlib plots will also be rendered in the html.

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
x = list(range(10))
y = [i**2 + 3 * i - 1 for i in x]
ax.plot(x, y)
ax.set_xlabel("x")
ax.set_ylabel("y")

###############################################################################
# Animations
# ~~~~~~~~~~
# You can even create animations.  See :ref:`ref_pyvista_mesh` for an example.
# Incidentally that is also how you link to another example (via `ref_pyvista_mesh`).
#
#
# Making a Pull Request
# ~~~~~~~~~~~~~~~~~~~~~
# Once your example is complete and you've verified builds locally, you can make a pull request (PR).
# Branches containing examples should be prefixed with `doc/` as per the branch
# naming conventions found here: :ref:`contributing`.
#
# Note that you only need to create the python source example (.py).  The jupyter
# notebook, the example html and the demo script will all be auto-generated via ``sphinx-gallery``.

###############################################################################
# stop mapdl
mapdl.exit()
