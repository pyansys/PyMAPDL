"""These PREP7 commands are used to create, modify, list, etc., elements.

Examples
--------
Create a single SURF154 element.

>>> mapdl.prep7()
>>> mapdl.et(1, 'SURF154')
>>> mapdl.n(1, 0, 0, 0)
>>> mapdl.n(2, 1, 0, 0)
>>> mapdl.n(3, 1, 1, 0)
>>> mapdl.n(4, 0, 1, 0)
>>> mapdl.e(1, 2, 3, 4)
1

Create a single hexahedral SOLID185 element

>>> mapdl.et(2, 'SOLID185')
>>> mapdl.type(2)
>>> mapdl.n(5, 0, 0, 0)
>>> mapdl.n(6, 1, 0, 0)
>>> mapdl.n(7, 1, 1, 0)
>>> mapdl.n(8, 0, 1, 0)
>>> mapdl.n(9, 0, 0, 1)
>>> mapdl.n(10, 1, 0, 1)
>>> mapdl.n(11, 1, 1, 1)
>>> mapdl.n(12, 0, 1, 1)
>>> mapdl.e(5, 6, 7, 8, 9, 10, 11, 12)
2

Print the volume of individual elements

>>> mapdl.clear()
>>> output = mapdl.input(examples.vmfiles['vm6'])
>>> mapdl.post1()
>>> label = 'MYVOLU'
>>> mapdl.etable(label, 'VOLU')
>>> print(mapdl.pretab(label))
PRINT ELEMENT TABLE ITEMS PER ELEMENT
   *****ANSYS VERIFICATION RUN ONLY*****
     DO NOT USE RESULTS FOR PRODUCTION
  ***** POST1 ELEMENT TABLE LISTING *****
    STAT     CURRENT
    ELEM     XDISP
       1  0.59135E-001
       2  0.59135E-001
       3  0.59135E-001
...

See the individual commands for more details.


"""
import warnings
import re
from typing import Optional, Union

from ..mapdl_types import MapdlInt, MapdlFloat
from ..plotting import general_plotter


def parse_e(msg: Optional[str]) -> Optional[int]:
    """Parse create element message and return element number."""
    if msg:
        res = re.search(r"(ELEMENT\s*)([0-9]+)", msg)
        if res is not None:
            return int(res.group(2))


def ekill(self, elem: Union[str, int] = "",
          **kwargs) -> Optional[str]:
    """Deactivates an element (for the birth and death capability).

    APDL Command: EKILL

    Parameters
    ----------
    elem
        Element to be deactivated. If ALL, deactivate all
        selected elements [ESEL]. A component name may also be
        substituted for ELEM.

    Notes
    -----
    Deactivates the specified element when the birth and death
    capability is being used. A deactivated element remains in
    the model but contributes a near-zero stiffness (or
    conductivity, etc.) value (ESTIF) to the overall matrix. Any
    solution-dependent state variables (such as stress, plastic
    strain, creep strain, etc.) are set to zero. Deactivated
    elements contribute nothing to the overall mass (or
    capacitance, etc.) matrix.

    The element can be reactivated with the EALIVE command.

    ANSYS, Inc. recommends using element deactivation/reactivation
    (EKILL/EALIVE) for linear elastic materials only. For all other
    materials, validate the results carefully before using them.

    This command is also valid in PREP7.
    """
    command = f"EKILL,{elem}"
    return self.run(command, **kwargs)


def e(self, i: MapdlInt = "", j: MapdlInt = "", k: MapdlInt = "",
      l: MapdlInt = "", m: MapdlInt = "", n: MapdlInt = "", o:
      MapdlInt = "", p: MapdlInt = "", **kwargs) -> Optional[int]:
    """APDL Command: E

    Defines an element by node connectivity.

    Parameters
    ----------
    i
        Number of node assigned to first nodal position (node
        ``i``).

    j, k, l, m, n, o, p
        Number assigned to second (node ``j``) through eighth
        (node ``p``) nodal position, if any.

    Examples
    --------
    Create a single SURF154 element.

    >>> mapdl.prep7()
    >>> mapdl.et(1, 'SURF154')
    >>> mapdl.n(1, 0, 0, 0)
    >>> mapdl.n(2, 1, 0, 0)
    >>> mapdl.n(3, 1, 1, 0)
    >>> mapdl.n(4, 0, 1, 0)
    >>> mapdl.e(1, 2, 3, 4)
    1

    Create a single hexahedral SOLID185 element

    >>> mapdl.et(2, 'SOLID185')
    >>> mapdl.type(2)
    >>> mapdl.n(5, 0, 0, 0)
    >>> mapdl.n(6, 1, 0, 0)
    >>> mapdl.n(7, 1, 1, 0)
    >>> mapdl.n(8, 0, 1, 0)
    >>> mapdl.n(9, 0, 0, 1)
    >>> mapdl.n(10, 1, 0, 1)
    >>> mapdl.n(11, 1, 1, 1)
    >>> mapdl.n(12, 0, 1, 1)
    >>> mapdl.e(5, 6, 7, 8, 9, 10, 11, 12)
    2

    Notes
    -----
    Defines an element by its nodes and attribute values. Up to 8
    nodes may be specified with the :meth:`e` command.  If more
    nodes are needed for the element, use the :meth:`emore`
    command. The number of nodes required and the order in which
    they should be specified are described in Chapter 4 of the
    Element Reference for each element type.  Elements are
    automatically assigned a number [NUMSTR] as generated. The
    current (or default) MAT, TYPE, REAL, SECNUM and ESYS
    attribute values are also assigned to the element.

    When creating elements with more than 8 nodes using this
    command and the EMORE command, it may be necessary to turn off
    shape checking using the
    :func:`~ansys.mapdl.core.mapdl_functions._MapdlCommands.shpp`
    command before issuing this command. If a valid element type
    can be created without using the additional nodes on the
    :meth:`emore` command, this command will create that
    element. The :meth:`emore` command will
    then modify the element to include the additional nodes. If
    shape checking is active, it will be performed before the
    :meth:`emore` command is issued.
    Therefore, if the shape checking limits are exceeded, element
    creation may fail before the
    :meth:`emore` command modifies the
    element into an acceptable shape.

    """
    command = f"E,{i},{j},{k},{l},{m},{n},{o},{p}"
    return parse_e(self.run(command, **kwargs))

def ewrite(self, fname: str = "", ext: str = "", kappnd: MapdlInt = "",
           format_: str = "", **kwargs) -> Optional[str]:
    """Writes elements to a file.

    APDL Command: EWRITE

    Parameters
    ----------
    fname
        File name and directory path (248 characters maximum,
        including the characters needed for the directory path).
        An unspecified directory path defaults to the working
        directory; in this case, you can use all 248 characters
        for the file name.

    ext
        Filename extension (eight-character maximum).

    kappnd
        Append key:

        0 - Rewind file before the write operation.

        1 - Append data to the end of the existing file.

    format_
        Format key:

        SHORT - I6 format (the default).

        LONG - I8 format.

    Examples
    --------
    >>> mapdl.ewrite('etable.txt', format_='LONG')

    Notes
    -----
    Writes the selected elements to a file. The write operation is
    not necessary in a standard ANSYS run but is provided as
    convenience to users wanting a coded element file. If issuing
    :meth:`ewrite` from ANSYS to be used in ANSYS, you must also
    issue
    :func:`~ansys.mapdl.core.mapdl_functions._MapdlCommands.nwrite`
    to store nodal information for later use. Only elements having
    all of their nodes defined (and selected) are written. Data
    are written in a coded format. The data description of each
    record is: I, J, K, L, M, N, O, P, MAT, TYPE, REAL, SECNUM,
    ESYS, IEL, where MAT, TYPE, REAL, and ESYS are attribute
    numbers, SECNUM is the beam section number, and IEL is the
    element number.

    The format is (14I6) if Format is set to SHORT and (14I8) if
    the Format is set to LONG, with one element description per
    record for elements having eight nodes of less. For elements
    having more than eight nodes, nodes nine and above are written
    on a second record with the same format.
    """
    return self.run(f"EWRITE,{fname},{ext},,{kappnd},{format_}", **kwargs)

