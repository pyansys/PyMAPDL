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


class SetUp:

    def immed(self, key: int | str = "", **kwargs):
        r"""Allows immediate display of a model as it is generated.

        Mechanical APDL Command: `IMMED <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_IMMED.html>`_

        Parameters
        ----------
        key : int or str
            Immediate mode key:

            * ``0`` - Display only upon request, that is, no immediate display (default with the GUI off ).

            * ``1`` - Display immediately as model is generated (default with the GUI on ).

        Notes
        -----

        .. _IMMED_notes:

        The command enables you to control whether or not the model is displayed immediately as it is
        generated in an interactive session. Available only during an interactive session at a graphics
        display terminal. A valid graphics device name must first be specified ( :ref:`show` ).

        By default in the GUI, your model is immediately displayed in the Graphics window as you create new
        entities (such as areas, keypoints, nodes, elements, local coordinate systems, boundary conditions,
        etc.), referred to as immediate mode graphics.

        Symbols (such as boundary conditions, local coordinate system triads, etc.) appear immediately and
        are present on subsequent displays unless you disable the appropriate symbol (via the GUI plot
        controls function or the appropriate graphics-specification command).

        An immediate image is also scaled automatically to fit within the Graphics window. The new scaling
        is usually apparent on the automatic replot associated with immediate mode. To suppress automatic
        replot, issue :ref:`uis`,REPLOT,0. (With automatic replot suppressed, the immediate image may not
        always be scaled correctly.)

        An immediate display in progress should not be aborted with the usual system "break" feature (or
        else the Mechanical APDL session itself terminates). When you run Mechanical APDL interactively
        without using the
        GUI, immediate mode is off by default.

        This command is valid only in PREP7.
        """
        command = f"IMMED,{key}"
        return self.run(command, **kwargs)

    def image(self, label: str = "", fname: str = "", ext: str = "", **kwargs):
        r"""Allows graphics data to be captured and saved.

        Mechanical APDL Command: `/IMAGE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_IMAGE.html>`_

        Parameters
        ----------
        label : str
            Label specifying the operation to be performed:

            * ``CAPTURE`` - Capture the image from the graphics window to a new window.

            * ``RESTORE`` - Restore the image from a file to a new window.

            * ``SAVE`` - Save the contents of the graphic window to a file.

            * ``DELETE`` - Delete the window that contains the file.

        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name.

        ext : str
            Filename extension (eight-character maximum). If no extension is specified, :file:`bmp` will be
            used on Windows systems, and :file:`img` will be used on Linux systems.
        """
        command = f"/IMAGE,{label},{fname},{ext}"
        return self.run(command, **kwargs)

    def dv3d(self, lab: str = "", key: int | str = "", **kwargs):
        r"""Sets 3D device option modes.

        Mechanical APDL Command: `/DV3D <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_DV3D.html>`_

        Parameters
        ----------
        lab : str
            Mode label:

            * ``ACCU`` - Activating the accumulation buffer for OpenGL graphics, providing faster model rotation when shaded
              backgrounds are in use. This feature is off by default.

            * ``ACTR`` - Label term to designate the cursor position as the center for automatic dynamic rotational center
              capability. The subsequent ``Key`` value (see below) turns this capability on and off. This feature
              is on by default. (Available for OpenGL displays only.)

            * ``ANIM`` - Animation mode. The ANIM option allows you to create animation frames in pixmap mode instead of
              display list mode. This may improve large model performance, but it eliminates local manipulation
              while animation is in progress. This feature is on by default.

            * ``ANTI`` - Label term to control Anti-aliasing, a smoothing technique for your graph plots. (see below) The
              subsequent ``Key`` value turns this capability on and off. The default for this feature is off.
              (Available for OpenGL displays only).

            * ``CNTR`` - Switches banded contours on (1) or off (0) for your 3D contour display. The default is 1 (ON). Other
              contour parameters such as number of contours or the increment and range are defined using the
              :ref:`contour` command. When either 9 or 128 contours are specified via :ref:`contour`, this command
              is ignored and a smooth contour is always displayed.

            * ``DGEN`` - Local manipulation degenerate mode. You access the DGEN option to set wire-frame local manipulation
              mode for 3D devices (device dependent). This feature is off by default.

            * ``DLIST`` - With DLIST, you can specify whether screen updates and redraws will be performed using the Mechanical APDL
              display list (off), or the 3D device's display list (on). DLIST is on by default for Windows
              systems, but off for Linux.

            * ``DELS`` - You use DELS to suppress contour display screen overwrites when :ref:`noerase` is active. This
              prevents the bleed-through that occurs when you overlay contour plots.

            * ``TRIS`` - Triangle strip mode. Tri-stripping provides faster 3D display capabilities and is on by default.
              Some display enhancements, such as texturing, are adversely affected by tri-stripping. You can turn
              off tri-stripping in order to improve these display functions. Be sure to turn tri-stripping on
              after the desired output is obtained.

        key : int or str
            The following key options apply to ``Lab`` = ACCU:

            * ``0`` - (OFF) The accumulation buffer is not accessed. (default)

            * ``1`` - (ON) Access to the buffer is enabled.

            The following key options apply to ``Lab`` = ACTR:

            * ``0`` - (OFF) The cursor position has no effect on the existing rotational center for dynamic operations.

            * ``1`` - (ON) The rotational center for dynamic rotations in OpenGL is determined by the position of the
              mouse cursor on (or within 15 pixels of) the model. Any rotations that are initiated with the cursor
              more than 15 pixels from the model will occur about the midpoint of the Z-axis at that point in
              space. If the Z-buffer has not been refreshed the Z-axis will have an infinite value, and rotations
              will appear to occur about an extremely long Z-axis. This behavior stops when the graphics window is
              refreshed or replotted. (default)

              Note that when using the GUI in 3D mode, when ACTR = 1, the ``Rotational Center`` option is grayed
              out under Utility Menu> PlotCtrls> View Setting because the rotational center is determined strictly
              by the position of the mouse cursor.

            The following key options apply to ``Lab`` = ANIM:

            * ``0`` - Display list animation. The object can be dynamically manipulated while animating. No legend,
              countour or annotation items are displayed. (see Notes, below)

            * ``1`` - On Linux, device-dependent pixmap animation is used. On the PC, bitmap animation is provided
              (default). When you animate in this mode, you cannot dynamically manipulate your model (see Notes,
              below).

            * ``2`` - On the PC only, this option provides AVI animation which uses the AVI movie player.

              Although you can create animations of multiple Mechanical APDL window schemes, animations created with
              OpenGL display lists ( :ref:`dv3d`, ANIM, 0) do not retain the windowing scheme information. You CAN
              save multiple windows via the X11/WIN32 drivers, or via the OpenGL driver with :ref:`dv3d`, ANIM,
              KEY in effect (where KEY is not zero).

            The following key options apply to ``Lab`` = ANTI

            * ``0`` - (OFF) Anti-aliasing is not active (default).

            * ``1`` - (ON) The anti-aliasing technique will be applied to smooth the lines in your displays (valid for
              OpenGL only).

            The following key options apply to ``Lab`` = DGEN:

            * ``0`` - Normal manipulation.

            * ``1`` - Wireframe Manipulation.

            The following key options apply to ``Lab`` = DLIST:

            * ``0`` - (OFF) The Mechanical APDL display list is used for plotting and dynamic graphics manipulation (Linux
              default).

            * ``1`` - (ON) The local (3D device) display list is used for plotting and dynamic rotation (Windows default).

            The following key options apply to ``Lab`` = TRIS:

            * ``0`` - (OFF) Tri-stripping is off.

            * ``1`` - (ON) Tri-stripping is on (default).

        Notes
        -----
        Mechanical APDL uses display list animation for its 3D models. This memory resident array method
        interfaces
        with the OpenGL model information to allow the program to efficiently pan, zoom, rotate and
        dynamically manipulate your model during animation. The logo, legend, contour and other annotation
        items are produced in 2D and will not appear when :ref:`dv3d`, ANIM, 0 is in effect. To display
        these items, use :ref:`dv3d`, ANIM, 1. All screen data will be displayed, but manipulation of the
        model will not be possible.
        """
        command = f"/DV3D,{lab},{key}"
        return self.run(command, **kwargs)

    def device(self, label: str = "", key: int | str = "", **kwargs):
        r"""Controls graphics device options.

        Mechanical APDL Command: `/DEVICE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_DEVICE.html>`_

        **Command default:**

        .. _s-DEVICE_default:

        Vector mode off (that is, raster mode); dithering on.

        Parameters
        ----------
        label : str
            Device function label:

            * ``BBOX`` - Bounding box mode. For PowerGraphics plots involving elements with :ref:`show`,x11 and
              :ref:`show`,win32, Mechanical APDL generally displays dynamic rotations faster. If KEY = 1 (ON), then a
              bounding box (not the elements) encompassing the model is displayed and rotated, rather than the
              element outlines (ON is default in preprocessing). When KEY = 0 (OFF), then dynamic rotations may be
              slower (Mechanical APDL redraws the element outlines) for plots involving elements with :ref:`show`,x11 and
              :ref:`show`,win32. OFF is default in postprocessing. This command is ignored if :ref:`edge`,WN,1 is
              set for any WN. This is ignored in POST1 and SOLUTION plots.

              For any PowerGraphics plots involving elements, regardless of :ref:`show` settings, plots will
              generally be displayed faster.

            * ``VECTOR`` - Vector mode. In vector mode, areas, volumes, elements, and postprocessing display geometries are
              shown as outlines (wireframes). When vector mode is off (default), these entities are shown filled
              with color.

            * ``DITHER`` - When dithering is turned on (default), color intensity transitions are smoothed. This selection a

              applies only to smooth-shaded images, that is, Z-buffered ( :ref:`slashtype` ), or raster plots with
              Gouraud or Phong shading ( :ref:`shade` ).

            * ``ANIM`` - Select the animation type used on 2D devices on the PC platform. A ``KEY`` value of BMP (or 0) sets
              animation mode to the Mechanical APDL animation controller (default). A ``KEY`` value of AVI (or 2) sets
              animation mode to AVI movie player file.

            * ``FONT`` - Font selection for the Mechanical APDL graphics window. When ``Label`` = FONT, the command format is:
              :ref:`device`,FONT, ``KEY``, ``Val1``, ``Val2``, ``Val3``, ``Val4``, ``Val5``, ``Val6`` where
              ``KEY`` determines the type of font being controlled, and values 1 through 6 control various font
              parameters. These values are device specific; using the same command input file ( :ref:`input` ) on
              different machines may yield different results.. The following ``KEY`` values determine the font
              information that will be supplied to the appropriate driver (for example, Postscript, X11, Win32,
              JPEG....):

              * ``KEY = 1`` - The command controls the LEGEND (documentation column) font.

              * ``KEY = 2`` - The command controls the ENTITY (node and keypoint number) font.

              * ``KEY = 3`` - The command controls the ANNOTATION/GRAPH font.

              Linux: Values 1 through 4 are used to find a match in the X11 database of font strings. Values 1, 2, and 3
              are character strings; value 4 is a nonzero integer:

              * ``Val1`` - Family name (for example, Courier). If ``Val1`` = MENU, all other values are ignored and a font
                selection menu appears (GUI must be active).

              * ``Val2`` - Weight (for example, medium)

              * ``Val3`` - Slant (for example, r)

              * ``Val4`` - Pixel size (for example, 14). Note that this value does no affect the annotation fonts ( ``KEY`` =
                3). Use the :ref:`tspec` command for annotation font size.

              * ``Val5`` - unused

              * ``Val6`` - unused

              PC: The values are encoded in a PC logical font structure. Value 1 is a character string, and the
              remaining values are integers:

              * ``Val1`` - Family name (for example, Courier\2New) Substitute an asterisk (\2) for any blank character that
                appears in a family name. If ``Val1`` = MENU, all other values are ignored and a font selection menu
                appears (GUI must be active). When this value is blank, Mechanical APDL uses the first available resource
                it finds.

              * ``Val2`` - Weight (0 - 1000)

              * ``Val3`` - Orientation (in tenths of a degree)

              * ``Val4`` - Height (in logical units)

              * ``Val5`` - Width (in logical units)

              * ``Val6`` - Italics (0 = OFF, 1 = ON)

            * ``TEXT`` - Text size specification for the Mechanical APDL graphics window. Using this label with the :ref:`device`
              command requires the following form: :ref:`device`,TEXT, ``KEY``, ``PERCENT``. ``KEY`` = 1 for
              LEGEND fonts; ``KEY`` = 2 for ENTITY fonts. ``PERCENT`` specifies the new text size as a percent of
              the default text size. If ``PERCENT`` = 100, the new text size is precisely the default size. If
              ``PERCENT`` = 200, the new text size is twice the default text size.

        key : int or str
            Control key:

            * ``OFF or 0`` - Turns specified function off.

            * ``ON or 1`` - Turns specified function on or designates the LEGEND font.

            * ``2`` - Designates the ENTITY font.

            * ``3`` - Designates the ANNOTATION/GRAPH font.

        Notes
        -----

        .. _s-DEVICE_notes:

        This command is valid in any processor.

        The :ref:`device`,BBOX command is ignored in POST1 and SOLUTION plots. Also, the elements are
        displayed and rotated if you use :ref:`device`,BBOX,ON and :ref:`edge`,WN,1,ANGLE (effectively
        ignoring the BBOX option).
        """
        command = f"/DEVICE,{label},{key}"
        return self.run(command, **kwargs)

    def dsys(self, kcn: str = "", **kwargs):
        r"""Activates a display coordinate system for geometry listings and plots.

        Mechanical APDL Command: `DSYS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_DSYS.html>`_

        **Command default:**

        .. _DSYS_default:

        Global Cartesian ( ``KCN`` = 0) display coordinate system.

        Parameters
        ----------
        kcn : str
            Coordinate system reference number. ``KCN`` may be 0,1,2 or any previously defined local
            coordinate system number. If a cylinder is displayed in its cylindrical coordinate system (with
            a 1,0,0 view), it will be unrolled (developed) into a flat plane (with theta along the Y
            direction).

        Notes
        -----

        .. _DSYS_notes:

        Boundary condition symbols, vector arrows, and element coordinate system triads are not transformed
        to the display coordinate system. The display system orientation (for the default view) is X
        horizontal to the right, Y vertical upward, and Z out of the screen (normal).

        Line directions and area directions ( :ref:`psymb`,LDIR and :ref:`psymb`,ADIR) are not plotted for
        ``KCN`` >0.

        When you create 3D annotation, the coordinates are stored to the database in the display coordinate
        system that was active at the time of creation. Changing the display coordinate system does not
        change the annotation coordinate data in the database.

        This command is valid in any processor.
        """
        command = f"DSYS,{kcn}"
        return self.run(command, **kwargs)

    def color(
        self,
        lab: str = "",
        clab: str = "",
        n1: str = "",
        n2: str = "",
        ninc: str = "",
        **kwargs,
    ):
        r"""Specifies the color mapping for various items.

        Mechanical APDL Command: `/COLOR <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_COLOR.html>`_

        **Command default:**

        .. _s-COLOR_default:

        Use the default color mapping.

        Parameters
        ----------
        lab : str
            Apply color to the items specified by the following labels:

            * ``AXES`` - Determines the color (specified in next argument, ``Clab`` ) that the axes of a graph will be
              plotted in.

            * ``AXNUM`` - Determines the color (specified in next argument, ``Clab`` ) that the numbering on the axes of a
              graph will be plotted in.

            * ``NUM`` - Discretely numbered items (such as element types, element materials, etc., as shown on the
              :ref:`pnum` command). Also specify number (1 to 11) in the ``N1`` field. For example,
              :ref:`color`,NUM,RED,3 will assign the color red to all items having the discrete number 3 (material
              displays would show elements having material 3 as red).

            * ``OUTL`` - Outline of elements, areas, and volumes. Ex: :ref:`color`,OUTL,BLUE.

            * ``ELEM`` - Elements. Use ``N1``, ``N2``, ``NINC`` fields for element numbers.

            * ``LINE`` - Solid model lines. Use ``N1``, ``N2``, ``NINC`` fields for line numbers.

            * ``AREA`` - Solid model areas. Use ``N1``, ``N2``, ``NINC`` fields for area numbers.

            * ``VOLU`` - Solid model volumes. Use ``N1``, ``N2``, ``NINC`` fields for volume numbers.

            * ``ISURF`` - Isosurfaces (surfaces of constant stress, etc.). This option is particularly useful when capturing
              frames for animating a single isosurface value.

            * ``WBAK`` - Window background. Use ``N1``, ``N2``, ``NINC`` fields for window numbers. The options that you
              select using ``Lab`` = PBAK will supersede those applied using ``Lab`` = WBAK.

            * ``b.c.label`` - Boundary condition label. Enter U, ROT, TEMP, PRES, V, VOLT, MAG, A, EMF, CURR, F, M, HEAT, FLOW,
              VF, AMPS, FLUX, CSG, CURT, MAST, CP, CE, NFOR, NMOM, RFOR, RMOM, PATH. See the :ref:`pbc` command
              for boundary condition label definitions.

            * ``GRBAK`` - Graph background.

            * ``GRID`` - Graph grid lines.

            * ``AXLAB`` - Graph X and Y axis labels.

            * ``CURVE`` - Graph curves (identify curve numbers (1-10) in ``N1``, ``N2``, ``NINC`` fields).

            * ``CM`` - Component group. Use ``N1`` field for component name, ignore ``N2`` and ``NINC``.

            * ``CNTR`` - Mechanical APDL contour stress colors. The maximum number of contours available is 128. The number of
              colors that can be specified interactively (GUI) is 9. ( :ref:`contour`, 9). Any other setting will
              yield inconsistent results.

            * ``SMAX`` - Specifies that all stress values above the maximum value entered in :ref:`contour` will be displayed
              in the color designated in the ``Clab`` field. Defaults to dark grey.

            * ``SMIN`` - Specifies that all stress values below the minimum value entered in :ref:`contour` will be displayed
              in the color designated in the ``Clab`` field. Defaults to dark grey.

            * ``PBAK`` - Activates background shading options (see command syntax at end of argument descriptions below). The
              options that you select using ``Lab`` = PBAK will supersede those applied using ``Lab`` = WBAK.

        clab : str
            Valid color labels are:

            * ``BLAC (0)`` - Black

            * ``MRED (1)`` - Magenta-Red

            * ``MAGE (2)`` - Magenta

            * ``BMAG (3)`` - Blue-Magenta

            * ``BLUE (4)`` - Blue

            * ``CBLU (5)`` - Cyan-Blue

            * ``CYAN (6)`` - Cyan

            * ``GCYA ((7)`` - Green-Cyan

            * ``GREE (8)`` - Green

            * ``YGRE (9)`` - Yellow-Green

            * ``YELL (10)`` - Yellow

            * ``ORAN (11)`` - Orange

            * ``RED (12)`` - Red

            * ``DGRA (13)`` - Dark Gray

            * ``LGRA (14)`` - Light Gray

            * ``WHIT (15)`` - White

        n1 : str
            Apply color to ``Lab`` items numbered ``N1`` to ``N2`` (defaults to ``N1`` ) in steps of
            ``NINC`` (defaults to 1). If ``N1`` is blank, apply color to entire selected range. If ``Lab``
            is CM, use component name for ``N1`` and ignore ``N2`` and ``NINC``. If ``N1`` = P, graphical
            picking of elements, lines, areas and volumes is enabled; your can assign colors to the entities
            via the picker. When picking is enabled, the ``Lab`` and ``Clab`` fields are ignored.

        n2 : str
            Apply color to ``Lab`` items numbered ``N1`` to ``N2`` (defaults to ``N1`` ) in steps of
            ``NINC`` (defaults to 1). If ``N1`` is blank, apply color to entire selected range. If ``Lab``
            is CM, use component name for ``N1`` and ignore ``N2`` and ``NINC``. If ``N1`` = P, graphical
            picking of elements, lines, areas and volumes is enabled; your can assign colors to the entities
            via the picker. When picking is enabled, the ``Lab`` and ``Clab`` fields are ignored.

        ninc : str
            Apply color to ``Lab`` items numbered ``N1`` to ``N2`` (defaults to ``N1`` ) in steps of
            ``NINC`` (defaults to 1). If ``N1`` is blank, apply color to entire selected range. If ``Lab``
            is CM, use component name for ``N1`` and ignore ``N2`` and ``NINC``. If ``N1`` = P, graphical
            picking of elements, lines, areas and volumes is enabled; your can assign colors to the entities
            via the picker. When picking is enabled, the ``Lab`` and ``Clab`` fields are ignored.

        Notes
        -----

        .. _s-COLOR_notes:

        Issue :ref:`color`,STAT to display the current color mapping. Issue :ref:`color`,DEFA to reset the
        default color mapping. Color labels may also be reassigned any "color" with the :ref:`cmap` command.

        This command is valid anywhere.
        """
        command = f"/COLOR,{lab},{clab},{n1},{n2},{ninc}"
        return self.run(command, **kwargs)

    def cmap(
        self, fname: str = "", ext: str = "", kywrd: str = "", ncntr: str = "", **kwargs
    ):
        r"""Changes an existing or creates a new color mapping table.

        Mechanical APDL Command: `/CMAP <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMAP.html>`_

        **Command default:**

        .. _s-CMAP_default:

        Use predefined Mechanical APDL color map table.

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. If blank, restore color map.

        ext : str
            Filename extension (eight-character maximum).

        kywrd : str
            Keyword indicating the disposition of the color map file.

            * ``(blank)`` - Loads existing color map file.

            * ``CREATE`` - Starts the CMAP utility and modifies or creates the specified file.

            * ``SAVE`` - Writes the active color map to the specified file, which can be imported into future sessions.

        ncntr : str
            Number of contours to be defined. Default = 9 (even if an existing file is being modified).
            Maximum = 128.

        Notes
        -----

        .. _s-CMAP_notes:

        Reads the color map file (RGB index specifications) to change from current specifications. Only one
        color map may be active at a time.

        For 2D drivers (especially Win32c), modifying the color map can produce anomalies, including
        legend/contour disagreement.

        When ``Kywrd`` equals CREATE, the 2D drivers (X11c and Win32c) display the CMAP utility with an
        additional contour color picker called CONTOURS. Colors selected via the CONTOURS picker affect
        result contour displays (such as stresses). No other drivers offer the CONTOURS picker in the CMAP
        utility.

        Changing the color map using the :ref:`cmap` command changes the meaning of the color labels on the
        :ref:`color` command. See :ref:`color` for other color controls.

        This command is valid anywhere.
        """
        command = f"/CMAP,{fname},{ext},,{kywrd},{ncntr}"
        return self.run(command, **kwargs)

    def window(
        self,
        wn: str = "",
        xmin: str = "",
        xmax: str = "",
        ymin: str = "",
        ymax: str = "",
        ncopy: str = "",
        **kwargs,
    ):
        r"""Defines the window size on the screen.

        Mechanical APDL Command: `/WINDOW <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WINDOW.html>`_

        Parameters
        ----------
        wn : str
            Window reference number (1 to 5). Defaults to 1. This number, or ALL (for all active windows),
            may be used on other commands.

        xmin : str
            Screen coordinates defining window size. Screen coordinates are measured as -1.0 to 1.67 with
            the origin at the screen center. For example, (-1,1.67,-1,1) is full screen, (-1,0,-1,0) is the
            left bottom quadrant. If ``XMIN`` = OFF, deactivate this previously defined window; if ON,
            reactivate this previously defined window. If FULL, LEFT, RIGH, TOP, BOT, LTOP, LBOT, RTOP,
            RBOT, form full, half, or quarter window. If SQUA, form largest square window within the current
            graphics area. If DELE, delete this window (cannot be reactivated with ON).

        xmax : str
            Screen coordinates defining window size. Screen coordinates are measured as -1.0 to 1.67 with
            the origin at the screen center. For example, (-1,1.67,-1,1) is full screen, (-1,0,-1,0) is the
            left bottom quadrant. If ``XMIN`` = OFF, deactivate this previously defined window; if ON,
            reactivate this previously defined window. If FULL, LEFT, RIGH, TOP, BOT, LTOP, LBOT, RTOP,
            RBOT, form full, half, or quarter window. If SQUA, form largest square window within the current
            graphics area. If DELE, delete this window (cannot be reactivated with ON).

        ymin : str
            Screen coordinates defining window size. Screen coordinates are measured as -1.0 to 1.67 with
            the origin at the screen center. For example, (-1,1.67,-1,1) is full screen, (-1,0,-1,0) is the
            left bottom quadrant. If ``XMIN`` = OFF, deactivate this previously defined window; if ON,
            reactivate this previously defined window. If FULL, LEFT, RIGH, TOP, BOT, LTOP, LBOT, RTOP,
            RBOT, form full, half, or quarter window. If SQUA, form largest square window within the current
            graphics area. If DELE, delete this window (cannot be reactivated with ON).

        ymax : str
            Screen coordinates defining window size. Screen coordinates are measured as -1.0 to 1.67 with
            the origin at the screen center. For example, (-1,1.67,-1,1) is full screen, (-1,0,-1,0) is the
            left bottom quadrant. If ``XMIN`` = OFF, deactivate this previously defined window; if ON,
            reactivate this previously defined window. If FULL, LEFT, RIGH, TOP, BOT, LTOP, LBOT, RTOP,
            RBOT, form full, half, or quarter window. If SQUA, form largest square window within the current
            graphics area. If DELE, delete this window (cannot be reactivated with ON).

        ncopy : str
            Copies the current specifications from window ``NCOPY`` (1 to 5) to this window. If ``NCOPY`` =
            0 (or blank), no specifications are copied.

        Notes
        -----

        .. _s-WINDOW_notes:

        Defines the window size on the screen. Windows may occupy a separate section of the screen or they
        may overlap. Requested displays are formed in all windows according to the selected window
        specifications.

        This command is valid in any processor.
        """
        command = f"/WINDOW,{wn},{xmin},{xmax},{ymin},{ymax},{ncopy}"
        return self.run(command, **kwargs)

    def replot(self, label: str = "", **kwargs):
        r"""Reissues the last display command.

        Mechanical APDL Command: `/REPLOT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_REPLOT.html>`_

        Parameters
        ----------
        label : str
            Controls the type of replot.

            * ``RESIZE`` - Issued internally when a graphics window resize occurs (Default).

            * ``FAST`` - Only applicable for 3D devices that allow a fast redisplay for changes in the view characteristics
              only.

        Notes
        -----

        .. _s-REPLOT_notes:

        Reissues the last display command ( :ref:`nplot`, :ref:`eplot`, :ref:`kplot`, :ref:`plnsol`,
        :ref:`plvar`, etc.), along with its parameters, for convenience. The current display specifications
        are used.

        When the last display command is invalid in a given processor, :ref:`replot` is also invalid in that
        processor. However, if you attempt a :ref:`replot` and the last display command is invalid in the
        current processor, Mechanical APDL generates an element display ( :ref:`eplot` ) instead, as long as
        the
        last display command was  :ref:`plnsol`, :ref:`plesol`, or  :ref:`pldisp`.

          Example: :ref:`replot` Replaced by :ref:`eplot` Automatically

          :ref:`plnsol`, used to display solution results as continuous contours, is a valid command in the
          POST1 general postprocessor.

          If you issue :ref:`plnsol` followed by :ref:`replot` while in POST1, :ref:`replot` effectively
          reissues your earlier :ref:`plnsol` command, along with its parameters.

          If you then exit POST1, enter the PREP7 preprocessor, and again issue :ref:`replot`, the program
          uses :ref:`eplot` internally instead.

          The command substitution occurs because :ref:`plnsol` is not a valid command in PREP7.

        When you click one of the buttons on the `Pan, Zoom, Rotate
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_wid/Hlp_UI_PanZoom.html#wpanzoomk>`_
        dialog box to manipulate the view of a model, :ref:`replot` is issued internally. Thus, the
        substitution of :ref:`replot` with :ref:`eplot` as described above may also occur for operations
        that you perform via with the `Pan, Zoom, Rotate
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_wid/Hlp_UI_PanZoom.html#wpanzoomk>`_
         dialog box.

        :ref:`replot` does not show boundary conditions if they are applied only to a solid model and the
        last display command (such as :ref:`eplot` ) displays the finite element model. To show boundary
        conditions, the following options are available:

        Issue :ref:`replot` after you issue :ref:`sbctran` to transfer solid model boundary conditions to
        the finite element model. Issue :ref:`replot` after you issue a solid model display command (such as
        :ref:`vplot` ).

        This command is valid in any processor (except as noted above).
        """
        command = f"/REPLOT,{label}"
        return self.run(command, **kwargs)

    def slashreset(self, **kwargs):
        r"""Resets display specifications to their initial defaults.

        Mechanical APDL Command: `/RESET <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_RESET_sl.html>`_

        Notes
        -----

        .. _s-RESET_notes:

        Resets slash display specifications ( :ref:`window`, :ref:`slashtype`, :ref:`view`, etc.) back to
        their initial default settings (for convenience). Also resets the focus location to the geometric
        center of the object.

        This command is valid in any processor.
        """
        command = "/RESET"
        return self.run(command, **kwargs)

    def noerase(self, **kwargs):
        r"""Prevents the screen erase between displays.

        Mechanical APDL Command: `/NOERASE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NOERASE.html>`_

        Notes
        -----

        .. _s-NOERASE_notes:

        Preventing the normal screen erase between requested displays allows you to overlay multiple views.

        Clearing the screen with the ``ERASE`` command ( Utility Menu> PlotCtrls> Erase Options> Erase
        screen ) active simply clears the display area. Subsequent replots will provide the cumulative plots
        previously generated by the :ref:`noerase` command.

        For 3D devices, you can issue :ref:`dv3d`,DELS to suppress repeated screen overlays and generate
        clear contour plots.

        Use the ``/ERASE`` command to reactivate automatic screen erase.

        For 3D devices ( :ref:`show`,3D), the model in all active windows will be the same, even if you
        issue a different display command ( :ref:`nplot`, :ref:`eplot`, etc.) for each active window. Use
        the Multi-Plot command ( :ref:`gplot` ) to display different entities, in different windows, on 3D
        devices.

        This command is valid in any processor.
        """
        command = "/NOERASE"
        return self.run(command, **kwargs)

    def pstatus(self, wn: str = "", **kwargs):
        r"""Displays the global or window display specifications.

        Mechanical APDL Command: `/PSTATUS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PSTATUS.html>`_

        Parameters
        ----------
        wn : str
            Window number for status (defaults to global specifications).

        Notes
        -----

        .. _s-PSTATUS_notes:

        Displays the current global or window display specifications. Global display specifications are
        common to all windows (e.g. :ref:`show`, etc.). Window display specifications are specific to one
        window (e.g. :ref:`view`, :ref:`slashtype`, etc.).

        This command is valid in any processor.
        """
        command = f"/PSTATUS,{wn}"
        return self.run(command, **kwargs)

    def pngr(self, kywrd: str = "", opt: str = "", val: int | str = "", **kwargs):
        r"""Provides PNG file export for Mechanical APDL displays.

        Mechanical APDL Command: `PNGR <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_PNGR.html>`_

        Parameters
        ----------
        kywrd : str
            Specifies various PNG file export options.

            * ``COMP`` - If ``Kywrd`` = COMP, then ``OPT`` is either ON or OFF (blank is interpreted as OFF). This option
              allows you to turn PNG file compression ON or OFF. If OPT = ON, then The VAL field is read to
              determine the degree of compression. See the VALUE argument for acceptable compression values.

            * ``ORIENT`` - If ``Kywrd`` = ORIENT, then ``OPT`` will determine the orientation of the entire plot. ``OPT`` can
              be either Horizontal (default) or Vertical.

            * ``COLOR`` - If ``Kywrd`` = COLOR, then ``OPT`` will determine the color depth of the saved file. ``OPT`` can be
              0, 1, or 2, corresponding to Black and White, Grayscale, and Color (default), respectively.

            * ``TMOD`` - If ``Kywrd`` = TMOD, then ``OPT`` will determine the text method. ``OPT`` can be either 1 or 0,
              corresponding to bitmap text (default) or line stroke text, respectively.

            * ``DEFAULT`` - If ``Kywrd`` = DEFAULT, then all of the default values, for all of the Kywrd parameters listed
              above, are active.

            * ``STAT`` - Shows the current status of PNG file export.

        opt : str
            ``OPT`` can have the following names or values, depending on the value for ``Kywrd`` (see above).

            * ``ON, OFF`` - If ``Kywrd`` = COMP, the values On and Off control the use of compression. The degree of compression
              is determined by VAL

            * ``Horizontal, Vertical`` - If ``Kywrd`` = ORIENT, the terms Horizontal or Vertical determine the orientation of the plot.

            * ``0, 1, 2`` - If ``Kywrd`` = COLOR, the numbers 0, 1, and 2 correspond to Black and White, Grayscale and Color,
              respectively.

            * ``1, 0`` - If ``Kywrd`` = TMOD, the values 1 and 0 determine whether bitmap (1) or stroke text (0) fonts will
              be used

        val : int or str
            ``VAL`` is active only when ``Kywrd`` = COMP, and determines the degree of compression applied to
            the exported file (see above).

            * ``-1`` - Apply the default, optimum value for compression. This value represents the best combination of
              speed and compression. It varies according to the release level of the ZLIB compression package.

            * ``1-9`` - Use this value to specify a specific compression level. 1 is the lowest compression level (fastest)
              and 9 is the highest compression level (slowest).

        """
        command = f"PNGR,{kywrd},{opt},{val}"
        return self.run(command, **kwargs)

    def tiff(self, kywrd: str = "", opt: str = "", **kwargs):
        r"""Provides TIFF file export for Mechanical APDL displays.

        Mechanical APDL Command: `TIFF <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TIFF.html>`_

        Parameters
        ----------
        kywrd : str
            Specifies various TIFF file export options.

            * ``COMP`` - If ``Kywrd`` = COMP, then ``OPT`` controls data compression for the output file. If COMP = 0, then
              compression is off. If COMP = 1 (default), then compression is on.

            * ``ORIENT`` - If ``Kywrd`` = ORIENT, then ``OPT`` will determine the orientation of the entire plot. ``OPT`` can
              be either Horizontal (default) or Vertical.

            * ``COLOR`` - If ``Kywrd`` = COLOR, then ``OPT`` will determine the color attribute of the saved file. ``OPT`` can
              be 0, 1, or 2, corresponding to Black and White, Grayscale, and Color (default), respectively.

            * ``TMOD`` - If ``Kywrd`` = TMOD, then ``OPT`` will determine the text method. ``OPT`` can be either 1 or 0,
              corresponding to bitmap text (default) or line stroke text, respectively.

            * ``DEFAULT`` - If ``Kywrd`` = DEFAULT, then all of the default values, for all of the Kywrd parameters listed
              above, are active.

        opt : str
            ``OPT`` can have the following names or values, depending on the value for ``Kywrd`` (see above).

            * ``1 or 0`` - If ``Kywrd`` = COMP, a value or 1 (on) or 0 (off) will control compression for the TIFF file.

            * ``Horizontal, Vertical`` - If ``Kywrd`` = ORIENT, the terms Horizontal or Vertical determine the orientation of the plot.

            * ``0, 1, 2`` - If ``Kywrd`` = COLOR, the numbers 0, 1, and 2 correspond to Black and White, Grayscale and Color,
              respectively.

            * ``1, 0`` - If ``Kywrd`` = TMOD, the values 1 and 0 determine whether bitmap (1) or stroke text (0) fonts will
              be used

        """
        command = f"TIFF,{kywrd},{opt}"
        return self.run(command, **kwargs)

    def mrep(
        self,
        name: str = "",
        arg1: str = "",
        arg2: str = "",
        arg3: str = "",
        arg4: str = "",
        arg5: str = "",
        arg6: str = "",
        arg7: str = "",
        arg8: str = "",
        arg9: str = "",
        arg10: str = "",
        arg11: str = "",
        arg12: str = "",
        arg13: str = "",
        arg14: str = "",
        arg15: str = "",
        arg16: str = "",
        arg17: str = "",
        arg18: str = "",
        **kwargs,
    ):
        r"""Enables you to reissue the graphics command macro "name" during a replot or zoom operation.

        Mechanical APDL Command: `/MREP <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_MREP.html>`_

        Parameters
        ----------
        name : str
            The name identifying the macro file or macro block on a macro library file. The name can contain
            up to eight characters maximum and must begin with a letter.

        arg1 : str
            Values to be passed into the file or block.

        arg2 : str
            Values to be passed into the file or block.

        arg3 : str
            Values to be passed into the file or block.

        arg4 : str
            Values to be passed into the file or block.

        arg5 : str
            Values to be passed into the file or block.

        arg6 : str
            Values to be passed into the file or block.

        arg7 : str
            Values to be passed into the file or block.

        arg8 : str
            Values to be passed into the file or block.

        arg9 : str
            Values to be passed into the file or block.

        arg10 : str
            Values to be passed into the file or block.

        arg11 : str
            Values to be passed into the file or block.

        arg12 : str
            Values to be passed into the file or block.

        arg13 : str
            Values to be passed into the file or block.

        arg14 : str
            Values to be passed into the file or block.

        arg15 : str
            Values to be passed into the file or block.

        arg16 : str
            Values to be passed into the file or block.

        arg17 : str
            Values to be passed into the file or block.

        arg18 : str
            Values to be passed into the file or block.

        Notes
        -----

        .. _s-MREP_notes:

        This command reissues the graphics command macro "name" during a replot operation ( :ref:`replot` )
        or a zoom ( :ref:`zoom` ) operation. The program passes the command macro arguments to the replot
        and zoom feature for use by the graphics macro. You should place the ``s-MREP`` command at the end
        of the graphics command macro, following the last graphics command within the macro, to enable the
        replot or zoom feature.
        """
        command = f"/MREP,{name},{arg1},{arg2},{arg3},,{arg4},{arg5},{arg6},{arg7},{arg8},{arg9},{arg10},{arg11},{arg12},{arg13},{arg14},{arg15},{arg16},{arg17},{arg18}"
        return self.run(command, **kwargs)

    def gresume(self, fname: str = "", ext: str = "", **kwargs):
        r"""Sets graphics settings to the settings on a file.

        Mechanical APDL Command: `/GRESUME <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GRESUME.html>`_

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. The file name defaults to :file:`Jobname`.

        ext : str
            Filename extension (eight-character maximum). The extension defaults to GSAV if ``Fname`` is
            blank.

        Notes
        -----

        .. _s-GRESUME_notes:

        Causes a file to be read to reset the graphics slash (/) commands as they were at the last
        :ref:`gsave` command.

        This command is valid in any processor.
        """
        command = f"/GRESUME,{fname},{ext}"
        return self.run(command, **kwargs)

    def gfile(self, size: str = "", **kwargs):
        r"""Specifies the pixel resolution on Z-buffered graphics files.

        Mechanical APDL Command: `/GFILE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GFILE.html>`_

        Parameters
        ----------
        size : str
            Pixel resolution. Defaults to a pixel resolution of 800. Valid values are from 256 to 2400.

        Notes
        -----

        .. _s-GFILE_notes:

        Defines the pixel resolution on subsequently written graphics files (for example, JPEG, PNG, TIFF)
        for software Z-buffered displays ( :ref:`slashtype` ). Lowering the pixel resolution produces a
        fuzzier image; increasing the resolution produces a sharper image but takes a little longer.

        This command is valid in any processor.
        """
        command = f"/GFILE,{size}"
        return self.run(command, **kwargs)

    def graphics(self, key: str = "", **kwargs):
        r"""Defines the type of graphics display.

        Mechanical APDL Command: `/GRAPHICS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GRAPHICS.html>`_

        Parameters
        ----------
        key : str
            Graphics key:

            * ``FULL`` - Display all model geometry and results.

            * ``POWER`` - Activate PowerGraphics (default when GUI is on).

        Notes
        -----

        .. _s-GRAPHICS_notes:

        The :ref:`graphics` command specifies the type of graphics display. ``Key`` = POWER activates the
        PowerGraphics capability. PowerGraphics offers faster plotting than the _nolinebreak? ``Key`` = FULL
        option, /_nolinebreak? and speeds up element, results, area, line, and volume displays.

        The default PowerGraphics mode is enabled automatically when accessing the GUI. This action
        supersedes all prior macros or start-up routines ( :file:`start.ans`, :file:`config.ans`, etc.).
        Full graphics mode is accessed only by issuing :ref:`graphics`,FULL after the GUI is active.

        Results values (both printed and plotted) may differ between the _nolinebreak? ``Key`` = FULL
        /_nolinebreak? and ``Key`` = POWER options because each option specifies a different set of data for
        averaging and display. For _nolinebreak? ``Key`` = FULL /_nolinebreak?, all element and results
        values (interior and surface) are included. For _nolinebreak? ``Key`` = POWER /_nolinebreak?, only
        element and results values along the model exterior surface are processed.

        When ``Key`` = FULL, it is possible to deselect an individual node, select all elements (including
        the element that contains that node), and then perform postprocessing calculations on those elements
        and have that unselected node not be considered in those calculations. If PowerGraphics is active,
        however, postprocessing always displays based on selected elements.

        If you have specified one facet per element edge for PowerGraphics displays (via the :ref:`efacet`
        command or options from the General Postproc or Utility menu), PowerGraphics does not plot midside
        nodes. ( :ref:`efacet` applies to element type displays only.)

        Maximum values shown in plots can differ from printed maximum values. This is due to different
        averaging schemes used for plotted and printed maximum values.

        When using solution coordinate systems for results output ( :ref:`rsys`,SOLU) with PowerGraphics,
        the deformed or displaced shape in a POST1 contour display can be unexpected (although the contours
        are displayed in the expected colors). The program does not rotate displacement values (Ux,Uy,Uz) to
        global; instead, the displacements (stored locally) are added directly to the global coordinates
        (X,Y,Z). For example, if in PREP7 the nodes are rotated 90 degrees about the z axis and the global
        Uy displacements are relatively large, the Ux values will be large, causing the model to display a
        large deformation in the global X direction.

        PowerGraphics displays do not average at geometric discontinuities. The printouts in PowerGraphics
        will, however, provide averaging information at geometric discontinuities if the models do not
        contain shell elements. Carefully inspect the data you obtain at geometric discontinuities.

        PowerGraphics does not support the following diffusion analysis results: CONC, CG, DF, EPDI.

        ``Key`` = FULL is not available for `XFEM-based crack-growth analysis
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_frac/Hlp_G_FRACXFEM.html#fracxfemreferences>`_.

        Excepting a few options, PowerGraphics supports these commands:

        InformalTables need to be added.
        The following commands are executed via the _nolinebreak? ``Key`` = FULL /_nolinebreak? option,
        regardless of whether PowerGraphics is activated:

        InformalTables need to be added.
        """
        command = f"/GRAPHICS,{key}"
        return self.run(command, **kwargs)

    def gcolumn(self, curve: str = "", string: str = "", **kwargs):
        r"""Allows the user to apply a label to a specified curve.

        Mechanical APDL Command: `/GCOLUMN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GCOLUMN.html>`_

        Parameters
        ----------
        curve : str
            Curve number on which label will be applied (integer value between 1 and 10).

        string : str
            Name or designation that will be applied to the curve (8 characters max).

        Notes
        -----

        .. _s-GCOLUMN_notes:

        This command is used for an array parameter plot (a plot created by the :ref:`starvplot` command).
        Normally the label for curve 1 is COL 1, the label for curve 2 is COL 2 and so on; the column number
        is the field containing the dependent variables for that particular curve. Issuing :ref:`gcolumn`,
        ``CURVE``, with no string value specified resets the label to the original value.
        """
        command = f"/GCOLUMN,{curve},{string}"
        return self.run(command, **kwargs)

    def gtype(self, wn: str = "", label: str = "", key: int | str = "", **kwargs):
        r"""Controls the entities that the :ref:`gplot` command displays.

        Mechanical APDL Command: `/GTYPE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GTYPE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which this command applies (defaults to 1)

        label : str
            This represents the type of entity to display:

            * ``NODE`` - Nodes

            * ``ELEM`` - Elements

            * ``KEYP`` - Keypoints

            * ``LINE`` - Lines

            * ``AREA`` - Areas

            * ``VOLU`` - Volumes

            * ``GRPH`` - Graph displays

        key : int or str
            Switch:

            * ``0`` - Turns the entity type off.

            * ``1`` - Turns the entity type on.

        Notes
        -----

        .. _s-GTYPE_notes:

        The :ref:`gtype` command controls which entities the :ref:`gplot` command displays. NODE, ELEM,
        KEYP, LINE, AREA, and VOLU are on by default. When ELEM is activated, you can control the type of
        element displayed via the :ref:`gcmd` command (which also controls the type of graph display). When
        the GRPH entity type is activated, all other entity types are deactivated. Conversely, when any of
        the NODE, ELEM, KEYP, LINE, AREA, and VOLU entity types are active, the GRPH entity type is
        deactivated.

        The :ref:`gtype` command gives you several options for multi-window layout:

        One window Two windows (left and right or top and bottom of the screen) Three windows (two at the
        top and one at the bottom of the screen, or one top and two bottom windows Four windows (two at the
        top and two at the bottom)

        Once you choose a window layout, you can choose one of the following: multiple plots, replotting, or
        no redisplay.

        This command is valid in any processor.
        """
        command = f"/GTYPE,{wn},{label},{key}"
        return self.run(command, **kwargs)

    def gsave(self, fname: str = "", ext: str = "", **kwargs):
        r"""Saves graphics settings to a file for later use.

        Mechanical APDL Command: `/GSAVE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GSAVE.html>`_

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. The file name defaults to :file:`Jobname`.

        ext : str
            Filename extension (eight-character maximum). The extension defaults to GSAV if ``Fname`` is
            blank.

        Notes
        -----

        .. _s-GSAVE_notes:

        This command does not save all graphics settings, but only those that may be reset by the
        :ref:`slashreset` command. The database remains untouched. Use the :ref:`gresume` command to read
        the file. Repeated use of the :ref:`gsave` command overwrites the previous data on the file. The
        following commands are saved by :ref:`gsave` :

        InformalTables need to be added.

        This command is valid in any processor.
        """
        command = f"/GSAVE,{fname},{ext}"
        return self.run(command, **kwargs)

    def gcmd(
        self,
        wn: str = "",
        lab1: str = "",
        lab2: str = "",
        lab3: str = "",
        lab4: str = "",
        lab5: str = "",
        lab6: str = "",
        lab7: str = "",
        lab8: str = "",
        lab9: str = "",
        lab10: str = "",
        lab11: str = "",
        lab12: str = "",
        **kwargs,
    ):
        r"""Controls the type of element or graph display used for the :ref:`gplot` command.

        Mechanical APDL Command: `/GCMD <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GCMD.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which this command applies (defaults to 1)

        lab1 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab2 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab3 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab4 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab5 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab6 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab7 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab8 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab9 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab10 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab11 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        lab12 : str
            Command labels (for example, :ref:`plnsol`,S,X)

        Notes
        -----

        .. _s-GCMD_notes:

        This command controls the type of element or graph display that appears when you issue the
        :ref:`gplot` command when the :ref:`gtype`,,(ELEM or GRPH) entity type is active. If you have
        multiple plotting windows enabled, you can also use :ref:`gcmd` to select one window when you wish
        to edit its contents.

        For related information, see the descriptions of the :ref:`gplot` and :ref:`gtype` commands in this
        manual.

        This command is valid in any processor.
        """
        command = f"/GCMD,{wn},{lab1},{lab2},{lab3},{lab4},{lab5},{lab6},{lab7},{lab8},{lab9},{lab10},{lab11},{lab12}"
        return self.run(command, **kwargs)

    def gplot(self, **kwargs):
        r"""Controls general plotting.

        Mechanical APDL Command: `GPLOT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GPLOT.html>`_

        Notes
        -----

        .. _GPLOT_notes:

        This command displays all entity types as specified via the :ref:`gtype` command. Only selected
        entities ( :ref:`nsel`, :ref:`esel`, :ref:`ksel`, :ref:`lsel`, :ref:`asel`, :ref:`vsel` ) will be
        displayed. See the descriptions of the :ref:`gtype` and :ref:`gcmd` commands for methods of setting
        the entity types displayed.

        This command is valid in any processor.
        """
        command = "GPLOT"
        return self.run(command, **kwargs)

    def jpeg(self, kywrd: str = "", opt: str = "", **kwargs):
        r"""Provides JPEG file export for Mechanical APDL displays.

        Mechanical APDL Command: `JPEG <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_JPEG.html>`_

        Parameters
        ----------
        kywrd : str
            Specifies various JPEG file export options.

            * ``QUAL`` - If ``Kywrd`` = QUAL, then ``OPT`` is an integer value defining the JPEG quality index on an
              arbitrary scale ranging from 1 to 100. The default value is 75.

            * ``ORIENT`` - If ``Kywrd`` = ORIENT, then ``OPT`` will determine the orientation of the entire plot. ``OPT`` can
              be either Horizontal (default) or Vertical.

            * ``COLOR`` - If ``Kywrd`` = COLOR, then ``OPT`` will determine the color depth of the saved file. ``OPT`` can be
              0, 1, or 2, corresponding to Black and White, Grayscale, and Color (default), respectively.

            * ``TMOD`` - If ``Kywrd`` = TMOD, then ``OPT`` will determine the text method. ``OPT`` can be either 1 or 0,
              corresponding to bitmap text (default) or line stroke text, respectively.

            * ``DEFAULT`` - If ``Kywrd`` = DEFAULT, then all of the default values, for all of the Kywrd parameters listed
              above, are active.

        opt : str
            ``OPT`` can have the following names or values, depending on the value for ``Kywrd`` (see above).

            * ``1 to 100`` - If ``Kywrd`` = QUAL, a value between 1 and 100 will determine the quality index of the JPEG file.

            * ``Horizontal, Vertical`` - If ``Kywrd`` = ORIENT, the terms Horizontal or Vertical determine the orientation of the plot.

            * ``0,1,2`` - If ``Kywrd`` = COLOR, the numbers 0, 1, and 2 correspond to Black and White, Grayscale and Color,
              respectively.

            * ``1,0`` - If ``Kywrd`` = TMOD, the values 1 and 0 determine whether bitmap (1) or stroke text (0) fonts will
              be used

        """
        command = f"JPEG,{kywrd},{opt}"
        return self.run(command, **kwargs)

    def show(
        self,
        fname: str = "",
        option: str = "",
        vect: int | str = "",
        ncpl: str = "",
        **kwargs,
    ):
        r"""Specifies the device and other parameters for graphics displays.

        Mechanical APDL Command: `/SHOW <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SHOW.html>`_

        Parameters
        ----------
        fname : str
            Device name, file name, or keyword, as listed below:

            * ``<, device name >`` - Any valid graphics display device name (for example, X11, 3D etc.). Defaults to X11 for most
              systems. See `Getting Started with Graphics
              <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_bas/Hlp_G_BAS8_7.html>`_ in the `Basic Analysis Guide <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_bas/Hlp_G_BAS19.html>`_
              for details. A device name must be defined before activating the Graphical User Interface (GUI).
              Once the GUI is activated, the device name cannot be changed for that session, except for switching
              between X11 and X11C.

            * ``TERM`` - Graphics displays are switched back to the last-specified device name.

            * ``CLOSE`` - This option purges the graphics file buffer. The CLOSE option should be issued any time you are
              changing graphics devices or file output types during a session. Graphics displays are switched back
              to the last-specified device name, and any open graphics files are closed. The CLOSE option is
              similar to the TERM option, however, with the CLOSE option, another process can access the data in
              the graphics file. The CLOSE option causes graphics file buffers to be flushed to the graphics file.

            * ``OFF`` - Graphics display requests are ignored.

            * ``(blank)`` - If blank in interactive mode, graphics will be displayed on screen as requested by display commands
              (no file written).

            * ``JPEG`` - Creates JPEG files that are named :file:`Jobname` nnn.jpg, where ``nnn`` is a numeric value that is
              incremented by one as each additional file is created; that is, :file:`Jobname000.jpg`,
              :file:`Jobname001.jpg`, :file:`Jobname002.jpg`, and so on. Ignores the ``Ext`` field.

            * ``TIFF`` - Creates tagged image format files that are named :file:`Jobname` nnn.tif, where ``nnn`` is a numeric
              value that is incremented by one as each additional file is created; that is,
              :file:`Jobname000.tif`, :file:`Jobname001.tif`, :file:`Jobname002.tif`, and so on. This value for
              the ``Fname`` argument ignores the ``Ext`` field. (See the :ref:`tiff` command for options.)

            * ``PNG`` - Creates PNG (Portable Network Graphics) files that are named :file:`Jobname` nnn.png, where ``nnn``
              is a numeric value that is incremented by one as each additional file is created; that is,
              :file:`Jobname000.png`, :file:`Jobname001.png`, :file:`Jobname002.png`, and so on. This value for
              the ``Fname`` argument ignores the ``Ext`` field. (See the :ref:`pngr` command for options.)

            * ``VRML`` - Creates Virtual Reality Meta Language files named :file:`Jobname000.wrl` that can be displayed on 3D
              Internet web browsers. Ignores the ``Ext`` and ``NCPL`` fields.

        option : str
            Assign a file name extension or specify reverse video output:

            * ``Ext`` - File name extension (eight-character maximum).

            * ``REV`` - Reverse background/image (black/white) colors. Valid with ``Fname`` = PNG (recommended), JPEG, and
              TIFF. This option is ignored if a previously specified color map table ( :ref:`cmap` or :ref:`rgb` )
              is in effect.

        vect : int or str
            Specifies raster or vector display mode. This affects area, volume, and element displays, as well as
            geometric results displays such as contour plots. See the :ref:`device` command for an alternate way to toggle between raster and vector mode. Changing ``VECT`` also resets the :ref:`slashtype` command to its default.

            * ``0`` - Raster display (color filled entities; default)

            * ``1`` - Vector display (outlined entities; that is, "wireframe")

        ncpl : str
            Sets the number of color planes (4 to 8). Default is device-dependent. ``NCPL`` is not supported
            by all graphics devices.

        Notes
        -----

        .. _s-SHOW_notes:

        Specifies the device to be used for graphics displays, and specifies other graphics display
        parameters. Display may be shown at the time of generation (for interactive runs at a graphics
        display terminal) or diverted to a file. Issue :ref:`pstatus` for display status.

        Batch runs do not have access to the fonts available on your system. The Courier and Helvetica font
        files used for JPEG, PNG and TIFF batch output are copyrighted by Adobe Systems Inc. and Digital
        Equipment Corp. Permission to use these trademarks is hereby granted only in association with the
        images described above. Batch run JPEG output is produced at the default quality index value of 75,
        unless specified otherwise.

        Interactive displays default to eight color planes ( ``NCPL`` = 8) for most monitors, while graph
        file output defaults to eight color planes for VRML output, and four color planes for JPEG, PNG, and
        TIFF.

        This command is valid in any processor.
        """
        command = f"/SHOW,{fname},{option},{vect},{ncpl}"
        return self.run(command, **kwargs)

    def seg(self, label: str = "", aviname: str = "", delay: str = "", **kwargs):
        r"""Allows graphics data to be stored in the local terminal memory.

        Mechanical APDL Command: `/SEG <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SEG.html>`_

        Parameters
        ----------
        label : str
            Storage key:

            * ``SINGL`` - Store subsequent display in a single segment (overwrites last storage).

            * ``MULTI`` - Store subsequent displays in unique segments ( :ref:`anim` ).

            * ``DELET`` - Delete all currently stored segments.

            * ``OFF`` - Stop storing display data in segments.

            * ``STAT`` - Display segment status.

            * ``PC`` - This option only applies to PC versions of Mechanical APDL and only when animating via the AVI movie player
              ( :ref:`device`,ANIM,2). The command appends frames to the :file:`File.AVI`, so that the animation
              goes in both directions (that is, forward--backward--forward). You must have a current animation
              file to use this option.

        aviname : str
            Name of the animation file that will be created when each frame is saved. The :file:`.AVI`
            extension is applied automatically. Defaults to :file:`Jobname.AVI` if no filename is specified.

        delay : str
            Delay factor between each frame, in seconds. Defaults to 0.015 seconds if no value is specified.

        Notes
        -----

        .. _s-SEG_notes:

        Allows graphics data to be stored in the terminal local memory (device-dependent). Storage occurs
        concurrently with the display.

        Although the information from your graphics window is stored as an individual segment, you cannot
        plot directly ( :ref:`gplot` ) from the segment memory.

        This command is valid in any processor.
        """
        command = f"/SEG,{label},{aviname},{delay}"
        return self.run(command, **kwargs)
