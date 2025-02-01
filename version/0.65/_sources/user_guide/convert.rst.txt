Translate scripts
===================
The `ansys-mapdl-core <pymapdl_docs_>`_
library contains a few basic functions to translate existing MAPDL
scripts into PyMAPDL scripts. Ideally, all math and variable setting
would take place within Python because APDL commands
are less transparent and more difficult to debug.


Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

In PyMAPDL v0.64.0 and later, you use the converter from the command line.
After you have activated and installed the package as described
in :ref:`installation`, you can use the converter from your terminal.
Here is how you use the ``pymapdl_convert_script`` command:

.. code:: console

    $ pymapdl_convert_script mapdl.dat -o python.py

    File mapdl.dat successfully converted to python.py.

To obtain help on converter usage, options, and examples, type this command:

.. code:: console

    $ pymapdl_convert_script --help

    Usage: pymapdl_convert_script [OPTIONS] FILENAME_IN

    PyMAPDL CLI tool for converting MAPDL scripts to PyMAPDL scripts.

    USAGE:

    ...

The ``pymapdl_convert_script`` command uses the
:func:`convert_script() <ansys.mapdl.core.convert_script>` function.
Hence, this command accepts most of this function's arguments.

Usage
-----

You can call this command from the terminal with different
arguments. Here is an example that converts the ``mapdl.dat``
file to a Python file named ``python.py``:

.. code:: console
    
    $ pymapdl_convert_script mapdl.dat -o python.py

    File mapdl.dat successfully converted to python.py.

The output argument is completely optional. If you don't specify it,
the ``py`` extension is used for the file that is outputted:

.. code:: console

    $ pymapdl_convert_script mapdl.dat

    File mapdl.dat successfully converted to mapdl.py.

You can use any option from the
:func:`convert_script() <ansys.mapdl.core.convert_script>` function.

For example, to avoid exiting the MAPDL instance after running
the script, you can use ``--auto-exit`` argument:

.. code:: console

    $ pymapdl_convert_script mapdl.dat --auto-exit False

    File mapdl.dat successfully converted to mapdl.py.

You can skip the imports by setting the ``--add_imports`` option
to ``False``:

.. code:: console

    $ pymapdl_convert_script mapdl.dat --filename_out mapdl.out --add_imports
    False

    File mapdl.dat successfully converted to mapdl.out.

For more information about possible options, use the help
command (``pymapdl_convert_script --help``) or the
:func:`convert_script() <ansys.mapdl.core.convert_script>` 
function documentation.

Caveats
~~~~~~~
These examples only show an automatic translation of a verification:
file and not optimized code. Should it be necessary to pull
parameters or arrays from ansys, use the :func:`Mapdl.get_value()
<ansys.mapdl.core.Mapdl.get_value>` function, which is quite similar to the
MAPDL :func:`Mapdl.get() <ansys.mapdl.core.Mapdl.get>` 
command shown here:

.. code:: pycon

   >>> mapdl.get_value("NODE", 2, "U", "Y")
   4.532094298033

Alternatively, if a parameter is already defined, you can access it
using the :attr:`Mapdl.parameters <ansys.mapdl.core.Mapdl.parameters>` attribute
with:

.. code:: pycon

    >>> mapdl.parameters
    ARR                              : ARRAY DIM (3, 1, 1)
    PARM_FLOAT                       : 20.0
    PARM_INT                         : 10.0
    PARM_LONG_STR                    : "stringstringstringstringstringst"
    PARM_STR                         : "string"
    DEF_Y                            : 4.532094298033

    >>> mapdl.parameters["DEF_Y"]
    4.532094298033


Script translation
~~~~~~~~~~~~~~~~~~
Existing Ansys scripts can be translated using the :func:`convert_script() <ansys.mapdl.core.convert_script>`
function:

.. code:: pycon

    >>> import ansys.mapdl.core as pymapdl
    >>> inputfile = "ansys_inputfile.inp"
    >>> pyscript = "pyscript.py"
    >>> pymapdl.convert_script(inputfile, pyscript)

Or, you can convert code in form of strings for later processing using the
:func:`convert_apdl_block() <ansys.mapdl.core.convert_apdl_block>` function:

.. code:: pycon

    from ansys.mapdl.core.convert import convert_apdl_block

    apdl_string = """/com, This is a block of APDL commands.
    /PREP7
    N,,0,0,0
    N,,0,0,1
    FINISH"""
    pycode = convert_apdl_block(apdl_string)  # apdl_string can be also a list of strings.


The script conversion functions allow some interesting arguments, which you can see in
the respective :func:`convert_script() <ansys.mapdl.core.convert_script>`
and :func:`convert_apdl_block() <ansys.mapdl.core.convert_apdl_block>`
function documentation. Especially interesting are the ``add_imports``, ``comment_solve``, and
``print_com`` keyword arguments.

