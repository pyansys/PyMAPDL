:orphan:

.. _executable_example:

=======================================
Create your own Python command-line app
=======================================

This example shows how to create your own command-line app
in Python that uses PyMAPDL to perform some simulations.
This usage is quite convenient when automating workflows.
You can build different PyMAPDL apps that can be called
from the command line with different arguments.


Simulation configuration
========================

The :download:`rotor.py <rotor.py>` script implements a
command-line interface for calculating the first
natural frequency of a simplified rotor with a given number of
blades and a specific material configuration.


.. literalinclude:: rotor.py


Convert a script to a Python app
================================

To use the preceding script from a terminal, you must convert it to
a Python app. In this case, the app uses a command-line interface to
provide the options to PyMAPDL.

To specify the options, the package `Click <https://click.palletsprojects.com>`_
is used. Another suitable package is the builtin package
`argparse <https://docs.python.org/3/library/argparse.html>`_.


First, you must convert the script to a function. You can
accomplish this by using the input arguments
in a function signature. 

In this case, the following arguments must be specified:

* ``n_blades``: Number of blades.
* ``blade_length``: Length of each blade.
* ``elastic_modulus``: Elastic modulus of the material.
* ``density``: Density of the material.

You can then define the function like this:

.. literalinclude:: cli_rotor.py
   :lines: 4-7, 19-24

You introduce the values of these parameters by adding this code
immediately before the function definition:


.. literalinclude:: cli_rotor.py
   :lines: 2-3,10-25

.. warning:: Because the *Click* package uses decorators (``@click.XXX``,
   you must specify *Click* commands immediately before the function definition.

In addition, you must add the call to the newly created function at the end
of the script:


.. literalinclude:: cli_rotor.py
   :lines: 150-151

This ensure the new function is called when the script is executed.

Now you can call your function from the command line using
this code:

.. code:: console

   $ python rotor.py 8
   Initialize script with values:
   Number of blades: 8
   Blade length: 0.2 m
   Elastic modulus: 200.0 GPa
   Density: 7850 Kg/m3
   Solving...
   The first natural frequency is 325.11 Hz.

The preceding code sets the number of blades to ``8``.
This code shows how you can input other arguments:

.. code:: console

   $ python rotor.py 8 --density 7000
   Initialize script with values:
   Number of blades: 8
   Blade length: 0.2 m
   Elastic modulus: 200.0 GPa
   Density: 7000 Kg/m3
   Solving...
   The first natural frequency is 344.28 Hz.


Advanced usage
==============

You can use these concepts to make Python create files with specific
results that you can later use in other apps.

Postprocess images using ImageMagick
------------------------------------

To create an image with PyMAPDL, you can add this code to the
``rotor.py`` file:

.. code:: python

   mapdl.vplot(savefig="volumes.jpg")


.. image:: volumes.jpg

To add a frame, you can use `ImageMagick <https://www.imagemagick.org>`_:

.. code:: console

   mogrify -mattecolor \#f1ce80 -frame 10x10 volumes.jpg


You can also use Imagemagick to add a watermark:

.. code:: console

   COMPOSITE=/usr/bin/composite
   $COMPOSITE -gravity SouthEast watermark.jpg volumes.jpg volumes_with_watermark.jpg

Here are descriptions for values used in the preceding code:

- ``-gravity``: Location of the watermark in case the watermark is
  smaller than the image.
- ``COMPOSITE``: Path to the ImageMagick ``composite`` function. 
- ``watermark.png``: Name of the PNG file with the watermark image.
- ``volumes_with_watermark.jpg``: Name of the JPG file to save the output to.

The final results should look like the ones in this image:


.. figure:: volumes_with_watermark.jpg

   Volumes image with watermark


Usage on the cloud
------------------

Using these concepts, you can deploy your own apps to the cloud.

For example, you can execute the previous example on a GitHub runner
using this approach (non-tested):

.. code:: yaml
  
   my_job:
      name: 'Generate watermarked images'
      runs-on: ubuntu-latest

      steps:
         - name: "Install Git and check out project"
           uses: actions/checkout@v3

         - name: "Set up Python"
           uses: actions/setup-python@v4

         - name: "Install ansys-mapdl-core"
           run: |
               python -m pip install ansys-mapdl-core
         
         - name: "Install ImageMagic"
           run: |
            sudo apt install imagemagick

         - name: "Generate images with PyMAPDL"
           run: |
            python rotor.py 4 --density 7000

         - name: "Postprocess images"
           run: |
              COMPOSITE=/usr/bin/composite
              mogrify -mattecolor #f1ce80 -frame 10x10 volume.jpg
              $COMPOSITE -gravity SouthEast watermark.jpg volumes.jpg volumes_with_watermark.jpg


Additional files
================

You can use these links to download the example files:

* Original :download:`rotor.py <rotor.py>` script
* App :download:`cli_rotor.py <cli_rotor.py>` script