def etable(self, lab: str = "", item: str = "", comp: str = "",
           option: str = "", **kwargs) -> Optional[str]:
    """Fills a table of element values for further processing.

    APDL Command: ETABLE

    Parameters
    ----------
    lab
        Any unique user defined label for use in subsequent
        commands and output headings (maximum of eight characters
        and not a General predefined Item label). Defaults to an
        eight character label formed by concatenating the first
        four characters of the Item and Comp labels. If the same
        as a previous user label, this result item will be
        included under the same label. Up to 200 different labels
        may be defined. The following labels are predefined and
        are not available for user-defined labels: ``'REFL''`,
        ``'STAT'``, and ``'ERAS'``.  ``lab='REFL'`` refills all
        tables previously defined with the :meth:`etable` commands
        (not the CALC module commands) according to the latest
        ETABLE specifications and is convenient for refilling
        tables after the load step (SET) has been
        changed. Remaining fields will be ignored if
        ``Lab='REFL'``.  ``lab='STAT'`` displays stored table
        values.  ``lab='ERAS'`` erases the entire table.

    item
        Label identifying the item. General item labels are shown
        in the table below. Some items also require a component
        label. Character parameters may be used. ``item='eras'``
        erases a Lab column.

    comp
        Component of the item (if required). General component
        labels are shown in the table below. Character parameters
        may be used.

    option
        Option for storing element table data:

        * ``'MIN'`` - Store minimum element nodal value of the specified
          item component.
        * ``'MAX'`` - Store maximum element nodal value of the specified
          item component.
        * ``'AVG'`` - Store averaged element centroid value of the
          specified item component (default).

    Examples
    --------
    Print the volume of individual elements.

    >>> mapdl.clear()
    >>> output = mapdl.input(examples.vmfiles['vm6'])
    >>> mapdl.post1()
    >>> label = 'MYVOLU'
    >>> mapdl.etable(label, 'VOLU')
    >>> print(mapdl.pretab(label))
    PRINT ELEMENT TABLE ITEMS PER ELEMENT
       *****ANSYS VERIFICATION RUN ONLY*****
         DO NOT USE RESULTS FOR PRODUCTION
      ***** POST1 ELEMENT TABLE LISTING *****
        STAT     CURRENT
        ELEM     XDISP
           1  0.59135E-001
           2  0.59135E-001
           3  0.59135E-001
    ...

    Notes
    -----
    The ETABLE command defines a table of values per element (the
    element table) for use in further processing. The element
    table is organized similar to spreadsheet, with rows
    representing all selected elements and columns consisting of
    result items which have been moved into the table (Item,Comp)
    via ETABLE. Each column of data is identified by a
    user-defined label (Lab) for listings and displays.

    After entering the data into the element table, you are not
    limited to merely listing or displaying your data (PLESOL,
    PRESOL, etc.). You may also perform many types of operations
    on your data, such as adding or multiplying columns (SADD,
    SMULT), defining allowable stresses for safety calculations
    (SALLOW), or multiplying one column by another (SMULT).  See
    Getting Started in the Basic Analysis Guide for more
    information.

    Various results data can be stored in the element table. For
    example, many items for an element are inherently
    single-valued (one value per element). The single-valued items
    include: SERR, SDSG, TERR, TDSG, SENE, SEDN, TENE, KENE, AENE,
    JHEAT, JS, VOLU, and CENT. All other items are multivalued
    (varying over the element, such that there is a different
    value at each node). Because only one value is stored in the
    element table per element, an average value (based on the
    number of contributing nodes) is calculated for multivalued
    items. Exceptions to this averaging procedure are FMAG and all
    element force items, which represent the sum only of the
    contributing nodal values.

    Two methods of data access can be used with the ETABLE
    command. The method you select depends upon the type of data
    that you want to store.  Some results can be accessed via a
    generic label (Component Name method), while others require a
    label and number (Sequence Number method).

    The Component Name method is used to access the General
    element data (that is, element data which is generally
    available to most element types or groups of element
    types). All of the single-valued items and some of the more
    general multivalued items are accessible with the Component
    Name method.  Various element results depend on the
    calculation method and the selected results location (AVPRIN,
    RSYS, LAYER, SHELL, and ESEL).

    Although nodal data is readily available for listings and
    displays (PRNSOL, PLNSOL) without using the element table, you
    may also use the Component Name method to enter these results
    into the element table for further "worksheet"
    manipulation. (See Getting Started in theBasic Analysis Guide
    for more information.) A listing of the General Item and Comp
    labels for the Component Name method is shown below.

    The Sequence Number method allows you to view results for data
    that is not averaged (such as pressures at nodes, temperatures
    at integration points, etc.), or data that is not easily
    described in a generic fashion (such as all derived data for
    structural line elements and contact elements, all derived
    data for thermal line elements, layer data for layered
    elements, etc.). A table illustrating the Items (such as LS,
    LEPEL, LEPTH, SMISC, NMISC, SURF, etc.) and corresponding
    sequence numbers for each element is shown in the Output Data
    section of each element description found in the Element
    Reference.

    Some element table data are reported in the results coordinate
    system.  These include all component results (for example, UX,
    UY, etc.; SX, SY, etc.). The solution writes component results
    in the database and on the results file in the solution
    coordinate system. When you issue the ETABLE command, these
    results are then transformed into the results coordinate
    system (RSYS) before being stored in the element table. The
    default results coordinate system is global Cartesian
    (RSYS,0).  All other data are retrieved from the database and
    stored in the element table with no coordinate transformation.

    Use the PRETAB, PLETAB, or ETABLE,STAT commands to display the
    stored table values. Issue ETABLE,ERAS to erase the entire
    table. Issue ETABLE,Lab,ERAS to erase a Lab column.

    The element table data option (Option) is not available for
    all output items.

    """
    command = f"ETABLE,{lab},{item},{comp},{option}"
    return self.run(command, **kwargs)

def eusort(self, **kwargs) -> Optional[str]:
    """Restore original order of the element table.

    APDL Command: EUSORT

    Examples
    --------
    >>> mapdl.post1()
    >>> mapdl.eusort()
    'ELEMENT SORT REMOVED'

    Notes
    -----
    Changing the selected element set [ESEL] also restores the original
    element order.
    """
    return self.run("EUSORT", **kwargs)

def edtp(self, option: MapdlInt = "", value1: MapdlInt = "",
         value2: MapdlFloat = "", **kwargs) -> Optional[str]:  # pragma: no cover
    """Plots explicit elements based on their time step size.

    APDL Command: EDTP

    Parameters
    ----------
    option
         Plotting option (default = 1).

        1 - Plots the elements with the smallest time step
            sizes. The number of elements plotted and listed is
            equal to VALUE1 (which defaults to 100).  Each element
            is shaded red or yellow based on its time step value
            (see "Notes" for details).

        2 - Produces the same plot as for OPTION = 1, and also
            produces a list of the plotted elements and their
            corresponding time step values.

        3 - Produces a plot similar to OPTION = 1, except that all
            selected elements are plotted. Elements beyond the
            first VALUE1 elements are blue and translucent. The
            amount of translucency is specified by VALUE2.  This
            option also produces a list of the first VALUE1
            elements with their corresponding time step values.

    value1
        Number of elements to be plotted and listed (default =
        100). For example, if VALUE1 = 10, only the elements with
        the 10 smallest time step sizes are plotted and listed.

    value2
        Translucency level ranging from 0 to 1 (default =
        0.9). VALUE2 is only used when OPTION = 3, and only for
        the elements plotted in blue. To plot these elements as
        non-translucent, set VALUE2 = 0.

    Notes
    -----
    EDTP invokes an ANSYS macro that plots and lists explicit
    elements based on their time step size. For OPTION = 1 or 2,
    the number of elements plotted is equal to VALUE1 (default =
    100). For OPTION = 3, all selected elements are plotted.

    The elements are shaded red, yellow, or blue based on their
    time step size. Red represents the smallest time step sizes,
    yellow represents the intermediate time step sizes, and blue
    represents the largest time step sizes. For example, if you
    specify VALUE1 = 30, and if T1 is the smallest critical time
    step of all elements and T30 is the time step of the 30th
    smallest element, then the elements are shaded as follows:

    Translucent blue elements only appear when OPTION = 3.

    This command is also valid in PREP7.

    Distributed ANSYS Restriction: This command is not supported in
    Distributed ANSYS.
    """
    command = f"EDTP,{option},{value1},{value2}"
    return self.run(command, **kwargs)

def estif(self, kmult: MapdlFloat = "", **kwargs) -> Optional[str]:
    """Specifies the matrix multiplier for deactivated elements.

    APDL Command: ESTIF

    Parameters
    ----------
    kmult
        Stiffness matrix multiplier for deactivated elements (defaults to
        1.0E-6).

    Examples
    --------
    >>> mapdl.prep7()
    >>> mapdl.estif(1E-8)
    'DEAD ELEMENT STIFFNESS MULTIPLIER= 0.10000E-07'

    Notes
    -----
    Specifies the stiffness matrix multiplier for elements deactivated with
    the EKILL command (birth and death).

    This command is also valid in PREP7.
    """
    command = f"ESTIF,{kmult}"
    return self.run(command, **kwargs)

def emodif(self, iel: Union[str, int] = "", stloc: Union[str, int] = "",
           i1: MapdlInt = "", i2: MapdlInt = "", i3: MapdlInt = "",
           i4: MapdlInt = "", i5: MapdlInt = "", i6: MapdlInt = "",
           i7: MapdlInt = "", i8: MapdlInt = "",
           **kwargs) -> Optional[str]:
    """Modifies a previously defined element.

    APDL Command: EMODIF

    Parameters
    ----------
    iel
        Modify nodes and/or attributes for element number IEL.  If
        ALL, modify all selected elements [ESEL]. A component name
        may also be substituted for IEL.

    stloc
        Starting location (n) of first node to be modified or the
        attribute label.

    i1, i2, i3, i4, i5, i6, i7, i8
        Replace the previous node numbers assigned to this element
        with these corresponding values. A (blank) retains the
        previous value (except in the I1 field, which resets the
        STLOC node number to zero).

    Examples
    --------
    Modify all elements to have a material number of 2.

    >>> mapdl.clear()
    >>> mapdl.prep7()
    >>> mp_num = 2
    >>> mapdl.mp('EX', mp_num, 210E9)
    >>> mapdl.mp('DENS', mp_num, 7800)
    >>> mapdl.mp('NUXY', mp_num, 0.3)
    >>> mapdl.block(0, 1, 0, 1, 0, 1)
    >>> mapdl.et(1, 'SOLID186')
    >>> mapdl.vmesh('ALL')
    >>> mapdl.emodif('ALL', 'MAT', i1=mp_num)
    'MODIFY ALL SELECTED ELEMENTS TO HAVE  MAT  =         2'

    Notes
    -----
    The nodes and/or attributes (MAT, TYPE, REAL, ESYS, and SECNUM
    values) of an existing element may be changed with this
    command.
    """
    command = f"EMODIF,{iel},{stloc},{i1},{i2},{i3},{i4},{i5},{i6},{i7},{i8}"
    return self.run(command, **kwargs)

def emore(self, q: MapdlInt = "", r: MapdlInt = "", s: MapdlInt = "",
          t: MapdlInt = "", u: MapdlInt = "", v: MapdlInt = "",
          w: MapdlInt = "", x: MapdlInt = "", **kwargs) -> Optional[str]:
    """Add more nodes to the just-defined element.

    APDL Command: EMORE

    Parameters
    ----------
    q, r, s, t, u, v, w, x
        Numbers of nodes typically assigned to ninth (node Q)
        through sixteenth (node X) nodal positions, if any.

    Examples
    --------
    Generate a single quadratic element.

    >>> mapdl.prep7()
    >>> mapdl.et(1, 'SOLID186')
    >>> mapdl.n(1, -1, -1, -1)
    >>> mapdl.n(2,  1, -1, -1)
    >>> mapdl.n(3,  1,  1, -1)
    >>> mapdl.n(4, -1,  1, -1)
    >>> mapdl.n(5, -1, -1,  1)
    >>> mapdl.n(6,  1, -1,  1)
    >>> mapdl.n(7,  1,  1,  1)
    >>> mapdl.n(8, -1,  1,  1)
    >>> mapdl.n(9,  0, -1, -1)
    >>> mapdl.n(10,  1,  0, -1)
    >>> mapdl.n(11,  0,  1, -1)
    >>> mapdl.n(12, -1,  0, -1)
    >>> mapdl.n(13,  0, -1,  1)
    >>> mapdl.n(14,  1,  0,  1)
    >>> mapdl.n(15,  0,  1,  1)
    >>> mapdl.n(16, -1,  0,  1)
    >>> mapdl.n(17, -1, -1,  0)
    >>> mapdl.n(18,  1, -1,  0)
    >>> mapdl.n(19,  1,  1,  0)
    >>> mapdl.n(20, -1,  1,  0)
    >>> mapdl.e(1, 2, 3, 4, 5, 6, 7, 8)
    >>> mapdl.emore(9, 10, 11, 12, 13, 14, 15, 16)
    >>> output = mapdl.emore(17, 18, 19, 20)
    'ELEMENT 1  1  2  3  4  5  6  7  8
                9 10 11 12 13 14 15 16
               17 18 19 20

    Notes
    -----
    Repeat EMORE command for up to 4 additional nodes (20
    maximum). Nodes are added after the last nonzero node of the
    element.  Node numbers defined with this command may be
    zeroes.
    """
    command = f"EMORE,{q},{r},{s},{t},{u},{v},{w},{x}"
    return self.run(command, **kwargs)

