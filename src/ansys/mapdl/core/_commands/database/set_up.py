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

    def clear(self, read: str = "", **kwargs):
        r"""Clears the database.

        Mechanical APDL Command: `/CLEAR <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CLEAR.html>`_

        Parameters
        ----------
        read : str
            File read option:

            * ``START`` - Reread :file:`start.ans` file (default).

            * ``NOSTART`` - Do not reread :file:`start.ans` file.

        Notes
        -----

        .. _s-CLEAR_notes:

        The :ref:`clear` command resets the database to the conditions present at the beginning of the
        problem.

        The command is typically used between multiple analyses in the same run, or between passes of a
        multipass analysis (such as between substructure generation, use, and expansion passes).

        The command sets the import and Boolean options back to the default, deletes all items from the
        database, and sets memory values to zero for items derived from database information. (All files
        remain intact.) The command also resets the jobname to match the currently open session :file:`.LOG`
        and :file:`.ERR` files, returning the jobname to its original value or to the most recent value
        specified via :ref:`filname` with ``KEY`` = 1.

        After the database is cleared, the :file:`start.ans` file is reread (by default) unless ``Read`` =
        NOSTART.

        Additional commands cannot be stacked (via the $ separator) on the same line as the :ref:`clear`
        command.

        Use caution when placing the :ref:`clear` command within branching constructs (for example, those
        using ``\*DO`` or ``\*IF`` commands), as the command deletes all parameters including the looping
        parameter for do-loops. (To preserve your iteration parameter, issue a :ref:`parsav` command prior
        to :ref:`clear`, then follow  :ref:`clear` with a :ref:`parres` command.)

        This command is valid in any processor. Issuing this command at any point clears the database.
        """
        command = f"/CLEAR,{read}"
        return self.run(command, **kwargs)

    def resume(
        self,
        fname: str = "",
        ext: str = "",
        nopar: int | str = "",
        knoplot: str = "",
        **kwargs,
    ):
        r"""Resumes the database from the database file.

        Mechanical APDL Command: `RESUME <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_RESUME.html>`_

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. The file name defaults to :file:`Jobname`.

        ext : str
            Filename extension (eight-character maximum). The extension defaults to DB if ``Fname`` is
            blank.

        nopar : int or str
            Parameter resume key:

            * ``0`` - All data in the database, including the scalar parameters, are replaced with the data saved on
              :file:`Jobname.db` (default).

            * ``1`` - All data in the database, except the scalar parameters, are replaced with the data saved on
              :file:`Jobname.db`.

        knoplot : str
            If equal to 1, will suppress automatic plot. Otherwise, if the GUI is on and this :ref:`resume`
            command was not read from a file, the selected elements from ``Fname`` are plotted. (If there
            are no selected elements, selected nodes are plotted. If no nodes, volumes; if no volumes,
            areas; if no areas, lines; if no lines, keypoints. If there are no selected keypoints, the
            screen is erased.)

        Notes
        -----

        .. _RESUME_notes:

        The :ref:`resume` command resumes a database file into Mechanical APDL. The command causes the
        database
        file ( :file:`Jobname.db` ) to be read, thereby resetting the database (including any geometry
        settings) either a) as it was at the last :ref:`save` command, or b) as it was saved with the last
        :ref:`slashexit` command, whichever was last.

        For multiple load step analyses (because only the data for one load step at a time may reside in the
        database), the load step data restored to the database will correspond to the load step data written
        when the save occurred.

        If the database file was saved in another Ansys, Inc. product, it may contain element type
        and :ref:`keyopt` specifications which are invalid in the resuming product. Immediately after the
        database resume is completed, you should redefine these invalid element types and :ref:`keyopt`
        settings to valid ones ( :ref:`et`, :ref:`keyopt` ).

        The ``NOPAR`` = 1 option should not be used if array parameters are defined, as existing array
        parameters might be redefined with arbitrary values. For a more general method of preventing the
        replacement of both scalar and array parameters, see :ref:`parsav` and :ref:`parres`.)

        If a radiosity mapping data file ( :file:`.rsm` file) was saved by the previous :ref:`save` command,
        that mapping file must be present in the directory along with the database file in order for
        radiosity surface elements ( SURF251, SURF252 ) to be correctly mapped onto the model when
        :ref:`resume` is issued.

        This command is valid in any processor. If used in the solution processor, this command is valid
        only within the first load step.
        """
        command = f"RESUME,{fname},{ext},,{nopar},{knoplot}"
        return self.run(command, **kwargs)

    def title(self, title: str = "", **kwargs):
        r"""Defines a main title.

        Mechanical APDL Command: `/TITLE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_TITLE.html>`_

        Parameters
        ----------
        title : str
            Input up to 72 alphanumeric characters. Parameter substitution may be forced within the title by
            enclosing the parameter name or parametric expression within percent (%) signs.

        Notes
        -----

        .. _s-TITLE_notes:

        The title is carried through the printout and written on various files. The title written to a file
        is the title defined at that time. Special characters may be used within the title text. Subtitles
        may also be defined ( :ref:`stitle` ).

        This command is valid in any processor.
        """
        command = f"/TITLE,{title}"
        return self.run(command, **kwargs)

    def units(
        self,
        label: str = "",
        lenfact: str = "",
        massfact: str = "",
        timefact: str = "",
        tempfact: str = "",
        toffst: str = "",
        chargefact: str = "",
        forcefact: str = "",
        heatfact: str = "",
        **kwargs,
    ):
        r"""Annotates the database with the system of units used.

        Mechanical APDL Command: `/UNITS <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_

        Parameters
        ----------
        label : str
            Label to denote the system of units used in this job:

            * ``USER`` - User-defined system (default).

            * ``SI`` - International system (m, kg, s, K).

            * ``MKS`` - MKS system (m, kg, s, °C).

            * ``uMKS`` - μMKS system (μm, kg, s, °C).

            * ``CGS`` - CGS system (cm, g, s, °C).

            * ``MPA`` - MPA system (mm, Mg, s, °C).

            * ``BFT`` - U. S. Customary system using feet (ft, slug, s, °F).

            * ``BIN`` - U. S. Customary system using inches (in, lbf\2s :sup:`2` /in, s, °F).

        lenfact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        massfact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        timefact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        tempfact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        toffst : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        chargefact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        forcefact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        heatfact : str
            The description of the argument is missing in the Python function. Please, refer to the `command
            documentation
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_UNITS.html>`_ for further
            information.

        Notes
        -----

        .. _s-UNITS_notes:

        Allows the user to set a marker in the database indicating the system of units used. The setting may
        be reviewed with the :ref:`slashstatus` command at the Begin level. The units label and conversion
        factors on this command are for user convenience only and have no effect on the analysis or data.
        That is, :ref:`units`  will not convert database items from one system to another (for example, from
        U. S. Customary to SI, etc.). The units setting will be written to the file of IGES data [
        :ref:`igesout` or :ref:`cdwrite` ], which can then be read by many programs that read IGES files.
        The user must still use consistent units for the results to be valid.

        If you choose the MKS system of units, the EPZRO option for the :ref:`emunit` command is set to 8.85
        e-12 F/m. (EPZRO specifies alternate free-space permittivity.)

        For micro-electromechanical systems (MEMS), where dimensions are on the order of microns, see the
        conversion factors in `System of Units
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cou/Hlp_G_COU1_3.html#couthermelesmksvfa>`_
        in the `Coupled-Field Analysis Guide
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_cou/Hlp_G_COU_N4.html>`_.

        If you use the Mechanical APDL ADAMS Interface to export model information to the ADAMS program, the
        :ref:`units` command is required to ensure the correct transfer of data between Mechanical APDL and
        ADAMS.
        You can choose a predefined unit system label ( ``Label`` = SI, CGS, etc.) or you can select the
        user-defined system option ( ``Label`` = USER) and input the appropriate conversion factors (
        ``LENFACT``, ``MASSFACT``, ``TIMEFACT``, and ``FORCEFACT`` ). The conversion factors are written to
        the ADAMS input file :file:`Jobname.MNF` to correctly generate the load. For more information, see
        `Export to ADAMS
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_substr/advexad.html#advverres12902>`_.


        All differences between the base solution units used by the Mechanical APDL and CFX solvers are
        noted in
        the Mechanical APDL output file. Unit conversions are applied automatically to all loads transferred
        unless
        ``Label`` = USER. Unit conversions are not applied to any of the loads transferred between the
        Mechanical APDL and CFX solvers if they use a user-defined unit system.

        This command is valid in any processor.
        """
        command = f"/UNITS,{label},{lenfact},{massfact},{timefact},{tempfact},{toffst},{chargefact},{forcefact},{heatfact}"
        return self.run(command, **kwargs)

    def smbc(self, mode: str = "", **kwargs):
        r"""Controls the display of solid model boundary condition symbols and labels.

        Mechanical APDL Command: `/SMBC <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SMBC_sl.html>`_

        Parameters
        ----------
        mode : str

            * ``CENT`` - Solid model boundary condition symbols and labels appear at the centroid of the solid model entity
              (default).

            * ``TESS`` - Solid model boundary condition symbols and labels appear inside each constituent element of the
              tessellation.

        Notes
        -----

        .. _s-SMBC_notes:

        ``Mode`` = CENT is designed to reduce the clutter of boundary condition symbols in solid model
        plots. For example, if you have assigned normal pressure loads to an area, you may choose to display
        the pressures as arrows with the :ref:`psf` command using :ref:`psf`,PRES,NORM,2. When ``Mode`` =
        CENT, the pressure arrow is displayed at the centroid of the area. When ``Mode`` = TESS, a pressure
        arrow is displayed at the centroid of each polygon of the area's tessellation.

        This command is valid in any processor.
        """
        command = f"/SMBC,{mode}"
        return self.run(command, **kwargs)

    def save(self, fname: str = "", ext: str = "", slab: str = "", **kwargs):
        r"""Saves all current database information.

        Mechanical APDL Command: `SAVE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_SAVE.html>`_

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. The file name defaults to :file:`Jobname`.

        ext : str
            Filename extension (eight-character maximum). The extension defaults to DB if ``Fname`` is
            blank.

        slab : str
            Mode for saving the database:

            * ``ALL`` - Save the model data, solution data and post data (element tables, etc.). This value is the default.

            * ``MODEL`` - Save the model data (solid model, finite element model, loadings, etc.) only.

            * ``SOLU`` - Save the model data and the solution data (nodal and element results).

        Notes
        -----

        .. _SAVE_notes:

        Saves all current database information to a file ( :file:`File.DB` ). In interactive mode, an
        existing :file:`File.DB` is first written to a backup file ( :file:`File.DBB` ). In batch mode, an
        existing :file:`File.DB` is replaced by the current database information with no backup. The command
        should be issued periodically to ensure a current file backup in case of a system "crash" or a "line
        drop." It may also be issued before a "doubtful" command so that if the result is not what was
        intended the database may be easily restored to the previous state. A save may be time consuming for
        large models. Repeated use of this command overwrites the previous data on the file (but a backup
        file is first written during an interactive run). When issued from within POST1, the nodal boundary
        conditions in the database (which were read from the results file) will overwrite the nodal boundary
        conditions existing on the database file.

        Internal nodes may be created during solution (for example, via the mixed u-P formulation or
        generalized plane strain option for `current-technology elements
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_elem/EL2oldnewtable.html#EL2curtechelembenefits>`_,
        the Lagrangian multiplier method for contact elements or the MPC184 elements, or the quadratic or
        cubic option of the BEAM188 and PIPE288 elements). It is sometimes necessary to save the internal
        nodes in the database for later operations, such as cutting boundary interpolations ( :ref:`cbdof` )
        for `submodeling
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_adv/Hlp_G_ADV4_5.html>`_. To do so,
        issue the :ref:`save` command after the first :ref:`solve` command.

        In general, saving after solving is always a good practice.

        If radiosity surface elements ( SURF251 or SURF252 ) are present in the model, a radiosity mapping
        data file, :file:`Fname.RSM,` is also saved when the :ref:`save` command is issued. For more
        information, see `Advanced Radiosity Options
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_the/Hlp_G_THEadvrad.html#themultrsymm>`_

        This command is valid in any processor.
        """
        command = f"SAVE,{fname},{ext},,{slab}"
        return self.run(command, **kwargs)

    def stitle(self, nline: str = "", title: str = "", **kwargs):
        r"""Defines subtitles.

        Mechanical APDL Command: `/STITLE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_STITLE.html>`_

        Parameters
        ----------
        nline : str
            Subtitle line number (1 to 4). Defaults to 1.

        title : str
            Input up to 70 alphanumeric characters. Parameter substitution may be forced within the title by
            enclosing the parameter name or parametric expression within percent (%) signs. If ``Title`` is
            blank, this subtitle is deleted.

        Notes
        -----

        .. _s-STITLE_notes:

        Up to four subtitles are displayed in the output along with the main title ( :ref:`title` ).

        Subtitles do not appear in GUI windows or in plot displays.

        The first subtitle is also written to various Mechanical APDL files along with the main title.

        Previous subtitles can be overwritten or deleted.

        Issue :ref:`slashstatus` to display titles.

        This command is valid in any processor.
        """
        command = f"/STITLE,{nline},{title}"
        return self.run(command, **kwargs)

    def stat(self, **kwargs):
        r"""Displays the status of database settings.

        Mechanical APDL Command: `STAT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_STAT.html>`_

        Notes
        -----

        .. _STAT_notes:

        :ref:`stat` is a command generated by the GUI and will appear in the log file ( :file:`Jobname.LOG`
        ) if status is requested for some items under Utility Menu> List> Status. Generally, :ref:`stat`
        will be preceded by one of the commands listed below, which specifies the particular topic that
        status was requested for.

        If entered directly into the program, the :ref:`stat` command should be immediately preceded by the
        desired topic command listed below. In processors other than those listed below (for example,
        AUX12), no topic command should proceed :ref:`stat`.

        This command is valid in any processor.

        PREP7 topic commands (and their corresponding topics) are:

        InformalTables need to be added.
        SOLUTION topic commands (and their corresponding topics) are:

        InformalTables need to be added.
        POST1 topic commands (and their corresponding topics) are:

        InformalTables need to be added.
        POST26 topic commands (and their corresponding topics) are:

        InformalTables need to be added.
        """
        command = "STAT"
        return self.run(command, **kwargs)
