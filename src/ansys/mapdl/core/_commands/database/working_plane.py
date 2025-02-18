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


class WorkingPlane:

    def kwplan(
        self, wn: str = "", korig: str = "", kxax: str = "", kplan: str = "", **kwargs
    ):
        r"""Defines the working plane using three keypoints.

        Mechanical APDL Command: `KWPLAN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KWPLAN.html>`_

        Parameters
        ----------
        wn : str
            Window number whose viewing direction will be modified to be normal to the working plane
            (defaults to 1). If ``WN`` is a negative value, the viewing direction will not be modified. If
            fewer than three points are used, the viewing direction of window ``WN`` will be used instead to
            define the normal to the working plane.

        korig : str
            Keypoint number defining the origin of the working plane coordinate system. If ``KORIG`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        kxax : str
            Keypoint number defining the x-axis orientation (defaults to the x-axis being parallel to the
            global X-axis; or if the normal to the working plane is parallel to the global X-axis, then
            defaults to being parallel to the global Y-axis).

        kplan : str
            Keypoint number defining the working plane (the normal defaults to the present display view (
            :ref:`view` ) of window ``WN`` ).

        Notes
        -----

        .. _KWPLAN_notes:

        Defines a working plane to assist in picking operations using three keypoints as an alternate to the
        :ref:`wplane` command. The three keypoints also define the working plane coordinate system. A
        minimum of one keypoint (at the working plane origin) is required. Immediate mode may also be
        active. See :ref:`wpstyl` command to set the style of working plane display.

        This command is valid in any processor.
        """
        command = f"KWPLAN,{wn},{korig},{kxax},{kplan}"
        return self.run(command, **kwargs)

    def kwpave(
        self,
        p1: str = "",
        p2: str = "",
        p3: str = "",
        p4: str = "",
        p5: str = "",
        p6: str = "",
        p7: str = "",
        p8: str = "",
        p9: str = "",
        **kwargs,
    ):
        r"""Moves the working plane origin to the average location of keypoints.

        Mechanical APDL Command: `KWPAVE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_KWPAVE.html>`_

        Parameters
        ----------
        p1 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p2 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p3 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p4 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p5 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p6 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p7 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p8 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        p9 : str
            Keypoints used in calculation of the average. At least one must be defined. If ``P1`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        Notes
        -----

        .. _KWPAVE_notes:

        Moves the origin of the working plane to the average of the specified keypoints. Averaging is based
        on the active coordinate system.

        This command is valid in any processor.
        """
        command = f"KWPAVE,{p1},{p2},{p3},{p4},{p5},{p6},{p7},{p8},{p9}"
        return self.run(command, **kwargs)

    def wprota(self, thxy: str = "", thyz: str = "", thzx: str = "", **kwargs):
        r"""Rotates the working plane.

        Mechanical APDL Command: `WPROTA <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPROTA.html>`_

        Parameters
        ----------
        thxy : str
            First rotation about the working plane Z axis (positive X toward Y).

        thyz : str
            Second rotation about working plane X axis (positive Y toward Z).

        thzx : str
            Third rotation about working plane Y axis (positive Z toward X).

        Notes
        -----

        .. _WPROTA_notes:

        The specified angles (in degrees) are relative to the orientation of the working plane.

        This command is valid in any processor.
        """
        command = f"WPROTA,{thxy},{thyz},{thzx}"
        return self.run(command, **kwargs)

    def wpstyl(
        self,
        snap: str = "",
        grspac: str = "",
        grmin: str = "",
        grmax: str = "",
        wptol: str = "",
        wpctyp: int | str = "",
        grtype: int | str = "",
        wpvis: int | str = "",
        snapang: str = "",
        **kwargs,
    ):
        r"""Controls the display and style of the working plane.

        Mechanical APDL Command: `WPSTYL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPSTYL.html>`_

        Parameters
        ----------
        snap : str
            Snap increment for a locational pick (1E-6 minimum). If -1, turn off snap capability. For
            example, a picked location of 1.2456 with a snap of 0.1 gives 1.2, with 0.01 gives 1.25, with
            0.001 gives 1.246, and with 0.025 gives 1.250 (defaults to 0.05).

        grspac : str
            Graphical spacing between grid points. For graphical representation only and not related to snap
            points (defaults to 0.1).

        grmin : str
            Defines the size of a square grid (if ``WPCTYP`` = 0) to be displayed over a portion of the
            working plane. The opposite corners of the grid will be located at grid points nearest the
            working plane coordinates of ( ``GRMIN``, ``GRMIN`` ) and ( ``GRMAX``, ``GRMAX`` ). If a polar
            system ( ``WPCTYP`` = 1), ``GRMAX`` is the outside radius of grid and ``GRMIN`` is ignored. If
            ``GRMIN`` = ``GRMAX``, no grid will be displayed (defaults to -1.0 and 1.0 for ``GRMIN`` and
            ``GRMAX`` respectively).

        grmax : str
            Defines the size of a square grid (if ``WPCTYP`` = 0) to be displayed over a portion of the
            working plane. The opposite corners of the grid will be located at grid points nearest the
            working plane coordinates of ( ``GRMIN``, ``GRMIN`` ) and ( ``GRMAX``, ``GRMAX`` ). If a polar
            system ( ``WPCTYP`` = 1), ``GRMAX`` is the outside radius of grid and ``GRMIN`` is ignored. If
            ``GRMIN`` = ``GRMAX``, no grid will be displayed (defaults to -1.0 and 1.0 for ``GRMIN`` and
            ``GRMAX`` respectively).

        wptol : str
            The tolerance that an entity's location can deviate from the specified working plane, while
            still being considered on the plane. Used only for locational picking of vertices for polygons
            and prisms (defaults to 0.003).

        wpctyp : int or str
            Working plane coordinate system type:

            * ``0`` - Cartesian (default). If working plane tracking is on ( :ref:`csys`,4), the updated active coordinate
              system will also be Cartesian.

            * ``1`` - Polar. If working plane tracking is on, the updated active coordinate system will be cylindrical.

            * ``2`` - Polar. If working plane tracking is on, the updated active coordinate system will be spherical.

        grtype : int or str
            Grid type:

            * ``0`` - Grid and WP triad.

            * ``1`` - Grid only.

            * ``2`` - WP triad only (default).

        wpvis : int or str
            Grid visibility:

            * ``0`` - Do not show ``GRTYPE`` entities (grid and/or triad) (default).

            * ``1`` - Show ``GRTYPE`` entities. Cartesian working planes will be displayed with a Cartesian grid, polar
              with a polar grid.

        snapang : str
            Snap angle (0--180) in degrees. Used only if ``WPCTYP`` = 1 or 2. Defaults to 5 degrees.

        Notes
        -----

        .. _WPSTYL_notes:

        Use :ref:`wpstyl`,DEFA to reset the working plane to its default location and style. Use
        :ref:`wpstyl`,STAT to list the status of the working plane. Blank fields will keep present settings.

        It is possible to specify ``SNAP`` and ``WPTOL`` values that will cause conflicts during picking
        operations. Check your values carefully, and if problems are noted, revert to the default values.

        :ref:`wpstyl` with no arguments will toggle the grid on and off. The working plane can be displayed
        in the non-GUI interactive mode only after issuing a :ref:`plopts`,WP,1 command. See the `Modeling
        and Meshing Guide
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_mod/Hlp_G_MOD14.html>`_
        for more information on working plane tracking. See :ref:`plopts` command for control of hidden line
        working plane.

        This command is valid in any processor.
        """
        command = f"WPSTYL,{snap},{grspac},{grmin},{grmax},{wptol},{wpctyp},{grtype},{wpvis},{snapang}"
        return self.run(command, **kwargs)

    def wpave(
        self,
        x1: str = "",
        y1: str = "",
        z1: str = "",
        x2: str = "",
        y2: str = "",
        z2: str = "",
        x3: str = "",
        y3: str = "",
        z3: str = "",
        **kwargs,
    ):
        r"""Moves the working plane origin to the average of specified points.

        Mechanical APDL Command: `WPAVE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPAVE.html>`_

        Parameters
        ----------
        x1 : str
            Coordinates (in the active coordinate system) of the first point. If ``X1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        y1 : str
            Coordinates (in the active coordinate system) of the first point. If ``X1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        z1 : str
            Coordinates (in the active coordinate system) of the first point. If ``X1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        x2 : str
            Coordinates (in the active coordinate system) of the second point.

        y2 : str
            Coordinates (in the active coordinate system) of the second point.

        z2 : str
            Coordinates (in the active coordinate system) of the second point.

        x3 : str
            Coordinates (in the active coordinate system) of the third point.

        y3 : str
            Coordinates (in the active coordinate system) of the third point.

        z3 : str
            Coordinates (in the active coordinate system) of the third point.

        Notes
        -----

        .. _WPAVE_notes:

        Moves the origin of the working plane to the average of the specified points. A point is considered
        specified only if at least one of its coordinates is non-blank, and at least one point (1, 2, or 3)
        must be specified. Blank coordinates of a specified point are assumed to be zero. Averaging is based
        on the active coordinate system.

        This command is valid in any processor.
        """
        command = f"WPAVE,{x1},{y1},{z1},{x2},{y2},{z2},{x3},{y3},{z3}"
        return self.run(command, **kwargs)

    def wpoffs(self, xoff: str = "", yoff: str = "", zoff: str = "", **kwargs):
        r"""Offsets the working plane.

        Mechanical APDL Command: `WPOFFS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPOFFS.html>`_

        Parameters
        ----------
        xoff : str
            Offset increments defined in the working plane coordinate system. If only ``ZOFF`` is used, the
            working plane will be redefined parallel to the present plane and offset by ``ZOFF``.

        yoff : str
            Offset increments defined in the working plane coordinate system. If only ``ZOFF`` is used, the
            working plane will be redefined parallel to the present plane and offset by ``ZOFF``.

        zoff : str
            Offset increments defined in the working plane coordinate system. If only ``ZOFF`` is used, the
            working plane will be redefined parallel to the present plane and offset by ``ZOFF``.

        Notes
        -----

        .. _WPOFFS_notes:

        Changes the origin of the working plane by translating the working plane along its coordinate system
        axes.

        This command is valid in any processor.
        """
        command = f"WPOFFS,{xoff},{yoff},{zoff}"
        return self.run(command, **kwargs)

    def wplane(
        self,
        wn: str = "",
        xorig: str = "",
        yorig: str = "",
        zorig: str = "",
        xxax: str = "",
        yxax: str = "",
        zxax: str = "",
        xplan: str = "",
        yplan: str = "",
        zplan: str = "",
        **kwargs,
    ):
        r"""Defines a working plane to assist in picking operations.

        Mechanical APDL Command: `WPLANE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPLANE.html>`_

        Parameters
        ----------
        wn : str
            Window number whose viewing direction will be modified to be normal to the working plane
            (defaults to 1). If ``WN`` is a negative value, the viewing direction will not be modified. If
            fewer than three points are used, the viewing direction of window ``WN`` will be used instead to
            define the normal to the working plane.

        xorig : str
            Global Cartesian coordinates of the origin of the working plane coordinate system.

        yorig : str
            Global Cartesian coordinates of the origin of the working plane coordinate system.

        zorig : str
            Global Cartesian coordinates of the origin of the working plane coordinate system.

        xxax : str
            Global Cartesian coordinates of a point defining the x-axis orientation. The x-axis aligns with
            the projection of the line from this orientation point to the origin.

        yxax : str
            Global Cartesian coordinates of a point defining the x-axis orientation. The x-axis aligns with
            the projection of the line from this orientation point to the origin.

        zxax : str
            Global Cartesian coordinates of a point defining the x-axis orientation. The x-axis aligns with
            the projection of the line from this orientation point to the origin.

        xplan : str
            Global Cartesian coordinates of the third point defining the working plane. This point will also
            define the location of the positive XY-sector of the working plane coordinate system.

        yplan : str
            Global Cartesian coordinates of the third point defining the working plane. This point will also
            define the location of the positive XY-sector of the working plane coordinate system.

        zplan : str
            Global Cartesian coordinates of the third point defining the working plane. This point will also
            define the location of the positive XY-sector of the working plane coordinate system.

        Notes
        -----

        .. _WPLANE_notes:

        Defines a working plane to assist in picking operations using the coordinates of three noncolinear
        points. The three points also define the working plane coordinate system. A minimum of one point
        (the working plane origin) is required. Immediate mode may also be active. See :ref:`wpstyl` command
        to set the style of working plane display.

        This command is valid in any processor.
        """
        command = f"WPLANE,{wn},{xorig},{yorig},{zorig},{xxax},{yxax},{zxax},{xplan},{yplan},{zplan}"
        return self.run(command, **kwargs)

    def wpcsys(self, wn: str = "", kcn: str = "", **kwargs):
        r"""Defines the working plane location based on a coordinate system.

        Mechanical APDL Command: `WPCSYS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_WPCSYS.html>`_

        Parameters
        ----------
        wn : str
            Window number whose viewing direction will be modified to be normal to the working plane
            (defaults to 1). If ``WN`` is a negative value, the viewing direction will not be modified.

        kcn : str
            Coordinate system number. ``KCN`` may be 0,1,2 or any previously defined local coordinate system
            number (defaults to the active system).

        Notes
        -----

        .. _WPCSYS_notes:

        Defines a working plane location and orientation based on an existing coordinate system. If a
        Cartesian system is used as the basis ( ``KCN`` ) for the working plane, the working plane will also
        be Cartesian, in the X-Y plane of the base system. If a cylindrical, spherical, or toroidal base
        system is used, the working plane will be a polar system in the R-θ plane of the base system.

        If working plane tracking has been activated ( :ref:`csys`,WP or :ref:`csys`,4), the updated active
        coordinate system will be of a similar type, except that a toroidal system will be updated to a
        cylindrical system. See the `Modeling and Meshing Guide
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_mod/Hlp_G_MOD14.html>`_ for more
        information on working plane tracking.

        This command is valid in any processor.

        Some primitive generation commands will not honor R-theta transformations for non-cartesian
        coordinate systems. Refer to the primitive commands table for more information.
        """
        command = f"WPCSYS,{wn},{kcn}"
        return self.run(command, **kwargs)

    def lwplan(self, wn: str = "", nl1: str = "", ratio: str = "", **kwargs):
        r"""Defines the working plane normal to a location on a line.

        Mechanical APDL Command: `LWPLAN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_LWPLAN.html>`_

        Parameters
        ----------
        wn : str
            Window number whose viewing direction will be modified to be normal to the working plane
            (defaults to 1). If ``WN`` is a negative value, the viewing direction will not be modified.

        nl1 : str
            Number of line to be used. If ``NL1`` = P, graphical picking is enabled and all remaining
            command fields are ignored (valid only in the GUI).

        ratio : str
            Location on ``NL1``, specified as a ratio of the line length. Must be between 0.0 and 1.0. If
            ``RATIO`` = P, use graphical picking to specify location on the line.

        Notes
        -----

        .. _LWPLAN_notes:

        Defines a working plane (to assist in picking operations) normal to a location on a line. See
        :ref:`wpstyl` command to set the style of working plane display.

        This command is valid in any processor.
        """
        command = f"LWPLAN,{wn},{nl1},{ratio}"
        return self.run(command, **kwargs)

    def nwplan(
        self, wn: str = "", norig: str = "", nxax: str = "", nplan: str = "", **kwargs
    ):
        r"""Defines the working plane using three nodes.

        Mechanical APDL Command: `NWPLAN <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NWPLAN.html>`_

        Parameters
        ----------
        wn : str
            Window number whose viewing direction will be modified to be normal to the working plane
            (defaults to 1). If ``WN`` is a negative value, the viewing direction will not be modified. If
            fewer than three points are used, the viewing direction of window ``WN`` will be used instead to
            define the normal to the working plane.

        norig : str
            Node number defining the origin of the working plane coordinate system. If ``NORIG`` = P,
            graphical picking is enabled and all remaining command fields are ignored (valid only in the
            GUI).

        nxax : str
            Node number defining the x-axis orientation (defaults to the x-axis being parallel to the global
            X-axis; or if the normal to the working plane is parallel to the global X-axis, then defaults to
            being parallel to the global Y-axis).

        nplan : str
            Node number defining the working plane (the normal defaults to the present display view (
            :ref:`view` ) of window ``WN`` ).

        Notes
        -----

        .. _NWPLAN_notes:

        Defines a working plane to assist in picking operations using three nodes as an alternate to the
        :ref:`wplane` command. The three nodes also define the working plane coordinate system. A minimum of
        one node (at the working plane origin) is required. Immediate mode may also be active. See the
        :ref:`wpstyl` command to set the style of the working plane display.

        This command is valid in any processor.
        """
        command = f"NWPLAN,{wn},{norig},{nxax},{nplan}"
        return self.run(command, **kwargs)

    def nwpave(
        self,
        n1: str = "",
        n2: str = "",
        n3: str = "",
        n4: str = "",
        n5: str = "",
        n6: str = "",
        n7: str = "",
        n8: str = "",
        n9: str = "",
        **kwargs,
    ):
        r"""Moves the working plane origin to the average location of nodes.

        Mechanical APDL Command: `NWPAVE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_NWPAVE.html>`_

        Parameters
        ----------
        n1 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n2 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n3 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n4 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n5 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n6 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n7 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n8 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        n9 : str
            Nodes used in calculation of the average. At least one must be defined. If ``N1`` = P, graphical
            picking is enabled and all remaining command fields are ignored (valid only in the GUI).

        Notes
        -----

        .. _NWPAVE_notes:

        Averaging is based on the active coordinate system.

        This command is valid in any processor.
        """
        command = f"NWPAVE,{n1},{n2},{n3},{n4},{n5},{n6},{n7},{n8},{n9}"
        return self.run(command, **kwargs)