def esol(self, nvar: MapdlInt = "", elem: MapdlInt = "",
         node: MapdlInt = "", item: str = "", comp: str = "",
         name: str = "", **kwargs) -> Optional[str]:
    """Specify element data to be stored from the results file.

    /POST26 APDL Command: ESOL

    Parameters
    ----------
    nvar
        Arbitrary reference number assigned to this variable (2 to
        NV [NUMVAR]). Overwrites any existing results for this
        variable.

    elem
        Element for which data are to be stored.

    node
        Node number on this element for which data are to be
        stored. If blank, store the average element value (except
        for FMAG values, which are summed instead of averaged).

    item
        Label identifying the item. General item labels are shown
        in Table 134: ESOL - General Item and Component Labels
        below. Some items also require a component label.

    comp
        Component of the item (if required). General component
        labels are shown in Table 134: ESOL - General Item and
        Component Labels below.  If Comp is a sequence number (n),
        the NODE field will be ignored.

    name
        Thirty-two character name for identifying the item on the
        printout and displays.  Defaults to a label formed by
        concatenating the first four characters of the Item and
        Comp labels.

    Examples
    --------
    Switch to the time-history postprocessor

    >>> mapdl.post26()

    Store the stress in the X direction for element 1 at node 1

    >>> nvar = 2
    >>> mapdl.esol(nvar, 1, 1, 'S', 'X')

    Move the value to an array and access it via mapdl.parameters

    >>> mapdl.dim('ARR', 'ARRAY', 1)
    >>> mapdl.vget('ARR', nvar)
    >>> mapdl.parameters['ARR']
    array(-1991.40234375)

    Notes
    -----
    See Table: 134:: ESOL - General Item and Component Labels for
    a list of valid item and component labels for element (except
    line element) results.

    The ESOL command defines element results data to be stored
    from a results file (FILE). Not all items are valid for all
    elements. To see the available items for a given element,
    refer to the input and output summary tables in the
    documentation for that element.

    Two methods of data access are available via the ESOL
    command. You can access some simply by using a generic label
    (component name method), while others require a label and
    number (sequence number method).

    Use the component name method to access general element data
    (that is, element data generally available to most element
    types or groups of element types).

    The sequence number method is required for data that is not
    averaged (such as pressures at nodes and temperatures at
    integration points), or data that is not easily described in a
    generic fashion (such as all derived data for structural line
    elements and contact elements, all derived data for thermal
    line elements, and layer data for layered elements).

    Element results are in the element coordinate system, except
    for layered elements where results are in the layer coordinate
    system.  Element forces and moments are in the nodal
    coordinate system. Results are obtainable for an element at a
    specified node. Further location specifications can be made
    for some elements via the SHELL, LAYERP26, and FORCE commands.

    For more information on the meaning of contact status and its
    possible values, see Reviewing Results in POST1 in the Contact
    Technology Guide.
    """
    command = f"ESOL,{nvar},{elem},{node},{item},{comp},{name}"
    return self.run(command, **kwargs)

def eshape(self, scale: Union[str, int] = "", key: MapdlInt = "",
           **kwargs) -> Optional[str]:
    """Displays elements with shapes determined from the real constants or section definition.

    APDL Command: /ESHAPE


    Parameters
    ----------
    scale
        Scaling factor:

        * 0 - Use simple display of line and area elements. This
          value is the default.

        * 1 - Use real constants or section definition to form a
            solid shape display of the applicable elements.

        FAC - Multiply certain real constants, such as thickness,
              by FAC (where FAC > 0.01) and use them to form a
              solid shape display of elements.

    key
        Current shell thickness key:

        * 0 - Use current thickness in the displaced solid shape
              display of shell elements (valid for SHELL181,
              SHELL208, SHELL209, and SHELL281). This value is the
              default.

        * 1 - Use initial thickness in the displaced solid shape
          display of shell elements.

    Notes
    -----
    The /ESHAPE command allows beams, shells, current sources, and
    certain special-purpose elements to be displayed as solids
    with the shape determined from the real constants or section
    types. Elements are displayed via the EPLOT command. No checks
    for valid or complete input are made for the display.

    Following are details about using this command with various
    element types:

    SOLID65 elements are displayed with internal lines that
    represent rebar sizes and orientations (requires vector mode
    [/DEVICE] with a basic type of display [/TYPE,,BASIC]). The
    rebar with the largest volume ratio in each element plots as a
    red line, the next largest as green, and the smallest as blue.

    COMBIN14, COMBIN39, and MASS21 are displayed with a graphics
    icon, with the offset determined by the real constants and
    KEYOPT settings.

    BEAM188, BEAM189, PIPE288, PIPE289 and ELBOW290 are displayed
    as solids with the shape determined via the section-definition
    commands (SECTYPE and SECDATA). The arbitrary section option
    (Subtype = ASEC) has no definite shape and appears as a thin
    rectangle to show orientation. The elements are displayed with
    internal lines representing the cross- section mesh.

    SOLID272 and SOLID273 are displayed as solids with the shape
    determined via the section-definition commands (SECTYPE and
    SECDATA).  The 2-D master plane is revolved around the
    prescribed axis of symmetry.

    Contour plots are available for these elements in
    postprocessing for PowerGraphics only (/GRAPHICS,POWER). To
    view 3-D deformed shapes for the elements, issue OUTRES,MISC
    or OUTRES,ALL for static or transient analyses. To view 3-D
    mode shapes for a modal or eigenvalue buckling analysis,
    expand the modes with element results calculation ON (Elcalc =
    YES for MXPAND).

    SOURC36, CIRCU124, and TRANS126 elements always plot using
    /ESHAPE when PowerGraphics is activated (/GRAPHICS,POWER).

    In most cases, /ESHAPE renders a thickness representation of
    your shell, plane and layered elements more readily in
    PowerGraphics (/GRAPHICS,POWER). This type of representation
    employs PowerGraphics to generate the enhanced representation,
    and will often provide no enhancement in Full Graphics
    (/GRAPHICS,FULL). This is especially true for POST1 results
    displays, where /ESHAPE is not supported for most element
    types with FULL graphics.

    When PowerGraphics is active, /ESHAPE may degrade the image if
    adjacent elements have overlapping material, such as shell
    elements which are not co-planar. Additionally, if adjacent
    elements have different thicknesses, the polygons depicting
    the connectivity between the "thicker" and "thinner" elements
    along the shared element edges may not always be displayed.

    For POST1 results displays (such as PLNSOL), the following
    limitations apply:

    Rotational displacements for beam elements are used to create
    a more realistic displacement display. When /ESHAPE is active,
    displacement plots (via PLNSOL,U,X and PLDISP, for example)
    may disagree with your PRNSOL listings. This discrepancy will
    become more noticeable when the SCALE value is not equal to
    one.

    When shell elements are not co-planar, the resulting PLNSOL
    display with /ESHAPE will actually be a PLESOL display as the
    non-coincident pseudo-nodes are not averaged. Additionally,
    /ESHAPE should not be used with coincident elements because
    the plot may incorrectly average the displacements of the
    coincident elements.

    When nodes are initially coincident and PowerGraphics is
    active, duplicate polygons are eliminated to conserve display
    time and disk space. The command may degrade the image if
    initially coincident nodes have different displacements. The
    tolerance for determining coincidence is 1E-9 times the
    model’s bounding box diagonal.

    If you want to view solution results (PLNSOL, etc.) on layered
    elements (such as SHELL181, SOLSH190, SOLID185 Layered Solid,
    SOLID186 Layered Solid, SHELL208, SHELL209, SHELL281, and
    ELBOW290), set KEYOPT(8) = 1 for the layer elements so that
    the data for all layers is stored in the results file.

    You can plot the through-thickness temperatures of elements
    SHELL131 and SHELL132 regardless of the thermal DOFs in use by
    issuing the PLNSOL,TEMP command (with PowerGraphics and
    /ESHAPE active).

    The /ESHAPE,1 and /ESHAPE,FAC commands are incompatible with
    the /CYCEXPAND command used in cyclic symmetry analyses.

    This command is valid in any processor.

    """
    warnings.warn('pymapdl does not support /ESHAPE when plotting in '
                  'Python using ``mapdl.eplot()``.  '
                  'Use ``mapdl.eplot(vtk=False)`` ')
    command = f"/ESHAPE,{scale},{key}"
    return self.run(command, **kwargs)

def etype(self, **kwargs) -> Optional[str]:
    """Specify "Element types" as the subsequent status topic.

    APDL Command: ETYPE

    Examples
    --------
    >>> mapdl.et(1, 'SOLID186')
    >>> mapdl.etype()
    >>> mapdl.stat()
     ELEMENT TYPE        1 IS SOLID186     3-D 20-NODE STRUCTURAL SOLID
      KEYOPT( 1- 6)=        0      0      0        0      0      0
      KEYOPT( 7-12)=        0      0      0        0      0      0
      KEYOPT(13-18)=        0      0      0        0      0      0

    Notes
    -----
    This is a status [STAT] topic command.
    The STAT command should immediately follow this command,
    which should report the status for the specified topic.
    """
    return self.run("ETYPE", **kwargs)

def enorm(self, enum: Union[str, int] = "",
          **kwargs) -> Optional[str]:
    """Reorients shell element normals or line element node
    connectivity.

    APDL Command: ENORM

    Parameters
    ----------
    enum
        Element number having the normal direction that the
        reoriented elements are to match.

    Examples
    --------
    >>> mapdl.enorm(1)

    Notes
    -----
    Reorients shell elements so that their outward normals are
    consistent with that of a specified element. ENORM can also be
    used to reorder nodal connectivity of line elements so that
    their nodal ordering is consistent with that of a specified
    element.

    For shell elements, the operation reorients the element by
    reversing and shifting the node connectivity pattern. For
    example, for a 4-node shell element, the nodes in positions I,
    J, K and L of the original element are placed in positions J,
    I, L and K of the reoriented element. All 3-D shell elements
    in the selected set are considered for reorientation, and no
    element is reoriented more than once during the
    operation. Only shell elements adjacent to the lateral (side)
    faces are considered.

    The command reorients the shell element normals on the same
    panel as the specified shell element. A panel is the geometry
    defined by a subset of shell elements bounded by free edges or
    T-junctions (anywhere three or more shell edges share common
    nodes).

    Reorientation progresses within the selected set until either
    of the following conditions is true:

    - The edge of the model is reached.

    - More than two elements (whether selected or unselected) are
      adjacent to a lateral face.

    In situations where unselected elements might undesirably
    cause case b to control, consider using ENSYM,0,,0,ALL instead
    of ENORM.  It is recommended that reoriented elements be
    displayed and graphically reviewed.

    You cannot use the ENORM command to change the normal
    direction of any element that has a body or surface load. We
    recommend that you apply all of your loads only after ensuring
    that the element normal directions are acceptable.

    Real constant values are not reoriented and may be invalidated
    by an element reversal.
    """
    return self.run(f"ENORM,{enum}", **kwargs)