Of particular note in the following examples is how most of the
commands can be called as a method to the Ansys object rather than
sending a string as a command. Additionally, take note that some
commands require the :attr:`Mapdl.non_interactive
<ansys.mapdl.core.Mapdl.non_interactive>` context manager since some
commands require and may break the server connection for some
interfaces (such as CORBA) or are invalid (as in gRPC).

Also note that APDL macros that use ``*CREATE`` have been replaced
with Python functions. This makes the code easier to debug
should it be necessary to insert a ``breakpoint()`` in the script.


Example: VM1 - statically indeterminate reaction force analysis
---------------------------------------------------------------
Ansys MAPDL contains over 200 verification files used for Ansys
validation and demonstration. These validation files are used here to
demo the use of the PyMAPDL file translator :func:`convert_script()
<ansys.mapdl.core.convert_script>` function and are available in:

.. code:: pycon

    >>> from ansys.mapdl.core import examples
    >>> examples.vmfiles["vm1"]
    '.../ansys/mapdl/core/examples/verif/vm1.dat'

This example translates the verification example ``"vm1.dat"``.

First, the MAPDL code:

.. code:: apdl

    /COM, 'ANSYS MEDIA REL. 150 (11/8/2013) REF. VERIF. MANUAL: REL. 150'
    /VERIFY, VM1
    /PREP7
    /TITLE,'  VM1, STATICALLY INDETERMINATE REACTION FORCE ANALYSIS'
    /COM,'      STR. OF MATL., TIMOSHENKO, PART 1, 3RD ED., PAGE 26, PROB.10'
    ANTYPE, STATIC                  ! STATIC ANALYSIS
    ET, 1, LINK180
    SECTYPE, 1, LINK
    SECDATA, 1  			       ! CROSS SECTIONAL AREA (ARBITRARY) = 1
    MP, EX, 1, 30E6
    N, 1
    N, 2, , 4
    N, 3, , 7
    N, 4, , 10
    E, 1, 2                          ! DEFINE ELEMENTS
    EGEN, 3, 1, 1
    D, 1, ALL, , , 4, 3                  ! BOUNDARY CONDITIONS AND LOADING
    F, 2, FY, -500
    F, 3, FY, -1000
    FINISH
    /SOLU
    OUTPR, BASIC, 1
    OUTPR, NLOAD, 1
    SOLVE
    FINISH
    /POST1
    NSEL, S, LOC, Y, 10
    FSUM
    *GET, REAC_1, FSUM, , ITEM, FY
    NSEL, S, LOC, Y, 0
    FSUM
    *GET, REAC_2, FSUM, , ITEM, FY

    *DIM, LABEL, CHAR, 2
    *DIM, VALUE, , 2, 3
    LABEL(1) = 'R1, lb', 'R2, lb '
    *VFILL, VALUE(1, 1), DATA, 900.0, 600.0
    *VFILL, VALUE(1, 2), DATA, ABS(REAC_1), ABS(REAC_2)
    *VFILL, VALUE(1, 3), DATA, ABS(REAC_1 / 900) , ABS( REAC_2 / 600)
    /OUT, vm1, vrt
    /COM
    /COM,' ------------------- VM1 RESULTS COMPARISON - --------------------'
    /COM,
    /COM,'         |   TARGET   |   Mechanical APDL   |   RATIO'
    /COM,
    *VWRITE, LABEL(1), VALUE(1, 1), VALUE(1, 2), VALUE(1, 3)
    (1X, A8, '   ', F10.1, '  ', F10.1, '   ', 1F5.3)
    /COM, ----------------------------------------------------------------
    /OUT
    FINISH
    *LIST, vm1, vrt

Translate the verification file with:

.. code:: pycon

    >>> from ansys.mapdl import core as pymapdl
    >>> from ansys.mapdl.core import examples
    >>> pymapdl.convert_script(examples.vmfiles["vm1"], "vm1.py")

Here is the translated code:

