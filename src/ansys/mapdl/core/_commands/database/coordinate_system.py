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


class CoordinateSystem:

    def csys(self, kcn: int | str = "", **kwargs):
        r"""Activates a previously defined coordinate system.

        Mechanical APDL Command: `CSYS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSYS.html>`_

        Parameters
        ----------
        kcn : int or str
            Specifies the active coordinate system, as follows:

            * ``0 (default)`` - Cartesian

            * ``1`` - Cylindrical with global Cartesian Z as the axis of rotation

            * ``2`` - Spherical

            * ``4 or WP`` - Working Plane

            * ``5`` - Cylindrical with global Cartesian Y as the axis of rotation

            * ``6`` - Cylindrical with global Cartesian X as the axis of rotation

            * ``11 or greater`` - Any previously defined local coordinate system

        Notes
        -----

        .. _CSYS_notes:

        The :ref:`csys` command activates a previously defined coordinate system for geometry input and
        generation. The :ref:`local`, :ref:`clocal`, :ref:`cs`, :ref:`cskp`, and :ref:`cswpla` commands also
        activate coordinate systems as they are defined. To set the active element coordinate system
        attribute pointer, issue the :ref:`esys` command.

        The active coordinate system for files created via the :ref:`cdwrite` command is Cartesian (
        :ref:`csys`,0).

        This command is valid in any processor.

        :ref:`csys`,4 (or :ref:`csys`,WP) activates working plane tracking, which updates the coordinate
        system to follow working plane changes. To deactivate working plane tracking, activate any other
        coordinate system (for example, :ref:`csys`,0 or :ref:`csys`,11).

        :ref:`csys`,5 is a cylindrical coordinate system with global Cartesian Y as the axis of rotation.
        The local x, y and z axes are radial, θ, and axial (respectively). The R-Theta plane is the
        global X-Z plane, as it is for an axisymmetric model. Thus, at θ = 0.0, :ref:`csys`,5 has a
        specific orientation: the local x is in the global +X direction, local y is in the global -Z
        direction, and local z (the cylindrical axis) is in the global +Y direction.

        :ref:`csys`,6 is a cylindrical coordinate system with global Cartesian X as the axis of rotation.
        The local x, y and z axes are axial, radial, and θ (respectively). The R-Theta plane is the
        global Y-Z plane, as it is for an axisymmetric model. Thus, at θ = 0.0, :ref:`csys`,6 has a
        specific orientation: the local x is in the global -Z direction, local y is in the global +Y
        direction, and local z (the cylindrical axis) is in the global +X direction.
        """
        command = f"CSYS,{kcn}"
        return self.run(command, **kwargs)

    def cswpla(
        self, kcn: str = "", kcs: str = "", par1: str = "", par2: str = "", **kwargs
    ):
        r"""Defines a local coordinate system at the origin of the working plane.

        Mechanical APDL Command: `CSWPLA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSWPLA.html>`_

        Parameters
        ----------
        kcn : str
            Arbitrary reference number assigned to this coordinate system. Must be greater than 10. A
            coordinate system previously defined with this number will be redefined.

        kcs : str
            Coordinate system type:

            * ``0 or CART`` - Cartesian

            * ``1 or CYLIN`` - Cylindrical (circular or elliptical)

            * ``2 or SPHE`` - Spherical (or spheroidal)

            * ``3 or TORO`` - Toroidal

        par1 : str
            Used for elliptical, spheroidal, or toroidal systems. If ``KCS`` = 1 or 2, ``PAR1`` is the ratio
            of the ellipse Y-axis radius to X-axis radius (defaults to 1.0 (circle)). If ``KCS`` = 3,
            ``PAR1`` is the major radius of the torus.

        par2 : str
            Used for spheroidal systems. If ``KCS`` = 2, ``PAR2`` = ratio of ellipse Z-axis radius to X-axis
            radius (defaults to 1.0 (circle)).

        Notes
        -----

        .. _CSWPLA_notes:

        Defines and activates a local right-handed coordinate system centered at the origin of the working
        plane. The coordinate system's local x-y plane (for a Cartesian system) or R-θ plane (for a
        cylindrical or spherical system) corresponds to the working plane. This local system becomes the
        active coordinate system. See the :ref:`cs`, :ref:`local`, :ref:`clocal`, and :ref:`cskp` commands
        for alternate ways to define a local coordinate system. Local coordinate systems may be displayed
        with the :ref:`psymb` command.

        This command is valid in any processor.
        """
        command = f"CSWPLA,{kcn},{kcs},{par1},{par2}"
        return self.run(command, **kwargs)

    def cskp(
        self,
        kcn: str = "",
        kcs: str = "",
        porig: str = "",
        pxaxs: str = "",
        pxypl: str = "",
        par1: str = "",
        par2: str = "",
        **kwargs,
    ):
        r"""Defines a local coordinate system by three keypoint locations.

        Mechanical APDL Command: `CSKP <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSKP.html>`_

        Parameters
        ----------
        kcn : str
            Arbitrary reference number assigned to this coordinate system. Must be greater than 10. A
            coordinate system previously defined with this number will be redefined.

        kcs : str
            Coordinate system type:

            * ``0 or CART`` - Cartesian

            * ``1 or CYLIN`` - Cylindrical (circular or elliptical)

            * ``2 or SPHE`` - Spherical (or spheroidal)

            * ``3 or TORO`` - Toroidal

        porig : str
            Keypoint defining the origin of this coordinate system. If ``PORIG`` = P, graphical picking is
            enabled and all remaining command fields are ignored (valid only in the GUI).

        pxaxs : str
            Keypoint defining the positive x-axis orientation of this coordinate system.

        pxypl : str
            Keypoint defining the x-y plane (with ``PORIG`` and ``PXAXS`` ) in the first or second quadrant
            of this coordinate system.

        par1 : str
            Used for elliptical, spheroidal, or toroidal systems. If ``KCS`` = 1 or 2, ``PAR1`` is the ratio
            of the ellipse Y-axis radius to X-axis radius (defaults to 1.0 (circle)). If ``KCS`` = 3,
            ``PAR1`` is the major radius of the torus.

        par2 : str
            Used for spheroidal systems. If ``KCS`` = 2, ``PAR2`` = ratio of ellipse Z-axis radius to X-axis
            radius (defaults to 1.0 (circle)).

        Notes
        -----

        .. _CSKP_notes:

        Defines and activates a local right-handed coordinate system by specifying three existing keypoints:
        to locate the origin, to locate the positive x-axis, and to define the positive x-y plane. This
        local system becomes the active coordinate system. See the :ref:`clocal`, :ref:`cs`, :ref:`cswpla`,
        and :ref:`local` commands for alternate definitions. Local coordinate systems may be displayed with
        the :ref:`psymb` command.

        This command is valid in any processor.
        """
        command = f"CSKP,{kcn},{kcs},{porig},{pxaxs},{pxypl},{par1},{par2}"
        return self.run(command, **kwargs)

    def cslist(self, kcn1: str = "", kcn2: str = "", kcinc: str = "", **kwargs):
        r"""Lists coordinate systems.

        Mechanical APDL Command: `CSLIST <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSLIST.html>`_

        Parameters
        ----------
        kcn1 : str
            List coordinate systems from ``KCN1`` to ``KCN2`` (defaults to ``KCN1`` ) in steps of ``KCINC``
            (defaults to 1). If ``KCN1`` = ALL (default), ``KCN2`` and ``KCINC`` are ignored and all
            coordinate systems are listed.

        kcn2 : str
            List coordinate systems from ``KCN1`` to ``KCN2`` (defaults to ``KCN1`` ) in steps of ``KCINC``
            (defaults to 1). If ``KCN1`` = ALL (default), ``KCN2`` and ``KCINC`` are ignored and all
            coordinate systems are listed.

        kcinc : str
            List coordinate systems from ``KCN1`` to ``KCN2`` (defaults to ``KCN1`` ) in steps of ``KCINC``
            (defaults to 1). If ``KCN1`` = ALL (default), ``KCN2`` and ``KCINC`` are ignored and all
            coordinate systems are listed.

        Notes
        -----

        .. _CSLIST_notes:

        This command is valid in any processor.
        """
        command = f"CSLIST,{kcn1},{kcn2},{kcinc}"
        return self.run(command, **kwargs)

    def csdele(self, kcn1: str = "", kcn2: str = "", kcinc: str = "", **kwargs):
        r"""Deletes local coordinate systems.

        Mechanical APDL Command: `CSDELE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSDELE.html>`_

        Parameters
        ----------
        kcn1 : str
            Delete coordinate systems from ``KCN1`` (must be greater than 10) to ``KCN2`` (defaults to
            ``KCN1`` ) in steps of ``KCINC`` (defaults to 1). If ``KCN1`` = ALL, ``KCN2`` and ``KCINC`` are
            ignored and all coordinate systems are deleted.

        kcn2 : str
            Delete coordinate systems from ``KCN1`` (must be greater than 10) to ``KCN2`` (defaults to
            ``KCN1`` ) in steps of ``KCINC`` (defaults to 1). If ``KCN1`` = ALL, ``KCN2`` and ``KCINC`` are
            ignored and all coordinate systems are deleted.

        kcinc : str
            Delete coordinate systems from ``KCN1`` (must be greater than 10) to ``KCN2`` (defaults to
            ``KCN1`` ) in steps of ``KCINC`` (defaults to 1). If ``KCN1`` = ALL, ``KCN2`` and ``KCINC`` are
            ignored and all coordinate systems are deleted.

        Notes
        -----

        .. _CSDELE_notes:

        This command is valid in any processor.
        """
        command = f"CSDELE,{kcn1},{kcn2},{kcinc}"
        return self.run(command, **kwargs)

    def clocal(
        self,
        kcn: str = "",
        kcs: str = "",
        xl: str = "",
        yl: str = "",
        zl: str = "",
        thxy: str = "",
        thyz: str = "",
        thzx: str = "",
        par1: str = "",
        par2: str = "",
        **kwargs,
    ):
        r"""Defines a local coordinate system relative to the active coordinate system.

        Mechanical APDL Command: `CLOCAL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CLOCAL.html>`_

        Parameters
        ----------
        kcn : str
            Arbitrary reference number assigned to this coordinate system. Must be greater than 10. A
            coordinate system previously defined with this number will be redefined.

        kcs : str
            Coordinate system type:

            * ``0 or CART`` - Cartesian

            * ``1 or CYLIN`` - Cylindrical (circular or elliptical)

            * ``2 or SPHE`` - Spherical (or spheroidal)

            * ``3 or TORO`` - Toroidal

        xl : str
            Location (in the active coordinate system) of the origin of the new coordinate system (R, θ, Z
            for cylindrical, R, θ,Φ for spherical or toroidal).

        yl : str
            Location (in the active coordinate system) of the origin of the new coordinate system (R, θ, Z
            for cylindrical, R, θ,Φ for spherical or toroidal).

        zl : str
            Location (in the active coordinate system) of the origin of the new coordinate system (R, θ, Z
            for cylindrical, R, θ,Φ for spherical or toroidal).

        thxy : str
            First rotation about local Z (positive X toward Y).

        thyz : str
            Second rotation about local X (positive Y toward Z).

        thzx : str
            Third rotation about local Y (positive Z toward X).

        par1 : str
            Used for elliptical, spheroidal, or toroidal systems. If ``KCS`` = 1 or 2, ``PAR1`` is the ratio
            of the ellipse Y-axis radius to X-axis radius (defaults to 1.0 (circle)). If ``KCS`` = 3,
            ``PAR1`` is the major radius of the torus.

        par2 : str
            Used for spheroidal systems. If ``KCS`` = 2, ``PAR2`` = ratio of ellipse Z-axis radius to X-axis
            radius (defaults to 1.0 (circle)).

        Notes
        -----

        .. _CLOCAL_notes:

        Defines and activates a local coordinate system by origin location and orientation angles relative
        to the active coordinate system. This local system becomes the active coordinate system, and is
        automatically aligned with the active system (that is, x is radial if a cylindrical system is
        active, etc.). Nonzero rotation angles (degrees) are relative to this automatic rotation. See the
        :ref:`cs`, :ref:`cskp`, :ref:`cswpla`, and :ref:`local` commands for alternate definitions. Local
        coordinate systems may be displayed with the :ref:`psymb` command.

        This command is valid in any processor.
        """
        command = (
            f"CLOCAL,{kcn},{kcs},{xl},{yl},{zl},{thxy},{thyz},{thzx},{par1},{par2}"
        )
        return self.run(command, **kwargs)

    def cscir(
        self, kcn: str = "", kthet: int | str = "", kphi: int | str = "", **kwargs
    ):
        r"""Locates the singularity for non-Cartesian local coordinate systems.

        Mechanical APDL Command: `CSCIR <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CSCIR.html>`_

        **Command default:**

        .. _CSCIR_default:

        Singularities at ±180°.

        Parameters
        ----------
        kcn : str
            Number of the local coordinate system in which singularity location is to be changed. Must be
            greater than 10.

        kthet : int or str
            Theta singularity location for cylindrical, spherical, and toroidal systems:

            * ``0`` - Singularity at ±180°.

            * ``1`` - Singularity at 0° (360°).

        kphi : int or str
            Phi singularity location for toroidal systems:

            * ``0`` - Singularity in phi direction at ±180°.

            * ``1`` - Singularity in phi direction at 0° (360°).

        Notes
        -----

        .. _CSCIR_notes:

        Continuous closed surfaces (circles, cylinders, spheres, etc.) have a singularity (discontinuity) at
        θ = ±180°. For local cylindrical, spherical, and toroidal coordinate systems, this
        singularity location may be changed to 0° (360°).

        An additional, similar singularity occurs in the toroidal coordinate system at Φ = ±180° and can be
        moved with ``KPHI``. Additional singularities occur in the spherical coordinate system at Φ = ±90°,
        but cannot be moved.

        This command is valid in any processor.
        """
        command = f"CSCIR,{kcn},{kthet},{kphi}"
        return self.run(command, **kwargs)

    def cs(
        self,
        kcn: str = "",
        kcs: str = "",
        norig: str = "",
        nxax: str = "",
        nxypl: str = "",
        par1: str = "",
        par2: str = "",
        **kwargs,
    ):
        r"""Defines a local coordinate system by three node locations.

        Mechanical APDL Command: `CS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CS.html>`_

        Parameters
        ----------
        kcn : str
            Arbitrary reference number assigned to this coordinate system. Must be greater than 10. A
            coordinate system previously defined with this number will be redefined.

        kcs : str
            Coordinate system type:

            * ``0 or CART`` - Cartesian

            * ``1 or CYLIN`` - Cylindrical (circular or elliptical)

            * ``2 or SPHE`` - Spherical (or spheroidal)

            * ``3 or TORO`` - Toroidal

        norig : str
            Node defining the origin of this coordinate system. If ``NORIG`` = P, graphical picking is
            enabled and all remaining command fields are ignored (valid only in the GUI).

        nxax : str
            Node defining the positive x-axis orientation of this coordinate system.

        nxypl : str
            Node defining the x-y plane (with ``NORIG`` and ``NXAX`` ) in the first or second quadrant of
            this coordinate system.

        par1 : str
            Used for elliptical, spheroidal, or toroidal systems. If ``KCS`` = 1 or 2, ``PAR1`` is the ratio
            of the ellipse Y-axis radius to X-axis radius (defaults to 1.0 (circle)). If ``KCS`` = 3,
            ``PAR1`` is the major radius of the torus.

        par2 : str
            Used for spheroidal systems. If ``KCS`` = 2, ``PAR2`` = ratio of ellipse Z-axis radius to X-axis
            radius (defaults to 1.0 (circle)).

        Notes
        -----

        .. _CS_notes:

        Defines and activates a local right-handed coordinate system by specifying three existing nodes: to
        locate the origin, to locate the positive x-axis, and to define the positive x-y plane. This local
        system becomes the active coordinate system. See the :ref:`clocal`, :ref:`cskp`, :ref:`cswpla`, and
        :ref:`local` commands for alternate definitions. Local coordinate systems may be displayed with the
        :ref:`psymb` command.

        This command is valid in any processor.
        """
        command = f"CS,{kcn},{kcs},{norig},{nxax},{nxypl},{par1},{par2}"
        return self.run(command, **kwargs)

    def local(
        self,
        kcn: str = "",
        kcs: str = "",
        xc: str = "",
        yc: str = "",
        zc: str = "",
        thxy: str = "",
        thyz: str = "",
        thzx: str = "",
        par1: str = "",
        par2: str = "",
        **kwargs,
    ):
        r"""Defines a local coordinate system by a location and orientation.

        Mechanical APDL Command: `LOCAL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LOCAL.html>`_

        Parameters
        ----------
        kcn : str
            Arbitrary reference number assigned to this coordinate system. Must be greater than 10. A
            coordinate system previously defined with this number will be redefined.

        kcs : str
            Coordinate system type:

            * ``0 or CART`` - Cartesian

            * ``1 or CYLIN`` - Cylindrical (circular or elliptical)

            * ``2 or SPHE`` - Spherical (or spheroidal)

            * ``3 or TORO`` - Toroidal

        xc : str
            Location (in the global Cartesian coordinate system) of the origin of the new coordinate system.

        yc : str
            Location (in the global Cartesian coordinate system) of the origin of the new coordinate system.

        zc : str
            Location (in the global Cartesian coordinate system) of the origin of the new coordinate system.

        thxy : str
            First rotation about local Z (positive X toward Y).

        thyz : str
            Second rotation about local X (positive Y toward Z).

        thzx : str
            Third rotation about local Y (positive Z toward X).

        par1 : str
            Used for elliptical, spheroidal, or toroidal systems. If ``KCS`` = 1 or 2, ``PAR1`` is the ratio
            of the ellipse Y-axis radius to X-axis radius (defaults to 1.0 (circle)). If ``KCS`` = 3,
            ``PAR1`` is the major radius of the torus.

        par2 : str
            Used for spheroidal systems. If ``KCS`` = 2, ``PAR2`` = ratio of ellipse Z-axis radius to X-axis
            radius (defaults to 1.0 (circle)).

        Notes
        -----

        .. _LOCAL_notes:

        Defines a local coordinate system by origin location and orientation angles. The local coordinate
        system is parallel to the global Cartesian system unless rotated. Rotation angles are in degrees and
        redefine any previous rotation angles. See the :ref:`clocal`, :ref:`cs`, :ref:`cswpla`, and
        :ref:`cskp` commands for alternate definitions. This local system becomes the active coordinate
        system ( :ref:`csys` ). Local coordinate systems may be displayed with the :ref:`psymb` command.

        This command is valid in any processor.
        """
        command = f"LOCAL,{kcn},{kcs},{xc},{yc},{zc},{thxy},{thyz},{thzx},{par1},{par2}"
        return self.run(command, **kwargs)