def edele(self, iel1: MapdlInt = "", iel2: MapdlInt = "",
          inc: MapdlInt = "", **kwargs) -> Optional[str]:
    """Deletes selected elements from the model.

    APDL Command: EDELE

    Parameters
    ----------
    iel1, iel2, inc
        Delete elements from ``iel1`` to ``iel2`` (defaults to
        ``iel1``) in steps of ``inc`` (defaults to 1). If
        ``iel1='ALL'``, ``iel2`` and ``inc`` are ignored and all
        selected elements [ESEL] are deleted.  A component name
        may also be substituted for ``iel1`` (``iel2`` and ``inc``
        are ignored).

    Examples
    --------
    Delete the elements 10 through 25

    >>> mapdl.edele(10, 25)
    'DELETE SELECTED ELEMENTS FROM         10 TO         25 BY          1'

    Notes
    -----
    Deleted elements are replaced by null or "blank"
    elements. Null elements are used only for retaining the
    element numbers so that the element numbering sequence for the
    rest of the model is not changed by deleting elements. Null
    elements may be removed (although this is not necessary) with
    the NUMCMP command. If related element data (pressures, etc.)
    are also to be deleted, delete that data before deleting the
    elements. EDELE is for unattached elements only. You can use
    the xCLEAR family of commands to remove any attached elements
    from the database.
    """
    return self.run(f"EDELE,{iel1},{iel2},{inc}", **kwargs)

def extopt(self, lab: str = "", val1: Union[str, int] = "",
           val2: Union[str, int] = "", val3: MapdlInt = "",
           val4: MapdlInt = "", **kwargs) -> Optional[str]:
    """Controls options relating to the generation of volume elements from area elements.

    APDL Command: EXTOPT

    Parameters
    ----------
    lab
        Label identifying the control option. The meanings of
        Val1, Val2, and Val3 will vary depending on Lab.

        ON - Sets carryover of the material attributes, real
             constant attributes, and element coordinate system
             attributes of the pattern area elements to the
             generated volume elements.  Sets the pattern
             area mesh to clear when volume generations are done.
             Val1, Val2, and Val3 are ignored.

        OFF - Removes all settings associated with this command.
              Val1, Val2, and Val3 are ignored.

        STAT - Shows all settings associated with this command.
               Val1, Val2, Val3, and Val4 are ignored.

        ATTR - Sets carryover of particular pattern area attributes
               (materials, real constants, and element coordinate
               systems) of the pattern area elements to the
               generated volume elements. (See 2.) Val1 can be:

            0 - Sets volume elements to use
                current MAT command settings.

            1 - Sets volume elements to use material
                attributes of the pattern area elements.

        Val2 can be:

            0 - Sets volume elements to use current REAL
                command settings.

            1 - Sets volume elements to use real constant attributes
                of the pattern area elements.

        Val3 can be:

            0 - Sets volume elements to use current ESYS command
                settings.

            1 - Sets volume elements to use element coordinate
                system attributes of the pattern area elements.

        Val4 can be:

            0 - Sets volume elements to use current SECNUM command
                settings.

            1 - Sets volume elements to use section attributes of
                the pattern area elements.

        ESIZE - Val1 sets the number of element divisions in the
                direction of volume generation or volume sweep.
                For VDRAG and VSWEEP, Val1 is overridden by the
                LESIZE command NDIV setting. Val2 sets the spacing
                ratio (bias) in the direction of volume generation
                or volume sweep. If positive, Val2 is the nominal
                ratio of last division size to first division size
                (if > 1.0, sizes increase, if < 1.0, sizes
                decrease). If negative, Val2 is the nominal ratio of
                center division(s) size to end divisions size. Ratio
                defaults to 1.0 (uniform spacing).
                Val3 and Val4 are ignored.

        ACLEAR - Sets clearing of pattern area mesh.
                 (See 3.) Val1 can be:

            0 - Sets pattern area to remain meshed when volume
                generation is done.

            1 - Sets pattern area mesh to clear when volume
                generation is done. Val2, Val3, and Val4 are
                ignored.

        VSWE - Indicates that volume sweeping options will be set
               using Val1 and Val2. Settings specified with EXTOPT,
               VSWE will be used the next time the VSWEEP command
               is invoked. If Lab = VSWE, Val1 becomes a label.
               Val1 can be:

        AUTO - Indicates whether you will be prompted for the source
               and target used by VSWEEP or if VSWE should
               automatically determine the source and target.
               If Val1 = AUTO, Val2 is ON by default. VSWE will
               automatically determine the source and target for
               VSWEEP. You will be allowed to pick more than one
               volume for sweeping. When Val2 = OFF, the user will
               be prompted for the source and target for VSWEEP.
               You will only be allowed to pick one volume for
               sweeping.

        TETS - Indicates whether VSWEEP will tet mesh non-sweepable
               volumes or leave them unmeshed. If Val1 = TETS,
               Val2 is OFF by default. Non-sweepable volumes will be
               left unmeshed. When Val2 = ON, the non-sweepable
               volumes will be tet meshed if the assigned element
               type supports tet shaped elements.

    val1, val2, val3, val4
        Additional input values as described under each option for
        Lab.

    Notes
    -----
    EXTOPT controls options relating to the generation of volume
    elements from pattern area elements using the VEXT, VROTAT,
    VOFFST, VDRAG, and VSWEEP commands.  (When using VSWEEP,
    the pattern area is referred to as the source area.)

    Enables carryover of the attributes  of the pattern area
    elements to the generated volume elements when you are using
    VEXT, VROTAT, VOFFST, or VDRAG. (When using VSWEEP, since the
    volume already exists, use the VATT command to assign attributes
    before sweeping.)

    When you are using VEXT, VROTAT, VOFFST, or VDRAG, enables
    clearing of the pattern area mesh when volume generations are
    done. (When you are using VSWEEP, if selected, the area meshes
    on the pattern (source), target, and/or side areas clear when
    volume sweeping is done.)

    Neither EXTOPT,VSWE,AUTO nor EXTOPT,VSWE,TETS will be affected
    by EXTOPT,ON or EXTOPT, OFF.
    """
    command = f"EXTOPT,{lab},{val1},{val2},{val3},{val4}"
    return self.run(command, **kwargs)

def ereinf(self, **kwargs) -> Optional[str]:
    """Generates reinforcing elements from selected existing (base) elements.

    APDL Command: EREINF

    Notes
    -----
    The EREINF command generates reinforcing elements (REINF264 and
    REINF265) directly from selected base elements (that is,
    existing standard elements in your model). The command scans all
    selected base elements and generates (if necessary) a compatible
    reinforcing element type for each base element. (ANSYS
    allows a combination of different base element types.)

    Although predefining the reinforcing element type (ET) is not
    required, you must define the reinforcing element section type
    (SECTYPE); otherwise, ANSYS cannot generate the
    reinforcing element.

    The EREINF command does not create new nodes. The reinforcing
    elements and the base elements share the common nodes.

    Elements generated by this command are not associated with
    the solid model.

    After the EREINF command executes, you can issue ETLIST, ELIST,
    and EPLOT commands to verify the newly created reinforcing
    element types and elements.

    Reinforcing elements do not account for any subsequent
    modifications made to the base elements. ANSYS,
    Inc. recommends issuing the EREINF command only after the
    base elements are finalized. If you delete or modify base
    elements (via EDELE, EMODIF, ETCHG, EMID, EORIENT, NUMMRG,
    or NUMCMP commands, for example), remove all affected
    reinforcing elements and reissue the EREINF command to avoid
    inconsistencies.
    """
    command = "EREINF,"
    return self.run(command, **kwargs)

def egen(self, itime: MapdlInt = "", ninc: MapdlInt = "",
         iel1: Union[str, int] = "", iel2: MapdlInt = "",
         ieinc: MapdlInt = "", minc: MapdlInt = "",
         tinc: MapdlInt = "", rinc: MapdlInt = "",
         cinc: MapdlInt = "", sinc: MapdlInt = "",
         dx: MapdlFloat = "", dy: MapdlFloat = "",
         dz: MapdlFloat = "", **kwargs) -> Optional[str]:
    """Generates elements from an existing pattern.

    APDL Command: EGEN

    Parameters
    ----------
    itime, ninc
        Do this generation operation a total of ITIMEs,
        incrementing all nodes in the given pattern by NINC each
        time after the first. ITIME must be >1 if generation is
        to occur. NINC may be positive, zero, or negative.
        If DX, DY, and/or DZ is specified, NINC should be set
        so any existing nodes (as on NGEN) are not overwritten.

    iel1, iel2, ieinc
        Generate elements from selected pattern beginning with
        IEL1 to IEL2 (defaults to IEL1) in steps of IEINC (
        defaults to 1). If IEL1 is negative, IEL2 and IEINC are
        ignored and the last \|IEL1\| elements
        (in sequence backward from the maximum element number)
        are used as the pattern to be repeated.  If IEL1 = ALL,
        IEL2 and IEINC are ignored and use all selected elements
        [ESEL] as pattern to be repeated. A component name may
        also be substituted for IEL1 (IEL2 and INC are
        ignored).

    minc
        Increment material number of all elements in the given
        pattern by
        MINC each time after the first.

    tinc
        Increment type number by TINC.

    rinc
        Increment real constant table number by RINC.

    cinc
        Increment element coordinate system number by CINC.

    sinc
        Increment section ID number by SINC.

    dx, dy, dz
        Define nodes that do not already exist but are needed by
        generated
        elements (as though the NGEN,ITIME,INC,NODE1,,,DX,DY,
        DZ were issued
        before EGEN). Zero is a valid value. If blank, DX, DY,
        and DZ are
        ignored.

    Notes
    -----
    A pattern may consist of any number of previously defined
    elements. The MAT, TYPE, REAL, ESYS, and SECNUM numbers of
    the new elements are based upon the elements in the pattern
    and not upon the current specification settings.

    You can use the EGEN command to generate interface elements (
    INTER192, INTER193, INTER194, and INTER195) directly.
    However, because interface elements require that the element
    connectivity be started from the bottom surface, you must
    make sure that you use the correct element node connectivity.
    See the element descriptions for INTER192, INTER193,
    INTER194, and INTER195 for the correct element node definition.
    """
    command = f"EGEN,{itime},{ninc},{iel1},{iel2},{ieinc},{minc}," \
              f"{tinc},{rinc},{cinc},{sinc},{dx},{dy},{dz}"
    return self.run(command, **kwargs)