.. code:: python

    """ Script generated by ansys-mapdl-core version 0.57.0"""
    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl()
    mapdl.run("/COM,ANSYS MEDIA REL. 150 (11/8/2013) REF. VERIF. MANUAL: REL. 150")
    mapdl.run("/VERIFY,VM1")
    mapdl.run("/PREP7")
    mapdl.run("/TITLE, VM1, STATICALLY INDETERMINATE REACTION FORCE ANALYSIS")
    mapdl.run("C***      STR. OF MATL., TIMOSHENKO, PART 1, 3RD ED., PAGE 26, PROB.10")
    mapdl.antype("STATIC")  # STATIC ANALYSIS
    mapdl.et(1, "LINK180")
    mapdl.sectype(1, "LINK")
    mapdl.secdata(1)  # CROSS SECTIONAL AREA (ARBITRARY) = 1
    mapdl.mp("EX", 1, 30e6)
    mapdl.n(1)
    mapdl.n(2, "", 4)
    mapdl.n(3, "", 7)
    mapdl.n(4, "", 10)
    mapdl.e(1, 2)  # DEFINE ELEMENTS
    mapdl.egen(3, 1, 1)
    mapdl.d(1, "ALL", "", "", 4, 3)  # BOUNDARY CONDITIONS AND LOADING
    mapdl.f(2, "FY", -500)
    mapdl.f(3, "FY", -1000)
    mapdl.finish()
    mapdl.run("/SOLU")
    mapdl.outpr("BASIC", 1)
    mapdl.outpr("NLOAD", 1)
    mapdl.solve()
    mapdl.finish()
    mapdl.run("/POST1")
    mapdl.nsel("S", "LOC", "Y", 10)
    mapdl.fsum()
    mapdl.run("*GET,REAC_1,FSUM,,ITEM,FY")
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.fsum()
    mapdl.run("*GET,REAC_2,FSUM,,ITEM,FY")
    mapdl.run("*DIM,LABEL,CHAR,2")
    mapdl.run("*DIM,VALUE,,2,3")
    mapdl.run("LABEL(1) = 'R1, lb','R2, lb '")
    mapdl.run("*VFILL,VALUE(1,1),DATA,900.0,600.0")
    mapdl.run("*VFILL,VALUE(1,2),DATA,ABS(REAC_1),ABS(REAC_2)")
    mapdl.run("*VFILL,VALUE(1,3),DATA,ABS(REAC_1 / 900) ,ABS( REAC_2 / 600)")
    mapdl.run("/OUT,vm1,vrt")
    mapdl.run("/COM")
    mapdl.run("/COM,------------------- VM1 RESULTS COMPARISON ---------------------")
    mapdl.run("/COM,")
    mapdl.run("/COM,         |   TARGET   |   Mechanical APDL   |   RATIO")
    mapdl.run("/COM,")
    with mapdl.non_interactive:
        mapdl.run("*VWRITE,LABEL(1),VALUE(1,1),VALUE(1,2),VALUE(1,3)")
        mapdl.run("(1X,A8,'   ',F10.1,'  ',F10.1,'   ',1F5.3)")
    mapdl.run("/COM,----------------------------------------------------------------")
    mapdl.run("/OUT")
    mapdl.finish()
    mapdl.run("*LIST,vm1,vrt")
    mapdl.exit()


Here are the results from running the converted file:

.. code:: output

    ------------------- VM1 RESULTS COMPARISON ---------------------
    |   TARGET   |   Mechanical APDL   |   RATIO
    /INPUT FILE=    LINE=       0
    R1, lb          900.0       900.0   1.000
    R2, lb          600.0       600.0   1.000
    ----------------------------------------------------------------

You can verify the reaction forces with:

.. code:: pycon

   >>> rst = mapdl.result
   >>> nnum, forces = rst.nodal_static_forces(0)
   >>> print(forces)
   [[   0. -600.    0.]
    [   0.  250.    0.]
    [   0.  500.    0.]
    [   0. -900.    0.]]

Note that some of the commands with ``/`` are not directly translated
to functions and are instead run as "classic" commands like
``mapdl.run('/COM')``. Also, note that the ``*VWRITE`` command
requires a command immediately following it. This normally locks the
interface, so it's implemented in the background as an input file
using the :attr:`Mapdl.non_interactive <ansys.mapdl.core.Mapdl.non_interactive>`
attribute.


VM7 - plastic compression of a pipe assembly
--------------------------------------------
Here is the input file from VM7:

