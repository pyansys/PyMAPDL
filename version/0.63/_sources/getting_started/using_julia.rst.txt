.. _using_julia:


***********************
Using PyMAPDL in Julia
***********************

If you like to work with Julia, you can use Python libraries as if they were Julia packages.


Installing Julia
=================

To install Julia go to their website `<https://julialang.org/>`_ and follow the instructions given in the *Download* section.

* `Windows <https://julialang.org/downloads/platform/#windows>`_
* `Linux <https://julialang.org/downloads/platform/#linux_and_freebsd>`_
* `MacOS <https://julialang.org/downloads/platform/#macos>`_

Setting Julia Environment
==========================

To have access to Python libraries within Julia, you must install the [PyCall](https://github.com/JuliaPy/PyCall.jl) Julia package.
To install it, run Julia and switch to the package manager by pressing  the``"]"`` key.

If you need to work with different package versions or applications, it is beneficial to create a virtual environment in Julia.
To create a virtual environment, use the ``activate`` command with the name of the new environment that you want to create or activate.

.. code-block::

    (@1.7) pkg> activate julia_test
      Activating project at `C:/Users/USER/julia_test`


A message should appear, indicating that the new package (``julia_test``) has been activated. This environment name will now precede the command line.

.. code-block:: julia

    (julia_test) pkg>

Next install the *PyCall* package by typing:

.. code-block:: julia

    (julia_test) pkg> add PyCall


To use *PyCall*, press the backspace key to go to the Julia command line.
The command line will now be precede by the name ``Julia``. 

.. code-block:: julia

    julia>

Next use the *PyCall* package with:

.. code-block:: julia

    julia> using PyCall


This should be enough to use packages included in a basic Python distribution. 


For example:

.. code-block:: julia

    julia> math = pyimport("math")
    math.sin(math.pi/4) # returns ≈ 1/√2 = 0.70710678..


Installing PyMAPDL in Julia
===========================

*PyCall* includes a lightweight Python environment that uses `Conda <https://conda.io>`_ to manage and access Python packages.
This environment, currently based on Python 3.9.7, includes the standard basic Python libraries.
However, because it is a fully working Python environment, you can still use it from outside the Julia command line and install Python packages using ``pip``.

To install PyMAPDL, first locate the Python executable with:

.. code-block:: julia

    julia> PyCall.python
    "C:\\Users\\USER\\.julia\\conda\\3\\python.exe"

In Linux, the above code prints the following, where ``python3`` is the default Python3 installation for the operating system.

.. code-block:: julia
    
    julia> PyCall.python
    "python3"


.. note::

    In Linux, there are no specific installation steps. You only need to add the Julia executable to the path.
    Hence, Julia's Python installation path can differ from user to user.
    For example, if you uncompress the source files in ``/home/USER/Julia``, Julia's path will be 
    ``/home/USER/Julia/julia-1.7.2/bin``

You would use this Python executable to install PyMAPDL:

.. code:: bash

    C:\Users\USER\.julia\conda\3\python.exe -m pip install ansys-mapdl-core

In Linux:, you would install with:

.. code:: bash

    python3 -m pip install ansys-mapdl-core


Finally, after restarting Julia, you can import PyMAPDL using the same procedure as described above:

.. code-block::
    
    julia> using PyCall
    julia> pymapdl = pyimport("ansys.mapdl.core")
    PyObject <module 'ansys.mapdl.core' from 'C:\\Users\\USER\\.julia\\conda\\3\\lib\\site-packages\\ansys\\mapdl\\core\\__init__.py'>
    julia> mapdl = pymapdl.launch_mapdl()
    julia> print(mapdl.__str__())
    Product:             Ansys Mechanical Enterprise
    MAPDL Version:       21.2
    ansys.mapdl Version: 0.60.6
    
.. note:: 
    If you experience errors when using *PyCall*, you can try to rebuild the package by pressing ``"]"`` to go to the package manager and typing:
    
    .. code::
        
        pkg> build PyCall


Using PyMAPDL in Julia
======================

Here is a simple example of using PyMAPDL in Julia:

.. code-block:: julia

    julia> using PyCall
    julia> pymapdl = pyimport("ansys.mapdl.core")
    julia> mapdl = pymapdl.launch_mapdl()
    julia> np = pyimport("numpy")
    julia> # define cylinder and mesh parameters
    julia> torque = 100
    julia> radius = 2
    julia> h_tip = 2
    julia> height = 20
    julia> elemsize = 0.5
    julia> pi = np.arccos(-1)
    julia> force = 100/radius
    julia> pressure = force/(h_tip*2*np.pi*radius)
    julia> # Define higher-order SOLID186
    julia> # Define surface effect elements SURF154 to apply torque
    julia> # as a tangential pressure
    julia> mapdl.prep7()
    julia> mapdl.et(1, 186)
    julia> mapdl.et(2, 154)
    julia> mapdl.r(1)
    julia> mapdl.r(2)
    julia> # Aluminum properties (or something)
    julia> mapdl.mp("ex", 1, 10e6)
    julia> mapdl.mp("nuxy", 1, 0.3)
    julia> mapdl.mp("dens", 1, 0.1/386.1)
    julia> mapdl.mp("dens", 2, 0)
    julia> # Simple cylinder
    julia> for i in 1:5
                mapdl.cylind(radius, "", "", height, 90*(i-1), 90*i)
    julia> end
    julia> mapdl.nummrg("kp")
    julia> # interactive volume plot (optional)
    julia> mapdl.vplot()
    julia> # mesh cylinder
    julia> mapdl.lsel("s", "loc", "x", 0)
    julia> mapdl.lsel("r", "loc", "y", 0)
    julia> mapdl.lsel("r", "loc", "z", 0, height - h_tip)
    julia> mapdl.lesize("all", elemsize*2)
    julia> mapdl.mshape(0)
    julia> mapdl.mshkey(1)
    julia> mapdl.esize(elemsize)
    julia> mapdl.allsel("all")
    julia> mapdl.vsweep("ALL")
    julia> mapdl.csys(1)
    julia> mapdl.asel("s", "loc", "z", "", height - h_tip + 0.0001)
    julia> mapdl.asel("r", "loc", "x", radius)
    julia> mapdl.local(11, 1)
    julia> mapdl.csys(0)
    julia> mapdl.aatt(2, 2, 2, 11)
    julia> mapdl.amesh("all")
    julia> mapdl.finish()
    julia> # plot elements
    julia> mapdl.eplot()


.. note:: Do notice the changes in the strings (only ``""`` strings are allowed) and the loops.