def ealive(self, elem: str = "", **kwargs) -> Optional[str]:
    """Reactivates an element (for the birth and death capability).

    APDL Command: EALIVE

    Parameters
    ----------
    elem
        Element to be reactivated:

        ALL  - Reactivates all selected elements (ESEL).

        Comp - Specifies a component name.

    Notes
    -----
    Reactivates the specified element when the birth and death
    capability is being used. An element can be reactivated only
    after it has been deactivated (EKILL).

    Reactivated elements have a zero strain (or thermal heat
    storage, etc.)  state.

    ANSYS, Inc. recommends using the element
    deactivation/reactivation procedure for analyses involving
    linear elastic materials only. Do not use element
    deactivation/reactivation in analyses involving time-
    dependent materials, such as viscoelasticity, viscoplasticity,
    and creep analysis.

    This command is also valid in PREP7.
    """
    command = f"EALIVE,{elem}"
    return self.run(command, **kwargs)

def escheck(self, sele: str = "", levl: str = "",
            defkey: MapdlInt = "", **kwargs) -> Optional[str]:
    """Perform element shape checking for a selected element set.

    APDL Command: ESCHECK

    Parameters
    ----------
    sele
        Specifies whether to select elements for checking:

        (blank) - List all warnings/errors from element shape
        checking.

        ESEL - Select the elements based on the .Levl criteria
        specified below.

    levl
        WARN - Select elements producing warning and error messages.

        ERR - Select only elements producing error messages (
        default).

    defkey
        Specifies whether check should be performed on deformed
        element
        shapes. .

        0 - Do not update node coordinates before performing
        shape checks (default).

        1 - Update node coordinates using the current set of
        deformations in the database.

    Notes
    -----
    Shape checking will occur according to the current SHPP
    settings. Although ESCHECK is valid in all processors,
    Defkey  uses the current results in the database. If no
    results are available a warning will be issued.

    This command is also valid in PREP7, SOLUTION and POST1.
    """
    command = f"ESCHECK,{sele},{levl},{defkey}"
    return self.run(command, **kwargs)

def esys(self, kcn: MapdlInt = "", **kwargs) -> Optional[str]:
    """Sets the element coordinate system attribute pointer.

    APDL Command: ESYS

    Parameters
    ----------
    kcn
        Coordinate system number:

        0 - Use element coordinate system orientation as defined
            (either by default or by KEYOPT setting) for the
            element (default).

        N - Use element coordinate system orientation based on
            local coordinate system N (where N must be greater
            than 10). For global system 0, 1, or 2, define a
            local system N parallel to appropriate system with
            the LOCAL or CS command (for example: LOCAL,11,1).

    Notes
    -----
    Identifies the local coordinate system to be used to define
    the element coordinate system of subsequently defined
    elements. Used only with area and volume elements. For
    non-layered volume elements, the local coordinate system N is
    simply assigned to be the element coordinate system. For
    shell and layered volume elements, the x and y axes of the
    local coordinate system N are projected onto the shell or
    layer plane to determine the element coordinate system. See
    Understanding the Element Coordinate System for more details.
    N refers to the coordinate system reference number (KCN)
    defined using the LOCAL (or similar) command. Element
    coordinate system numbers may be displayed [/PNUM].
    """
    command = f"ESYS,{kcn}"
    return self.run(command, **kwargs)

def eslv(self, type_: str = "", **kwargs) -> Optional[str]:
    """Selects elements associated with the selected volumes.

    APDL Command: ESLV

    Parameters
    ----------
    type_
        Label identifying the type of element selected:

        S - Select a new set (default).

        R - Reselect a set from the current set.

        A - Additionally select a set and extend the current set.

        U - Unselect a set from the current set.

    Notes
    -----
    Selects volume elements belonging to meshed [VMESH], selected
    [VSEL]
    volumes.

    This command is valid in any processor.
    """
    command = f"ESLV,{type_}"
    return self.run(command, **kwargs)

def esla(self, type_: str = "", **kwargs) -> Optional[str]:
    """Selects those elements associated with the selected areas.

    APDL Command: ESLA

    Parameters
    ----------
    type_
        Label identifying the type of element select:

        S - Select a new set (default).

        R - Reselect a set from the current set.

        A - Additionally select a set and extend the current set.

        U - Unselect a set from the current set.

    Notes
    -----
    Selects area elements belonging to meshed [AMESH], selected
    [ASEL] areas.

    This command is valid in any processor.
    """
    command = f"ESLA,{type_}"
    return self.run(command, **kwargs)

def errang(self, emin: MapdlInt = "", emax: MapdlInt = "",
           einc: MapdlInt = "", **kwargs) -> Optional[str]:
    """Specifies the element range to be read from a file.

    APDL Command: ERRANG

    Parameters
    ----------
    emin, emax, einc
        Elements with numbers from EMIN (defaults to 1) to EMAX
        (defaults to 99999999) in steps of EINC (defaults to 1)
        will be read.

    Notes
    -----
    Defines the element number range to be read [EREAD] from the
    element file. If a range is also implied from the NRRANG
    command, only those elements satisfying both ranges will be
    read.
    """
    command = f"ERRANG,{emin},{emax},{einc}"
    return self.run(command, **kwargs)

def erefine(self, ne1: Union[str, int] = "", ne2: MapdlInt = "",
            ninc: MapdlInt = "", level: MapdlInt = "",
            depth: MapdlInt = "", post: str = "", retain: str = "",
            **kwargs) -> Optional[str]:
    """Refines the mesh around specified elements.

    APDL Command: EREFINE

    Parameters
    ----------
    ne1, ne2, ninc
        Elements (NE1 to NE2 in increments of NINC) around which
        the mesh is to be refined. NE2 defaults to NE1, and NINC
        defaults to 1. If NE1 = ALL, NE2 and NINC are ignored and
        all selected elements are used for refinement. A component
        name may also be substituted for NE1 (NE2 and NINC are
        ignored).

    level
        Amount of refinement to be done. Specify the value of
        LEVEL as an integer from 1 to 5, where a value of 1
        provides minimal refinement, and a value of 5 provides
        maximum refinement (defaults to 1).

    depth
        Depth of mesh refinement in terms of number of elements
        outward from the indicated elements, NE1 to NE2
        (defaults to 0).

    post
        Type of postprocessing to be done after element
        splitting, in order to improve element quality:

        OFF - No postprocessing will be done.

        SMOOTH - Smoothing will be done. Node locations may change.

        CLEAN - Smoothing and cleanup will be done. Existing
                elements may be deleted, and node
                locations may change (default).

    retain
        Flag indicating whether quadrilateral elements must be
        retained in the refinement of an all-quadrilateral mesh.
        (The ANSYS program ignores the RETAIN argument when you
        are refining anything other than a quadrilateral mesh.)

        ON - The final mesh will be composed entirely of
             quadrilateral elements, regardless
             of the element quality (default).

        OFF - The final mesh may include some triangular elements
              in order to maintain
              element quality and provide transitioning.

    Notes
    -----
    EREFINE performs local mesh refinement around the specified
    elements. By default, the surrounding elements are split to
    create new elements with 1/2 the edge length of the original
    elements (LEVEL = 1).

    EREFINE refines all area elements and tetrahedral volume
    elements that are adjacent to the specified elements. Any
    volume elements that are adjacent to the specified elements,
    but are not tetrahedra (for example, hexahedra, wedges,
    and pyramids), are not refined.

    You cannot use mesh refinement on a solid model that contains
    initial conditions at nodes [IC], coupled nodes
    [CP family of commands], constraint equations [CE family of
    commands], or boundary conditions or loads applied directly
    to any of its nodes or elements. This applies to nodes and
    elements anywhere in the model, not just in the
    region where you want to request mesh refinement. If you have
    detached the mesh from the solid model, you must disable
    postprocessing cleanup or smoothing (POST = OFF) after the
    refinement to preserve the element attributes.

    For additional restrictions on mesh refinement, see Revising
    Your Model in the Modeling and Meshing Guide.

    This command is also valid for rezoning.
    """
    command = f"EREFINE,{ne1},{ne2},{ninc}," \
              f"{level},{depth},{post},{retain}"
    return self.run(command, **kwargs)

def eintf(self, toler: MapdlFloat = "", k: MapdlInt = "",
          tlab: str = "", kcn: str = "", dx: MapdlFloat = "",
          dy: MapdlFloat = "", dz: MapdlFloat = "",
          knonrot: MapdlInt = "", **kwargs) -> Optional[str]:
    """Defines two-node elements between coincident or offset nodes.

    APDL Command: EINTF

    Parameters
    ----------
    toler
        Tolerance for coincidence (based on maximum Cartesian
        coordinate difference for node locations and on angle
        differences for node orientations). Defaults to 0.0001.
        Only nodes within the tolerance are considered to be
        coincident.

    k
        Only used when the type of the elements to be generated is
        PRETS179. K is the pretension node that is common to the
        pretension section that is being created. If K is not
        specified, it will be created by ANSYS automatically and
        will have an ANSYS-assigned node number. If K is
        specified but does not already exist, it will be
        created automatically but will have the user-specified
        node number. K cannot be connected to any existing element.

    tlab
        Nodal number ordering. Allowable values are:

        LOW - The 2-node elements are generated from the lowest
              numbered node to the highest numbered node.

        HIGH - The 2-node elements are generated from the highest
               numbered node to the lowest numbered node.

        REVE - Reverses the orientation of the selected 2-node
               element.

    kcn
        In coordinate system KCN, elements are created between
        node 1 and node 2 (= node 1 + dx dy dz).

    dx, dy, dz
        Node location increments that define the node offset in
        the active coordinate system (DR, Dθ, DZ for cylindrical
        and DR, Dθ, DΦ for spherical or toroidal).

    knonrot
        When KNONROT = 0, the nodes coordinate system is not
        rotated. When KNONROT = 1, the nodes belonging to the
        elements created are rotated into coordinate system KCN
        (see NROTAT command description).

    Notes
    -----
    Defines 2-node elements (such as gap elements) between
    coincident or offset nodes (within a tolerance). May be used,
    for example, to "hook" together elements interfacing at a
    seam, where the seam consists of a series of node pairs. One
    element is generated for each set of two coincident nodes.
    For more than two coincident or offset nodes in a cluster,
    an element is generated from the lowest numbered
    node to each of the other nodes in the cluster. If fewer than
    all nodes are to be checked for coincidence, use the NSEL
    command to select the nodes. Element numbers are incremented
    by one from the highest previous element number. The element
    type must be set [ET] to a 2-node element before issuing this
    command. Use the CPINTF command to connect nodes by
    coupling instead of by elements. Use the CEINTF command to
    connect the nodes by constraint equations instead of by
    elements.

    For contact element CONTA178, the tolerance is based on the
    maximum Cartesian coordinate difference for node locations
    only. The angle differences for node orientations are not
    checked.
    """
    command = f"EINTF,{toler},{k},{tlab}," \
              f"{kcn},{dx},{dy}," \
              f"{dz},{knonrot}"
    return self.run(command, **kwargs)