.. code:: apdl

    /COM,'ANSYS MEDIA REL. 150 (11/8/2013) REF. VERIF. MANUAL: REL. 150'
    /VERIFY,VM7
    /PREP7
    /TITLE,' VM7, PLASTIC COMPRESSION OF A PIPE ASSEMBLY'
    /COM,'          MECHANICS OF SOLIDS, CRANDALL AND DAHL, 1959, PAGE 180, EX. 5.1'
    /COM,'          USING PIPE288, SOLID185 AND SHELL181 ELEMENTS'
    THETA=6                              ! SUBTENDED ANGLE
    ET,1,PIPE288,,,,2
    ET,2,SOLID185
    ET,3,SHELL181,,,2                    ! FULL INTEGRATION
    SECTYPE,1,SHELL
    SECDATA,0.5,1,0,5	                   ! THICKNESS (SHELL181)
    SECTYPE,2,SHELL
    SECDATA,0.5,2,0,5	                   ! THICKNESS (SHELL181)
    SECTYPE,3,PIPE
    SECDATA,4.9563384,0.5                ! OUTSIDE DIA. AND WALL THICKNESS FOR INSIDE TUBE (PIPE288)
    SECTYPE,4,PIPE
    SECDATA,8.139437,0.5                 ! OUTSIDE DIA. AND WALL THICKNESS FOR OUTSIDE TUBE (PIPE288)
    MP,EX  ,1,26.875E6                   ! STEEL
    MP,PRXY,1,0.3
    MP,EX  ,2,11E6                       ! ALUMINUM
    MP,PRXY,2,0.3
    TB,BKIN,1,1                          ! DEFINE NON-LINEAR MATERIAL PROPERTY FOR STEEL
    TBTEMP,0
    TBDATA,1,86000,0
    TB,BKIN,2,1                          ! DEFINE NON-LINEAR MATERIAL PROPERTY FOR ALUMINUM
    TBTEMP,0
    TBDATA,1,55000,0
    N,1                                  ! GENERATE NODES AND ELEMENTS FOR PIPE288
    N,2,,,10
    MAT,1  
    SECNUM,3                             ! STEEL (INSIDE) TUBE
    E,1,2
    MAT,2  
    SECNUM,4                             ! ALUMINUM (OUTSIDE) TUBE
    E,1,2
    CSYS,1
    N,101,1.9781692                      ! GENERATE NODES AND ELEMENTS FOR SOLID185
    N,102,2.4781692
    N,103,3.5697185
    N,104,4.0697185
    N,105,1.9781692,,10
    N,106,2.4781692,,10
    N,107,3.5697185,,10
    N,108,4.0697185,,10
    NGEN,2,10,101,108,,,THETA            ! GENERATE 2ND SET OF NODES TO FORM A THETA DEGREE SLICE
    NROTAT,101,118,1
    TYPE,2
    MAT,1                                ! INSIDE (STEEL) TUBE
    E,101,102,112,111,105,106,116,115
    MAT,2                                ! OUTSIDE (ALUMINUM) TUBE
    E,103,104,114,113,107,108,118,117
    N,201,2.2281692                      ! GENERATE NODES AND ELEMENTS FOR SHELL181
    N,203,2.2281692,,10
    N,202,3.8197185
    N,204,3.8197185,,10
    NGEN,2,4,201,204,,,THETA             ! GENERATE NODES TO FORM A THETA DEGREE SLICE
    TYPE,3
    SECNUM,1                             ! INSIDE (STEEL) TUBE
    E,203,201,205,207
    SECNUM,2                             ! OUTSIDE (ALUMINUM) TUBE
    E,204,202,206,208
    /COM,' APPLY CONSTRAINTS TO PIPE288 MODEL'
    D,1,ALL                              ! FIX ALL DOFS FOR BOTTOM END OF PIPE288
    D,2,UX,,,,,UY,ROTX,ROTY,ROTZ         ! ALLOW ONLY UZ DOF AT TOP END OF PIPE288 MODEL
    /COM,' APPLY CONSTRAINTS TO SOLID185 AND SHELL181 MODELS'
    CP,1,UX,101,111,105,115              ! COUPLE NODES AT BOUNDARY IN RADIAL DIR FOR SOLID185
    CPSGEN,4,,1
    CP,5,UX,201,205,203,20               ! COUPLE NODES AT BOUNDARY IN RADIAL DIR FOR SHELL181
    CPSGEN,2,,5
    CP,7,ROTY,201,205                    ! COUPLE NODES AT BOUNDARY IN ROTY DIR FOR SHELL181
    CPSGEN,4,,7
    NSEL,S,NODE,,101,212                 ! SELECT ONLY NODES IN SOLID185 AND SHELL181 MODELS
    NSEL,R,LOC,Y,0                       ! SELECT NODES AT THETA = 0 FROM THE SELECTED SET
    DSYM,SYMM,Y,1                        ! APPLY SYMMETRY BOUNDARY CONDITIONS
    NSEL,S,NODE,,101,212                 ! SELECT ONLY NODES IN SOLID185 AND SHELL181 MODELS
    NSEL,R,LOC,Y,THETA                   ! SELECT NODES AT THETA FROM THE SELECTED SET
    DSYM,SYMM,Y,1                        ! APPLY SYMMETRY BOUNDARY CONDITIONS
    NSEL,ALL
    NSEL,R,LOC,Z,0                       ! SELECT ONLY NODES AT Z = 0
    D,ALL,UZ,0                           ! CONSTRAIN BOTTOM NODES IN Z DIRECTION
    NSEL,ALL
    FINISH
    /SOLU    
    OUTPR,BASIC,LAST                     ! PRINT BASIC SOLUTION AT END OF LOAD STEP
    /COM,' APPLY DISPLACEMENT LOADS TO ALL MODELS'
    *CREATE,DISP
    NSEL,R,LOC,Z,10                      ! SELECT NODES AT Z = 10 TO APPLY DISPLACEMENT
    D,ALL,UZ,ARG1
    NSEL,ALL
    /OUT,SCRATCH
    SOLVE
    *END
    *USE,DISP,-.032
    *USE,DISP,-.05
    *USE,DISP,-.1
    FINISH
    /OUT,
    /POST1
    /COM,' CREATE MACRO TO GET RESULTS FOR EACH MODEL'
    *CREATE,GETLOAD
    NSEL,S,NODE,,1,2                    ! SELECT NODES IN PIPE288 MODEL
    NSEL,R,LOC,Z,0
    /OUT,SCRATCH
    FSUM                                ! FZ IS TOTAL LOAD FOR PIPE288 MODEL
    *GET,LOAD_288,FSUM,,ITEM,FZ
    NSEL,S,NODE,,101,118                ! SELECT NODES IN SOLID185 MODEL
    NSEL,R,LOC,Z,0
    FSUM
    *GET,ZFRC,FSUM,0,ITEM,FZ
    LOAD=ZFRC*360/THETA                 ! MULTIPLY BY 360/THETA FOR FULL 360 DEGREE RESULTS
    *STATUS,LOAD
    LOAD_185 = LOAD
    NSEL,S,NODE,,201,212                ! SELECT NODES IN SHELL181 MODEL
    NSEL,R,LOC,Z,0
    FSUM
    /OUT,
    *GET,ZFRC,FSUM,0,ITEM,FZ
    LOAD=ZFRC*360/THETA                 ! MULTIPLY BY 360/THETA FOR FULL 360 DEGREE RESULTS
    *STATUS,LOAD
    LOAD_181 = LOAD
    *VFILL,VALUE_288(1,1),DATA,1024400,1262000,1262000
    *VFILL,VALUE_288(I,2),DATA,ABS(LOAD_288)
    *VFILL,VALUE_288(I,3),DATA,ABS(LOAD_288)/(VALUE_288(I,1))
    *VFILL,VALUE_185(1,1),DATA,1024400,1262000,1262000
    *VFILL,VALUE_185(J,2),DATA,ABS(LOAD_185)
    *VFILL,VALUE_185(J,3),DATA,ABS(LOAD_185)/(VALUE_185(J,1))
    *VFILL,VALUE_181(1,1),DATA,1024400,1262000,1262000
    *VFILL,VALUE_181(K,2),DATA,ABS(LOAD_181)
    *VFILL,VALUE_181(K,3),DATA,ABS(LOAD_181)/(VALUE_181(K,1))
    *END
    /COM,' GET TOTAL LOAD FOR DISPLACEMENT = 0.032'
    /COM,' ---------------------------------------'
    SET,1,1
    I = 1
    J = 1
    K = 1
    *DIM,LABEL,CHAR,3,2
    *DIM,VALUE_288,,3,3
    *DIM,VALUE_185,,3,3
    *DIM,VALUE_181,,3,3
    *USE,GETLOAD
    /COM,' GET TOTAL LOAD FOR DISPLACEMENT = 0.05'
    /COM,' --------------------------------------'
    SET,2,1
    I = I + 1
    J = J + 1
    K = K + 1
    *USE,GETLOAD
    /COM,' GET TOTAL LOAD FOR DISPLACEMENT = 0.1'
    /COM,' -------------------------------------'
    SET,3,1
    I = I +1
    J = J + 1
    K = K + 1
    *USE,GETLOAD
    LABEL(1,1) = 'LOAD, lb','LOAD, lb','LOAD, lb'
    LABEL(1,2) = ' UX=.032',' UX=0.05',' UX=0.10'
    FINISH
    /OUT,vm7,vrt
    /COM,------------------- VM7 RESULTS COMPARISON ---------------------
    /COM,
    /COM,'                 |   TARGET   |   Mechanical APDL   |   RATIO'
    /COM,
    /COM,RESULTS FOR PIPE288:
    /COM,
    *VWRITE,LABEL(1,1),LABEL(1,2),VALUE_288(1,1),VALUE_288(1,2),VALUE_288(1,3)
    (1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)
    /COM,
    /COM,RESULTS FOR SOLID185:
    /COM,
    *VWRITE,LABEL(1,1),LABEL(1,2),VALUE_185(1,1),VALUE_185(1,2),VALUE_185(1,3)
    (1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)
    /COM,
    /COM,RESULTS FOR SHELL181:
    /COM,
    *VWRITE,LABEL(1,1),LABEL(1,2),VALUE_181(1,1),VALUE_181(1,2),VALUE_181(1,3)
    (1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)
    /COM,
    /COM,-----------------------------------------------------------------
    /OUT
    *LIST,vm7,vrt

