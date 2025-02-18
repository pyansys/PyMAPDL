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


class Graphs:

    def xrange(self, xmin: str = "", xmax: str = "", **kwargs):
        r"""Specifies a linear abscissa (X) scale range.

        Mechanical APDL Command: `/XRANGE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_XRANGE.html>`_

        Parameters
        ----------
        xmin : str
            Minimum abscissa scale value.

        xmax : str
            Maximum abscissa scale value.

        Notes
        -----

        .. _s-XRANGE_notes:

        Specifies a linear abscissa (X) scale range for the line graph display. Use :ref:`xrange`,DEFAULT to
        return to automatic scaling.

        Automatic scaling will often yield inappropriate range values for logarithmic scales ( :ref:`gropt`,
        LOGX).

        This command is valid in any processor.
        """
        command = f"/XRANGE,{xmin},{xmax}"
        return self.run(command, **kwargs)

    def yrange(self, ymin: str = "", ymax: str = "", num: str = "", **kwargs):
        r"""Specifies a linear ordinate (Y) scale range.

        Mechanical APDL Command: `/YRANGE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_YRANGE.html>`_

        Parameters
        ----------
        ymin : str
            Minimum ordinate scale value.

        ymax : str
            Maximum ordinate scale value.

        num : str
            Y-axis number to which range applies (defaults to 1). Valid numbers are 1 to 3 for
            :ref:`grtyp`,2 and 1 to 6 for :ref:`grtyp`,3. If ALL, apply to all Y-axes.

        Notes
        -----

        .. _s-YRANGE_notes:

        Specifies a linear ordinate (Y) scale range for the line graph display. Use :ref:`yrange`,DEFAULT to
        return to automatic scaling. For multiple Y-axes graphs ( :ref:`grtyp` ), see :ref:`gropt`, ASCAL to
        automatically scale the additional Y-axes.

        Automatic scaling will often yield inappropriate range values for logarithmic scales ( :ref:`gropt`,
        LOGY).

        This command is valid in any processor.
        """
        command = f"/YRANGE,{ymin},{ymax},{num}"
        return self.run(command, **kwargs)

    def axlab(self, axis: str = "", lab: str = "", **kwargs):
        r"""Labels the X and Y axes on graph displays.

        Mechanical APDL Command: `/AXLAB <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_AXLAB.html>`_

        **Command default:**

        .. _s-AXLAB_default:

        Labels are determined by the program.

        Parameters
        ----------
        axis : str
            Axis specifier:

            * ``X`` - Apply label to X axis.

            * ``Y`` - Apply label to Y axis.

        lab : str
            Axis label (user defined text up to 30 characters long). Leave blank to reestablish the default
            for ``Axis`` axis.

        Notes
        -----

        .. _s-AXLAB_notes:

        This command is valid in any processor.
        """
        command = f"/AXLAB,{axis},{lab}"
        return self.run(command, **kwargs)

    def grtyp(self, kaxis: int | str = "", **kwargs):
        r"""Selects single or multiple Y-axes graph displays.

        Mechanical APDL Command: `/GRTYP <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GRTYP.html>`_

        Parameters
        ----------
        kaxis : int or str
            Axis selection key:

            * ``0 or 1`` - Single Y-axis. Up to 10 curves scaled to a single Y-axis.

            * ``2`` - Additional Y-axes (one for each curve) (3 curves maximum). Allows better scaling of curves with
              widely differing numbering ranges.

            * ``3`` - Same as 2 but with additional Y-axis and curves projected out of the plane (6 curves maximum).
              Allows clearer display with an isometric view. The default view when ``KAXIS`` = 3 is View,1,1,2,3.

        Notes
        -----

        .. _s-GRTYP_notes:

        The basic line graph has one or more curves plotted against the same Y and X axes. Multiple curve
        graphs can also be plotted with individual Y axes and the same X axis. The Y axis of the first curve
        is referred to as the base Y-axis and the Y axes of the other curves as additional Y axes. Curves
        are numbered sequentially from 1 (the base curve) in the order in which they are displayed. See the
        :ref:`axlab`, :ref:`gropt`, :ref:`grid`, and :ref:`gthk` commands for other display options.

        This command is valid in any processor.
        """
        command = f"/GRTYP,{kaxis}"
        return self.run(command, **kwargs)

    def gropt(self, lab: str = "", key: str = "", **kwargs):
        r"""Sets various line graph display options.

        Mechanical APDL Command: `/GROPT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GROPT.html>`_

        Parameters
        ----------
        lab : str
            Apply display style as selected from the following labels:

            * ``AXDV`` - Axis division (tick) marks (defaults to ``KEY`` = ON).

            * ``AXNM`` - Axis scale numbers (defaults to ``KEY`` = ON, which puts numbers at the back plane of the graph). If
              ``KEY`` = FRONT, numbers are on the front plane of the graph.

            * ``AXNSC`` - Axis number size scale factor. Input the scale value for ``KEY`` (defaults to 1.0).

            * ``ASCAL`` - Automatic scaling of additional Y-axes for multi-curve ( :ref:`grtyp`, 2 or 3) graphs (defaults to
              ``KEY`` = ON). If ``KEY`` = OFF, use base Y-axis scaling (see the :ref:`yrange` command).

            * ``LOGX`` - Log X scale (defaults to ``KEY`` = OFF (linear)).

            * ``LOGY`` - Log Y scale (applies only to the base Y axis) (defaults to ``KEY`` = OFF (linear)).

            * ``FILL`` - Color fill areas under curves (defaults to ``KEY`` = OFF).

            * ``CGRID`` - Superimpose background grid ( :ref:`grid` ) over areas under filled curves (defaults to ``KEY`` =
              OFF).

            * ``DIG1`` - Number of significant digits before decimal point for axis values. Input the value for ``KEY``
              (defaults to 4).

            * ``DIG2`` - Number of significant digits after decimal point for axis values. Input the value for ``KEY``
              (defaults to 3).

            * ``VIEW`` - View key for graph displays (defaults to ``KEY`` = OFF, in which case the view is (0,0,1) for 2D
              graph displays or (1,2,3) for 3D graph displays). If ``KEY`` = ON, the view settings for graph
              displays are the same as the view settings for the model.

            * ``REVX`` - Plots the values on the X-axis in reverse order.

            * ``REVY`` - Plots the values on the Y-axis in reverse order.

            * ``DIVX`` - Determines the number of divisions (grid markers) that will be plotted on the X axis.

            * ``DIVY`` - Determines the number of divisions (grid markers) that will be plotted on the Y axis.

            * ``LTYP`` - Specifies whether program-generated ( ``KEY`` = 1) or system-derived ( ``KEY`` = 0) fonts are used
              for the axis labels.

            * ``CURL`` - Determines the position of the curve labels. If ( ``KEY`` = 1), the curve label will be plotted in
              the legend column, and the label will be displayed in the same color as the curve. If ( ``KEY`` = 0)
              the curve labels will be plotted near the curve. (default).

            * ``XAXO`` - When you use this label, the subsequent ``KEY`` value will determine an offset amount from the
              default (along the bottom) location for the X axis. If ``KEY`` = 1.0, a full offset occurs (the X
              axis is moved to the top of the graph). If ``KEY`` = 0.5, the axis is offset to the midpoint of the
              graph, and if ``KEY`` = 0 the axis remains in the original position, along the bottom of the graph.
              For any offset, a grey copy of the original axis (containing the axis numbering) remains at the
              original location.

            * ``YAXO`` - When you use this label, the subsequent ``KEY`` value will determine an offset amount from the
              default (along the left side of the graph) location for the Y axis. If ``KEY`` = 1.0, a full offset
              occurs (the Y axis is moved to the right side of the graph). If ``KEY`` = 0.5, the axis is offset to
              the midpoint of the graph, and if ``KEY`` = 0 the axis remains in the original position, along the
              left side of the graph. For any offset, a gray copy of the original axis (containing the axis
              numbering) remains at the original location.

        key : str
            Option values:

            * ``OFF (0)`` - Do not apply selected style.

            * ``ON (1)`` - Apply selected style.

            * ``nnnn`` - If ``Lab`` is DIG1 or DIG2, input the number of digits.

            * ``nn`` - If ``Lab`` is AXNSC, input the scale factor.

            * ``FRONT`` - If ``Lab`` is AXNM, FRONT may also be input.

            * ``Ndiv`` - If ``Lab`` is DIVX or DIVY, determines the number of divisions (1-99) that will be applied to the
              axis.

            * ``Kfont`` - If ``Lab`` is LTYP, ``Kfont`` is ON (1) or OFF(0). ON uses program-generated fonts for the axis
              labels, while OFF uses SYSTEM (Windows, X-system, etc.) fonts. Default: ``Kfont`` = ON (Mechanical APDL
              fonts).

        Notes
        -----

        .. _s-GROPT_notes:

        Sets various line graph display options. Issue :ref:`gropt`,STAT to display the current settings.

        Issue :ref:`gropt`,DEFA to reset default specifications.

        Unless you issue :ref:`gropt`,VIEW,ON, the program indicates that graph-view manipulation is
        inactive.

        See :ref:`axlab`, :ref:`grtyp`, :ref:`grid`, and :ref:`gthk` for other graph-control options.

        Automatic scaling using the :ref:`xrange` and :ref:`yrange` commands often yields inappropriate
        range values for logarithmic scales ( :ref:`gropt`, LOGX or :ref:`gropt`, LOGY).

        This command is valid in any processor.
        """
        command = f"/GROPT,{lab},{key}"
        return self.run(command, **kwargs)

    def grid(self, key: str = "", **kwargs):
        r"""Selects the type of grid on graph displays.

        Mechanical APDL Command: `/GRID <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GRID.html>`_

        Parameters
        ----------
        key : str
            Grid key:

            * ``0 (OFF)`` - No grid.

            * ``1 (ON)`` - Full grid (X and Y grid lines).

            * ``2 (X)`` - Partial grid (X grid lines only).

            * ``3 (Y)`` - Partial grid (Y grid lines only)

        Notes
        -----

        .. _s-GRID_notes:

        Selects the type of grid on graph displays. Graphs with multiple Y-axes can have multiple grids (
        :ref:`grtyp` ). The grid of the first curve is also used as the background grid (above and behind
        the curve). Grids for other curves are limited to be under the curves. See also :ref:`gthk` and
        :ref:`gropt` for other grid options.

        This command is valid in any processor.
        """
        command = f"/GRID,{key}"
        return self.run(command, **kwargs)

    def gthk(self, label: str = "", thick: int | str = "", **kwargs):
        r"""Sets line thicknesses for graph lines.

        Mechanical APDL Command: `/GTHK <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_GTHK.html>`_

        Parameters
        ----------
        label : str
            Apply thicknesses as selected from the following labels:

            * ``AXIS`` - Modify thickness of ordinate and abscissa axes on graph displays.

            * ``GRID`` - Modify thickness of grid lines on graph displays.

            * ``CURVE`` - Modify thickness of curve lines (when no area fill ( :ref:`gropt` )).

        thick : int or str
            Thickness ratio (whole numbers only, from -1 to 10):

            * ``-1`` - Do not draw the curve, but show only the markers specified by :ref:`gmarker`.

            * ``0 or 1`` - Thin lines.

            * ``2`` - The default thickness.

            * ``3`` - 1.5 times the default thickness.

            * ``etc.`` - (up to 10)

        Notes
        -----

        .. _s-GTHK_notes:

        Sets line thicknesses for graph lines (in raster mode only). Use :ref:`gthk`,STAT to show settings.

        This command is valid in any processor.
        """
        command = f"/GTHK,{label},{thick}"
        return self.run(command, **kwargs)
