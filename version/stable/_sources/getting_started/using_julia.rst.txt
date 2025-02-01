.. _using_julia:


*****************
Julia and PyMAPDL
*****************

If you like to work with Julia, you can use Python libraries as if they were Julia packages.


Install Julia
=============

To install Julia, go to `their website <julia_>`_ and follow the instructions given in the **Download** section.

* `Windows <julia_windows_>`_
* `Linux <julia_linux_and_freebsd_>`_
* `MacOS <julia_macos_>`_

Set the Julia environment
=========================

To have access to Python libraries within Julia, you must install the `PyCall <pycall_>`_ Julia package.
To install it, run Julia and switch to the package manager by pressing the ``"]"`` key.

If you need to work with different package versions or applications, it is beneficial to create a virtual environment in Julia.
To create a virtual environment, use the ``activate`` command with the name of the new environment that you want to create or activate.

.. code:: jlcon

    pkg> activate julia_test
      Activating project at `C:/Users/USER/julia_test`


A message should appear, indicating that the new package (``julia_test``) has been activated. This environment name now precedes the command line.

.. code:: jlcon

    (julia_test) pkg>

Next install the PyCall package by typing:

.. code:: jlcon

    (julia_test) pkg> add PyCall


To use PyCall, press the backspace key to go to the Julia command line.
The command line is then preceded by the name ``Julia``. 

.. code:: jlcon

    julia>

Next use the PyCall package with:

.. code:: jlcon

    julia> using PyCall


This should be enough to use packages included in a basic Python distribution. 


For example:

.. code:: jlcon

    julia> math = pyimport("math")
    math.sin(math.pi/4) # returns ≈ 1/√2 = 0.70710678..


Install PyMAPDL in Julia
========================

PyCall includes a lightweight Python environment that uses `Conda <conda_>`_ to manage and access Python packages.
This environment, currently based on Python 3.9.7, includes the standard basic Python libraries.
However, because it is a fully working Python environment, you can still use it from outside the Julia command line and install Python packages using ``pip``.

To install PyMAPDL, first locate the Python executable with:

.. code:: jlcon

    julia> PyCall.python
    "C:\\Users\\USER\\.julia\\conda\\3\\python.exe"

In Linux, the preceding code prints the following, where ``python3`` is the default Python3 installation for the operating system.

.. code:: jlcon
    
    julia> PyCall.python
    "python3"


.. note::

    In Linux, there are no specific installation steps. You only need to add the Julia executable to the path.
    Hence, Julia's Python installation path can differ from user to user.
    For example, if you uncompress the source files in ``/home/USER/Julia``, Julia's path is 
    ``/home/USER/Julia/julia-1.7.2/bin``.

You would use this Python executable to install PyMAPDL:

.. code:: console

    C:\Users\USER\.julia\conda\3\python.exe -m pip install ansys-mapdl-core

In Linux:, you would install with:

.. code:: console

    python3 -m pip install ansys-mapdl-core


Finally, after restarting Julia, you can import PyMAPDL using the same procedure as described earlier:

.. code:: jlcon
    
    julia> using PyCall
    julia> pymapdl = pyimport("ansys.mapdl.core")
    PyObject <module 'ansys.mapdl.core' from 'C:\\Users\\USER\\.julia\\conda\\3\\lib\\site-packages\\ansys\\mapdl\\core\\__init__.py'>
    julia> mapdl = pymapdl.launch_mapdl()
    julia> print(mapdl.__str__())
    Product:             Ansys Mechanical Enterprise
    MAPDL Version:       24.1
    ansys.mapdl Version: 0.68.0
    
.. note::
    If you experience errors when using PyCall, you can try to rebuild the package by pressing ``"]"`` to go to the package manager and typing:
    
    .. code:: jlcon
        
        pkg> build PyCall


Use PyMAPDL in Julia
====================

Here is a simple example of how you use PyMAPDL in Julia:

.. code:: julia

    using PyCall
    pymapdl = pyimport("ansys.mapdl.core")
    mapdl = pymapdl.launch_mapdl()
    np = pyimport("numpy")
    # define cylinder and mesh parameters
    torque = 100
    radius = 2
    h_tip = 2
    height = 20
    elemsize = 0.5
    pi = np.arccos(-1)
    force = 100/radius
    pressure = force/(h_tip*2*np.pi*radius)
    # Define higher-order SOLID186
    # Define surface effect elements SURF154 to apply torque
    # as a tangential pressure
    mapdl.prep7()
    mapdl.et(1, 186)
    mapdl.et(2, 154)
    mapdl.r(1)
    mapdl.r(2)
    # Aluminum properties (or something)
    mapdl.mp("ex", 1, 10e6)
    mapdl.mp("nuxy", 1, 0.3)
    mapdl.mp("dens", 1, 0.1/386.1)
    mapdl.mp("dens", 2, 0)
    # Simple cylinder
    for i in 1:5
        mapdl.cylind(radius, "", "", height, 90*(i-1), 90*i)
    end
    mapdl.nummrg("kp")
    # interactive volume plot (optional)
    mapdl.vplot()
    # mesh cylinder
    mapdl.lsel("s", "loc", "x", 0)
    mapdl.lsel("r", "loc", "y", 0)
    mapdl.lsel("r", "loc", "z", 0, height - h_tip)
    mapdl.lesize("all", elemsize*2)
    mapdl.mshape(0)
    mapdl.mshkey(1)
    mapdl.esize(elemsize)
    mapdl.allsel("all")
    mapdl.vsweep("ALL")
    mapdl.csys(1)
    mapdl.asel("s", "loc", "z", "", height - h_tip + 0.0001)
    mapdl.asel("r", "loc", "x", radius)
    mapdl.local(11, 1)
    mapdl.csys(0)
    mapdl.aatt(2, 2, 2, 11)
    mapdl.amesh("all")
    mapdl.finish()
    # plot elements
    mapdl.eplot()


.. note:: Notice the changes in the strings and the loops. Only ``""`` strings are allowed.
