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


class Labeling:

    def hbc(self, wn: str = "", key: str = "", **kwargs):
        r"""Determines how boundary condition symbols are displayed in a display window.

        Mechanical APDL Command: `/HBC <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_HBC.html>`_

        Parameters
        ----------
        wn : str
            Window reference number. This number can be any window numbered 1 to 5, or ALL (for all active
            windows). Default = 1.

        key : str
            Controls hidden-surface boundary condition display behavior:

            ON, YES or 1 = Enable - Your boundary condition symbols are processed by the hidden-surface
            algorithm (for 2D graphics devices) and use an improved pressure-contour display (for 2D and 3D
            graphics devices).

            OFF, NO or 0 (default) = Disable (default) - Your boundary condition symbols are not processed
            by the hidden-surface algorithm..

        Notes
        -----

        .. _s-HBC_notes:

        With :ref:`hbc`, ``WN``,ON in effect, Mechanical APDL does not display symbols obscured by the model
        in the
        current view (that is, symbols inside of or behind the model are not drawn). This behavior lessens
        display clutter.
        """
        command = f"/HBC,{wn},{key}"
        return self.run(command, **kwargs)

    def cformat(self, nfirst: str = "", nlast: str = "", **kwargs):
        r"""Controls the graphical display of alphanumeric character strings for parameters, components,
        assemblies, and tables.

        Mechanical APDL Command: `/CFORMAT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CFORMAT_sl.html>`_

        Parameters
        ----------
        nfirst : str
            Display the first ``n`` characters of the parameter, component, assembly, or table name, up to
            32. Defaults to 32.

        nlast : str
            Display the last ``n`` characters of the parameter, component, assembly, or table name, up to
            32. Defaults to 0.

        Notes
        -----

        .. _s-CFORMAT_notes:

        Use this command to control the length of the character string that is shown in the graphics window
        for a parameter, component, assembly, or table name.

        The total number of characters ( ``NFIRST`` + ``NLAST`` +3) cannot exceed 32.

        If ``NFIRST`` is greater than zero and ``NLAST`` = 0, only the ``NFIRST`` characters are displayed,
        followed by an ellipsis.

        If ``NFIRST`` = 0 and ``NLAST`` is greater than zero, only the ``NLAST`` characters are displayed,
        preceded by an ellipsis (...).

        If both ``NFIRST`` and ``NLAST`` are greater than zero, the name will be shown as ``NFIRST``,
        followed by an ellipsis (...), followed by ``NLAST``, up to a maximum of 32 characters.

        For example, if ``NFIRST`` = 6 and ``NLAST`` = 3, and the character string is LENGTHOFSIDEONE, then
        it will appear in the graphics window as LENGTH...ONE.

        If the actual length of the character string is less than the specified combination of ``NFIRST`` +
        ``NLAST`` +3, then the actual string will be used.

        This command is valid in any processor.
        """
        command = f"/CFORMAT,{nfirst},{nlast}"
        return self.run(command, **kwargs)

    def cval(
        self,
        wn: str = "",
        v1: str = "",
        v2: str = "",
        v3: str = "",
        v4: str = "",
        v5: str = "",
        v6: str = "",
        v7: str = "",
        v8: str = "",
        **kwargs,
    ):
        r"""Specifies nonuniform contour values on stress displays.

        Mechanical APDL Command: `/CVAL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CVAL.html>`_

        **Command default:**

        .. _s-CVAL_default:

        Nine contour values uniformly spaced between the extreme values.

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        v1 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v2 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v3 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v4 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v5 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v6 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v7 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        v8 : str
            Up to 8 contour values may be specified (in ascending order). The 0.0 value (if any) must not be
            the last value specified. If no values are specified, all contour specifications are erased and
            contours are automatically calculated.

        Notes
        -----

        .. _s-CVAL_notes:

        This command is similar to the :ref:`contour` command. With :ref:`cval`, however, you define the
        upper level of each contour band instead of having the contours uniformly distributed over the
        range. The minimum value (including a zero value for the first band) for a contour band cannot be
        specified. If you use both :ref:`contour` and :ref:`cval`, the last command issued takes precedence.

        This command is valid in any processor.
        """
        command = f"/CVAL,{wn},{v1},{v2},{v3},{v4},{v5},{v6},{v7},{v8}"
        return self.run(command, **kwargs)

    def contour(
        self,
        wn: str = "",
        ncont: str = "",
        vmin: str = "",
        vinc: str = "",
        vmax: str = "",
        **kwargs,
    ):
        r"""Specifies the uniform contour values on stress displays.

        Mechanical APDL Command: `/CONTOUR <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CONTOUR.html>`_

        **Command default:**

        .. _s-CONTOUR_default:

        Nine contour values uniformly spaced between the extreme values, or no contours if the ratio of
        range to minimum value (or range to maximum if minimum = 0) is less than 0.001.

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        ncont : str
            Number of contour values. ``NCONT`` defaults to 9 for X11 or WIN32 and to 128 for X11c or
            WIN32C. The default graphics window display for 3D devices is a smooth continuous shading effect
            that spans the maximum of 128 contours available. Use the :ref:`dv3d` command to create defined
            banding for your contour values (values of 9 and 128 are displayed in smooth shading only). The
            legend, however, will display only nine color boxes, which span the full range of colors
            displayed in the graphics window.

        vmin : str
            Minimum contour value. If ``VMIN`` = AUTO, automatically calculate contour values based upon
            ``NCONT`` uniformly spaced values over the min-max extreme range. Or, if ``VMIN`` = USER, set
            contour values to those of the last display (useful when last display automatically calculated
            contours).

        vinc : str
            Value increment (positive) between contour values. Defaults to ( ``VMAX`` - ``VMIN`` )
            ``/NCONT``.

        vmax : str
            Maximum contour value. Ignored if both ``VMIN`` and ``VINC`` are specified.

        Notes
        -----

        .. _s-CONTOUR_notes:

        Values represent contour lines in vector mode, and the algebraic maximum of contour bands in raster
        mode.

        Regardless of how many contours ( ``NCONT`` ) are specified, the actual number of contours appearing
        on your display depends also on the device name, whether the display is directed to the screen or to
        a file, the display mode (vector or raster), and the number of color planes. (All of those items are
        controlled via :ref:`show`.) In any case, regardless of whether they are smoothed or banded, only
        128 contours can be displayed.

        For more information about changing the number of contours, see `Creating Geometric Results Displays
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_bas/Hlp_G_BAS12_6.html>`_.

        When the current Mechanical APDL graphics are not displayed as Multi-Plots:

        If the current device is a 3D device ( :ref:`show`,3D), the model contours in all active windows are
        the same, even if separate :ref:`contour` commands are issued for each active window. Mechanical
        APDL
        maintains a single data structure (segment) containing one set of contours. The program displays the
        same segment in all windows. The view settings of each window constitute the only differences in the
        contour plots in the active windows.

        This command is valid in any processor.

        For alternate specifications, see :ref:`cval`.
        """
        command = f"/CONTOUR,{wn},{ncont},{vmin},{vinc},{vmax}"
        return self.run(command, **kwargs)

    def clabel(self, wn: str = "", key: int | str = "", **kwargs):
        r"""Specifies contour labeling.

        Mechanical APDL Command: `/CLABEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CLABEL.html>`_

        **Command default:**

        .. _s-CLABEL_default:

        Show contour line labels.

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        key : int or str
            Labeling key:

            * ``0 or 1`` - Label contours with legend or color (default).

            * ``-1`` - No contour labeling.

            * ``N`` - Same as 1 except show alphabetic legend only on every ``N`` th element.

        Notes
        -----

        .. _s-CLABEL_notes:

        Labels contours for identification with alphabetic legend for vector displays and color for raster
        displays. Number of contours is automatically reduced to 9 (or fewer) for clarity. Use
        :ref:`contour` command to increase (24 maximum for alphabetic labeling; no limit for color
        labeling).

        This command is valid in any processor.
        """
        command = f"/CLABEL,{wn},{key}"
        return self.run(command, **kwargs)

    def number(self, nkey: int | str = "", **kwargs):
        r"""Specifies whether numbers, colors, or both are used for displays.

        Mechanical APDL Command: `/NUMBER <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NUMBER.html>`_

        Parameters
        ----------
        nkey : int or str
            Numbering style:

            * ``0`` - Color (terminal dependent) the numbered items and show numbers.

            * ``1`` - Color the numbered items. Do not show the numbers.

            * ``2`` - Show the numbers. Do not color the items.

            * ``-1`` - Do not color the items or show the numbers. For contour plots, the resulting display will vary (see
              below).

        Notes
        -----

        .. _s-NUMBER_notes:

        Specifies whether numbers, colors, or both are used for numbering displays ( :ref:`pnum` ) of nodes,
        elements, keypoints, lines, areas, and volumes.

        Shading is also available for terminals configured with more than 4 color planes ( :ref:`show` ).
        Color automatically appears for certain items and may be manually controlled (off or on) for other
        items.

        When you suppress color ( ``NKEY`` = -1) your contour plots will produce different results,
        depending on your graphics equipment. For non-3D devices (X11, Win32, etc.) your contour plot will
        be white (no color). For 3D devices, such as OpenGL, the resulting display will be in color.

        The following items are automatically given discrete colors: Boundary condition symbols ( :ref:`pbc`
        ), curves on graph displays, and distorted geometry on postprocessing displays. Contour lines in
        postprocessing displays are automatically colored based upon a continuous, rather than a discrete,
        spectrum so that red is associated with the highest contour value. On terminals with raster
        capability ( :ref:`show` ), the area between contour lines is filled with the color of the higher
        contour.

        Explicit entity colors or the discrete color mapping may be changed with the :ref:`color` command.

        This command is valid in any processor.
        """
        command = f"/NUMBER,{nkey}"
        return self.run(command, **kwargs)

    def pbf(self, item: str = "", key: int | str = "", **kwargs):
        r"""Shows magnitude of body-force loads on displays.

        Mechanical APDL Command: `/PBF <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PBF.html>`_

        **Command default:**

        .. _s-PBF_default:

        No body-force load contours displayed.

        Parameters
        ----------
        item : str
            Label identifying the item:

            * ``TEMP`` - Applied temperatures.

            * ``FLUE`` - Applied fluences.

            * ``HGEN`` - Applied heat generation rates.

            * ``JS`` - Applied current density magnitude.

            * ``JSX`` - X-component of current density.

            * ``JSY`` - Y-component of current density.

            * ``JSZ`` - Z-component of current density.

            * ``PHASE`` - Phase angle of applied load.

            * ``MVDI`` - Applied magnetic virtual displacements flag.

            * ``CHRGD`` - Applied electric charge density.

        key : int or str
            Symbol key:

            * ``0`` - Do not show body-force load contours.

            * ``1`` - Show body-force load contours.

            * ``2`` - Show current density as a vector (not a contour).

        Notes
        -----

        .. _s-PBF_notes:

        Shows body-force loads as contours on displays for the selected elements.

        The effects of the **/PBF** command are not cumulative (that is, the command does not modify an
        existing setting from a
        previously issued **/PBF** command). If you issue multiple **/PBF** commands during an analysis,
        only the setting specified by the most recent :ref:`pbf` command applies.

        Use :ref:`pstatus` or :ref:`pbf`,STAT to display settings. Use :ref:`pbf`,DEFA to reset all
        specifications back to default. See also the :ref:`psf` and :ref:`pbc` command for other display
        contours.

        Portions of this command are not supported by PowerGraphics ( :ref:`graphics`,POWER).

        This command is valid in any processor.
        """
        command = f"/PBF,{item},,{key}"
        return self.run(command, **kwargs)

    def plopts(self, label: str = "", key: int | str = "", **kwargs):
        r"""Controls graphics options on subsequent displays.

        Mechanical APDL Command: `/PLOPTS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PLOPTS.html>`_

        **Command default:**

        .. _s-PLOPTS_default:

        See individual label defaults.

        The Multi-legend mode ( :ref:`plopts`,INFO,3) is the default for contour legend displays.

        Parameters
        ----------
        label : str
            Apply display items as selected from the following labels:

            * ``INFO`` - Controls the display of the legend (ON or OFF) and allows the choice of preset or Multi-legend
              placement. Control is provided by the ``KEY`` values. (Defaults to ``KEY`` =3 when the GUI is on.
              Defaults to ``KEY`` = 2 otherwise.)

            * ``LEG1`` - Header portion of legend column (defaults to ON).

            * ``LEG2`` - View portion of legend column (defaults to ON (except off with contour displays)).

            * ``LEG3`` - View the contour section of the legend column (defaults to ON).

            * ``FRAME`` - Frame border lines around windows (defaults to ON).

            * ``TITLE`` - Title (bottom left text) (defaults to ON).

            * ``MINM`` - Min-Max symbols on contour displays (defaults to ON).

            * ``LOGO`` - Ansys logo (defaults to OFF (displayed as text at top of legend column)). If ``KEY`` = ON,
              the text is removed from legend column but the logo symbol is displayed in whichever active window
              is either in the uppermost right corner and on top, or if there is no window in that location, then
              in the window to the furthest right of the screen. Version information remains in the legend column.

            * ``WINS`` - Controls whether graphics windows automatically stretch or shrink to adjust to screen size as the
              legend column is turned off or on ( :ref:`plopts`,INFO) (defaults to ON). If WINS is on and the
              legend column is changed from off to on, all windows are shrunk regardless of what their correct
              size is.

            * ``WP`` - Working plane (defaults to OFF). The working plane is drawn as part of the display ( not just an
              overlaid image as in :ref:`wpstyl` ). This option is best used in combination with a hidden-line
              technique ( :ref:`slashtype` ).

            * ``DATE`` - Controls the display of the date and time in your legend. Subsequent ``KEY`` values control the
              display as follows:

              0 â No date or time displays are included in your legend. 1 â Only the date is shown. 2 â Both
              the date and time are shown (default).

            * ``FILE`` - Controls the display of the Mechanical APDL jobname in your legend. Subsequent ``KEY`` values control the
              display as follows:

              0 â The Mechanical APDL jobname is not included in your legend (default). 1 â The Mechanical APDL jobname is
              included in your legend.

        key : int or str
            Switch:

            * ``OFF or 0`` - Do not apply this display item. For ``Label`` = DATE, no time or date are displayed.

            * ``ON or 1`` - Apply this display item. For ``Label`` = DATE, show only the date.

            * ``AUTO or 2`` - For ``Label`` = INFO, initiate Auto-legend mode. If the display has contours, the legend is ON; if
              the display has no contours, the legend is OFF. For ``Label`` = DATE, display both the date and
              time.

            * ``3`` - For ``Label`` = INFO, switch to Multi-legend mode. See the :ref:`udoc` command for the available
              legend configurations.

        Notes
        -----

        .. _s-PLOPTS_notes:

        Use :ref:`plopts`,STAT to display settings. Use :ref:`plopts`,DEFA to reset all specifications back
        to their defaults.

        When you perform multiple results displays, contours on the legend column may be truncated. To avoid
        this, specify :ref:`plopts`,LEG1,0.

        The Multi-legend mode provides a number of legend data item priority and placement options. These
        options are accessed via the GUI at Utility Menu> PlotCtrls> Window Controls> Window Options. The
        :ref:`udoc` command provides command line o  ptions for this capability.

        This command is valid in any processor.

        This command is not available for Academic Research or Teaching level products
        """
        command = f"/PLOPTS,{label},{key}"
        return self.run(command, **kwargs)

    def pbc(
        self,
        item: str = "",
        key: int | str = "",
        min: str = "",
        max: str = "",
        abs: str = "",
        **kwargs,
    ):
        r"""Shows boundary condition (BC) symbols and values on displays.

        Mechanical APDL Command: `/PBC <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PBC.html>`_

        **Command default:**

        .. _s-PBC_default:

        No symbols displayed.

        Parameters
        ----------
        item : str
            Label identifying the item:

            * ``U`` - Applied translational constraints (UX, UY, UZ).

            * ``ROT`` - Applied rotational constraints (ROTX, ROTY, ROTZ).

            * ``TEMP`` - Applied temperatures (TEMP, TBOT, TE2, TE3...., TTOP).

            * ``PRES`` - Applied fluid pressures.

            * ``V`` - Applied flow velocities (VX, VY, VZ).

            * ``VOLT`` - Applied voltages.

            * ``MAG`` - Applied scalar magnetic potentials.

            * ``A`` - Applied vector magnetic potentials.

            * ``CONC`` - Concentration.

            * ``CHRG`` - Applied electric charge.

            * ``F or FORC`` - Applied structural forces (FX, FY, FZ).

            * ``M or MOME`` - Applied structural moments (MX, MY, MZ).

            * ``HEAT`` - Applied heat flows (HEAT, HBOT, HE2, HE3...., HTOP).

            * ``FLOW`` - Applied fluid flow.

            * ``AMPS`` - Applied current flow.

            * ``FLUX`` - Applied magnetic flux.

            * ``CSG`` - Applied magnetic current segments.

            * ``RATE`` - Diffusion flow rate.

            * ``MAST`` - Master degrees of freedom.

            * ``CP`` - Coupled nodes.

            * ``CE`` - Nodes in constraint equations.

            * ``NFOR`` - POST1 nodal forces.

            * ``NMOM`` - POST1 nodal moments

            * ``RFOR`` - POST1 reaction forces.

            * ``RMOM`` - POST1 reaction moments (MX, MY, MZ).

            * ``PATH`` - Path geometry (undistorted) associated with the :ref:`path` command after a :ref:`pdef` or
              :ref:`pvect` command has been issued.

            * ``ACEL`` - Global acceleration (ACELX, ACELY, ACELZ vector).

            * ``OMEG`` - Global angular velocity (OMEGX, OMEGY, OMEGZ vector) and acceleration (DOMEGX, DOMEGY, DOMEGZ
              vector).

            * ``ALL`` - Represents all appropriate labels.

        key : int or str
            Symbol key:

            * ``0`` - Do not show symbol.

            * ``1`` - Show symbol.

            * ``2`` - Plot value next to symbol.

        min : str
            Minimum value in a range of values plotted on screen.

        max : str
            Maximum value in a range of values plotted on screen.

        abs : str
            Absolute number. If ``KEY`` = 2 and ``ABS`` = 0, a number falling between the ``MIN`` and
            ``MAX`` is displayed. If ``ABS`` is not specified, it defaults to 0. If ``KEY`` = 2 and ``ABS``
            = 1, an absolute value falling between the ``MIN`` and ``MAX`` is displayed. ``ABS`` = 1 lets
            you eliminate the display of numbers whose absolute values are less than a desired tolerance.
            For example, if ``ABS`` = 1, ``MIN`` = 10 and ``MAX`` = 1e8, values such as.83646 and -5.59737
            are not displayed.

        Notes
        -----

        .. _s-PBC_notes:

        The **/PBC** command adds degree of freedom constraint, force load, and other symbols to displays.

        Symbols are applied to the selected nodes only. All arrow and arrowhead symbols are oriented in the
        nodal coordinate system and lie in two perpendicular planes. Force arrows are scaled proportional to
        their magnitude. (If ``KEY`` = 1, use :ref:`vscale` to change arrow length.) For scalar quantities,
        the specific component direction (that is, x, y, or z) of the symbol has no meaning, but the
        positive or negative sense (for example, positive or negative x) represents a positive or negative
        scalar value, respectively.

        The effects of the **/PBC** command are not cumulative (that is, the command does not modify an
        existing setting from a
        previously issued **/PBC** command). If you issue multiple **/PBC** commands during an analysis,
        only the setting specified by the most recent :ref:`pbc` command applies.

        Use :ref:`pstatus` or :ref:`pbc`,STAT to display settings. Use :ref:`pbc`,DEFA to reset all
        specifications back to default. See the :ref:`psf` and :ref:`pbf` commands for other display
        symbols.

        In a `cyclic symmetry analysis
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cycsym/cycsym_example.html>`_, the
        :ref:`pbc` command is deactivated when `cyclic expansion
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cycsym/advcycmodalans.html#eqb90240e8-a774-4a6b-8243-74b9d8bf8886>`_
        is active ( :ref:`cycexpand`,,ON). To view boundary conditions on the `base sector
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cycsym/advcycbasesect.html#cycsym_modeling_mistuning>`_,
        deactivate cyclic expansion ( :ref:`cycexpand`,,OFF) and issue this command: :ref:`pbc`,ALL,,1


        Issuing the command :ref:`pbc`,PATH,,1 displays all defined paths.

        The :ref:`pbc` command is valid in any processor.
        """
        command = f"/PBC,{item},,{key},{min},{max},{abs}"
        return self.run(command, **kwargs)

    def psf(
        self,
        item: str = "",
        comp: str = "",
        key: int | str = "",
        kshell: int | str = "",
        color: str = "",
        **kwargs,
    ):
        r"""Shows surface load symbols on model displays.

        Mechanical APDL Command: `/PSF <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PSF.html>`_

        **Command default:**

        .. _s-PSF_default:

        No surface load symbols are displayed.

        Parameters
        ----------
        item : str
            Labels identifying the surface load to be shown; see.

        comp : str
            Labels identifying the surface load to be shown; see.

        key : int or str
            Key to turn surface load symbols on or off:

            * ``0`` - Off (default).

            * ``1`` - On, shown as face outlines. Line surface loads ( :ref:`sfl` ) on solid model plots are shown as
              arrows.

            * ``2`` - On, shown as arrows.

            * ``3`` - On, shown as color filled surfaces. Line and area surface loads ( :ref:`sfl` and :ref:`sfa` ) on
              solid model plots are shown as arrows.

        kshell : int or str
            Visibility key for shell elements.

            * ``0`` - Off (default), surface load symbols are displayed only on visible load faces.

            * ``1`` - On, surface load symbols are displayed even if load face is not visible.

        color : str
            Visibility key for contour legend.

            * ``ON`` - The symbols (arrows or face outlines) will show up in color with the legend showing the
              corresponding color labels (default).

            * ``OFF`` - The contour legend will not be displayed. The symbols (arrows or face outlines) will show up in
              grey. The size of the arrows will be proportional to the applied load.

        Notes
        -----

        .. _s-PSF_notes:

        :ref:`psf` determines whether and how to show surface loads on subsequent model displays.

        If surface loads are applied to solid model entities, only solid model plots show the load symbols;
        node and element plots do not show them unless the loads are transferred ( :ref:`sftran` or
        :ref:`sbctran` ). Similarly, solid model plots do not show the load symbols if surface loads are
        applied to nodes and elements. For node and element plots of shell element models, the surface load
        symbols are shown only if the load face is visible from the current viewing direction.

        The effects of the **/PSF** command are not cumulative (that is, the command does not modify an
        existing setting from a
        previously issued :ref:`psf` command). Only the setting specified via the most recent :ref:`psf`
        command applies.

        If you issue a `postprocessing (POST1)
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_CH2_7.html#cmdpost1failure>`_
        plot command that produces result contours (such as :ref:`plnsol` ), :ref:`psf` has no effect. This
        behavior prevents conflicting contours in the graphics window.

        When using the radiosity method ( ``Item`` = RDSF and ``Comp`` = ENCL) with ``Key`` = 2, the
        radiation arrows point outward from any element face.

        :ref:`psf`,STAT displays current :ref:`psf` settings, and :ref:`psf`,DEFA resets them back to
        default.

        Other useful commands are :ref:`pnum`,SVAL,1 to show the values of the surface loads, :ref:`vscale`
        to change arrow lengths, and :ref:`pbc` and :ref:`pbf` to activate other load symbols.

        For beam elements, only the colors representing shear (GREEN) and normal (RED) pressures are
        displayed for the arrows. The color of these arrows does not correspond to the magnitudes in the
        contour legend. The length of these arrows does, however, correlate to the relative magnitude of the
        pressures.

        For elements SURF159, SOLID272, SOLID273, PIPE288 and PIPE289, :ref:`psf` is not available when
        displaying elements with shapes determined from the real constants or section definition (
        :ref:`eshape` ). For PIPE288 and PIPE289, only external loads applied via :ref:`sfbeam` are
        displayed.

        This command is valid in any processor.

        **/PSF - Valid Item and Component Labels**

        .. flat-table::
           :header-rows: 1

           * - Item
             - Comp
             - Description
             - Comments
           * - :rspan:`14` PRES [ ]
             - NORM (or blank)
             - Applied pressure normal to the face (real component only).
             - For element types other than  SURF153, SURF154 and SURF156.
           * - NORM
             - Applied pressure normal to the face (real component).
             - :rspan:`5` For element types SURF153, SURF154 and SURF156 with KEYOPT(2) = 0. For `supported structural elements<https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SFCONTROL.html#>`_ with``KCSYS`` = 0. [ ]
           * - TANX
             - Applied pressure in the element tangential x direction (real component).
           * - TANY
             - Applied pressure in the element tangential- y direction (real component).
           * - INRM
             - Applied pressure normal to the face (imaginary component).
           * - ITNX
             - Applied pressure in the element tangential x direction (imaginary component).
           * - ITNY
             - Applied pressure in the element tangential y direction (imaginary component).
           * - LOCX
             - Applied pressure in the local x direction (real component).
             - :rspan:`5` For element types SURF153, SURF154 and SURF156 with KEYOPT(2) = 1. For `supported structural element`_ with``KCSYS`` = 1. [ ]
           * - LOCY
             - Applied pressure in the local y direction (real component).
           * - LOCZ
             - Applied pressure in the local z direction (real component).
           * - ILCX
             - Applied pressure in the local x direction (imaginary component).
           * - ILCY
             - Applied pressure in the local y direction (imaginary component).
           * - ILCZ
             - Applied pressure in the local z direction (imaginary component).
           * - RVEC
             - Applied pressure in the user-defined direction (real component).
             - :rspan:`1` For `supported structural element`_ with``KCSYS`` = 2. [ ]
           * - IVEC
             - Applied pressure in the user-defined direction (imaginary component).
           * - :rspan:`1` CONV
             - HCOEF
             - Applied convection (film coefficient).
             -
           * - TBULK
             - Applied convection (bulk temperature).
             -
           * - :rspan:`1` RAD
             - EMIS
             - Applied radiation (emissivity).
             -
           * - TAMB
             - Applied radiation (ambient temperature).
             -
           * - :rspan:`1` RDSF
             - EMSS
             - Radiation emissivity.
             -
           * - ENCL
             - Enclosure number.
             -
           * - FSIN
             -
             - Fluid-solid interface number.
             -
           * - HFLUX
             -
             - Applied heat flux.
             -
           * - FSI
             -
             - Acoustic fluid-structure interface flag.
             -
           * - IMPD
             -
             - Applied acoustic impedance.
             -
           * - :rspan:`1` SHLD
             - COND
             - Applied conductivity.
             -
           * - MUR
             - Applied relative permeability.
             -
           * - MXWF
             -
             - Maxwell force flag.
             -
           * - INF
             -
             - Exterior surface flag.
             -
           * - CHRGS
             -
             - Applied electric surface charge density.
             -
           * - BLI
             -
             - Boundary layer impedance flag.
             -

        Pressure loads apply to the element coordinate system (KEYOPT(2) = 0). Adjust appropriately for a
        local coordinate system (KEYOPT(2) = 1). See, and in the Element Reference.

        ``KCSYS`` is specified when issuing :ref:`sfcontrol`.
        """
        command = f"/PSF,{item},{comp},{key},{kshell},{color}"
        return self.run(command, **kwargs)

    def psymb(self, label: str = "", key: int | str = "", **kwargs):
        r"""Shows various symbols on displays.

        Mechanical APDL Command: `/PSYMB <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PSYMB.html>`_

        Parameters
        ----------
        label : str
            Show symbols as selected from the following labels:

            * ``CS`` - Local coordinate systems.

            * ``NDIR`` - Nodal coordinate systems (on rotated nodes only).

            * ``ESYS`` - Element coordinate systems (element displays only).

            * ``LDIR`` - Line directions (line displays only).

            * ``LDIV`` - Controls the display of element divisions on lines.

            * ``ADIR`` - Area direction symbol (for keypoint, line, area and volume plots).

            * ``LAYR`` - Layer orientations (relative to the projected element x-axis) or fiber orientations in smeared
              reinforcing elements. Used only within an element display. Use ``KEY`` to specify the layer number.

            * ``ECON`` - Element mesh symbols on keypoints and lines.

            * ``DOT`` - Larger symbols displayed for node and keypoint locations. When ``Label`` = DOT, ``KEY`` = 1 by
              default.

            * ``XNOD`` - Extra node of surface or circuit elements.

            * ``FBCS`` - Force boundary condition scaling. Subsequent ``KEY`` value determines whether or not to scale the
              applied and derived forces/moments to the same maximum value.

            * ``DEFA`` - Resets the symbol keys so that Mechanical APDL displays none of the symbols controlled by the :ref:`psymb`
              command. The value of the ``KEY`` field is ignored.

            * ``STAT`` - Prints the status of the settings of the symbol keys controlled by the :ref:`psymb` command. The
              ``KEY`` field is ignored.

            * ``MARK`` - Controls the marker size ( :ref:`gmarker` ). When ``Label`` = MARK, ``KEY`` = 10 by default.

        key : int or str
            Symbol key:

            * ``-1`` - Effective only if ``Label`` = LAYR and solid shape element display ( :ref:`eshape` ) is active.
              Orientation of all layers appears with the solid shape element display.

            * ``0`` - No symbol (default). If ``Label`` = LDIV, then ``KEY`` = 0 indicates that the displayed element
              divisions will correspond to the existing mesh (the word MESHED or EXISTING can also be
              substituted). Also, for ``Label`` = LDIV, if you execute any meshing command (such as :ref:`amesh`
              or :ref:`vmesh` ), ``KEY`` is set to 0 (MESHED) automatically. If ``Label`` = FBCS, then ``KEY`` = 0
              indicates that boundary condition scaling will not be common. The applied and derived forces/moments
              will be scaled to their respective maximum values.

            * ``1`` - Include symbol. If ``Label`` = LDIV, then ``KEY`` = 1 indicates that the displayed line divisions
              will correspond to the value assigned by :ref:`lesize` (the word LESIZE can also be substituted).
              Also, for ``Label`` = LDIV, if you execute the :ref:`lesize` command, ``KEY`` is set to 1 (LESIZE)
              automatically. If ``Label`` = FBCS, then ``KEY`` = 1 indicates that boundary condition scaling will
              be common. The applied and derived forces/moments will be scaled to the same maximum value.

            * ``N`` - If ``Label`` = LAYR, then ``N`` is equal to the layer number. If ``Label`` = DOT, then ``N`` can be
              equal to 0,1,.....15, indicating the dot size. If ``Label`` = MARK, then ``N`` can be equal to
              1,.....10, indicating the marker size. If

               ``Label`` = LDIV, then ``KEY`` = -1, indicates that no element divisions will be displayed (the
              word OFF can also be substituted).

        Notes
        -----

        .. _s-PSYMB_notes:

        Includes various symbols on the display. Triads are right-handed with x displayed as the longest
        leg. Where color is displayed, x is white, y is green, and z is blue. For beams, x is always along
        the length of the element. For lines, an arrow represents the direction of a line, from the
        beginning keypoint to the end keypoint. See :ref:`plopts` command for additional display options.
        Use :ref:`pstatus` or :ref:`psymb`,STAT to display settings. Use :ref:`psymb`,DEFA to reset all
        specifications back to their defaults. The command :ref:`psymb`,ECON,1 causes the symbol "M" to be
        displayed on keypoints and lines associated with meshed entities. When you issue the command
        :ref:`psymb`,DOT,1, a larger symbol is displayed for each node and keypoint location. Using
        :ref:`psymb`,MARK,1, a smaller marker size can be displayed.

        PowerGraphics ( :ref:`graphics`,POWER) does not support :ref:`psymb`,ESYS and :ref:`psymb`,LAYR.

        If ``KEY`` = ``N`` and PowerGraphics is off, the centroid of the surface elements is connected to
        the extra node using a gray line. However, if PowerGraphics is on, the color of the line connecting
        the centroid to the extra node is the same as that for the elements themselves (as determined by
        :ref:`pnum` ).

        When ``Label`` = LAYR, the layer systems can be visualized with all current-technology layered
        elements and the smeared reinforcing element REINF265. To use :ref:`psymb`,LAYR with REINF265, first
        set the vector-mode graphics option ( :ref:`device`,VECTOR,1).

        This command is valid in any processor.
        """
        command = f"/PSYMB,{label},{key}"
        return self.run(command, **kwargs)

    def pnum(self, label: str = "", key: int | str = "", **kwargs):
        r"""Controls entity numbering/coloring on plots.

        Mechanical APDL Command: `/PNUM <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PNUM.html>`_

        Parameters
        ----------
        label : str
            Type of numbering/coloring:

            * ``NODE`` - Node numbers on node and element plots.

            * ``ELEM`` - Element numbers and colors on element plots.

            * ``SEC`` - Section numbers and colors on element and solid model plots (see ).

            * ``MAT`` - Material set numbers and colors on element and solid model plots (see ).

            * ``TYPE`` - Element type reference numbers and colors on element and solid model plots (see ).

            * ``REAL`` - Real constant set numbers and colors on element and solid model plots (see ).

            * ``ESYS`` - Element coordinate system numbers on element and solid model plots (see ).

            * ``LOC`` - Location numbers/colors of the element in matrix assembly order on element plots.

              LOC and ELEM numbers will be the same unless the model has been reordered.

            * ``KP`` - Keypoint numbers on solid model plots.

            * ``LINE`` - Line numbers on solid model plots (both numbers and colors on line plots).

            * ``AREA`` - Area numbers on solid model plots (both numbers and colors on area plots).

            * ``VOLU`` - Volume numbers on solid model plots (both numbers and colors on volume plots).

            * ``SVAL`` - Stress (or any contour) values on postprocessing plots, and surface load values and colors on model
              plots when surface load symbols are on ( :ref:`psf` ). For tabular boundary conditions, the table-
              evaluated values will be displayed on node, element, or contour displays in POST1 when load symbols
              ( :ref:`pbf`, :ref:`psf`, :ref:`pbc` ) are on and TABNAM is OFF.

            * ``TABNAM`` - Table names for tabular boundary conditions. If this label is turned on, the table name appears next
              to the appropriate symbol, arrow, face outline, or contour as dictated by the :ref:`psf`,
              :ref:`pbc`, and :ref:`pbf` commands.

            * ``STAT`` - Shows current settings for :ref:`pnum`.

            * ``DEFA`` - Resets all :ref:`pnum` specifications back to default.

        key : int or str
            Switch:

            * ``0`` - Turns OFF numbers/colors for specified label.

            * ``1`` - Turns ON numbers/colors for specified label.

        Notes
        -----

        .. _s-PNUM_notes:

        This command specifies entity numbering and coloring for subsequent plots.

        The MAT, TYPE, REAL, and ESYS labels activate both the numbering and coloring of the corresponding
        attributes for :ref:`eplot`, :ref:`kplot`, :ref:`lplot`, :ref:`aplot`, and :ref:`vplot`. The ELEM,
        MAT, TYPE, REAL, ESYS, and LOC labels are mutually exclusive, that is, only one can be specified at
        a time. Also, turning on a LINE, AREA, or VOLU label will turn off the MAT, TYPE, and REAL labels.

        PowerGraphics ( :ref:`graphics`,POWER) displays for :ref:`pnum` can be problematic. :ref:`pnum`,ELEM
        will display erratically depending on other display command specifications, while :ref:`pnum`,LOC
        and :ref:`pnum`,ESYS are not supported.

        Element and volume numbers are not visible for 3D elements and volumes when Z-buffering is turned on
        ( :ref:`slashtype`,,[6,7, or 8]).

        Use :ref:`pstatus` or :ref:`pnum`,STAT to show settings. Use :ref:`pnum`,DEFA to reset all
        specifications back to default. Use the :ref:`number` command to control whether numbers and colors
        are displayed together.

        This command is valid in any processor
        """
        command = f"/PNUM,{label},{key}"
        return self.run(command, **kwargs)

    def triad(self, lab: str = "", **kwargs):
        r"""Shows the global XYZ coordinate triad on displays.

        Mechanical APDL Command: `/TRIAD <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TRIAD.html>`_

        Parameters
        ----------
        lab : str
            Display triad as follows:

            * ``ORIG`` - Display triad at global origin (default).

            * ``OFF`` - Turn off triad display.

            * ``LBOT`` - Display triad in lower left screen corner.

            * ``RBOT`` - Display triad in lower right screen corner.

            * ``LTOP`` - Display triad in upper left screen corner.

            * ``RTOP`` - Display triad in upper right screen corner.

        Notes
        -----

        .. _s-TRIAD_notes:

        For efficiency, Mechanical APDL maintains a single data structure (segment) which includes the triad
        as a
        3D data object.

        If a 3D device is involved ( :ref:`show`,3D) and the graphics are not being displayed as multi-
        plots, the triad location is determined by the view settings for window #1.

        A request for triad display anywhere except for the origin may yield an improper display in windows
        2 through 5.

        The program displays the same segment in all windows. The view settings of each window constitute
        the only difference in the display in the active windows.

        This command is valid in any processor.
        """
        command = f"/TRIAD,{lab}"
        return self.run(command, **kwargs)

    def udoc(self, wind: str = "", class_: str = "", key: str = "", **kwargs):
        r"""Determines position and content for the multi-legend options.

        Mechanical APDL Command: `/UDOC <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UDOC_sl.html>`_

        Parameters
        ----------
        wind : str
            The window number to which the command applies. (defaults to 1)

        class_ : str
            The type (and relative importance) of legend item being displayed:

            * ``CNTR`` - Contour legend. This legend item is controlled separately from the other legend items (see note
              below).

            * ``DATE`` - The items in the DATE class include the date and time, or the Mechanical APDL graphical logo (
              :ref:`plopts`,LOGO,1). This item is shown by default in all plots.

            * ``GWIN`` - The items in the GWIN class include the entity acronyms that appear in the legend of a multiplot of
              entities (Nodes, Elements, Keypoints, Lines, Areas, Volumes). GWIN items are shown by default for
              all :ref:`gplot` displays.

            * ``TYPE`` - Items in the TYPE class include the plot type (e.g. ELEMENTS, MATERIALS, NODAL SOLUTIONS, etc.).
              TYPE items are shown by default in all plots.

            * ``TYP2`` - Items in the TYP2 class include supplementary type information, such as DMAX and SMAX for nodal
              solutions. TYP2 items are shown by default in all plots.

            * ``INUM`` - Items in the INUM class include the number labels generated by the :ref:`pnum` command. This class
              is displayed by default in all plots that contain :ref:`pnum` information.

            * ``BCDC`` - The items in the BCDC class include labels created by the :ref:`pbc` command. This class is shown by
              default in all plots which contain :ref:`pbc` information.

            * ``VECT`` - Items in the VECT class include labels created by the :ref:`plvect` command. This class is shown by
              default for all :ref:`plvect` plots.

            * ``SURF`` - The items in the SURF class include labels from the :ref:`psf` legend. This class is shown by
              default on all plots of surface boundary conditions.

            * ``BODY`` - Items from the BODY class include labels from the :ref:`pbf` legend. This class is shown by default
              in all plots of body forces.

            * ``PSTA`` - Items from the PSTA class include stress scaling statistics, such as the :ref:`sscale` setting. This
              class is not shown as the default for any type of plot, and must be specifically referenced to
              display the included data.

            * ``VIEW`` - The items in the VIEW class include view statistics. This class is not shown as the default for any
              type of plot, and must be specifically referenced to display the included data.

            * ``MISC`` - The items in the MISC class include supplementary labels like /EXPANDED and Stress Section Cross
              Section. This class is not shown as the default for any type of plot, and must be specifically
              referenced to display the included data.

        key : str
            Switch:

            InformalTables need to be added.

        Notes
        -----

        .. _s-UDOC_notes:

        The legend classes conform to the controls specified in the window options panel ( PlotCtrls> Window
        Controls> Window Options ). In many instances, the legend controls specified with the :ref:`plopts`
        command will take precedence and override :ref:`udoc` specifications. For instance:

        :ref:`plopts`,LEG1,OFF will disable the TYPE, TYP2, INUM, and MISC classes, regardless of the
        :ref:`udoc` settings.

        :ref:`plopts`,LEG2,OFF will disable the VIEW class, regardless of the :ref:`udoc` settings.

        :ref:`plopts`,LEG3,OFF will disable the PSTA class, regardless of the :ref:`udoc` settings.

        All items in a class are listed with the same X coordinate (except for contours). The contents of
        the text classes are dumped onto the display window from top to bottom, in order of class
        importance.

        The font specification for text items that are included in the user-specified legends are controlled
        with the :ref:`device` command ( PlotCtrls> Font Controls> Anno/Graph Font ).

        The floating point values for the data presented in the legend(s) are controlled by the
        :ref:`gformat` command.
        """
        command = f"/UDOC,{wind},{class_},{key}"
        return self.run(command, **kwargs)

    def gformat(self, ftype: str = "", nwidth: str = "", dsignf: str = "", **kwargs):
        r"""Specifies the format for the graphical display of numbers.

        Mechanical APDL Command: `/GFORMAT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GFORMAT.html>`_

        Parameters
        ----------
        ftype : str
            FORTRAN format types (G is the default if this field is left blank.)

            * ``G`` - G ``xx``. ``yy``. ``xx`` and ``yy`` are described below.

            * ``F`` - F ``xx``. ``yy``

            * ``E`` - E ``xx``. ``yy``

        nwidth : str
            Total width (12 maximum) of the field (the ``xx`` in ``Ftype`` ). Defaults to 12.

        dsignf : str
            Number of digits after the decimal point ( ``yy`` in F or E format) or number of significant
            digits in G format. Range is 1 to ``xx`` -6 for ``Ftype`` = G or E; and 0 to ``xx`` -3 for
            ``Ftype`` = F. The default is a function of ``Ftype`` and ``NWIDTH``.

        Notes
        -----

        .. _s-GFORMAT_notes:

        Enables you to control the format of the graphical display of floating point numbers.

        To display the current settings, issue :ref:`gformat`,STAT..

        To allow Mechanical APDL to select the format for the graphical display of floating numbers, issue
        :ref:`gformat`,DEFA.

        This command is valid in any processor.
        """
        command = f"/GFORMAT,{ftype},{nwidth},{dsignf}"
        return self.run(command, **kwargs)