def ensym(self, iinc: MapdlInt = "", ninc: MapdlInt = "",
          iel1: MapdlInt = "", iel2: MapdlInt = "",
          ieinc: MapdlInt = "", **kwargs) -> Optional[str]:
    """Generates elements by symmetry reflection.

    APDL Command: ENSYM

    Parameters
    ----------
    iinc
        Increment to be added to element numbers in existing set.

    ninc
        Increment nodes in the given pattern by NINC.

    iel1, iel2, ieinc
        Reflect elements from pattern beginning with IEL1 to IEL2
        (defaults to IEL1) in steps of IEINC (defaults to 1). If
        IEL1 = ALL, IEL2 and IEINC are ignored and pattern is all
        selected elements [ESEL]. A component name may also be
        substituted for IEL1 (IEL2 and IEINC are ignored).

    Notes
    -----
    This command is the same as the ESYM command except it allows
    explicitly assigning element numbers to the generated set (in
    terms of an increment IINC). Any existing elements already
    having these numbers will be redefined.

    The operation generates a new element by incrementing the
    nodes on the original element, and reversing and shifting the
    node connectivity pattern.  For example, for a 4-node 2-D
    element, the nodes in positions I, J, K and L of the original
    element are placed in positions J, I, L and K of the reflected
    element.

    Similar permutations occur for all other element types. For
    line elements, the nodes in positions I and J of the original
    element are placed in positions J and I of the reflected
    element. In releases prior to ANSYS 5.5, no node pattern
    reversing and shifting occurred for line elements generated by
    ENSYM. To achieve the same results as you did in releases
    prior to ANSYS 5.5, use the ENGEN command instead.

    See the ESYM command for additional information about symmetry
    elements.

    The ENSYM command also provides a convenient way to reverse
    shell element normals. If the IINC and NINC argument fields
    are left blank, the effect of the reflection is to reverse the
    direction of the outward normal of the specified elements. You
    cannot use the ENSYM command to change the normal direction of
    any element that has a body or surface load. We recommend that
    you apply all of your loads only after ensuring that the
    element normal directions are acceptable. Also note that real
    constants (such as nonuniform shell thickness and tapered beam
    constants) may be invalidated by an element reversal. See
    Revising Your Model in the Modeling and Meshing Guide for more
    information about controlling element normals.
    """
    return self.run(f"ENSYM,{iinc},,{ninc},{iel1},{iel2},{ieinc}",
                    **kwargs)

def esym(self, ninc: MapdlInt = "", iel1: MapdlInt = "",
         iel2: MapdlInt = "",
         ieinc: MapdlInt = "", **kwargs) -> Optional[str]:
    """Generates elements from a pattern by a symmetry reflection.

    APDL Command: ESYM

    Parameters
    ----------
    ninc
        Increment nodes in the given pattern by NINC.

    iel1, iel2, ieinc
        Reflect elements from pattern beginning with IEL1 to IEL2
        (defaults to IEL1) in steps of IEINC (defaults to 1). If
        IEL1 = ALL, IEL2 and IEINC are ignored and pattern is all
        selected elements [ESEL]. A component name may
        also be substituted for IEL1 (IEL2 and IEINC are ignored).

    Notes
    -----
    Generates additional elements from a given pattern (similar
    to EGEN) except with a "symmetry" reflection. The operation
    generates a new element by incrementing the nodes on the
    original element, and reversing and shifting  the node
    connectivity pattern. For example, for a 4-node 2-D element,
    the nodes in positions I, J, K, and L of the original element
    are placed in positions J, I, L, and K of the reflected element.

    Similar permutations occur for all other element types. For line
    elements, the nodes in positions I and J of the original
    element are placed in positions J and I of the reflected
    element. In releases prior
    to ANSYS 5.5, no node pattern reversing and shifting occurred
    for line elements generated by ESYM. To achieve the same
    results with ANSYS 5.5 as you did in prior releases, use the
    EGEN command instead.

    It is recommended that symmetry elements be displayed and
    graphically reviewed.

    If the nodes are also reflected (as with the NSYM command)
    this pattern is such that the orientation of the symmetry
    element remains similar to the original element (i.e.,
    clockwise elements are generated from
    clockwise elements).

    For a non-reflected node pattern, the reversed orientation
    has the effect of reversing the outward normal direction (
    clockwise elements are generated from counterclockwise
    elements).

    Note:: : Since nodes may be defined anywhere in the model
    independently of this command, any orientation of the
    "symmetry" elements is possible. See also the ENSYM command
    for modifying existing elements.
    """
    return self.run(f"ESYM,,{ninc},{iel1},{iel2},{ieinc}", **kwargs)

def esll(self, type_: str = "", **kwargs) -> Optional[str]:
    """Selects those elements associated with the selected lines.

    APDL Command: ESLL

    Parameters
    ----------
    type_
        Label identifying the type of element select:

        S - Select a new set (default).

        R - Reselect a set from the current set.

        A - Additionally select a set and extend the current set.

        U - Unselect a set from the current set.

    Notes
    -----
    Selects line elements belonging to meshed [LMESH], selected
    [LSEL] lines.

    This command is valid in any processor.
    """
    command = f"ESLL,{type_}"
    return self.run(command, **kwargs)


def elist(self, iel1: Union[str, int] = "", iel2: MapdlInt = "",
          inc: MapdlInt = "", nnkey: MapdlInt = "",
          rkey: MapdlInt = "", ptkey: MapdlInt = "",
          **kwargs) -> Optional[str]:
    """APDL Command: ELIST

    Lists the elements and their attributes.

    Parameters
    ----------
    iel1, iel2, inc
        Lists elements from IEL1 to IEL2 (defaults to IEL1) in
        steps of INC (defaults to 1). If IEL1 = ALL (default),
        IEL2 and INC are ignored and all selected elements [ESEL]
        are listed. A component name may also be substituted
        for IEL1 (IEL2 and INC are ignored).

    nnkey
        Node listing key:

        0 - List attribute references and nodes.

        1 - List attribute references but not nodes.

    rkey
        Real constant listing key:

        0 - Do not show real constants for each element.

        1 - Show real constants for each element. This includes
            default values chosen for
            the element.

    ptkey
        LS-DYNA part number listing key (applicable to ANSYS
        LS-DYNA only):

        0 - Do not show part ID number for each element.

        1 - Show part ID number for each element.

    Notes
    -----
    Lists the elements with their nodes and attributes (MAT,
    TYPE, REAL, ESYS, SECNUM, PART). See also the LAYLIST command
    for listing layered elements.

    This command is valid in any processor.
    """
    command = f"ELIST,{iel1},{iel2},{inc},{nnkey},{rkey},{ptkey}"
    return self.run(command, **kwargs)

def eorient(self, etype: str = "", dir_: Union[str, int] = "",
            toler: MapdlFloat = "", **kwargs) -> Optional[str]:
    """Reorients solid element normals.

    APDL Command: EORIENT

    Parameters
    ----------
    etype
        Specifies which elements to orient.

        LYSL - Specifies that certain solid elements (such as
               SOLID185 with KEYOPT(3) = 1,
               SOLID186 with KEYOPT(3) = 1, and SOLSH190) will be
               oriented. This value is the default.

    dir_
        The axis and direction for orientation, or an element
        number. If Dir is set to a positive number (n),
        then all eligible elements are oriented as similarly as
        possible to element n.

        NEGX - The element face with the outward normal most
               nearly parallel to the element coordinate system’s
               negative x-axis is designated (reoriented) as face 1.

        POSX - The element face with the outward normal most
               nearly parallel to the element coordinate system’s
               positive x-axis is designated (reoriented) as face 1.

        NEGY - The element face with the outward normal most
               nearly parallel to the element coordinate system’s
               negative y-axis is designated (reoriented) as face
               1. .

        POSY - The element face with the outward normal most
               nearly parallel to the element coordinate system’s
               positive y-axis is designated (reoriented) as face 1.

        NEGZ - (Default) The element face with the outward normal
               most nearly parallel to the element coordinate
               system’s negative z-axis is designated (reoriented)
               as face 1.

        POSZ - The element face with the outward normal most
               nearly parallel to the element coordinate system’s
               positive z-axis is designated (reoriented) as face 1.

    toler
        The maximum angle (in degrees) between the outward normal
        face and the target axis. Default is 90.0.
        Lower toler values will reduce the number of faces that
        are considered as the basis of element reorientation.

    Notes
    -----
    EORIENT renumbers the element faces, designating the face  most
    parallel to the XY plane of the element coordinate system (set
    with ESYS) as face 1 (nodes I-J-K-L, parallel to the layers
    in layered elements). It calculates the outward normal of
    each face and changes the node designation  of the elements
    so the face with a normal most nearly parallel with and in
    the same general direction as the target axis becomes face 1.

    The target axis, defined by Dir, is either the negative or
    positive indicated axis or the outward normal of face 1 of
    that element.

    All SOLID185 Layered Structural Solid, SOLID186 Layered
    Structural Solid, and SOLSH190 solid shell elements in the
    selected set are considered for reorientation.

    After reorienting elements, you should always display and
    graphically review results using the /ESHAPE command. When
    plotting models with many or symmetric layers, it may be
    useful to temporarily reduce the number of layers to two,
    with one layer being much thicker than the other.

    You cannot use EORIENT to change the normal direction of any
    element that has a body or surface load.  We recommend that
    you apply all of your loads only after ensuring that the
    element normal directions are acceptable.

    Prisms and tetrahedrals are also supported, within the current
    limitations of the SOLID185, SOLID186, and SOLSH190 elements.
    (Layers parallel to the four-node face of the prism are not
    supported.)
    """
    command = f"EORIENT,{etype},{dir_},{toler}"
    return self.run(command, **kwargs)