Convert the verification file with:

.. code:: pycon

    >>> from ansys.mapdl import core as pymapdl
    >>> pymapdl.convert_script("vm7.dat", "vm7.py")

Here is the translated Python script:

.. code:: python

    """ Script generated by ansys-mapdl-core version 0.57.0"""
    from ansys.mapdl.core import launch_mapdl

    mapdl = launch_mapdl()
    mapdl.run("/COM,ANSYS MEDIA REL. 150 (11/8/2013) REF. VERIF. MANUAL: REL. 150")
    mapdl.run("/VERIFY,VM7")
    mapdl.run("/PREP7")
    mapdl.run("/TITLE, VM7, PLASTIC COMPRESSION OF A PIPE ASSEMBLY")
    mapdl.run(
        "C***          MECHANICS OF SOLIDS, CRANDALL AND DAHL, 1959, PAGE 180, EX. 5.1"
    )
    mapdl.run("C***          USING PIPE288, SOLID185 AND SHELL181 ELEMENTS")
    mapdl.run("THETA=6                              ")  # SUBTENDED ANGLE
    mapdl.et(1, "PIPE288", "", "", "", 2)
    mapdl.et(2, "SOLID185")
    mapdl.et(3, "SHELL181", "", "", 2)  # FULL INTEGRATION
    mapdl.sectype(1, "SHELL")
    mapdl.secdata(0.5, 1, 0, 5)  # THICKNESS (SHELL181)
    mapdl.sectype(2, "SHELL")
    mapdl.secdata(0.5, 2, 0, 5)  # THICKNESS (SHELL181)
    mapdl.sectype(3, "PIPE")
    mapdl.secdata(
        4.9563384, 0.5
    )  # OUTSIDE DIA. AND WALL THICKNESS FOR INSIDE TUBE (PIPE288)
    mapdl.sectype(4, "PIPE")
    mapdl.secdata(
        8.139437, 0.5
    )  # OUTSIDE DIA. AND WALL THICKNESS FOR OUTSIDE TUBE (PIPE288)
    mapdl.mp("EX", 1, 26.875e6)  # STEEL
    mapdl.mp("PRXY", 1, 0.3)
    mapdl.mp("EX", 2, 11e6)  # ALUMINUM
    mapdl.mp("PRXY", 2, 0.3)
    mapdl.tb("BKIN", 1, 1)  # DEFINE NON-LINEAR MATERIAL PROPERTY FOR STEEL
    mapdl.tbtemp(0)
    mapdl.tbdata(1, 86000, 0)
    mapdl.tb("BKIN", 2, 1)  # DEFINE NON-LINEAR MATERIAL PROPERTY FOR ALUMINUM
    mapdl.tbtemp(0)
    mapdl.tbdata(1, 55000, 0)
    mapdl.n(1)  # GENERATE NODES AND ELEMENTS FOR PIPE288
    mapdl.n(2, "", "", 10)
    mapdl.mat(1)
    mapdl.secnum(3)  # STEEL (INSIDE) TUBE
    mapdl.e(1, 2)
    mapdl.mat(2)
    mapdl.secnum(4)  # ALUMINUM (OUTSIDE) TUBE
    mapdl.e(1, 2)
    mapdl.csys(1)
    mapdl.n(101, 1.9781692)  # GENERATE NODES AND ELEMENTS FOR SOLID185
    mapdl.n(102, 2.4781692)
    mapdl.n(103, 3.5697185)
    mapdl.n(104, 4.0697185)
    mapdl.n(105, 1.9781692, "", 10)
    mapdl.n(106, 2.4781692, "", 10)
    mapdl.n(107, 3.5697185, "", 10)
    mapdl.n(108, 4.0697185, "", 10)
    mapdl.ngen(
        2, 10, 101, 108, "", "", "THETA"
    )  # GENERATE 2ND SET OF NODES TO FORM A THETA DEGREE SLICE
    mapdl.nrotat(101, 118, 1)
    mapdl.type(2)
    mapdl.mat(1)  # INSIDE (STEEL) TUBE
    mapdl.e(101, 102, 112, 111, 105, 106, 116, 115)
    mapdl.mat(2)  # OUTSIDE (ALUMINUM) TUBE
    mapdl.e(103, 104, 114, 113, 107, 108, 118, 117)
    mapdl.n(201, 2.2281692)  # GENERATE NODES AND ELEMENTS FOR SHELL181
    mapdl.n(203, 2.2281692, "", 10)
    mapdl.n(202, 3.8197185)
    mapdl.n(204, 3.8197185, "", 10)
    mapdl.ngen(
        2, 4, 201, 204, "", "", "THETA"
    )  # GENERATE NODES TO FORM A THETA DEGREE SLICE
    mapdl.type(3)
    mapdl.secnum(1)  # INSIDE (STEEL) TUBE
    mapdl.e(203, 201, 205, 207)
    mapdl.secnum(2)  # OUTSIDE (ALUMINUM) TUBE
    mapdl.e(204, 202, 206, 208)
    mapdl.run("C*** APPLY CONSTRAINTS TO PIPE288 MODEL")
    mapdl.d(1, "ALL")  # FIX ALL DOFS FOR BOTTOM END OF PIPE288
    mapdl.d(
        2, "UX", "", "", "", "", "UY", "ROTX", "ROTY", "ROTZ"
    )  # ALLOW ONLY UZ DOF AT TOP END OF PIPE288 MODEL
    mapdl.run("C*** APPLY CONSTRAINTS TO SOLID185 AND SHELL181 MODELS")
    mapdl.cp(
        1, "UX", 101, 111, 105, 115
    )  # COUPLE NODES AT BOUNDARY IN RADIAL DIR FOR SOLID185
    mapdl.cpsgen(4, "", 1)
    mapdl.cp(
        5, "UX", 201, 205, 203, 20
    )  # COUPLE NODES AT BOUNDARY IN RADIAL DIR FOR SHELL181
    mapdl.cpsgen(2, "", 5)
    mapdl.cp(7, "ROTY", 201, 205)  # COUPLE NODES AT BOUNDARY IN ROTY DIR FOR SHELL181
    mapdl.cpsgen(4, "", 7)
    mapdl.nsel(
        "S", "NODE", "", 101, 212
    )  # SELECT ONLY NODES IN SOLID185 AND SHELL181 MODELS
    mapdl.nsel("R", "LOC", "Y", 0)  # SELECT NODES AT THETA = 0 FROM THE SELECTED SET
    mapdl.dsym("SYMM", "Y", 1)  # APPLY SYMMETRY BOUNDARY CONDITIONS
    mapdl.nsel(
        "S", "NODE", "", 101, 212
    )  # SELECT ONLY NODES IN SOLID185 AND SHELL181 MODELS
    mapdl.nsel("R", "LOC", "Y", "THETA")  # SELECT NODES AT THETA FROM THE SELECTED SET
    mapdl.dsym("SYMM", "Y", 1)  # APPLY SYMMETRY BOUNDARY CONDITIONS
    mapdl.nsel("ALL")
    mapdl.nsel("R", "LOC", "Z", 0)  # SELECT ONLY NODES AT Z = 0
    mapdl.d("ALL", "UZ", 0)  # CONSTRAIN BOTTOM NODES IN Z DIRECTION
    mapdl.nsel("ALL")
    mapdl.finish()
    mapdl.run("/SOLU")
    mapdl.outpr("BASIC", "LAST")  # PRINT BASIC SOLUTION AT END OF LOAD STEP
    mapdl.run("C*** APPLY DISPLACEMENT LOADS TO ALL MODELS")


    def DISP(
        ARG1="",
        ARG2="",
        ARG3="",
        ARG4="",
        ARG5="",
        ARG6="",
        ARG7="",
        ARG8="",
        ARG9="",
        ARG10="",
        ARG11="",
        ARG12="",
        ARG13="",
        ARG14="",
        ARG15="",
        ARG16="",
        ARG17="",
        ARG18="",
    ):
        mapdl.nsel("R", "LOC", "Z", 10)  # SELECT NODES AT Z = 10 TO APPLY DISPLACEMENT
        mapdl.d("ALL", "UZ", ARG1)
        mapdl.nsel("ALL")
        mapdl.run("/OUT,SCRATCH")
        mapdl.solve()


    DISP(-0.032)
    DISP(-0.05)
    DISP(-0.1)
    mapdl.finish()
    mapdl.run("/OUT,")
    mapdl.run("/POST1")
    mapdl.run("C*** CREATE MACRO TO GET RESULTS FOR EACH MODEL")


    def GETLOAD(
        ARG1="",
        ARG2="",
        ARG3="",
        ARG4="",
        ARG5="",
        ARG6="",
        ARG7="",
        ARG8="",
        ARG9="",
        ARG10="",
        ARG11="",
        ARG12="",
        ARG13="",
        ARG14="",
        ARG15="",
        ARG16="",
        ARG17="",
        ARG18="",
    ):
        mapdl.nsel("S", "NODE", "", 1, 2)  # SELECT NODES IN PIPE288 MODEL
        mapdl.nsel("R", "LOC", "Z", 0)
        mapdl.run("/OUT,SCRATCH")
        mapdl.fsum()  # FZ IS TOTAL LOAD FOR PIPE288 MODEL
        mapdl.run("*GET,LOAD_288,FSUM,,ITEM,FZ")
        mapdl.nsel("S", "NODE", "", 101, 118)  # SELECT NODES IN SOLID185 MODEL
        mapdl.nsel("R", "LOC", "Z", 0)
        mapdl.fsum()
        mapdl.run("*GET,ZFRC,FSUM,0,ITEM,FZ")
        mapdl.run(
            "LOAD=ZFRC*360/THETA                 "
        )  # MULTIPLY BY 360/THETA FOR FULL 360 DEGREE RESULTS
        mapdl.run("*STATUS,LOAD")
        mapdl.run("LOAD_185 = LOAD")
        mapdl.nsel("S", "NODE", "", 201, 212)  # SELECT NODES IN SHELL181 MODEL
        mapdl.nsel("R", "LOC", "Z", 0)
        mapdl.fsum()
        mapdl.run("/OUT,")
        mapdl.run("*GET,ZFRC,FSUM,0,ITEM,FZ")
        mapdl.run(
            "LOAD=ZFRC*360/THETA                 "
        )  # MULTIPLY BY 360/THETA FOR FULL 360 DEGREE RESULTS
        mapdl.run("*STATUS,LOAD")
        mapdl.run("LOAD_181 = LOAD")
        mapdl.run("*VFILL,VALUE_288(1,1),DATA,1024400,1262000,1262000")
        mapdl.run("*VFILL,VALUE_288(I,2),DATA,ABS(LOAD_288)")
        mapdl.run("*VFILL,VALUE_288(I,3),DATA,ABS(LOAD_288)/(VALUE_288(I,1))")
        mapdl.run("*VFILL,VALUE_185(1,1),DATA,1024400,1262000,1262000")
        mapdl.run("*VFILL,VALUE_185(J,2),DATA,ABS(LOAD_185)")
        mapdl.run("*VFILL,VALUE_185(J,3),DATA,ABS(LOAD_185)/(VALUE_185(J,1))")
        mapdl.run("*VFILL,VALUE_181(1,1),DATA,1024400,1262000,1262000")
        mapdl.run("*VFILL,VALUE_181(K,2),DATA,ABS(LOAD_181)")
        mapdl.run("*VFILL,VALUE_181(K,3),DATA,ABS(LOAD_181)/(VALUE_181(K,1))")


    mapdl.run("C*** GET TOTAL LOAD FOR DISPLACEMENT = 0.032")
    mapdl.run("C*** ---------------------------------------")
    mapdl.set(1, 1)
    mapdl.run("I = 1")
    mapdl.run("J = 1")
    mapdl.run("K = 1")
    mapdl.run("*DIM,LABEL,CHAR,3,2")
    mapdl.run("*DIM,VALUE_288,,3,3")
    mapdl.run("*DIM,VALUE_185,,3,3")
    mapdl.run("*DIM,VALUE_181,,3,3")
    GETLOAD()
    mapdl.run("C*** GET TOTAL LOAD FOR DISPLACEMENT = 0.05")
    mapdl.run("C*** --------------------------------------")
    mapdl.set(2, 1)
    mapdl.run("I = I + 1")
    mapdl.run("J = J + 1")
    mapdl.run("K = K + 1")
    GETLOAD()
    mapdl.run("C*** GET TOTAL LOAD FOR DISPLACEMENT = 0.1")
    mapdl.run("C*** -------------------------------------")
    mapdl.set(3, 1)
    mapdl.run("I = I +1")
    mapdl.run("J = J + 1")
    mapdl.run("K = K + 1")
    GETLOAD()
    mapdl.run("LABEL(1,1) = 'LOAD, lb','LOAD, lb','LOAD, lb'")
    mapdl.run("LABEL(1,2) = ' UX=.032',' UX=0.05',' UX=0.10'")
    mapdl.finish()
    mapdl.run("/OUT,vm7,vrt")
    mapdl.run("/COM,------------------- VM7 RESULTS COMPARISON ---------------------")
    mapdl.run("/COM,")
    mapdl.run("/COM,                 |   TARGET   |   Mechanical APDL   |   RATIO")
    mapdl.run("/COM,")
    mapdl.run("/COM,RESULTS FOR PIPE288:")
    mapdl.run("/COM,")
    with mapdl.non_interactive:
        mapdl.run(
            "*VWRITE,LABEL(1,1),LABEL(1,2),VALUE_288(1,1),VALUE_288(1,2),VALUE_288(1,3)"
        )
        mapdl.run("(1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)")
        mapdl.run("/COM,")
        mapdl.run("/COM,RESULTS FOR SOLID185:")
        mapdl.run("/COM,")
        mapdl.run(
            "*VWRITE,LABEL(1,1),LABEL(1,2),VALUE_185(1,1),VALUE_185(1,2),VALUE_185(1,3)"
        )
        mapdl.run("(1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)")
        mapdl.run("/COM,")
        mapdl.run("/COM,RESULTS FOR SHELL181:")
        mapdl.run("/COM,")
        mapdl.run(
            "*VWRITE,LABEL(1,1),LABEL(1,2),VALUE_181(1,1),VALUE_181(1,2),VALUE_181(1,3)"
        )
        mapdl.run("(1X,A8,A8,'   ',F10.0,'  ',F14.0,'   ',1F15.3)")
        mapdl.run("/COM,")
        mapdl.run("/COM,-----------------------------------------------------------------")
        mapdl.run("/OUT")
        mapdl.run("*LIST,vm7,vrt")
    mapdl.exit()
