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


class Components:

    def cmlist(self, name: str = "", key: int | str = "", entity: str = "", **kwargs):
        r"""Lists the contents of a component or assembly.

        Mechanical APDL Command: `CMLIST <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMLIST.html>`_

        Parameters
        ----------
        name : str
            Name of the component or assembly to be listed (if blank, list all selected components and
            assemblies). If ``Name`` is specified, then ``Entity`` is ignored.

        key : int or str
            Expansion key:

            * ``0`` - Do not list individual entities in the component.

            * ``1 or EXPA`` - List individual entities in the component.

        entity : str
            If ``Name`` is blank, then the following entity types can be specified:

            * ``VOLU`` - List the volume components only.

            * ``AREA`` - List the area components only.

            * ``LINE`` - List the line components only.

            * ``KP`` - List the keypoint components only

            * ``ELEM`` - List the element components only.

            * ``NODE`` - List the node components only.

        Notes
        -----

        .. _CMLIST_notes:

        This command is valid in any processor. For components, it lists the type of geometric entity. For
        assemblies, it lists the components and/or assemblies that make up the assembly.

        Examples of possible usage:

        :ref:`cmlist` - List all selected components. :ref:`cmlist`, EXPA - List all selected components
        and for each component list the underlying entity ID's. :ref:`cmlist`, ``Name`` - List the specified
        component. :ref:`cmlist`, ``Name``,EXPA - List specified component along with all underlying entity
        ID's. :ref:`cmlist`, EXPA,  ``Entity`` - List all selected components of specified entity
        type. For each component also list the underlying entity ID's.
        """
        command = f"CMLIST,{name},{key},{entity}"
        return self.run(command, **kwargs)

    def cmgrp(
        self,
        aname: str = "",
        cnam1: str = "",
        cnam2: str = "",
        cnam3: str = "",
        cnam4: str = "",
        cnam5: str = "",
        cnam6: str = "",
        cnam7: str = "",
        cnam8: str = "",
        **kwargs,
    ):
        r"""Groups components and assemblies into an assembly.

        Mechanical APDL Command: `CMGRP <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMGRP.html>`_

        Parameters
        ----------
        aname : str
            An alphanumeric name used to identify this assembly. ``Aname`` may be up to 256 characters,
            beginning with a letter and containing only letters, numbers, dots (.), and underscores (_).
            Overwrites a previously defined

             ``Aname`` (and removes it from higher level assemblies, if any).

        cnam1 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam2 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam3 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam4 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam5 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam6 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam7 : str
            Names of existing components or other assemblies to be included in this assembly.

        cnam8 : str
            Names of existing components or other assemblies to be included in this assembly.

        Notes
        -----

        .. _CMGRP_notes:

        Groups components and other assemblies into an assembly identified by a name. :ref:`cmgrp` is used
        for the initial definition of an assembly. An assembly is used in the same manner as a component. Up
        to 5 levels of assemblies within assemblies may be used.

        An assembly is a convenient grouping of previously defined components and other assemblies.
        Assemblies may contain components only, other assemblies, or any combination. A component may belong
        to any number of assemblies. Up to 5 levels of nested assemblies may be defined. Components and
        assemblies may be added to or deleted from an existing assembly by the :ref:`cmedit` command. Once
        defined, an assembly may be listed, deleted, selected, or unselected using the same commands as for
        a component. Assemblies are automatically updated to reflect deletions of one or more of their
        components or lower-level assemblies. Assemblies are not automatically deleted when all their
        components or subassemblies are deleted.

        This command is valid in any processor.
        """
        command = f"CMGRP,{aname},{cnam1},{cnam2},{cnam3},{cnam4},{cnam5},{cnam6},{cnam7},{cnam8}"
        return self.run(command, **kwargs)

    def cmdele(self, name: str = "", **kwargs):
        r"""Deletes a component or assembly definition.

        Mechanical APDL Command: `CMDELE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMDELE.html>`_

        Parameters
        ----------
        name : str
            Name of the component or assembly whose definition is to be removed.

        Notes
        -----

        .. _CMDELE_notes:

        Entities contained in the component, or the components within the assembly, are unaffected. Only the
        grouping relationships are deleted. Assemblies are automatically updated to reflect deletion of
        their components or subassemblies, but they are not automatically deleted when all their components
        or subassemblies are deleted.

        This command is valid in any processor.
        """
        command = f"CMDELE,{name}"
        return self.run(command, **kwargs)

    def cm(self, cname: str = "", entity: str = "", kopt: str = "", **kwargs):
        r"""Groups geometry items into a component.

        Mechanical APDL Command: `CM <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CM.html>`_

        Parameters
        ----------
        cname : str
            An alphanumeric name used to identify this component. ``Cname`` may be up to 256 characters,
            beginning with a letter and containing only letters, numbers, dots (.) and underscores (_).
            Component names beginning with an underscore (for example, _LOOP) are reserved for use by
            Mechanical APDL and should be avoided. Components named "ALL," "STAT," and "DEFA" are not
            permitted. Overwrites a previously defined name.

        entity : str
            Label identifying the type of geometry items to be grouped:

            * ``VOLU`` - Volumes.

            * ``AREA`` - Areas.

            * ``LINE`` - Lines.

            * ``KP`` - Keypoints.

            * ``ELEM`` - Elements.

            * ``NODE`` - Nodes.

        kopt : str
            Controls how element component contents are updated during `nonlinear mesh adaptivity analysis
            <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_nlad/advmnaexample.html>`_ :

            0 - Component is not updated during remeshing and therefore contains only initial mesh elements
            (default). 1 - Component is updated during remeshing to contain the updated elements.

            This argument is valid only for nonlinear mesh adaptivity analysis with ``Entity`` = ELEM, and
            for solid element components only.

        Notes
        -----

        .. _CM_notes:

        Components may be further grouped into assemblies ( :ref:`cmgrp` ). The selected items of the
        specified entity type will be stored as the component. Use of this component in the select command (
        :ref:`cmsel` ) causes all these items to be selected at once, for convenience.

        A component is a grouping of some geometric entity that can then be conveniently selected or
        unselected. A component may be redefined by reusing a previous component name. The following entity
        types may belong to a component: nodes, elements, keypoints, lines, areas, and volumes. A component
        may contain only 1 entity type, but an individual item of any entity may belong to any number of
        components. Once defined, the items contained in a component may then be easily selected or
        unselected ( :ref:`cmsel` ). Components may be listed ( :ref:`cmlist` ), modified ( :ref:`cmmod` )
        and deleted ( :ref:`cmdele` ). Components may also be further grouped into assemblies ( :ref:`cmgrp`
        ). Other entities associated with the entities in a component (for example, the lines and keypoints
        associated with areas) may be selected by the :ref:`allsel` command.

        An item will be deleted from a component if it has been deleted by another operation (see the
        :ref:`kmodif` command for an example). Components are automatically updated to reflect deletions of
        one or more of their items. Components are automatically deleted and a warning message is issued if
        all their items are deleted. Assemblies are also automatically updated to reflect deletions of one
        or more of their components or subassemblies, but are not deleted if all their components and
        subassemblies are deleted.

        For `nonlinear mesh adaptivity analysis
        <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en/ans_nlad/advmnaexample.html>`_, an extra
        option is available to update the element component contents automatically during the analysis,
        applicable in cases where the remeshing region overlaps the defined solid element component region.
        By enabling the option, the component element boundary is maintained, and the validity of the
        defined component is guaranteed during the entire analysis run; therefore, the component can be used
        during both solution and postprocessing.

        Components are often used as input to other commands. Some commands restrict the component name to
        32 characters. For those commands, this limitation is documented within the command description.

        This command is valid in any processor.
        """
        command = f"CM,{cname},{entity},,{kopt}"
        return self.run(command, **kwargs)

    def cmmod(self, cname: str = "", keyword: str = "", value: str = "", **kwargs):
        r"""Modifies the specification of a component.

        Mechanical APDL Command: `CMMOD <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMMOD.html>`_

        Parameters
        ----------
        cname : str
            Name of the existing component or assembly to be modified.

        keyword : str
            The label identifying the type of value to be modified.

            NAME - Modify the NAME of the component

        value : str
            If ``Keyword`` is NAME, then the value is the alphanumeric label to be applied. See the
            :ref:`cm` command for naming convention details. If a component named ``Value`` already exists,
            the command will be ignored and an error message will be generated.

        Notes
        -----

        .. _CMMOD_notes:

        The naming conventions for components, as specified in the :ref:`cm` command, apply for :ref:`cmmod`
        ( 256 characters, "ALL", "STAT" and "DEFA" are not allowed, etc.). However, if you choose a
        component name that is already designated for another component, an error message will be issued and
        the command will be ignored.

        This command is valid in any processor.
        """
        command = f"CMMOD,{cname},{keyword},{value}"
        return self.run(command, **kwargs)

    def cmedit(
        self,
        aname: str = "",
        oper: str = "",
        cnam1: str = "",
        cnam2: str = "",
        cnam3: str = "",
        cnam4: str = "",
        cnam5: str = "",
        cnam6: str = "",
        cnam7: str = "",
        **kwargs,
    ):
        r"""Edits an existing assembly.

        Mechanical APDL Command: `CMEDIT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMEDIT.html>`_

        Parameters
        ----------
        aname : str
            Name of the assembly to be edited.

        oper : str
            Operation label:

            * ``ADD`` - To add more components. The level of any assembly to be added must be lower than that of the
              assembly ``Aname`` (see :ref:`cmgrp` command).

            * ``DELE`` - To remove components.

        cnam1 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam2 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam3 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam4 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam5 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam6 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        cnam7 : str
            Names of components and assemblies to be added to or deleted from the assembly.

        Notes
        -----

        .. _CMEDIT_notes:

        This command is valid in any processor.
        """
        command = f"CMEDIT,{aname},{oper},{cnam1},{cnam2},{cnam3},{cnam4},{cnam5},{cnam6},{cnam7}"
        return self.run(command, **kwargs)

    def cmwrite(self, fname: str = "", ext: str = "", fmat: str = "", **kwargs):
        r"""Writes node and element components and assemblies to a file.

        Mechanical APDL Command: `CMWRITE <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMWRITE.html>`_

        Parameters
        ----------
        fname : str
            File name and directory path (248 characters maximum, including the characters needed for the
            directory path). An unspecified directory path defaults to the working directory; in this case,
            you can use all 248 characters for the file name. The file name defaults to Jobname.

        ext : str
            Filename extension (eight-character maximum). The extension defaults to CM if ``Fname`` is
            blank.

        fmat : str
            Format of the output file (defaults to BLOCKED).

            * ``BLOCKED`` - Blocked format. This format allows faster reading of the file.

            * ``UNBLOCKED`` - Unblocked format.

        """
        command = f"CMWRITE,{fname},{ext},,,{fmat}"
        return self.run(command, **kwargs)

    def cmplot(self, label: str = "", entity: str = "", keyword: str = "", **kwargs):
        r"""Plots the entities contained in a component or assembly.

        Mechanical APDL Command: `CMPLOT <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMPLOT.html>`_

        Parameters
        ----------
        label : str
            Name of the component or assembly to be plotted.

            * ``(blank)`` - All selected components and assemblies are plotted (default). If fewer than 11 components are
              selected, then all are plotted. If more than 11 components are selected, then only the first 11 are
              plotted.

            * ``ALL`` - All selected components are plotted. If number of selected components is greater than 11, then the
              legend showing component names will not be shown.

            * ``N`` - Next set of defined components and assemblies is plotted.

            * ``P`` - Previous set of defined components and assemblies is plotted.

            * ``Cname`` - The specified component or assembly is plotted.

            * ``SetNo.`` - The specified set number is plotted.

        entity : str
            If ``Label`` is BLANK or ALL, then the following entity types can be specified:

            * ``VOLU`` - Plot the volume components only.

            * ``AREA`` - Plot the area components only.

            * ``LINE`` - Plot the line components only.

            * ``KP`` - Plot the keypoint components only.

            * ``ELEM`` - Plot the element components only.

            * ``NODE`` - Plot the node components only.

        keyword : str
            For ``Keyword`` = ALL, plot the specified component name in the ``Label`` field in the context
            of all entities of the same type. Not valid if ``Label`` field is BLANK or ALL.

        Notes
        -----

        .. _CMPLOT_notes:

        Components are plotted with their native entities. For assemblies, all native entities for the
        underlying component types are plotted simultaneously. Although more components can be plotted, the
        legend displays only 11 at a time. When more than eleven are plotted, the legend is not displayed.

        Possible usage:

        :ref:`cmplot`, ``CNAME`` - Plots the specified component (if selected). :ref:`cmplot`, ``CNAME``,
        ALL - Plot component in the context of all other selected entity components of the same type as the
        component. :ref:`cmplot` - Plot the first eleven selected components. :ref:`cmplot`,ALL - Plot all
        selected components. :ref:`cmplot`,N or :ref:`cmplot`,P - Plot next or previous set of eleven
        components. :ref:`cmplot`,ALL, ``Entity`` - Plot all selected components of type specified in
        ``Entity``. :ref:`cmplot`, ``Entity`` - Plot components of type specified in ``Entity``, from the
        first eleven components. :ref:`cmplot`,N, ``Entity`` - Plot components of type specified in
        ``Entity``, if any, from the next set of eleven components (substitute P for N to plot from previous
        set).

        This command is valid in any processor.
        """
        command = f"CMPLOT,{label},{entity},{keyword}"
        return self.run(command, **kwargs)

    def cmsel(self, type_: str = "", name: str = "", entity: str = "", **kwargs):
        r"""Selects a subset of components and assemblies.

        Mechanical APDL Command: `CMSEL <https://ansyshelp.ansys.com/Views/Secured/corp/v232/en//ans_cmd/Hlp_C_CMSEL.html>`_

        Parameters
        ----------
        type_ : str
            Label identifying the type of select:

            * ``S`` - Select a new set (default).

            * ``R`` - Reselect a set from the current set.

            * ``A`` - Additionally select a set and extend the current set.

            * ``U`` - Unselect a set from the current set.

            * ``ALL`` - Also select all components.

            * ``NONE`` - Unselect all components.

        name : str
            Name of component or assembly whose items are to be selected (valid only if ``Type`` = S, R, A,
            or U).

            Graphical picking is enabled if ``Type`` is blank and ``Name`` = PICK (or simply "P").

        entity : str
            If ``Name`` is blank, then the following entity types can be specified:

            * ``VOLU`` - Select the volume components only.

            * ``AREA`` - Select the area components only.

            * ``LINE`` - Select the line components only.

            * ``KP`` - Select the keypoint components only.

            * ``ELEM`` - Select the element components only.

            * ``NODE`` - Select the node components only.

        Notes
        -----

        .. _CMSEL_notes:

        Selecting by component is a convenient adjunct to individual item selection (for example,
        :ref:`vsel`, :ref:`esel`, etc.). :ref:`cmsel`, ALL allows you to select components **in addition**
        to other items you have already selected.

        If ``Type`` = R for an assembly selection ( :ref:`cmsel`,R,< assembly-name >), the reselect
        operation is performed on each component in the assembly in the order in which the components make
        up the assembly. Thus, if one reselect operation results in an empty set, subsequent operations will
        also result in empty sets. For example, if the first reselect operation tries to reselect node 1
        from the selected set of nodes 3, 4, and 5, the operation results in an empty set (that is, no nodes
        are selected). Since the current set is now an empty set, if the second reselect operation tries to
        reselect any nodes, the second operation also results in an empty set, and so on. This is equivalent
        to repeating the command :ref:`cmsel`,R,< component-name > once for each component making up the
        assembly.

        This command is valid in any processor.
        """
        command = f"CMSEL,{type_},{name},{entity}"
        return self.run(command, **kwargs)