def engen(self, iinc: MapdlInt = "", itime: MapdlInt = "",
          ninc: MapdlInt = "", iel1: MapdlInt = "",
          iel2: MapdlInt = "", ieinc: MapdlInt = "",
          minc: MapdlInt = "", tinc: MapdlInt = "",
          rinc: MapdlFloat = "", cinc: MapdlInt = "",
          sinc: MapdlInt = "", dx: MapdlInt = "", dy: MapdlInt = "",
          dz: MapdlInt = "", **kwargs) -> Optional[str]:
    """Generates elements from an existing pattern.

    APDL Command: ENGEN

    Parameters
    ----------
    iinc
        Increment to be added to element numbers in pattern.

    itime, ninc
        Do this generation operation a total of ITIMEs,
        incrementing all nodes in the given pattern by NINC each
        time after the first. ITIME must be > 1 if generation is
        to occur. NINC may be positive, zero, or negative.

    iel1, iel2, ieinc
        Generate elements from the pattern that begins with IEL1
        to IEL2 (defaults to IEL1) in steps of IEINC (defaults to
        1). If IEL1 is negative, IEL2 and IEINC are ignored and
        use the last \|IEL1\| elements (in sequence backward from
        the maximum element number) as the pattern to be
        repeated.  If IEL1 = ALL, IEL2 and IEINC are ignored and
        all selected elements [ESEL] are used as the
        pattern to be repeated. A component name may also be
        substituted for IEL1 (IEL2 and IEINC are ignored).

    minc
        Increment material number of all elements in the given
        pattern by MINC each time after the first.

    tinc
        Increment type number by TINC.

    rinc
        Increment real constant table number by RINC.

    cinc
        Increment element coordinate system number by CINC.

    sinc
        Increment section ID number by SINC.

    dx, dy, dz
        Define nodes that do not already exist but are needed by
        generated elements (NGEN,ITIME,INC,NODE1,,,DX,DY,
        DZ). Zero is a valid value. If blank, DX, DY, and DZ are
        ignored.

    Notes
    -----
    Same as the EGEN command except it allows element numbers to be
    explicitly incremented (IINC) from the generated set. Any
    existing elements already having these numbers will be
    redefined.
    """
    command = f"ENGEN,{iinc},{itime},{ninc},{iel1},{iel2}," \
              f"{ieinc},{minc},{tinc},{rinc},{cinc},{sinc},{dx}," \
              f"{dy},{dz}"
    return self.run(command, **kwargs)

def esln(self, type_: str = "", ekey: MapdlInt = "",
         nodetype: str = "", **kwargs) -> Optional[str]:
    """Selects those elements attached to the selected nodes.

    APDL Command: ESLN

    Parameters
    ----------
    type_
        Label identifying the type of element selected:

        S - Select a new set (default).

        R - Reselect a set from the current set.

        A - Additionally select a set and extend the current set.

        U - Unselect a set from the current set.

    ekey
        Node set key:

        0 - Select element if any of its nodes are in the
        selected nodal set (default).

        1 - Select element only if all of its nodes are in the
        selected nodal set.

    nodetype
        Label identifying type of nodes to consider when selecting:

        ALL - Select elements considering all of their nodes (
              default).

        ACTIVE - Select elements considering only their active
                 nodes. An active node is a node
                 that contributes DOFs to the model.

        INACTIVE - Select elements considering only their
                   inactive nodes (such as orientation or
                   radiation nodes).

        CORNER - Select elements considering only their corner
                 nodes.

        MID - Select elements considering only their midside nodes.

    Notes
    -----
    ESLN selects elements which have any (or all EKEY) NodeType
    nodes in the currently-selected set of nodes. Only elements
    having nodes in the currently-selected set can be selected.

    This command is valid in any processor.
    """
    command = f"ESLN,{type_},{ekey},{nodetype}"
    return self.run(command, **kwargs)

def ematwrite(self, key: str = "", **kwargs) -> Optional[str]:
    """Forces the writing of all the element matrices to File.EMAT.

    APDL Command: EMATWRITE

    Parameters
    ----------
    key
        Write key:

        YES - Forces the writing of the element matrices to
              File.EMAT even if not normally
              done.

        NO - Element matrices are written only if required. This
             value is the default.

    Notes
    -----
    The EMATWRITE command forces ANSYS to write the File.EMAT
    file. The file is necessary if you intend to follow the
    initial load step with a subsequent inertia relief
    calculation (IRLF). If used in the solution
    processor (/SOLU), this command is only valid within the
    first load step.

    This command is also valid in PREP7.
    """
    command = f"EMATWRITE,{key}"
    return self.run(command, **kwargs)

def en(self, iel: MapdlInt = "", i: MapdlInt = "", j: MapdlInt = "",
       k: MapdlInt = "", l: MapdlInt = "",
       m: MapdlInt = "", n: MapdlInt = "", o: MapdlInt = "",
       p: MapdlInt = "", **kwargs) -> Optional[str]:
    """Defines an element by its number and node connectivity.

    APDL Command: EN

    Parameters
    ----------
    iel
        Number assigned to element being defined.

    i
        Number of node assigned to first nodal position (node I).

    j, k, l, m, n, o, p
        Number assigned to second (node J) through eighth (node
        P) nodal position, if any.

    Notes
    -----
    Defines an element by its nodes and attribute values. Similar
    to the E command except it allows the element number (IEL) to be defined
    explicitly. Element numbers need not be consecutive. Any
    existing element already having this number will be redefined.

    Up to 8 nodes may be specified with the EN command. If more
    nodes are needed for the element, use the
    :meth:`emore` command. The number of nodes required and the
    order in which they should be specified are described in the
    Element Reference for each element type.  The current (or
    default) MAT, TYPE, REAL, SECNUM, and ESYS attribute values
    are also assigned to the element.

    When creating elements with more than 8 nodes using this
    command and the :meth:`emore` command, it may be necessary to
    turn off shape checking using the SHPP command before
    issuing this command. If a valid element type can be created
    without using the additional nodes on the :meth:`emore`
    command, this command will create that element. The
    :meth:`emore` command will then modify the element to include
    the additional nodes. If shape checking is active, it will be
    performed before the :meth:`emore` command is issued.
    Therefore, if the shape checking limits are exceeded, element
    creation may fail before the :meth:`emore` command modifies
    the element into an acceptable shape.
    """
    command = f"EN,{iel},{i},{j},{k},{l},{m},{n},{o},{p}"
    return self.run(command, **kwargs)
def elem(self, **kwargs) -> Optional[str]:
    """Specifies "Elements" as the subsequent status topic.

    APDL Command: ELEM

    Notes
    -----

    The STAT command should immediately follow this command,
    which should report the status for the specified topic.
    """
    command = "ELEM,"
    return self.run(command, **kwargs)

def einfin(self, compname: str = "", pnode: MapdlInt = "",
           **kwargs) -> Optional[str]:
    """Generates structural infinite elements from selected nodes.

    APDL Command: EINFIN

    Parameters
    ----------
    compname
        Component name containing one node to be used as the pole
        node for generating INFIN257 structural infinite
        elements. The pole node is generally located at or near
        the geometric center of the finite element domain.

    pnode
        Node number for the direct input of the pole node. A
        parameter or parametric expression is also valid. Specify
        this value when no CompName has been specified. If
        CompName is specified, this value is ignored.

    Notes
    -----
    The EINFIN command generates structural infinite elements
    (INFIN257) directly from the selected face of valid base
    elements (existing standard elements in your model). The
    command scans all base elements for the selected nodes and
    generates a compatible infinite element type for each base
    element. A combination of different base element types is
    allowed if the types are all compatible with the infinite
    elements.

    The infinite element type requires no predefinition (ET).

    The faces of base elements are determined from the selected
    node set (NSEL), and the geometry of the infinite element is
    determined based on the shape of the face. Element
    characteristics and options are determined according to the
    base element. For the face to be used, all nodes on the face
    of a base element must be selected

    Use base elements to model the near-field domain that
    interacts with the solid structures or applied loads. To
    apply the truncated far-field effect, a single layer of
    infinite elements must be attached to the near-field domain.
    The outer surface of the near-field domain
    must be convex.

    After the EINFIN command executes, you can verify the newly
    created infinite element types and elements (ETLIST, ELIST,
    EPLOT).

    Infinite elements do not account for any subsequent
    modifications made to the base elements. It is good practice
    to issue the EINFIN
    command only after the base elements are finalized. If you
    delete or modify base elements, remove all affected infinite
    elements and reissue the EINFIN command; doing so prevents
    inconsistencies.
    """
    command = f"EINFIN,{compname},{pnode}"
    return self.run(command, **kwargs)

def eread(self, fname: str = "",
          ext: str = "", **kwargs) -> Optional[str]:
    """Reads elements from a file.

    APDL Command: EREAD

    Parameters
    ----------
    fname
        File name and directory path (248 characters maximum,
        including the characters needed for the directory path).
        An unspecified directory path defaults to the working
        directory; in this case, you can use all 248 characters
        for the file name.

    ext
        Filename extension (eight-character maximum).

    Notes
    -----
    This read operation is not necessary in a standard ANSYS run
    but is provided as a convenience to users wanting to read a
    coded element file, such as from another mesh generator or
    from a CAD/CAM program.  Data should be formatted as produced
    with the EWRITE command. If issuing EREAD to acquire element
    information generated from ANSYS EWRITE, you must also issue
    NREAD before the EREAD command. The element types [ET] must be
    defined before the file is read so that the file may be read
    properly. Only elements that are specified with the ERRANG
    command are read from the file. Also, only elements that are
    fully attached to the nodes specified on the NRRANG command
    are read from the file. Elements are assigned numbers
    consecutively as read from the file, beginning with the
    current highest database element number plus one. The file is
    rewound before and after reading. Reading continues until the
    end of the file.
    """
    command = f"EREAD,{fname},{ext}"
    return self.run(command, **kwargs)

