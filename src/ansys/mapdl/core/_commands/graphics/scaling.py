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


class Scaling:

    def icscale(self, wn: str = "", factor: str = "", **kwargs):
        r"""Scales the icon size for elements supported in the circuit builder.

        Mechanical APDL Command: `/ICSCALE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ICSCALE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        factor : str
            Factor applied to the default icon size (defaults to 1).

        Notes
        -----

        .. _s-ICSCALE_notes:

        Scaling the icon size can provide better visualization of the circuit components when using the
        Circuit Builder (an interactive builder available in the Mechanical APDL GUI).
        """
        command = f"/ICSCALE,{wn},{factor}"
        return self.run(command, **kwargs)

    def iclwid(self, factor: str = "", **kwargs):
        r"""Scales the line width of circuit builder icons.

        Mechanical APDL Command: `/ICLWID <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ICLWID.html>`_

        Parameters
        ----------
        factor : str
            Multiplication factor applied to the default line width (defaults to 1). The minimum is 1 and
            the maximum is 6.
        """
        command = f"/ICLWID,{factor}"
        return self.run(command, **kwargs)

    def slashdscale(self, wn: str = "", dmult: int | str = "", **kwargs):
        r"""Sets the displacement multiplier for displacement displays.

        Mechanical APDL Command: `/DSCALE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_DSCALE_sl.html>`_

        **Command default:**

        .. _s-DSCALE_default:

        The default value is AUTO or 0 except when:

        Large deflection effects are included ( :ref:`nlgeom`,ON) and it is not a modal analysis; then the
        default is 1. It is a spectrum analysis ( :ref:`antype`,SPECTR); then the default is OFF. The
        amplitude of a time-harmonic solution is computed using the :ref:`hrcplx` command (OMEGAT _font
        FamName="Agency FB"? ≥ /_font? 360 _font FamName="Agency FB"? ° /_font? ); then the default is OFF.
        The amplitude of a complex modal or harmonic solution is stored into the database using the
        :ref:`set` command ( ``KIMG`` = AMPL); then the default is OFF.

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        dmult : int or str

            * ``AUTO or 0`` - Scale displacements automatically so that maximum displacement (vector amplitude) displays as 5
              percent of the maximum model length, as measured in the global Cartesian X, Y, or Z directions.

            * ``1`` - Do not scale displacements (that is, scale displacements by 1.0, true to geometry). Often used with
              large deflection results.

            * ``FACTOR`` - Scale displacements by numerical value input for FACTOR.

            * ``OFF`` - Remove displacement scaling (that is, scale displacements by 0.0, no distortion).

            * ``USER`` - Set ``DMULT`` to that used for last display (useful when last ``DMULT`` value was automatically
              calculated).

        Notes
        -----

        .. _s-DSCALE_notes:

        If Multi-Plots are not being displayed, and the current device is a 3D device ( :ref:`show`,3D),
        then the displacement scale in all active windows will be the same, even if separate
        :ref:`slashdscale` commands are issued for each active window. For efficiency, the program maintains
        a single data structure (segment) containing only one displacement scale. The program displays the
        same segment (displacement scale) in all windows. Only the view settings will be different in each
        of the active windows.

        This command is valid in any processor.
        """
        command = f"/DSCALE,{wn},{dmult}"
        return self.run(command, **kwargs)

    def ratio(self, wn: str = "", ratox: str = "", ratoy: str = "", **kwargs):
        r"""Distorts the object geometry.

        Mechanical APDL Command: `/RATIO <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_RATIO.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        ratox : str
            Distort object in the window X direction by this factor (defaults to 1.0).

        ratoy : str
            Distort object in the window Y direction by this factor (defaults to 1.0).

        Notes
        -----

        .. _s-RATIO_notes:

        Distorts the object geometry in a particular direction. An example of this command's use would be to
        allow long narrow sections to be distorted to a more square area for better display visualization.

        This command is valid in any processor.
        """
        command = f"/RATIO,{wn},{ratox},{ratoy}"
        return self.run(command, **kwargs)

    def vscale(self, wn: str = "", vratio: str = "", key: int | str = "", **kwargs):
        r"""Scales the length of displayed vectors.

        Mechanical APDL Command: `/VSCALE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSCALE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        vratio : str
            Ratio value applied to the automatically calculated scale factor (defaults to 1.0, that is, use
            scale factor as automatically calculated).

        key : int or str
            Relative scaling key:

            * ``0`` - Use relative length scaling among vectors based on magnitudes.

            * ``1`` - Use uniform length scaling for all vector lengths.

        Notes
        -----

        .. _s-VSCALE_notes:

        Allows scaling of the vector length displayed with the :ref:`plvect` command of POST1 and the
        :ref:`pbc` and :ref:`psf` commands. Also allows the scaling of the element (that is,
        :ref:`psymb`,ESYS) and the nodal (that is, :ref:`psymb`,NDIR) coordinate system symbols.

        This command is valid in any processor.
        """
        command = f"/VSCALE,{wn},{vratio},{key}"
        return self.run(command, **kwargs)

    def sscale(self, wn: str = "", smult: str = "", **kwargs):
        r"""Sets the contour multiplier for topographic displays.

        Mechanical APDL Command: `/SSCALE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SSCALE.html>`_

        Parameters
        ----------
        wn : str
            Window number (or ALL) to which command applies (defaults to 1).

        smult : str
            Contour multiplier that factors in results based on the product of the multiplier and the result
            being plotted. Defaults to 0.0 (no topographic effects).

        Notes
        -----

        .. _s-SSCALE_notes:

        Use this command to scale values to the geometry when the contours are shown elevated. For section
        displays ( :ref:`slashtype` ), the elevation is performed perpendicular to the section face.

        Nonzero contour multipliers factoring in large results (stresses or displacements) can produce very
        large distortion, causing images to disappear. To bring a distorted image back into view, reduce the
        contour multiplier value.

        Portions of this command are not supported by PowerGraphics ( :ref:`graphics`,POWER).
        """
        command = f"/SSCALE,{wn},{smult}"
        return self.run(command, **kwargs)

    def shrink(self, ratio: str = "", **kwargs):
        r"""Shrinks elements, lines, areas, and volumes for display clarity.

        Mechanical APDL Command: `/SHRINK <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SHRINK.html>`_

        Parameters
        ----------
        ratio : str
            Shrinkage ratio (input as a decimal (0.0 to 0.5)). Defaults to 0.0 (no shrinkage). Values
            greater than 0.5 default to 0.1 (10% shrinkage).

        Notes
        -----

        .. _s-SHRINK_notes:

        Shrinks the elements, lines, areas, and volumes so that adjacent entities are separated for clarity.
        Portions of this command are not supported by PowerGraphics ( :ref:`graphics`,POWER).

        If only the common lines of non-coplanar faces are drawn (as per the :ref:`edge` command), then this
        command is ignored.

        This command is valid in any processor.
        """
        command = f"/SHRINK,{ratio}"
        return self.run(command, **kwargs)
