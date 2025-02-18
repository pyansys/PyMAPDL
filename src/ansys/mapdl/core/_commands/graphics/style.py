# Copyright (C) 2016 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import warnings


class Style:

    def ctype(
        self,
        key: int | str = "",
        dotd: str = "",
        dots: str = "",
        dshp: int | str = "",
        tlen: str = "",
        **kwargs,
    ):
        r"""Specifies the type of contour display.

        Mechanical APDL Command: `/CTYPE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CTYPE.html>`_

        **Command default:**

        .. _s-CTYPE_default:

        Standard contour display.

        Parameters
        ----------
        key : int or str
            Type of display:

            * ``0`` - Standard contour display.

            * ``1`` - Isosurface display.

            * ``2`` - Particle gradient display.

            * ``3`` - Gradient triad display.

        dotd : str
            Maximum dot density for particle gradient display ( ``KEY`` = 2). Density is expressed as dots
            per screen width (defaults to 30).

        dots : str
            Dot size for particle gradient display ( ``KEY`` = 2). Size is expressed as a fraction of the
            screen width (defaults to 0.0 (single dot width)).

        dshp : int or str
            Spherical dot shape precision for particle gradient display ( ``KEY`` = 2). (3D options are supported only on 3D devices):

            * ``0`` - Flat 2D circular dot.

            * ``1`` - Flat-sided 3D polyhedron.

            * ``n`` - 3D sphere with ``n`` (>1) polygon divisions per 90° of radius.

        tlen : str
            Maximum length of triads for gradient triad display ( ``KEY`` = 3). Value is expressed as a
            fraction of the screen width (defaults to 0.067).

        Notes
        -----

        .. _s-CTYPE_notes:

        Use :ref:`ctype`,STAT to display the current settings. Only the standard contour display (
        :ref:`ctype`,0) and the isosurface contour display ( :ref:`ctype`,1) are supported by PowerGraphics
        ( :ref:`graphics`,POWER).

        This command is valid in any processor.
        """
        command = f"/CTYPE,{key},{dotd},{dots},{dshp},{tlen}"
        return self.run(command, **kwargs)

    def cplane(self, key: int | str = "", **kwargs):
        r"""Specifies the cutting plane for section and capped displays.

        Mechanical APDL Command: `/CPLANE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CPLANE.html>`_

        **Command default:**

        .. _s-CPLANE_default:

        The cutting plane is normal to the viewing vector at the focus point.

        Parameters
        ----------
        key : int or str
            Specifies the cutting plane:

            * ``0`` - Cutting plane is normal to the viewing vector ( :ref:`view` ) and passes through the focus point (
              :ref:`focus` ) (default).

            * ``1`` - The working plane ( :ref:`wplane` ) is the cutting plane.

        Notes
        -----

        .. _s-CPLANE_notes:

        Defines the cutting plane to be used for section and capped displays ( :ref:`slashtype`,,(1, 5, or
        7)).

        This command is valid in any processor.
        """
        command = f"/CPLANE,{key}"
        return self.run(command, **kwargs)

    def light(
        self,
        wn: str = "",
        num: int | str = "",
        int: str = "",
        xv: str = "",
        yv: str = "",
        zv: str = "",
        refl: str = "",
        **kwargs,
    ):
        r"""Specifies the light direction for the display window.

        Mechanical APDL Command: `/LIGHT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LIGHT.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        num : int or str
            Ambient or directional light key:

            * ``0`` - Ambient light (default).

            * ``1`` - Directional light.

        int : str
            Light intensity factor (defaults to 0.3 for ambient, 1.0 for directional). This option is valid
            only for 3D devices).

        xv : str
            Light direction (valid only for ``NUM`` = 1). The directional light source is parallel to the
            line from point ``XV``, ``YV``, ``ZV`` to the origin, in the global Cartesian system origin.
            Defaults to the viewing direction ( :ref:`view` ).

        yv : str
            Light direction (valid only for ``NUM`` = 1). The directional light source is parallel to the
            line from point ``XV``, ``YV``, ``ZV`` to the origin, in the global Cartesian system origin.
            Defaults to the viewing direction ( :ref:`view` ).

        zv : str
            Light direction (valid only for ``NUM`` = 1). The directional light source is parallel to the
            line from point ``XV``, ``YV``, ``ZV`` to the origin, in the global Cartesian system origin.
            Defaults to the viewing direction ( :ref:`view` ).

        refl : str
            Light reflectance factor (valid only for ``NUM`` = 1 and 3D devices).

        Notes
        -----

        .. _s-LIGHT_notes:

        Defines the light direction for the window. Use this command only with 3D graphics devices or 2D
        devices when Z-buffering is used ( :ref:`slashtype`,,(6 or 7)). The ambient light has no direction,
        only an intensity. You can position the directional light source by defining a point (in the global
        Cartesian coordinate system) representing a point along the light directional line. This point, and
        the global Cartesian coordinate system origin, define the line along which the light is positioned
        looking toward the origin. You can use any point along the light line; for example, both (1.,1.,1.)
        and (2.,2.,2.) give the same light effect. For 3D graphics devices only, the directional light
        source also has intensity and reflectance factors.

        By choosing the highest intensity ambient light for 3D graphics devices (via :ref:`light`,WN,0,1),
        you can nullify color shading and other effects of directional lighting.

        This command is valid in any processor.
        """
        command = f"/LIGHT,{wn},{num},{int},{xv},{yv},{zv},{refl}"
        return self.run(command, **kwargs)

    def eshape(self, scale: str = "", key: str = "", **kwargs):
        r"""Displays elements with shapes determined from the real constants, section definition, or other
        inputs.

        Mechanical APDL Command: `/ESHAPE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESHAPE.html>`_

        **Command default:**

        .. _s-ESHAPE_default:

        Use simple display of line and area elements ( ``SCALE`` = 0).

        Parameters
        ----------
        scale : int or str
            Scaling factor:

            * ``0`` - Use simple display of line and area elements. This value is the default.

            * ``1`` - Use real constants, section definition, or other information to form a solid shape display of the
              applicable elements.

            * ``FAC`` - Multiply certain real constants, such as thickness, by ``FAC`` (where ``FAC`` > 0.01) and use them
              to form a solid shape display of elements.

        key : int or str
            Current shell thickness key:

            * ``0`` - Use current thickness in the displaced solid shape display of shell elements (valid for SHELL181,
              SHELL208, SHELL209, and SHELL281 ). This value is the default.

            * ``1`` - Use initial thickness in the displaced solid shape display of shell elements.

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
        model``s bounding box diagonal.

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
        warnings.warn(
            "pymapdl does not support /ESHAPE when plotting in Python using ``mapdl.eplot()``.  Use ``mapdl.eplot(vtk=False)`` "
        )
        command = f"/ESHAPE,{scale},{key}"
        return self.run(command, **kwargs)

    def edge(self, wn: str = "", key: int | str = "", angle: str = "", **kwargs):
        r"""Displays only the common lines (“edges”) of an object.

        Mechanical APDL Command: `/EDGE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_EDGE.html>`_

        **Command default:**

        .. _s-EDGE_default:

        For element plots, display common lines between all adjacent element faces. For contour plots,
        display only the common lines between non-coplanar faces.

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies. The default window is 1.

        key : int or str
            Edge key:

            **Elements Plots**

            * ``0`` - Display common lines between all adjacent element faces.

            * ``1`` - Display only the common lines between non-coplanar faces (that is, show only the edges).

            **Contour Plots**

            * ``0`` - Display only the common lines between non-coplanar faces.

            * ``1`` - Display common lines between all element faces.

        angle : str
            Largest angle between two faces for which the faces are considered to be coplanar (0° to 180°).
            Defaults to 45°. A smaller angle produces more edges, a larger angle produces fewer edges.

        Notes
        -----

        .. _s-EDGE_notes:

        The ``ANGLE`` field is used in PowerGraphics to determine geometric discontinuities. It is a
        tolerance measure for the differences between the normals of the surfaces being considered. Values
        within the tolerance are accepted as coplanar (geometrically continuous). In postprocessing
        displays, results are not averaged across discontinuous surfaces.

        A surface can be displayed as an edge outline without interior detail. This is useful for both
        geometry and postprocessing displays. Element outlines are normally shown as solid lines for
        geometry and displacement displays. Lines common to adjacent "coplanar" element faces are removed
        from the display. Midside nodes of elements are ignored.

        The :ref:`shrink` option is ignored with the edge option.

        :ref:`edge` is not supported for :ref:`plesol` and :ref:`eshape` displays when in PowerGraphics mode
        ( :ref:`graphics`,POWER).

        The :ref:`edge` command is valid in any processor.
        """
        command = f"/EDGE,{wn},{key},{angle}"
        return self.run(command, **kwargs)

    def facet(self, lab: str = "", **kwargs):
        r"""Specifies the facet representation used to form solid model displays.

        Mechanical APDL Command: `/FACET <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_FACET.html>`_

        Parameters
        ----------
        lab : str
            Valid labels:

            * ``FINE`` - Use finer tessellation to increase the number of facets for the display. Provides the best
              representation (but decreases speed of operation).

            * ``NORML`` - Use the basic number of facets for the display (default).

            * ``COAR`` - Use a limited number of facets for the display. This option will increase the speed of the
              operations, but may produce poor representations for some imported models.

            * ``WIRE`` - Display model with a wireframe representation (fast, but surfaces will not be shown).

        Notes
        -----

        .. _s-FACET_notes:

        Specifies the facet (or polygon) representation used to form solid model displays. Used only with
        the :ref:`aplot`, :ref:`asum`, :ref:`vplot`, and :ref:`vsum` commands.

        This command is valid in any processor.
        """
        command = f"/FACET,{lab}"
        return self.run(command, **kwargs)

    def normal(self, wn: str = "", key: int | str = "", **kwargs):
        r"""Allows displaying area elements by top or bottom faces.

        Mechanical APDL Command: `/NORMAL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NORMAL.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        key : int or str
            Display key:

            * ``0`` - No face distinction.

            * ``1`` - Show only area elements having their positive normals directed toward the viewing point.

            * ``-1`` - Show only area elements having their positive normals directed away from the viewing point.

        Notes
        -----

        .. _s-NORMAL_notes:

        :ref:`normal` allows you to select area elements and area plots by the top or bottom faces. It is
        useful for checking the normal directions on shell elements. The positive normal (element Z
        direction) is defined by the right-hand rule following the node I, J, K, L input direction. This
        command is available only with raster or hidden-line displays, for WIN32 or X11 2D displays only.

        This command is valid in any processor.
        """
        command = f"/NORMAL,{wn},{key}"
        return self.run(command, **kwargs)

    def txtre(
        self,
        lab: str = "",
        num: int | str = "",
        n1: str = "",
        n2: str = "",
        ninc: str = "",
        **kwargs,
    ):
        r"""Controls application of texture to selected items.

        Mechanical APDL Command: `/TXTRE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TXTRE.html>`_

        Parameters
        ----------
        lab : str
            You can apply texture according to the following labels:

            * ``ELEM`` - Apply texture to elements ``N1`` through ``N2`` in steps of ``NINC``.

            * ``AREA`` - Apply texture to areas ``N1`` through ``N2`` in steps of ``NINC``.

            * ``VOLU`` - Apply texture to volumes ``N1`` through ``N2`` in steps of ``NINC``.

            * ``CM`` - Apply texture to the component named in ``N1``. ``N2`` and ``NINC`` are ignored.

            * ``ON, OFF`` - Sets the specified texture display on or off. All other fields are ignored.

            * ``File`` - If Lab = File, the command format is :ref:`txtre`, File, ``Key_Index``, ``Fname``, ``Fext``, ``--``, ``Format`` (This variant of the command is applicable to 2D drivers).

              * ``Key_Index`` - The texture index associated with the file. If the number fifty-one (51) is used, the imported
                bitmap will be used as the window's logo.

              * ``Fname`` - File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case, you
            can use all 248 characters for the file name.
              * ``Fext`` - Filename extension (eight-character maximum).
              * ``Format`` - The file format. If ``Format`` = 0, the file is a pixmap (Linux) or Bitmap (PC). The file cannot
                contain a compressed image, and the PC file must be 8 or 24 bit BI_RGB format. If ``Format`` = 1 or
                JPEG, then the file is in JPEG (Joint Photographic Experts Group) format. If ``Format`` = 2 or PNG,
                then the file is in PNG (Portable Network Graphics) format.

        num : int or str
            Select the texture index number from the following list:

            * ``0`` - No Texturing

            * ``1`` - Aluminum

            * ``2`` - Aluminum, Brushed

            * ``3`` - Steel With Bumps

            * ``4`` - Steel, Embossed

            * ``5`` - Iron

            * ``6`` - Steel, Pattern

            * ``7`` - Steel, Riveted

            * ``8`` - Steel, Scratched

            * ``9`` - Tin

            * ``10`` - Metal

            * ``11`` - Steel, Etched

            * ``12`` - Metal, Hot

            * ``13`` - Iron, Grainy

            * ``14`` - Metal, Rusty

            * ``15`` - Brick

            * ``16`` - Block

            * ``17`` - Wood

            * ``18`` - Wood, Light

            * ``19`` - Wood, Walnut

            * ``20`` - Plastic, Hard Blue

            * ``21`` - Plastic, Light Blue

            * ``22`` - Plastic, Hard Red

            * ``31`` - Gold

            * ``32`` - Brass

            * ``33`` - Silver

            * ``34`` - Plastic, Black

            * ``35`` - Plastic, Ivory

            * ``36`` - Plastic, Blue

            * ``37`` - Plastic, Red

            * ``38`` - Plastic, Yellow

            * ``39`` - Plastic, Green

            * ``40`` - Plastic, Brown

        n1 : str
            Apply texture to ``Lab`` items numbered ``N1`` through ``N2`` in steps of ``NINC`` (defaults to
            1). If ``Lab`` = CM, then N1 is used to for the component name and ``N2`` and ``NINC`` are
            ignored. If ``Lab`` = ELEM, AREA, or VOLU and ``N1`` = blank or ALL, then the specified texture
            will be applied to all entities of type ``Lab``. If ``N1`` = P, then graphical picking is
            enabled.

        n2 : str
            Apply texture to ``Lab`` items numbered ``N1`` through ``N2`` in steps of ``NINC`` (defaults to
            1). If ``Lab`` = CM, then N1 is used to for the component name and ``N2`` and ``NINC`` are
            ignored. If ``Lab`` = ELEM, AREA, or VOLU and ``N1`` = blank or ALL, then the specified texture
            will be applied to all entities of type ``Lab``. If ``N1`` = P, then graphical picking is
            enabled.

        ninc : str
            Apply texture to ``Lab`` items numbered ``N1`` through ``N2`` in steps of ``NINC`` (defaults to
            1). If ``Lab`` = CM, then N1 is used to for the component name and ``N2`` and ``NINC`` are
            ignored. If ``Lab`` = ELEM, AREA, or VOLU and ``N1`` = blank or ALL, then the specified texture
            will be applied to all entities of type ``Lab``. If ``N1`` = P, then graphical picking is
            enabled.

        Notes
        -----

        .. _s-TXTRE_notes:

        This command is available for 3D Open GL devices. 2D devices are supported **only** for the ``Lab``
        = File variation of the command, allowing imported bitmaps to be used for texturing and annotation.
        Textures can affect the speed of many of your display operations. You can increase the speed by
        temporarily turning the textures off ( Utility Menu> PlotCtrls> Style> Texturing(3D)> Display
        Texturing ). This menu selection toggles your textures on and off. When textures are toggled off,
        all of the
        texture information is retained and reapplied when texturing is toggled back on.

        For some displays, the texture will appear distorted because of a technique used to enhance 3D
        displays ( :ref:`dv3d`,TRIS,1). Disabling this function ( :ref:`dv3d`,TRIS,0) will improve the
        quality of some texture displays. Disabling the TRIS option of the :ref:`dv3d` command will slow
        down 3D displays significantly. Be sure to reapply the TRIS option after you obtain a satisfactory
        output.

        Specifying :ref:`txtre`,DEFA removes all texturing.
        """
        command = f"/TXTRE,{lab},{num},{n1},{n2},{ninc}"
        return self.run(command, **kwargs)

    def slashtype(self, wn: str = "", type_: str = "", **kwargs):
        r"""Defines the type of display.

        Mechanical APDL Command: `/TYPE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TYPE_sl.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        type_ : str
            Display type. Defaults to ZBUF for raster mode displays or BASIC for vector mode displays:

            * ``BASIC or 0`` - Basic display (no hidden or section operations).

            * ``SECT or 1`` - Section display (plane view). Use the :ref:`cplane` command to define the cutting plane.

            * ``HIDC or 2`` - Centroid hidden display (based on item centroid sort).

            * ``HIDD or 3`` - Face hidden display (based on face centroid sort).

            * ``HIDP or 4`` - Precise hidden display (like HIDD but with more precise checking). Because all facets are sorted,
              this mode can be extremely slow, especially for large models.

            * ``CAP or 5`` - Capped hidden display (same as combined SECT and HIDD with model in front of section plane removed).

            * ``ZBUF or 6`` - Z-buffered display (like HIDD but using software Z-buffering).

            * ``ZCAP or 7`` - Capped Z-buffered display (same as combined SECT and ZBUF with model in front of section plane
              removed).

            * ``ZQSL or 8`` - QSLICE Z-buffered display (same as SECT but the edge lines of the remaining 3D model are shown).

            * ``HQSL or 9`` - QSLICE precise hidden display (like ZQSL but using precise hidden).

        Notes
        -----

        .. _s-TYPE_notes:

        Defines the type of display, such as section display or hidden-line display. Use the :ref:`device`
        command to specify either raster or vector mode.

        The SECT, CAP, ZCAP, ZQSL, and HQSL options produce section displays. The section or "cutting" plane
        is specified on the :ref:`cplane` command as either normal to the viewing vector at the focus point
        (default), or as the working plane.

        When you use PowerGraphics, the section display options (Section, Slice, and Capped) use different
        averaging techniques for the interior and exterior results. Because of the different averaging
        schemes, anomalies may appear at the transition areas. In many cases, the automatically computed MIN
        and MAX values will differ from the full range of interior values. You can lessen the effect of
        these anomalies by issuing :ref:`avres`,,FULL ( Main Menu> General Post Proc> Options for Outp ).
        This command sets your legend's automatic contour interval range according to the minimum and
        maximum results found throughout the entire model.

        With PowerGraphics active ( :ref:`graphics`,POWER), the averaging scheme for surface data with
        interior element data included ( :ref:`avres`,,FULL) and multiple facets per edge ( :ref:`efacet`,2
        or :ref:`efacet`,4) will yield differing minimum and maximum contour values depending on the
        Z-Buffering options ( :ref:`slashtype`,,6 or :ref:`slashtype`,,7). When the Section data is not
        included in the averaging schemes ( :ref:`slashtype`,,7), the resulting absolute value for the
        midside node is significantly smaller.

        The HIDC, HIDD, HIDP, ZBUF, ZQSL, and HQSL options produce displays with "hidden" lines removed.
        Hidden lines are lines obscured from view by another element, area, etc. The choice of non-Z-
        buffered hidden-line procedure types is available only for raster mode ( :ref:`device` ) displays.
        For vector mode displays, all non-Z-buffered "hidden-line" options use the same procedure (which is
        slightly different from the raster procedures). Both geometry and postprocessing displays may be of
        the hidden-line type. Interior stress contour lines within solid elements can also be removed as
        hidden lines, leaving only the stress contour lines and element outlines on the visible surfaces.
        Midside nodes of elements are ignored on postprocessing displays. Overlapping elements will not be
        displayed.

        The ZBUF, ZCAP, and ZQSL options use a specific hidden-line technique called software Z-buffering.
        This technique allows a more accurate display of overlapping surfaces (common when using Boolean
        operations or :ref:`eshape` on element displays), and allows smooth shaded displays on all
        interactive graphics displays. Z-buffered displays can be performed faster than HIDP and CAP type
        displays for large models. See also the :ref:`light`, :ref:`shade`, and :ref:`gfile` commands for
        additional options when Z-buffering is used.

        This command is valid in any processor.
        """
        command = f"/TYPE,{wn},{type_}"
        return self.run(command, **kwargs)

    def trlcy(
        self,
        lab: str = "",
        tlevel: str = "",
        n1: str = "",
        n2: str = "",
        ninc: str = "",
        **kwargs,
    ):
        r"""Specifies the level of translucency.

        Mechanical APDL Command: `/TRLCY <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TRLCY.html>`_

        Parameters
        ----------
        lab : str
            Apply translucency level to the items specified by the following labels:

            * ``ELEM`` - Elements. Use ``N1``, ``N2``, ``NINC`` fields for element numbers.

            * ``AREA`` - Solid model areas. Use ``N1``, ``N2``, ``NINC`` fields for area numbers.

            * ``VOLU`` - Solid model volumes. Use ``N1``, ``N2``, ``NINC`` fields for volume numbers.

            * ``ISURF`` - Isosurfaces (surfaces of constant stress, etc., value). Translucency varies with result value, to a
              maximum of the specified translucency level.

            * ``CM`` - Component group. Use ``N1`` for component name, ignore ``N2`` and ``NINC``.

            * ``CURVE`` - Filled areas under curves of line graphs. Use ``N1``, ``N2``, ``NINC`` fields for curve numbers.

            * ``ZCAP`` - If :ref:`slashtype`, ``WN``,ZCAP is the current display type, then :ref:`trlcy`,ZCAP, ``TLEVEL``
              will display the model in window ``WN`` with the portion of the model in front of the section plane
              displayed at the translucency level ``TLEVEL``.

            * ``ON, OFF`` - Sets the specified translucency display on or off. All other fields are ignored.

        tlevel : str
            Translucency level: 0.0 (opaque) to 1.0 (transparent).

        n1 : str
            Used only with labels as noted above. Apply translucency level to ``Lab`` items numbered ``N1``
            to ``N2`` (defaults to ``N1`` ) in steps of ``NINC`` (defaults to 1). If ``N1`` is blank or ALL,
            apply specified translucency level to entire selected range. If ``Lab`` is CM, use component
            name for ``N1`` and ignore ``N2`` and ``NINC``. A value of ``N1`` = P allows you to graphically
            pick elements, areas, and volumes. You can then assign translucency levels to the entities via
            the picker. The ``Lab`` and ``TLEVEL`` fields are ignored when translucency is applied by
            picking.

        n2 : str
            Used only with labels as noted above. Apply translucency level to ``Lab`` items numbered ``N1``
            to ``N2`` (defaults to ``N1`` ) in steps of ``NINC`` (defaults to 1). If ``N1`` is blank or ALL,
            apply specified translucency level to entire selected range. If ``Lab`` is CM, use component
            name for ``N1`` and ignore ``N2`` and ``NINC``. A value of ``N1`` = P allows you to graphically
            pick elements, areas, and volumes. You can then assign translucency levels to the entities via
            the picker. The ``Lab`` and ``TLEVEL`` fields are ignored when translucency is applied by
            picking.

        ninc : str
            Used only with labels as noted above. Apply translucency level to ``Lab`` items numbered ``N1``
            to ``N2`` (defaults to ``N1`` ) in steps of ``NINC`` (defaults to 1). If ``N1`` is blank or ALL,
            apply specified translucency level to entire selected range. If ``Lab`` is CM, use component
            name for ``N1`` and ignore ``N2`` and ``NINC``. A value of ``N1`` = P allows you to graphically
            pick elements, areas, and volumes. You can then assign translucency levels to the entities via
            the picker. The ``Lab`` and ``TLEVEL`` fields are ignored when translucency is applied by
            picking.

        Notes
        -----

        .. _s-TRLCY_notes:

        Specifies the level of translucency for various items. Issue :ref:`trlcy`,DEFA to reset the default
        (0) translucency levels. This command is valid only on selected 2D and 3D graphics devices; see
        filename="Hlp_G_BAS11_3.html"? in the `Basic Analysis Guide
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_bas/Hlp_G_BAS19.html>`_ for more
        information on applying translucency.

        For 2D devices, the program displays only the visible faces of the items being displayed. The
        information behind the facing planes is not displayed. Issuing the :ref:`shrink` command will force
        the hardware to display information behind the translucent items.

        This command is valid in any processor.
        """
        command = f"/TRLCY,{lab},{tlevel},{n1},{n2},{ninc}"
        return self.run(command, **kwargs)

    def gmface(self, lab: str = "", n: str = "", **kwargs):
        r"""Specifies the facet representation used to form solid models.

        Mechanical APDL Command: `GMFACE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GMFACE.html>`_

        Parameters
        ----------
        lab : str
            Valid Labels:

            * ``FINE`` - Value that determines how coarse the facets will be.

        n : str
            An integer value between one (small) and ten (large) that determines the tolerances that will be
            applied to the creation of arcs and surfaces. Ten will create many facets, which may in turn
            cause Mechanical APDL to run very slowly. One will create fewer facets, which may in turn cause
            larger tolerance errors.
        """
        command = f"GMFACE,{lab},{n}"
        return self.run(command, **kwargs)

    def gmarker(self, curve: str = "", key: int | str = "", incr: str = "", **kwargs):
        r"""Specifies the curve marking style.

        Mechanical APDL Command: `/GMARKER <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GMARKER.html>`_

        Parameters
        ----------
        curve : str
            Curve number markers will be applied on (integer value between 1 and 10).

        key : int or str
            Marker key:

            * ``0`` - No markers will be applied (default).

            * ``1`` - TRIANGLES will be applied.

            * ``2`` - SQUARES will be applied.

            * ``3`` - DIAMONDS will be applied.

            * ``4`` - CROSSES will be applied.

        incr : str
            Determines the curve marking frequency. (a whole number value between 1 and 255). If ``INCR`` =
            1, markers are displayed at every data point on the curve. If ``INCR`` = 2 then markers are
            displayed at every second data point. If ``INCR`` = 3 then they are displayed at every third
            data point.

        Notes
        -----

        .. _s-GMARKER_notes:

        The user-specified markers will not be drawn when the area under the curve is color-filled (
        :ref:`gropt`, FILL).
        """
        command = f"/GMARKER,{curve},{key},{incr}"
        return self.run(command, **kwargs)

    def gline(self, wn: str = "", style: int | str = "", **kwargs):
        r"""Specifies the element outline style.

        Mechanical APDL Command: `/GLINE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GLINE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        style : int or str
            Outline key:

            * ``0`` - Solid element outlines (default)

            * ``1`` - Dashed element outlines

            * ``-1`` - No element outlines

        Notes
        -----

        .. _s-GLINE_notes:

        Determines the element outline style. Often used when node numbers are displayed to prevent element
        lin  es from overwriting node numbers.

        Unless you are using an OpenGL or Starbase driver, the dashed element outline option ( :ref:`gline`,
        ``WN``,1) is not available in the following situations:

        Z-buffered displays ( :ref:`slashtype`, ``WN``,6).
        Capped Z-buffered displays ( :ref:`slashtype`, ``WN``,7).
        Qslice Z-buffered displays ( :ref:`slashtype`, ``WN``,8).

        This command is valid in any processor.
        """
        command = f"/GLINE,{wn},{style}"
        return self.run(command, **kwargs)

    def shade(self, wn: str = "", type_: str = "", **kwargs):
        r"""Defines the type of surface shading used with Z-buffering.

        Mechanical APDL Command: `/SHADE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SHADE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        type_ : str
            Shading type:

            * ``FACET or 0`` - Facet shading (one color per area face).

            * ``GOURAUD or 1`` - Gouraud smooth shading (smooth variation of color based on interpolated vertex colors) (default).

            * ``PHONG or 2`` - Phong smooth shading (smooth variation of color based on interpolated vertex normals).

        Notes
        -----

        .. _s-SHADE_notes:

        Defines the type of surface shading used on area, volume, and PowerGraphics ( :ref:`graphics`,POWER)
        displays when software Z-buffering is enabled ( :ref:`slashtype` ). This command is only functional
        for 2D display devices.

        This command is valid in any processor.
        """
        command = f"/SHADE,{wn},{type_}"
        return self.run(command, **kwargs)