def esel(self, type_: str = "", item: str = "", comp: str = "",
         vmin: Union[str, int, float] = "",
         vmax: Union[str, int, float] = "", vinc: MapdlInt = "",
         kabs: MapdlInt = "", **kwargs) -> Optional[str]:
    """Selects a subset of elements.

    APDL Command: ESEL

    Parameters
    ----------
    type\_
        Label identifying the type of select:

        - S - Select a new set (default).
        - R - Reselect a set from the current set.
        - A - Additionally select a set and extend the current set.
        - U - Unselect a set from the current set.
        - ALL - Restore the full set.
        - NONE - Unselect the full set.
        - INVE - Invert the current set (selected becomes
          unselected and vice versa).
        - STAT - Display the current select status.

    item
        Label identifying data, see Table 110: ESEL - Valid Item
        and Component Labels. Some items also require a
        component label. Defaults to ELEM. If Item = STRA
        (straightened), elements are selected whose midside nodes
        do not conform to the curved line or non-flat area on
        which they should lie. (Such elements are sometimes
        formed during volume meshing (VMESH) in an attempt to
        avoid excessive element distortion.) You should
        graphically examine any such elements to evaluate their
        possible effect on solution accuracy.

    comp
        Component of the item (if required). Valid component
        labels are shown in Table 110: ESEL - Valid Item and
        Component Labels below.

    vmin
        Minimum value of item range. Ranges are element numbers,
        attribute numbers, load values, or result values
        as appropriate for the item. A component name (as
        specified via the CM command) can also be substituted for
        VMIN (in which case VMAX and VINC are ignored).

    vmax
        Maximum value of item range. VMAX defaults to VMIN for
        input values. For result values, VMAX defaults to infinity if VMIN is
        positive, or to zero if VMIN is negative.

    vinc
        Value increment within range. Used only with integer
        ranges (such as for element and attribute numbers).
        Defaults to 1. VINC cannot be negative.

    kabs
        Absolute value key:

            - `kabs = 0` - Check sign of value during selection.
            - `kabs = 1` - Use absolute value during selection (sign
              ignored).

    Notes
    -----
    The fields `item`, `comp`, `vmin`, `vmax`, `vinc` and `kabs` are
    used only with `type_` = `"S"`, `"R"`, `"A"`, or `"U"`.

    Selects elements based on values of a labeled item and
    component. For example, to select a new set of elements
    based on element numbers 1
    through 7, use ESEL,S,ELEM,,1,7.  The subset is used when the
    ALL label is entered (or implied) on other commands, such as
    ELIST, ALL. Only data identified by element number are
    selected. Selected data are internally flagged; no actual
    removal of data from the database occurs. Different element
    subsets cannot be used for different load steps [SOLVE] in a
    /SOLU sequence.  The subset used in the first load step
    will be used for all subsequent load steps regardless of
    subsequent ESEL specifications.

    This command is valid in any processor.

    Elements crossing the named path (see PATH command) will be
    selected. This option is only available in PREP7 and POST1.
    If no geometry data has been mapped to the path (i.e.,
    via PMAP and PDEF commands), the path will assume the default
    mapping option (PMAP,UNIFORM) to map the geometry prior to
    selecting the elements. If an invalid path name is
    given, the ESEL command is ignored (status of selected
    elements is unchanged). If there are no elements crossing the
    path, the ESEL command will return zero elements selected.

    For selections based on non-integer numbers (coordinates,
    results, etc.), items that are within the range VMIN -Toler
    and VMAX + Toler are selected. The default tolerance Toler is
    based on the relative values of VMIN and VMAX as follows:

    If VMIN = VMAX, Toler = 0.005 x VMIN.

    If VMIN = VMAX = 0.0, Toler = 1.0E-6.

    If VMAX ≠ VMIN, Toler = 1.0E-8 x (VMAX - VMIN).

    Use the SELTOL command to override this default and specify
    Toler explicitly.

    Table: 133:: : ESEL - Valid Item and Component Labels
    """
    command = f"ESEL,{type_},{item},{comp},{vmin},{vmax},{vinc}," \
              f"{kabs}"
    return self.run(command, **kwargs)

def esort(self, item: str = "", lab: str = "", order: MapdlInt = "",
          kabs: MapdlInt = "", numb: MapdlInt = "",
          **kwargs) -> Optional[str]:
    """Sorts the element table.

    APDL Command: ESORT

    Parameters
    ----------
    item
        Label identifying the item:
        ETAB - (currently the only Item available)

    lab
        element table label: Lab - Any user-defined label from
        the ETABLE command (input in the Lab field of the ETABLE
        command).

    order
        Order of sort operation:

        0 - Sort into descending order.

        1 - Sort into ascending order.

    kabs
        Absolute value key:

        0 - Sort according to real value.

        1 - Sort according to absolute value.

    numb
        Number of elements (element table rows) to be sorted in
        ascending or descending order (ORDER) before sort is
        stopped (remainder will be in unsorted sequence)
        (defaults to all elements).

    Notes
    -----
    The element table rows are sorted based on the column
    containing the Lab values. Use EUSORT to restore the original
    order. If ESORT is specified with PowerGraphics on
    [/GRAPHICS,POWER], then the nodal solution results listing
    [PRNSOL] will be the same as with the full graphics mode
    [/GRAPHICS,FULL].
    """
    command = f"ESORT,{item},{lab},{order},{kabs},{numb}"
    return self.run(command, **kwargs)

def esurf(self, xnode: MapdlInt = "", tlab: str = "",
          shape: str = "", **kwargs) -> Optional[str]:
    """Generates elements overlaid on the free faces of selected nodes.

    APDL Command: ESURF

    Parameters
    ----------
    xnode
        Node number that is used only in the following two cases:

    tlab
        Generates target, contact, and hydrostatic fluid elements
        with correct direction of normals.

        TOP - Generates target and contact elements over beam and
              shell elements, or hydrostatic fluid elements over
              shell elements, with the normals the same as the
              underlying beam and shell elements (default).

        BOTTOM - Generates target and contact elements over beam
                 and shell elements, or hydrostatic fluid
                 elements over shell elements, with the
                 normals opposite to the underlying beam and shell
                 elements.

        If target or contact elements and hydrostatic fluid
        elements are defined on the same underlying shell
        elements, you only need to use this option once to orient
        the normals opposite to the
        underlying shell elements.

        REVERSE - Reverses the direction of the normals on
                  existing selected target elements, contact
                  elements, and hydrostatic fluid elements. - If
                  target or contact elements and hydrostatic
                  fluid elements are defined on the same
                  underlying shell elements, you only need to use
                  this option once to reverse the normals for all
                  selected elements.

    shape
        Used to specify the element shape for target element
        TARGE170 (Shape = LINE or POINT) or TARGE169 elements
        (Shape = POINT).

        (blank) - The target element takes the same shape as the
                  external surface of the underlying element
                  (default).

        LINE - Generates LINE or PARA (parabolic) segments on
               exterior of selected 3-D elements.

        POINT - Generates POINT segments on selected nodes.

    Notes
    -----
    The ESURF command generates elements of the currently active
    element type overlaid on the free faces of existing elements.
    For example, surface elements (such as SURF151, SURF152,
    SURF153, SURF154, or SURF159) can be generated over solid
    elements (such as PLANE55, SOLID70, PLANE182, SOLID185,
    or SOLID272, respectively).

    Element faces are determined from the selected node set
    (NSEL) and the load faces for that element type. The
    operation is similar to that used for generating element
    loads from selected nodes via the SF,ALL command, except that
    elements (instead of loads) are generated. All nodes on the
    face must be selected for the face to be used. For shell
    elements, only face one of the element is available. If nodes
    are shared by adjacent selected element faces, the faces are not
    free and no element is generated.

    Elements created by ESURF are oriented such that their
    surface load directions are consistent with those of the
    underlying elements. Carefully check generated elements and
    their orientations.

    Generated elements use the existing nodes and the active MAT,
    TYPE, REAL, and ESYS attributes. The exception is when Tlab =
    REVERSE. The reversed target and contact elements have the
    same attributes as the original elements. If the underlying
    elements are solid elements, Tlab = TOP or BOTTOM has no effect.

    When the command generates a target element, the shape is by
    default the same as that of the underlying element. Issue
    ESURF,,, LINE or ESURF,,,POINT to generate LINE, PARA,
    and POINT segments.

    The ESURF command can also generate the 2-D or 3-D
    node-to-surface element CONTA175, based on the selected node
    components of the underlying solid elements. When used to
    generate CONTA175 elements, all ESURF arguments are ignored.
    (If CONTA175 is the active element type, the path Main Menu>
    Preprocessor> Modeling> Create> Elements> Node-to-Surf uses
    ESURF to generate elements.)

    To generate SURF151 or SURF152 elements that have two extra
    nodes from FLUID116 elements, KEYOPT(5) for SURF151 or
    SURF152 is first set to 0 and ESURF is issued. Then KEYOPT(5)
    for SURF151 or SURF152 is set to 2 and MSTOLE is issued. For
    more information, see Using the Surface Effect Elements in
    the Thermal Analysis Guide.

    For hydrostatic fluid elements HSFLD241 and HSFLD242,
    the ESURF command generates triangular (2-D) or
    pyramid-shaped (3-D) elements with bases that are overlaid on
    the faces of selected 2-D or 3-D solid or shell elements.
    The single vertex for all generated elements is at the
    pressure node specified as XNODE. The generated elements fill
    the volume enclosed by the solid or shell elements. The nodes
    on the overlaid faces have translational degrees of freedom,
    while the pressure node shared by all generated elements has
    a single hydrostatic pressure degree of freedom, HDSP (see
    HSFLD241 and HSFLD242 for more information about the pressure
    node).
    """
    command = f"ESURF,{xnode},{tlab},{shape}"
    return self.run(command, **kwargs)

def eplot(self, show_node_numbering=False, vtk=None, **kwargs):
    """Plots the currently selected elements.

    APDL Command: EPLOT

    Parameters
    ----------
    vtk : bool, optional
        Plot the currently selected elements using ``pyvista``.
        Defaults to current ``use_vtk`` setting.

    show_node_numbering : bool, optional
        Plot the node numbers of surface nodes.

    **kwargs
        See ``help(ansys.mapdl.core.plotter.general_plotter)`` for more
        keyword arguments related to visualizing using ``vtk``.

    Examples
    --------
    >>> mapdl.clear()
    >>> mapdl.prep7()
    >>> mapdl.block(0, 1, 0, 1, 0, 1)
    >>> mapdl.et(1, 186)
    >>> mapdl.esize(0.1)
    >>> mapdl.vmesh('ALL')
    >>> mapdl.vgen(2, 'all')
    >>> mapdl.eplot(show_edges=True, smooth_shading=True,
                    show_node_numbering=True)

    Save a screenshot to disk without showing the plot

    >>> mapdl.eplot(background='w', show_edges=True, smooth_shading=True,
                    window_size=[1920, 1080], savefig='screenshot.png',
                    off_screen=True)

    """
    if vtk is None:
        vtk = self._use_vtk

    if vtk:
        kwargs.setdefault('title', 'MAPDL Element Plot')
        if not self._mesh.n_elem:
            warnings.warn('There are no elements to plot.')
            return general_plotter([], [], [], **kwargs)

        # TODO: Consider caching the surface
        esurf = self.mesh._grid.linear_copy().extract_surface().clean()
        kwargs.setdefault('show_edges', True)

        # if show_node_numbering:
        labels = []
        if show_node_numbering:
            labels = [{'points': esurf.points, 'labels': esurf['ansys_node_num']}]

        return general_plotter([{'mesh': esurf}],
                               [],
                               labels,
                               **kwargs)

    # otherwise, use MAPDL plotter
    self._enable_interactive_plotting()
    return super().eplot(**kwargs)
