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


class Selecting:

    def dofsel(
        self,
        type_: str = "",
        dof1: str = "",
        dof2: str = "",
        dof3: str = "",
        dof4: str = "",
        dof5: str = "",
        dof6: str = "",
        **kwargs,
    ):
        r"""Selects a DOF label set for reference by other commands.

        Mechanical APDL Command: `DOFSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_DOFSEL.html>`_

        **Command default:**

        .. _DOFSEL_default:

        Degree of freedom (and the corresponding force) labels are determined from the model.

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set of labels.

            * ``A`` - Add labels to the current set.

            * ``U`` - Unselect (remove) labels from the current set.

            * ``ALL`` - Restore the full set of labels.

            * ``STAT`` - Display the current select status.

        dof1 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        dof2 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        dof3 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        dof4 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        dof5 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        dof6 : str
            Used only with ``Type`` = S, A, or U. Valid lables are:

            **Structural labels** : UX, UY, or UZ (displacements); U (UX, UY, and UZ) ; ROTX, ROTY, or ROTZ
            (rotations); ROT (ROTX,
            ROTY, and ROTZ); DISP (U and ROT); HDSP (Hydrostatic pressure).
            **Thermal labels** : TEMP, TBOT, TE2, TE3...., TTOP (temperature).
            **Acoustic labels** : PRES (pressure); UX, UY, or UZ (displacements for FSI coupled elements).
            **Electric labels** : VOLT (voltage); EMF (electromotive force drop); CURR (current).
            **Magnetic labels** : MAG (scalar magnetic potential); AZ (vector magnetic potential); A (AZ); CURR
            (current).
            **Structural force labels** : FX, FY, or FZ (forces); F (FX, FY, and FZ); MX, MY, or MZ (moments); M
            (MX, MY, and MZ); FORC (F
            and M); DVOL (fluid mass flow rate).
            **Thermal force labels** : HEAT, HBOT, HE2, HE3...., HTOP (heat flow).
            **Fluid flow force label** : FLOW (fluid flow).
            **Electric force labels** : AMPS (current flow); CHRG (electric charge).
            **Magnetic force labels** : FLUX (scalar magnetic flux); CSGZ (magnetic current segment).
            **Diffusion labels** : CONC (concentration); RATE (diffusion flow rate).

        Notes
        -----

        .. _DOFSEL_notes:

        Selects a degree of freedom label set for reference by other commands. The label set is used on
        certain commands where ALL is either input in the degree of freedom label field or implied. The
        active label set has no effect on the solution degrees of freedom. Specified labels which are not
        active in the model (from the :ref:`et` or :ref:`dof` command) are ignored. As a convenience, a set
        of force labels corresponding to the degree of freedom labels is also selected. For example,
        selecting UX also causes FX to be selected (and vice versa). The force label set is used on certain
        commands where ALL is input in the force label field.

        This command is valid in any processor.
        """
        command = f"DOFSEL,{type_},{dof1},{dof2},{dof3},{dof4},{dof5},{dof6}"
        return self.run(command, **kwargs)

    def ksln(self, type_: str = "", **kwargs):
        r"""Selects those keypoints associated with the selected nodes.

        Mechanical APDL Command: `KSLN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSLN.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of keypoint select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _KSLN_notes:

        Valid only if the nodes were generated by a meshing operation ( :ref:`kmesh`, :ref:`lmesh`,
        :ref:`amesh`, :ref:`vmesh` ) on a solid model that contains the associated keypoints.

        This command is valid in any processor.
        """
        command = f"KSLN,{type_}"
        return self.run(command, **kwargs)

    def ksll(self, type_: str = "", **kwargs):
        r"""Selects those keypoints contained in the selected lines.

        Mechanical APDL Command: `KSLL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSLL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of keypoint select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _KSLL_notes:

        This command is valid in any processor.
        """
        command = f"KSLL,{type_}"
        return self.run(command, **kwargs)

    def ksel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kabs: str = "",
        **kwargs,
    ):
        r"""Selects a subset of keypoints or hard points.

        Mechanical APDL Command: `KSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        kabs : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KSEL.html>`_ for further
            information.

        Notes
        -----

        .. _KSEL_notes:

        Selects a subset of keypoints or hard points. For example, to select a new set of keypoints based on
        keypoint numbers 1 through 7, use :ref:`ksel`,S,KP,,1,7. The selected subset is used when the ALL
        label is entered (or implied) on other commands, such as :ref:`klist`,ALL. Only data identified by
        keypoint number are selected. Data are flagged as selected and unselected; no data are actually
        deleted from the database.

        This command is valid in any processor.

        For selections based on non-integer numbers (coordinates, results, etc.), items that are within the
        range ``VMIN`` - ``Toler`` and ``VMAX`` + ``Toler`` are selected. The default tolerance ``Toler`` is
        based on the relative values of ``VMIN`` and ``VMAX`` as follows:

        If ``VMIN`` = ``VMAX``, ``Toler`` = 0.005 x ``VMIN``.
        If ``VMIN`` = ``VMAX`` = 0.0, ``Toler`` = 1.0E-6.
        If ``VMAX`` ≠ ``VMIN``, ``Toler`` = 1.0E-8 x ( ``VMAX`` - ``VMIN`` ).

        Use the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command to override this default and specify ``Toler`` explicitly.

        **KSEL - Valid Item and Component Labels**

        .. flat-table:: Valid Item and Component Labels :ref:`ksel`, ``Type, Item, Comp, VMIN, VMAX, VINC,`` KABS
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - KP
             -
             - Keypoint number.
           * - EXT
             -
             - Keypoint numbers on exterior of selected lines (ignore remaining fields).
           * - HPT
             -
             - Hard point number.
           * - LOC
             - X,Y,Z
             - X, Y, or Z location in the active coordinate system.
           * - MAT
             -
             - Material number associated with the keypoint.
           * - TYPE
             -
             - Element type number associated with the keypoint.
           * - REAL
             -
             - Real constant set number associated with the keypoint.
           * - ESYS
             -
             - Element coordinate system associated with the keypoint.

        """
        command = f"KSEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kabs}"
        return self.run(command, **kwargs)

    def lslk(self, type_: str = "", lskey: int | str = "", **kwargs):
        r"""Selects those lines containing the selected keypoints.

        Mechanical APDL Command: `LSLK <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSLK.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of line select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        lskey : int or str
            Specifies whether all contained line keypoints must be selected ( :ref:`ksel` ):

            * ``0`` - Select line if any of its keypoints are in the selected keypoint set.

            * ``1`` - Select line only if all of its keypoints are in the selected keypoint set.

        Notes
        -----

        .. _LSLK_notes:

        This command is valid in any processor.
        """
        command = f"LSLK,{type_},{lskey}"
        return self.run(command, **kwargs)

    def lsla(self, type_: str = "", **kwargs):
        r"""Selects those lines contained in the selected areas.

        Mechanical APDL Command: `LSLA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSLA.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of line select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _LSLA_notes:

        This command is valid in any processor.
        """
        command = f"LSLA,{type_}"
        return self.run(command, **kwargs)

    def lsel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kswp: str = "",
        **kwargs,
    ):
        r"""Selects a subset of lines.

        Mechanical APDL Command: `LSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        kswp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LSEL.html>`_ for further
            information.

        Notes
        -----

        .. _LSEL_notes:

        Selects lines based on values of a labeled item and component. For example, to select a new set of
        lines based on line numbers 1 through 7, use :ref:`lsel`,S,LINE,,1,7. The subset is used when the
        ALL label is entered (or implied) on other commands, such as :ref:`llist`,ALL. Only data identified
        by line number are selected. Data are flagged as selected and unselected; no data are actually
        deleted from the database.

        If ``Item`` = LCCA, the command selects only those lines that were created by concatenation. The
        ``KSWP`` field is processed, but the ``Comp``, ``VMIN``, ``VMAX``, and ``VINC`` fields are ignored.

        If ``Item`` = HPT, the command selects only those lines that contain hard points.

        ``Item`` = RADIUS is only valid for lines that are circular arcs.

        :ref:`lsel` is valid in any processor.

        For selections  based on non-integer numbers (coordinates, results, etc.), items that are
        within the range ``VMIN`` - ``Toler`` and ``VMAX`` + ``Toler`` are selected. The default tolerance
        ``Toler`` is based on the relative values of ``VMIN`` and ``VMAX`` as follows:

        If ``VMIN`` = ``VMAX``, ``Toler`` = 0.005 x ``VMIN``.
        If ``VMIN`` = ``VMAX`` = 0.0, ``Toler`` = 1.0E-6.
        If ``VMAX`` ≠ ``VMIN``, ``Toler`` = 1.0E-8 x ( ``VMAX`` - ``VMIN`` ).

        Use the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command to override this default and specify ``Toler`` explicitly.

        **LSEL - Valid Item and Component Labels**

        .. flat-table:: Valid Item and Component Labels :ref:`lsel`, ``Type, Item, Comp, VMIN, VMAX, VINC, KSWP``
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - LINE
             -
             - Line number.
           * - EXT
             -
             - Line numbers on exterior of selected area (ignore remaining fields).
           * - LOC
             - X,Y,Z
             - X, Y, or Z center location in the active coordinate system.
           * - TAN1
             - X,Y,Z
             - Unit vector component of outward tangent at beginning of line.
           * - TAN2
             - X,Y,Z
             - Unit vector component of outward tangent at end of line.
           * - NDIV
             -
             - Number of divisions within the line.
           * - SPACE
             -
             - Spacing ratio of line divisions.
           * - MAT
             -
             - Material number associated with the line.
           * - TYPE
             -
             - Element type number associated with the line.
           * - REAL
             -
             - Real constant set number associated with the line.
           * - ESYS
             -
             - Element coordinate system associated with the line.
           * - SEC
             -
             - Cross section ID number. ( :ref:`secnum` )
           * - LENGTH
             -
             - Length of the line.
           * - RADIUS
             -
             - Radius of the line.
           * - HPT
             -
             - Line number (selects only lines with associated hard points).
           * - LCCA
             -
             - Concatenated lines (selects only lines that were created by concatenation ( :ref:`lccat` )).

        """
        command = f"LSEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kswp}"
        return self.run(command, **kwargs)

    def esll(self, type_: str = "", **kwargs):
        r"""Selects those elements associated with the selected lines.

        Mechanical APDL Command: `ESLL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESLL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of element select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _ESLL_notes:

        Selects line elements belonging to meshed ( :ref:`lmesh` ), selected ( :ref:`lsel` ) lines.

        This command is valid in any processor.
        """
        command = f"ESLL,{type_}"
        return self.run(command, **kwargs)

    def esln(self, type_: str = "", ekey: int | str = "", nodetype: str = "", **kwargs):
        r"""Selects those elements attached to the selected nodes.

        Mechanical APDL Command: `ESLN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESLN.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of element selected:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        ekey : int or str
            Node set key:

            * ``0`` - Select element if any of its nodes are in the selected nodal set (default).

            * ``1`` - Select element only if all of its nodes are in the selected nodal set.

        nodetype : str
            Label identifying type of nodes to consider when selecting:

            * ``ALL`` - Select elements considering all of their nodes (default).

            * ``ACTIVE`` - Select elements considering only their active nodes. An active node is a node that contributes DOFs
              to the model.

            * ``INACTIVE`` - Select elements considering only their inactive nodes (such as orientation or radiation nodes).

            * ``CORNER`` - Select elements considering only their corner nodes.

            * ``MID`` - Select elements considering only their midside nodes.

        Notes
        -----

        .. _ESLN_notes:

        :ref:`esln` selects elements which have any (or all ``EKEY`` )  ``NodeType`` nodes in the
        currently-selected set of nodes. Only elements having nodes in the currently-selected set can be
        selected.

        This command is valid in any processor.
        """
        command = f"ESLN,{type_},{ekey},{nodetype}"
        return self.run(command, **kwargs)

    def esla(self, type_: str = "", **kwargs):
        r"""Selects those elements associated with the selected areas.

        Mechanical APDL Command: `ESLA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESLA.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of element select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _ESLA_notes:

        Selects area elements belonging to meshed ( :ref:`amesh` ), selected ( :ref:`asel` ) areas.

        This command is valid in any processor.
        """
        command = f"ESLA,{type_}"
        return self.run(command, **kwargs)

    def eslv(self, type_: str = "", **kwargs):
        r"""Selects elements associated with the selected volumes.

        Mechanical APDL Command: `ESLV <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESLV.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of element selected:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _ESLV_notes:

        Selects volume elements belonging to meshed ( :ref:`vmesh` ), selected ( :ref:`vsel` ) volumes.

        This command is valid in any processor.
        """
        command = f"ESLV,{type_}"
        return self.run(command, **kwargs)

    def esel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kabs: str = "",
        **kwargs,
    ):
        r"""Selects a subset of elements.

        Mechanical APDL Command: `ESEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_

        **Command default:**

        .. _ESEL_default:

        All elements are selected.

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        kabs : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ESEL.html>`_ for further
            information.

        Notes
        -----

        .. _ESEL_notes:

        Selects elements based on values of a labeled item and component. For example, to select a new set
        of elements based on element numbers 1 through 7, use :ref:`esel`,S,ELEM,,1,7. The subset is used
        when the ALL label is entered (or implied) on other commands, such as :ref:`elist`,ALL. Only data
        identified by element number are selected. Selected data are internally flagged; no actual removal
        of data from the database occurs. Different element subsets cannot be used for different load steps
        ( :ref:`solve` ) in a :ref:`slashsolu` sequence. The subset used in the first load step is used for
        all subsequent load steps regardless of subsequent :ref:`esel` specifications.

        This command is valid in any processor.

        Elements crossing the named path ( :ref:`path` ) are selected. This option is available only in
        PREP7 and POST1. If no geometry data has been mapped to the path (via :ref:`pmap` and :ref:`pdef`,
        for example), the path assumes the default mapping option ( :ref:`pmap`,UNIFORM) to map the geometry
        prior to selecting the elements. If an invalid path name is given, the :ref:`esel` command is
        ignored (and the status of selected elements is unchanged). If no elements are crossing the path,
        the :ref:`esel` command returns zero elements selected.

        For selections based on non-integer numbers (coordinates, results, etc.), items that are within the
        range ``VMIN`` - ``Toler`` and ``VMAX`` + ``Toler`` are selected. The default tolerance ``Toler`` is
        based on the relative values of ``VMIN`` and ``VMAX`` as follows:

        If ``VMIN`` = ``VMAX``, ``Toler`` = 0.005 x ``VMIN``.
        If ``VMIN`` = ``VMAX`` = 0.0, ``Toler`` = 1.0E-6.
        If ``VMAX`` ≠ ``VMIN``, ``Toler`` = 1.0E-8 x ( ``VMAX`` - ``VMIN`` ).

        To override this default and specify ``Toler`` explicitly, issue the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command.

        **ESEL - Valid Item and Component Labels**

        .. flat-table:: Valid Item and Component Labels :ref:`esel`, ``Type, Item, Comp, VMIN, VMAX, VINC, KABS``
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - ELEM
             -
             - Element number.
           * - ADJ
             -
             - Elements adjacent to element ``VMIN`` ( ``VMAX`` and ``VINC`` fields are ignored). Only elements (of the same dimensionality) adjacent to lateral faces are considered. Progression continues until edge of model or until more than two elements are adjacent at a face.
           * - CENT
             - X, Y, Z
             - X, Y, or Z location in the active coordinate system.
           * - TYPE
             -
             - Element type number.
           * - ENAME
             -
             - Element name (or identifying number).
           * - MAT
             -
             - Material ID number.
           * - REAL
             - (blank)
             - Real constant number.
           * - ESYS
             -
             - Element coordinate system number.
           * - OVER
             -
             - Overlapping contact elements created during contact pair splitting ( :ref:`cncheck`,SPLIT/DMP)
           * - LIVE
             -
             - Active elements ( :ref:`ealive` ). ``VMIN`` and ``VMAX`` fields are ignored.
           * - LAYER
             -
             - Layer number (where only composite elements with a nonzero thickness for the requested layer number are included) ( :ref:`layer` ).
           * - SEC
             - (blank)
             - Cross section ID number ( :ref:`secnum` )
           * - STRA
             -
             - Straightened. See the description of the ``Item`` argument above.
           * - SFE
             - PRES
             - Element pressure.
           * - BFE
             - TEMP
             - Element temperature.
           * - PATH
             - ``Lab``
             - Selects all elements being crossed by the path with name ``Lab`` ( :ref:`path` ). If ``Lab`` = ALL, all elements related to all defined paths are selected.
           * - Valid item and component labels for element result values are:
           * - ETAB
             - ``Lab``
             - Any user-defined element table label ( :ref:`etable` ).

        """
        command = f"ESEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kabs}"
        return self.run(command, **kwargs)

    def nslk(self, type_: str = "", **kwargs):
        r"""Selects those nodes associated with the selected keypoints.

        Mechanical APDL Command: `NSLK <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSLK.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of node select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _NSLK_notes:

        Valid only if the nodes were generated by a keypoint meshing operation ( :ref:`kmesh`, :ref:`lmesh`,
        :ref:`amesh`, :ref:`vmesh` ) on a solid model that contains the selected keypoints.

        This command is valid in any processor.
        """
        command = f"NSLK,{type_}"
        return self.run(command, **kwargs)

    def nsle(self, type_: str = "", nodetype: str = "", num: str = "", **kwargs):
        r"""Selects those nodes attached to the selected elements.

        Mechanical APDL Command: `NSLE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSLE.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of node select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        nodetype : str
            Label identifying type of nodes to consider when selecting:

            * ``ALL`` - Select all nodes of the selected elements (default).

            * ``ACTIVE`` - Select only the active nodes. An active node is a node that contributes DOFs to the model.

            * ``INACTIVE`` - Select only inactive nodes (such as orientation or radiation).

            * ``CORNER`` - Select only corner nodes.

            * ``MID`` - Select only midside nodes.

            * ``POS`` - Select nodes in position Num.

            * ``FACE`` - Select nodes on face Num.

        num : str
            Position or face number for NodeType  = POS or FACE.

        Notes
        -----

        .. _NSLE_notes:

        :ref:`nsle` selects ``NodeType`` nodes attached to the currently-selected set of elements. Only
        nodes on elements in the currently-selected element set can be selected.

        When using degenerate hexahedral elements, :ref:`nsle`, ``U``, ``CORNER`` and :ref:`nsle`, ``S``,
        ``MID`` will not select the same set of nodes because some nodes appear as both corner and midside
        nodes.

        This command is valid in any processor.
        """
        command = f"NSLE,{type_},{nodetype},{num}"
        return self.run(command, **kwargs)

    def nsll(self, type_: str = "", nkey: int | str = "", **kwargs):
        r"""Selects those nodes associated with the selected lines.

        Mechanical APDL Command: `NSLL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSLL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of node select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        nkey : int or str
            Specifies whether only interior line nodes are to be selected:

            * ``0`` - Select only nodes interior to selected lines.

            * ``1`` - Select all nodes (interior to line and at keypoints) associated with the selected lines.

        Notes
        -----

        .. _NSLL_notes:

        Valid only if the nodes were generated by a line meshing operation ( :ref:`lmesh`, :ref:`amesh`,
        :ref:`vmesh` ) on a solid model that contains the associated lines.

        This command is valid in any processor.
        """
        command = f"NSLL,{type_},{nkey}"
        return self.run(command, **kwargs)

    def nsla(self, type_: str = "", nkey: int | str = "", **kwargs):
        r"""Selects those nodes associated with the selected areas.

        Mechanical APDL Command: `NSLA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSLA.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of node select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        nkey : int or str
            Specifies whether only interior area nodes are to be selected:

            * ``0`` - Select only nodes interior to selected areas.

            * ``1`` - Select all nodes (interior to area, interior to lines, and at keypoints) associated with the
              selected areas.

        Notes
        -----

        .. _NSLA_notes:

        Valid only if the nodes were generated by an area meshing operation ( :ref:`amesh`, :ref:`vmesh` )
        on a solid model that contains the selected areas.

        This command is valid in any processor.
        """
        command = f"NSLA,{type_},{nkey}"
        return self.run(command, **kwargs)

    def nsel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kabs: str = "",
        **kwargs,
    ):
        r"""Selects a subset of nodes.

        Mechanical APDL Command: `NSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        kabs : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSEL.html>`_ for further
            information.

        Notes
        -----

        .. _NSEL_notes:

        Selects a subset of nodes. For example, to select a new set of nodes based on node numbers 1 through
        7, use :ref:`nsel`,S,NODE,,1,7. The subset is used when the ALL label is entered (or implied) on
        other commands, such as :ref:`nlist`,ALL. Only data identified by node number are selected. Data are
        flagged as selected and unselected; no data are actually deleted from the database.

        When selecting nodes by results, the full graphics value is used, regardless of whether
        PowerGraphics is on.

        Solution result data consists of two types, 1) nodal degree of freedom--results initially calculated
        at the nodes (such as displacement, temperature, pressure, etc.), and 2) element--results initially
        calculated elsewhere (such as at an element integration point or thickness location) and then
        recalculated at the nodes (such as stresses, strains, etc.). Various element results also depend
        upon the recalculation method and the selected results location ( :ref:`avprin`, :ref:`rsys`,
        :ref:`force`, :ref:`layer` and :ref:`shell` ).

        You must have all the nodes (corner and midside nodes) on the external face of the element selected
        to use ``Item`` = EXT.

        This command is valid in any processor.

        For Selects based on non-integer numbers (coordinates, results, etc.), items that are within the
        range VMIN- ``Toler`` and VMAX+ ``Toler`` are selected. The default tolerance ``Toler`` is based on
        the relative values of VMIN and VMAX as follows:

        If VMIN = VMAX, ``Toler`` = 0.005 x VMIN.
        If VMIN = VMAX = 0.0, ``Toler`` = 1.0E-6.
        If VMAX ≠ VMIN, ``Toler`` = 1.0E-8 x (VMAX-VMIN).

        Use the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command to override this default and specify ``Toler`` explicitly.

        **NSEL - Valid Item and Component Labels**

        .. flat-table:: Valid Item and Component Labels :ref:`nsel`, ``Type,Item,Comp,VMIN,VMAX,VINC,KABS``
           :header-rows: 2

           * - Valid item and component labels for input values are:
           * - Item
             - Comp
             - Description
           * - NODE
             -
             - Node number.
           * - EXT
             -
             - Nodes on exterior of selected elements (ignore remaining fields).
           * - LOC
             - X, Y, Z
             - X, Y, or Z location in the active coordinate system.
           * - ANG
             - XY, YZ, ZX
             - THXY, THYZ, or THZX rotation angle.
           * - M
             -
             - Master node number.
           * - CP
             -
             - Coupled set number.
           * - CE
             -
             - Constraint equation set number.
           * - D
             - U
             - Any of X, Y, or Z structural displacements. Amplitude only, if complex.
           * - "
             - UX, UY, UZ
             - X, Y, or Z structural displacement. Amplitude only, if complex.
           * - "
             - ROT
             - Any of X, Y, or Z structural rotations. Amplitude only, if complex.
           * - "
             - ROTX, ROTY, ROTZ
             - X, Y, or Z structural rotation. Amplitude only, if complex.
           * - "
             - TEMP, TBOT, TE2, TE3,..., TTOP
             - Temperature.
           * - "
             - PRES
             - Pressure (for example, PRES degree of freedom for acoustic elements).
           * - "
             - VOLT
             - Electric potential.
           * - "
             - MAG
             - Magnetic scalar potential.
           * - "
             - V
             - Any of X, Y, or Z fluid velocities.
           * - "
             - VX, VY, VZ
             - X, Y, or Z fluid velocity.
           * - "
             - AZ
             - 2D magnetic vector potential. Amplitude only, if complex.
           * - "
             - CURR
             - Current.
           * - "
             - EMF
             - Electromotive force drop.
           * - F
             - F
             - Any of X, Y, or Z structural forces. Amplitude only, if complex.
           * - "
             - FX, FY, FZ
             - X, Y, or Z structural force. Amplitude only, if complex.
           * - "
             - M
             - Any of X, Y, or Z structural moments. Amplitude only, if complex
           * - "
             - MX, MY, MZ
             - X, Y, or Z structural moment. Amplitude only, if complex.
           * - "
             - HEAT, HBOT, HE2, HE3,..., HTOP
             - Heat flow.
           * - "
             - FLOW
             - Fluid flow.
           * - "
             - AMPS
             - Current flow.
           * - "
             - FLUX
             - Magnetic flux.
           * - "
             - CSGZ
             - Magnetic current segment component. Amplitude only, if complex.
           * - "
             - CHRG
             - Electric charge.
           * - "
             - CHRGD
             - Electric charge density.
           * - BF
             - TEMP
             - Nodal temperature.
           * - "
             - FLUE
             - Nodal fluence.
           * - "
             - HGEN
             - Nodal heat generation rate.
           * - "
             - JS
             - Any of X, Y, or Z current densities. Amplitude only, if complex.
           * - "
             - JSX, JSY, JSZ
             - X, Y, or Z current density. Amplitude only, if complex.
           * - "
             - MVDI
             - Magnetic virtual displacements flag.
           * - "
             - DGEN
             - Nodal diffusing substance generation rate.

        **NSEL - Valid Item and Component Labels for Nodal DOF Result Values**

        .. flat-table::
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - U
             - X, Y, Z, SUM
             - X, Y, or Z structural displacement or vector sum.
           * - ROT
             - X, Y, Z, SUM
             - X, Y, or Z structural rotation or vector sum.
           * - TEMP
             -
             - Temperature.
           * - PRES
             -
             - Pressure.
           * - VOLT
             -
             - Electric potential.
           * - MAG
             -
             - Magnetic scalar potential.
           * - V
             - X, Y, Z, SUM
             - X, Y, or Z fluid velocity or vector sum.
           * - A
             - X, Y, Z, SUM
             - X, Y, or Z magnetic vector potential or vector sum.
           * - CONC
             -
             - Concentration.
           * - CURR
             -
             - Current.
           * - EMF
             -
             - Electromotive force drop.

        **NSEL - Valid Item and Component Labels for Element Result Values**

        .. flat-table::
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - S
             - X, Y, Z, XY, YZ, XZ
             - Component stress.
           * - "
             - 1, 2, 3
             - Principal stress.
           * - "
             - INT, EQV
             - Stress intensity or equivalent stress.
           * - EPTO
             - X, Y, Z, XY, YZ, XZ
             - Component total strain (EPEL + EPPL + EPCR).
           * - "
             - 1,2,3
             - Principal total strain.
           * - "
             - INT, EQV
             - Total strain intensity or total equivalent strain.
           * - EPEL
             - X, Y, Z, XY, YZ, XZ
             - Component elastic strain.
           * - "
             - 1, 2, 3
             - Principal elastic strain.
           * - "
             - INT, EQV
             - Elastic strain intensity or elastic equivalent strain.
           * - EPPL
             - X, Y, Z, XY, YZ, XZ
             - Component plastic strain.
           * - "
             - 1,2,3
             - Principal plastic strain.
           * - "
             - INT, EQV
             - Plastic strain intensity or plastic equivalent strain.
           * - EPCR
             - X, Y, Z, XY, YZ, XZ
             - Component creep strain.
           * - "
             - 1,2,3
             - Principal creep strain.
           * - "
             - INT, EQV
             - Creep strain intensity or creep equivalent strain.
           * - EPTH
             - X, Y, Z, XY, YZ, XZ
             - Component thermal strain.
           * - "
             - 1, 2, 3
             - Principal thermal strain.
           * - "
             - INT, EQV
             - Thermal strain intensity or thermal equivalent strain.
           * - EPSW
             -
             - Swelling strain.
           * - EPDI
             - X, Y, Z, XY, YZ, XZ
             - Component diffusion strain.
           * - "
             - 1, 2, 3
             - Principal diffusion strain.
           * - "
             - INT, EQV
             - Diffusion strain intensity or diffusion equivalent strain.
           * - NL
             - SEPL
             - Equivalent stress (from stress-strain curve).
           * - "
             - SRAT
             - Stress state ratio.
           * - "
             - HPRES
             - Hydrostatic pressure.
           * - "
             - EPEQ
             - Accumulated equivalent plastic strain.
           * - "
             - PSV
             - Plastic state variable.
           * - "
             - PLWK
             - Plastic work/volume.
           * - CONT
             - STAT
             - Contact status.
           * - "
             - PENE
             - Contact penetration.
           * - "
             - PRES
             - Contact pressure.
           * - "
             - SFRIC
             - Contact friction stress.
           * - "
             - STOT
             - Contact total stress (pressure plus friction).
           * - "
             - SLIDE
             - Contact sliding distance.
           * - TG
             - X, Y, Z, SUM
             - Component thermal gradient or vector sum.
           * - TF
             - X, Y, Z, SUM
             - Component thermal flux or vector sum.
           * - PG
             - X, Y, Z, SUM
             - Component pressure gradient or vector sum.
           * - EF
             - X, Y, Z, SUM
             - Component electric field or vector sum.
           * - D
             - X, Y, Z, SUM
             - Component electric flux density or vector sum.
           * - H
             - X, Y, Z, SUM
             - Component magnetic field intensity or vector sum.
           * - B
             - X, Y, Z, SUM
             - Component magnetic flux density or vector sum.
           * - CG
             - X, Y, Z, SUM
             - Component concentration gradient or vector sum
           * - DF
             - X, Y, Z, SUM
             - Component diffusion flux density or vector sum
           * - FMAG
             - X, Y, Z, SUM
             - Component electromagnetic forces or vector sum.

        For more information on the meaning of contact status and its possible values, see `Reviewing
        Results in POST1
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_ctec/Hlp_ctec_revresu.html#ctecpostslide>`_
        """
        command = f"NSEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kabs}"
        return self.run(command, **kwargs)

    def nslv(self, type_: str = "", nkey: int | str = "", **kwargs):
        r"""Selects those nodes associated with the selected volumes.

        Mechanical APDL Command: `NSLV <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NSLV.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of node select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        nkey : int or str
            Specifies whether only interior volume nodes are to be selected:

            * ``0`` - Select only nodes interior to selected volumes.

            * ``1`` - Select all nodes (interior to volume, interior to areas, interior to lines, and at keypoints)
              associated with the selected volumes.

        Notes
        -----

        .. _NSLV_notes:

        Valid only if the nodes were generated by a volume meshing operation ( :ref:`vmesh` ) on a solid
        model that contains the selected volumes.

        This command is valid in any processor.
        """
        command = f"NSLV,{type_},{nkey}"
        return self.run(command, **kwargs)

    def vsel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kswp: str = "",
        **kwargs,
    ):
        r"""Selects a subset of volumes.

        Mechanical APDL Command: `VSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of volume select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        kswp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSEL.html>`_ for further
            information.

        Notes
        -----

        .. _VSEL_notes:

        Selects volumes based on values of a labeled item and component. For example, to select a new set of
        volumes based on volume numbers 1 through 7, use :ref:`vsel`,S,VOLU,,1,7. The subset is used when
        the ALL label is entered (or implied) on other commands, such as :ref:`vlist`,ALL. Only data
        identified by volume number are selected. Data are flagged as selected and unselected; no data are
        actually deleted from the database.

        This command is valid in any processor.

        For Selects based on non-integer numbers (coordinates, results, etc.), items that are within the
        range VMIN- ``Toler`` and VMAX+ ``Toler`` are selected. The default tolerance ``Toler`` is based on
        the relative values of VMIN and VMAX as follows:

        If VMIN = VMAX, ``Toler`` = 0.005 x VMIN.
        If VMIN = VMAX = 0.0, ``Toler`` = 1.0E-6.
        If VMAX ≠ VMIN, ``Toler`` = 1.0E-8 x (VMAX-VMIN).

        Use the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command to override this default and specify ``Toler`` explicitly.

        **VSEL - Valid Item and Component Labels**

        .. flat-table:: :ref:`vsel`  ``Type, Item, Comp, VMIN, VMAX, VINC, KABS``
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - VOLU
             -
             - Volume number.
           * - LOC
             - X, Y, Z
             - X, Y, or Z center (picking "hot spot" location in the active coordinate system).
           * - MAT
             -
             - Material number associated with the volume.
           * - TYPE
             -
             - Element type number associated with the volume.
           * - REAL
             -
             - Real constant set number associated with the volume.
           * - ESYS
             -
             - Element coordinate system associated with the volume.

        """
        command = f"VSEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kswp}"
        return self.run(command, **kwargs)

    def vsla(self, type_: str = "", vlkey: int | str = "", **kwargs):
        r"""Selects those volumes containing the selected areas.

        Mechanical APDL Command: `VSLA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_VSLA.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of volume select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        vlkey : int or str
            Specifies whether all contained volume areas must be selected ( :ref:`asel` ):

            * ``0`` - Select volume if any of its areas are in the selected area set.

            * ``1`` - Select volume only if all of its areas are in the selected area set.

        Notes
        -----

        .. _VSLA_notes:

        This command is valid in any processor.
        """
        command = f"VSLA,{type_},{vlkey}"
        return self.run(command, **kwargs)

    def asll(self, type_: str = "", arkey: int | str = "", **kwargs):
        r"""Selects those areas containing the selected lines.

        Mechanical APDL Command: `ASLL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASLL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of area select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        arkey : int or str
            Specifies whether all contained area lines must be selected ( :ref:`lsel` ):

            * ``0`` - Select area if any of its lines are in the selected line set.

            * ``1`` - Select area only if all of its lines are in the selected line set.

        Notes
        -----

        .. _ASLL_notes:

        This command is valid in any processor.
        """
        command = f"ASLL,{type_},{arkey}"
        return self.run(command, **kwargs)

    def allsel(self, labt: str = "", entity: str = "", **kwargs):
        r"""Selects all entities with a single command.

        Mechanical APDL Command: `ALLSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ALLSEL.html>`_

        Parameters
        ----------
        labt : str
            Type of selection to be made:

            * ``ALL`` - Selects all items of the specified entity type and all items of lower entity types (default).

            * ``BELOW`` - Selects all items directly associated with and below the selected items of the specified entity
              type.

        entity : str
            Entity type on which selection is based:

            * ``ALL`` - All entity types (default).

            * ``VOLU`` - Volumes.

            * ``AREA`` - Areas.

            * ``LINE`` - Lines.

            * ``KP`` - Keypoints.

            * ``ELEM`` - Elements.

            * ``NODE`` - Nodes.

        Notes
        -----

        .. _ALLSEL_notes:

        :ref:`allsel` is a convenience command that allows the user to select all items of a specified
        entity type or to select items associated with the selected items of a higher entity.

        An entity hierarchy is used to decide what entities will be available in the selection process. This
        hierarchy from top to bottom is as follows: volumes, areas, lines, keypoints, elements, and nodes.
        The hierarchy may also be divided into two branches: the solid model and the finite element model.
        The label ALL selects items based on one branch only, while BELOW uses the entire entity hierarchy.
        For example, :ref:`allsel`,ALL,VOLU selects all volumes, areas, lines, and keypoints in the data
        base. :ref:`allsel`,BELOW,AREA selects all lines belonging to the selected areas; all keypoints
        belonging to those lines; all elements belonging to those areas, lines, and keypoints; and all nodes
        belonging to those elements.

        The $ character should not be used after the :ref:`allsel` command.

        This command is valid in any processor.
        """
        command = f"ALLSEL,{labt},{entity}"
        return self.run(command, **kwargs)

    def aslv(self, type_: str = "", **kwargs):
        r"""Selects those areas contained in the selected volumes.

        Mechanical APDL Command: `ASLV <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASLV.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of area select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

        Notes
        -----

        .. _ASLV_notes:

        This command is valid in any processor.
        """
        command = f"ASLV,{type_}"
        return self.run(command, **kwargs)

    def asel(
        self,
        type_: str = "",
        item: str = "",
        comp: str = "",
        vmin: str = "",
        vmax: str = "",
        vinc: str = "",
        kswp: str = "",
        **kwargs,
    ):
        r"""Selects a subset of areas.

        Mechanical APDL Command: `ASEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_

        **Command default:**

        .. _ASEL_default:

        All areas are selected.

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default)

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Restore the full set.

            * ``NONE`` - Unselect the full set.

            * ``INVE`` - Invert the current set (selected becomes unselected and vice versa).

            * ``STAT`` - Display the current select status.

        item : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        comp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        vmin : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        vmax : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        vinc : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        kswp : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_ASEL.html>`_ for further
            information.

        Notes
        -----

        .. _ASEL_notes:

        Selects a subset of areas. For example, to select those areas with area numbers 1 through 7, use
        :ref:`asel`,S,AREA,,1,7. The selected subset is then used when the ALL label is entered (or implied)
        on other commands, such as :ref:`alist`,ALL. Only data identified by area number are selected. Data
        are flagged as selected and unselected; no data are actually deleted from the database.

        In a cyclic symmetry analysis, area hot spots can be modified. Consequently, the result of an area
        selection may be different before and after the :ref:`cyclic` command.

        If ``Item`` = ACCA, the command selects only those areas that were created by concatenation. The
        ``KSWP`` field is processed, but the ``Comp``, ``VMIN``, ``VMAX``, and ``VINC`` fields are ignored.

        This command is valid in any processor.

        For Selects based on non-integer numbers (coordinates, results, etc.), items that are within the
        range VMIN- ``Toler`` and VMAX+ ``Toler`` are selected. The default tolerance ``Toler`` is based on
        the relative values of VMIN and VMAX as follows:

        If VMIN = VMAX, ``Toler`` = 0.005 x VMIN.
        If VMIN = VMAX = 0.0, ``Toler`` = 1.0E-6.
        If VMAX ≠ VMIN, ``Toler`` = 1.0E-8 x (VMAX-VMIN).

        Use the `SELTOL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_SELTOL.html#SELTOL.menupath>`_
        :ref:`seltol` command to override this default and specify ``Toler`` explicitly.

        **ASEL - Valid Item and Component Labels**

        .. flat-table:: Valid Item and Component Labels :ref:`asel`, ``Type Item,Comp,VMIN,VMAX,VINC,KSWP``
           :header-rows: 1

           * - Item
             - Comp
             - Description
           * - AREA
             -
             - Area number.
           * - EXT
             -
             - Area numbers on exterior of selected volumes (ignore remaining fields).
           * - LOC
             - X, Y, Z
             - X, Y, or Z center (picking "hot spot" location in the active coordinate system).
           * - HPT
             -
             - Area number (selects only areas with associated hard points).
           * - MAT
             -
             - Material number associated with the area.
           * - TYPE
             -
             - Element type number associated with the area.
           * - REAL
             -
             - Real constant set number associated with the area.
           * - ESYS
             -
             - Element coordinate system associated with the area.
           * - SECN
             -
             - Section number associated with the area.
           * - ACCA
             -
             - Concatenated areas (selects only areas that were created by area concatenation ( :ref:`accat` )).

        """
        command = f"ASEL,{type_},{item},{comp},{vmin},{vmax},{vinc},{kswp}"
        return self.run(command, **kwargs)

    def seltol(self, toler: str = "", **kwargs):
        r"""Sets the tolerance for subsequent select operations.

        Mechanical APDL Command: `SELTOL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SELTOL.html>`_

        Parameters
        ----------
        toler : str
            Tolerance value. If blank, restores the default tolerance logic.

        Notes
        -----
        For selects based on non-integer numbers (e.g. coordinates, results, etc.), items within the range
        VMIN - ``Toler`` and VMAX + ``Toler`` are selected, where VMIN and VMAX are the range values input
        on the xSEL commands ( `ASEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_ASEL.html#ASEL.menupath>`_
        :ref:`asel`, `ESEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_ESEL.html#ESEL.menupath>`_
        :ref:`esel`, `KSEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_KSEL.html#KSEL.menupath>`_
        :ref:`ksel`, `LSEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_LSEL.html#LSEL.menupath>`_
        :ref:`lsel`, `NSEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_NSEL.html#NSEL.menupath>`_
        :ref:`nsel`, and `VSEL
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_VSEL.html#VSEL.menupath>`_
        :ref:`vsel` ).

        The default tolerance logic is based on the relative values of VMIN and VMAX as follows:

        If VMIN = VMAX, ``Toler`` = 0.005 x VMIN.
        If VMIN = VMAX = 0.0, ``Toler`` = 1.0E-6.
        If VMAX ≠ VMIN, ``Toler`` = 1.0E-8 x (VMAX-VMIN).

        This command is typically used when VMAX-VMIN is very large so that the computed default tolerance
        is therefore large and the xSEL  commands selects more than what is desired.

        ``Toler`` remains active until respecified by a subsequent :ref:`seltol` command. A :ref:`seltol` <
        blank > resets back to the default ``Toler`` logic.
        """
        command = f"SELTOL,{toler}"
        return self.run(command, **kwargs)
