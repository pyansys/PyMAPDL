"""
Replacing Result in PyMAPDL.
"""


"""
COMMENTS
========


TODO's
======
* Check #todos
* Allow (step, substep) in rnum
* Component support
* Check what happens when a node does not have results in all the steps. In DPF is it zero?
* Adding 'principal' support ("SIGMA1, SIGMA2, SIGMA3, SINT, SEQV when principal is True.")
* Check DPF issues

"""

from functools import wraps
import os
import pathlib
import tempfile
from typing import Iterable
import weakref

# from ansys.dpf import post
from ansys.dpf import core as dpf
from ansys.dpf.core import Model
from ansys.mapdl.reader.rst import Result
import numpy as np

from ansys.mapdl.core import LOG as logger
from ansys.mapdl.core.errors import MapdlRuntimeError
from ansys.mapdl.core.misc import random_string


class ResultNotFound(MapdlRuntimeError):
    """Results not found"""

    def __init__(self, msg=""):
        MapdlRuntimeError.__init__(self, msg)


def update_result(function):
    """
    Decorator to wrap :class:`DPFResult <ansys.mapdl.core.reader.result.DPFResult>`
    methods to force update the RST when accessed the first time.

    Parameters
    ----------
    update : bool, optional
        If ``True``, the class information is updated by calling ``/STATUS``
        before accessing the methods. By default ``False``
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if self._update_required or not self._loaded or self._cached_dpf_model is None:
            self._update()
            self._log.debug("RST file updated.")
        return function(self, *args, **kwargs)

    return wrapper


class DPFResult(Result):
    """
    Result object based on DPF library.


    This class replaces the class Result in PyMAPDL-Reader.

    The

    Parameters
    ----------
    rst_file_path : str
        Path to the RST file.

    mapdl : _MapdlCore
        Mapdl instantiated object.

    """

    def __init__(self, rst_file_path=None, mapdl=None):
        """Initialize Result instance"""

        self.__rst_directory = None
        self.__rst_name = None
        self._mapdl_weakref = None

        if rst_file_path is not None:
            if os.path.exists(rst_file_path):
                self.__rst_directory = os.path.dirname(rst_file_path)
                self.__rst_name = os.path.basename(rst_file_path)
            else:
                raise FileNotFoundError(
                    f"The RST file '{rst_file_path}' could not be found."
                )

            self._mode_rst = True

        elif mapdl is not None:
            from ansys.mapdl.core.mapdl import _MapdlCore  # avoid circular import fail.

            if not isinstance(mapdl, _MapdlCore):  # pragma: no cover
                raise TypeError("Must be initialized using Mapdl instance")
            self._mapdl_weakref = weakref.ref(mapdl)
            self._mode_rst = False

        else:
            raise ValueError(
                "One of the following kwargs must be supplied: 'rst_file_path' or 'mapdl'"
            )

        # dpf
        self._loaded = False
        self._update_required = False  # if true, it triggers a update on the RST file
        self._cached_dpf_model = None

        # old attributes
        ELEMENT_INDEX_TABLE_KEY = None  # todo: To fix
        ELEMENT_RESULT_NCOMP = None  # todo: to fix

        # this will be removed once the reader class has been fully substituted.
        super().__init__(self._rst, read_mesh=False)

    @property
    def _mapdl(self):
        """Return the weakly referenced instance of MAPDL"""
        if self._mapdl_weakref:
            return self._mapdl_weakref()

    @property
    def _log(self):
        """alias for mapdl log"""
        if self._mapdl:
            return self._mapdl._log
        else:
            return logger

    @property
    def logger(self):
        """Logger property"""
        return self._log

    @property
    def mode(self):
        if self._mode_rst:
            return "RST"
        elif self._mode_rst:
            return "MAPDL"

    @property
    def mode_rst(self):
        if self._mode_rst:
            return True
        else:
            return False

    @property
    def mode_mapdl(self):
        if not self._mode_rst:
            return True
        else:
            return False

    @property
    def _rst(self):
        return os.path.join(self._rst_directory, self._rst_name)

    @property
    def local(self):
        if self._mapdl:
            return self._mapdl._local

    @property
    def _rst_directory(self):
        if self.__rst_directory is None:
            if self.mode_mapdl:
                if self.local:
                    _rst_directory = self._mapdl.directory
                else:
                    _rst_directory = os.path.join(
                        tempfile.gettempdir(), random_string()
                    )
                    if not os.path.exists(_rst_directory):
                        os.mkdir(_rst_directory)
                self.__rst_directory = _rst_directory

            else:  # rst mode
                # It should have been initialized with this value already.
                pass

        return self.__rst_directory

    @property
    def _rst_name(self):
        if self.__rst_name is None:
            if self.local:
                self.__rst_name = self._mapdl.jobname
            else:
                self.__rst_name = f"model_{random_string()}.rst"
        return self.__rst_name

    def _update(self, progress_bar=None, chunk_size=None):
        if self._mapdl:
            self._update_rst(progress_bar=progress_bar, chunk_size=chunk_size)

        # Updating model
        self._build_dpf_object()

        # Resetting flag
        self._loaded = True
        self._update_required = False

    def _update_rst(self, progress_bar=None, chunk_size=None):
        # Saving model
        self._mapdl.save(self._rst_name[:-4], "rst", "model")

        if self.local and not self.local:
            self._log.debug("Updating the local copy of remote RST file.")
            # download file
            self._mapdl.download(
                self._rst_name,
                self._rst_directory,
                progress_bar=progress_bar,
                chunk_size=chunk_size,
            )
        # self._update_required = not self._update_required # demonstration

    def _build_dpf_object(self):
        if self._log:
            self._log.debug("Building DPF Model object.")
        self._cached_dpf_model = Model(self._rst)
        # self._cached_dpf_model = post.load_solution(self._rst)  # loading file

    @property
    def model(self):
        if self._cached_dpf_model is None or self._update_required:
            self._build_dpf_object()
        return self._cached_dpf_model

    @property
    def metadata(self):
        return self.model.metadata

    @property
    def mesh(self):
        """Mesh from result file."""
        # TODO: this should be a class equivalent to reader.mesh class.
        return self.model.mesh

    @property
    def grid(self):
        return self.model.mesh.grid

    def _get_nodes_for_argument(self, nodes):
        """Get nodes from 'nodes' which can be int, floats, or list/tuple of int/floats, or
        components( strs, or iterable[strings]"""
        if isinstance(nodes, (int, float)):
            return nodes
        elif isinstance(nodes, str):
            # it is component name
            nodes = [nodes]
        elif isinstance(nodes, Iterable):
            if all([isinstance(each, (int, float)) for each in nodes]):
                return nodes
            elif all([isinstance(each, str) for each in nodes]):
                pass
        else:
            raise TypeError(
                "Only ints, floats, strings or iterable of the previous ones are allowed."
            )

        # For components selections:
        nodes_ = []
        available_ns = self.model.mesh.available_named_selections
        for each_named_selection in nodes:
            if each_named_selection not in available_ns:
                raise ValueError(
                    f"The named selection '{each_named_selection}' does not exist."
                )

            scoping = self.model.mesh.named_selection(each_named_selection)
            if scoping.location != "Nodal":
                raise ValueError(
                    f"The named selection '{each_named_selection}' does not contain nodes."
                )

            nodes_.append(scoping.ids)

        return nodes

    def _get_principal(self, op):
        fc = op.outputs.fields_as_fields_container()[
            0
        ]  # This index 0 is the step indexing.

        op1 = dpf.operators.invariant.principal_invariants()
        op1.inputs.field.connect(fc)
        # Get output data
        result_field_eig_1 = op.outputs.field_eig_1()
        result_field_eig_2 = op.outputs.field_eig_2()
        result_field_eig_3 = op.outputs.field_eig_3()

        op2 = dpf.operators.invariant.invariants()
        op2.inputs.field.connect(fc)

        # Get output data
        result_field_int = op.outputs.field_int()
        result_field_eqv = op.outputs.field_eqv()
        # result_field_max_shear = op.outputs.field_max_shear()

        return np.hstack(
            (
                result_field_eig_1,
                result_field_eig_2,
                result_field_eig_3,
                result_field_int,
                result_field_eqv,
            )
        )

    def _extract_data(self, op):
        fc = op.outputs.fields_as_fields_container()[
            0
        ]  # This index 0 is the step indexing.

        # When we destroy the operator, we might lose access to the array, that is why we copy.
        ids = fc.scoping.ids.copy()
        data = fc.data.copy()

        return ids, data

    def _set_rescope(self, op, scope_ids):
        fc = op.outputs.fields_container()

        rescope = dpf.operators.scoping.rescope()
        rescope.inputs.mesh_scoping(sorted(scope_ids))
        rescope.inputs.fields(fc)
        return rescope

    def _set_mesh_scoping(self, op, mesh, requested_location, scope_ids):
        scop = dpf.Scoping()

        if requested_location.lower() == "nodal":
            scop.location = dpf.locations.nodal
            if scope_ids:
                scop.ids = scope_ids
            else:
                scop.ids = mesh.nodes.scoping.ids

        elif requested_location.lower() == "elemental_nodal":
            if scope_ids:
                scop.ids = scope_ids
            else:
                scop.ids = mesh.elements.scoping.ids

        elif requested_location.lower() == "elemental":
            scop.location = dpf.locations.elemental
            if scope_ids:
                scop.ids = scope_ids
            else:
                scop.ids = mesh.elements.scoping.ids
        else:
            raise ValueError(
                f"The 'requested_location' value ({requested_location}) is not allowed."
            )
        op.inputs.mesh_scoping.connect(scop)
        return scop.ids

    def _set_element_results(self, op, mesh):

        fc = op.outputs.fields_container()

        op2 = dpf.operators.averaging.to_elemental_fc(collapse_shell_layers=True)
        op2.inputs.fields_container.connect(fc)
        op2.inputs.mesh.connect(mesh)

        return op2

    def _set_input_timestep_scope(self, op, rnum):

        if not rnum:
            rnum = [int(1)]
        else:
            if isinstance(rnum, (int, float)):
                rnum = [rnum]
            elif isinstance(rnum, (list, tuple)):
                rnum = [self.parse_step_substep(rnum)]
            else:
                raise TypeError(
                    "Only 'int' and 'float' are supported to define the steps."
                )

        my_time_scoping = dpf.Scoping()
        my_time_scoping.location = "time_freq_steps"  # "time_freq"
        my_time_scoping.ids = rnum

        op.inputs.time_scoping.connect(my_time_scoping)

    def _get_operator(self, result_field):
        if not hasattr(self.model.results, result_field):
            list_results = "\n    ".join(
                [each for each in dir(self.model.results) if not each.startswith("_")]
            )
            raise ResultNotFound(
                f"The result '{result_field}' cannot be found on the RST file. "
                f"The current results are:\n    {list_results}"
            )

        # Getting field
        return getattr(self.model.results, result_field)()

    def _get_nodes_result(
        self,
        rnum,
        result_type,
        in_nodal_coord_sys=False,
        nodes=None,
        return_operator=False,
    ):
        return self._get_result(
            rnum,
            result_type,
            requested_location="Nodal",
            scope_ids=nodes,
            result_in_entity_cs=in_nodal_coord_sys,
            return_operator=return_operator,
        )

    def _get_elem_result(
        self,
        rnum,
        result_type,
        in_element_coord_sys=False,
        elements=None,
        return_operator=False,
    ):
        return self._get_result(
            rnum,
            result_type,
            requested_location="Elemental",
            scope_ids=elements,
            result_in_entity_cs=in_element_coord_sys,
            return_operator=return_operator,
        )

    def _get_elemnodal_result(
        self,
        rnum,
        result_type,
        in_element_coord_sys=False,
        elements=None,
        return_operator=False,
    ):
        return self._get_result(
            rnum,
            result_type,
            requested_location="Elemental_Nodal",
            scope_ids=elements,
            result_in_entity_cs=in_element_coord_sys,
            return_operator=return_operator,
        )

    @update_result
    def _get_result(
        self,
        rnum,
        result_field,
        requested_location="Nodal",
        scope_ids=None,
        result_in_entity_cs=False,
        return_operator=False,
    ):
        """
        Get elemental/nodal/elementalnodal results.

        Parameters
        ----------
        rnum : int
            Result step/set
        result_field : str
            Result type, for example "stress", "strain", "displacement", etc.
        requested_location : str, optional
            Results given at which type of entity, by default "Nodal"
        scope_ids : Union([int, floats, List[int]]), optional
            List of entities (nodal/elements) to get the results from, by default None
        result_in_entity_cs : bool, optional
            Obtain the results in the entity coordenate system, by default False
        return_operator : bool, optional
            Return the last used operator (most of the times it will be a Rescope operator).
            Defaults to ``False``.

        Returns
        -------
        np.array
            Ids of the entities (nodes or elements)
        np.array
            Values of the entities for the requested solution
        dpf.Operator
            If ``return_operator`` is ``True``, then it will return the last instantiated
            operator (most of the times a

            `Rescope operator<https://dpf.docs.pyansys.com/api/ansys.dpf.core.operators.scoping.rescope.html>`_

            :class:`rescope <ansys.dpf.core.operators.scoping.rescope.rescope>`
            .)

        Raises
        ------
        ResultNotFound
            The given result (stress, strain, ...) could not be found in the RST file.
        TypeError
            Only floats and ints are allowed to scope steps/time.
        NotImplementedError
            Component input selection is still not supported.
        """

        # todo: accepts components in nodes.
        mesh = self.metadata.meshed_region

        if isinstance(scope_ids, np.ndarray):
            scope_ids = scope_ids.tolist()

        op = self._get_operator(result_field)

        # CS output
        if not result_in_entity_cs:
            op.inputs.bool_rotate_to_global.connect(True)
        else:
            op.inputs.bool_rotate_to_global.connect(False)

        # Setting time steps
        self._set_input_timestep_scope(op, rnum)

        # Set type of return
        ids = self._set_mesh_scoping(op, mesh, requested_location, scope_ids)

        if requested_location.lower() == "elemental":
            op = self._set_element_results(
                op, mesh
            )  # overwrite op to be the elemental results OP

        # Applying rescope to make sure the order is right
        op = self._set_rescope(op, ids.astype(int).tolist())

        fc = op.outputs.fields_as_fields_container()[0]
        if fc.shell_layers is not dpf.shell_layers.nonelayer:
            # check
            pass

        if return_operator:
            return op
        else:
            return self._extract_data(op)

    def nodal_displacement(self, rnum, in_nodal_coord_sys=None, nodes=None):
        """Returns the DOF solution for each node in the global
        cartesian coordinate system or nodal coordinate system.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        in_nodal_coord_sys : bool, optional
            When ``True``, returns results in the nodal coordinate
            system.  Default ``False``.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : int np.ndarray
            Node numbers associated with the results.

        result : float np.ndarray
            Array of nodal displacements.  Array
            is (``nnod`` x ``sumdof``), the number of nodes by the
            number of degrees of freedom which includes ``numdof`` and
            ``nfldof``

        Examples
        --------
        Return the nodal soltuion (in this case, displacement) for the
        first result of ``"file.rst"``

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, data = rst.nodal_solution(0)

        Return the nodal solution just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, data = rst.nodal_solution(0, nodes='MY_COMPONENT')

        Return the nodal solution just for the nodes from 20 through 50.

        >>> nnum, data = rst.nodal_solution(0, nodes=range(20, 51))

        Notes
        -----
        Some solution results may not include results for each node.
        These results are removed by and the node numbers of the
        solution results are reflected in ``nnum``.
        """
        return self._get_nodes_result(rnum, "displacement", in_nodal_coord_sys, nodes)

    def nodal_solution(self, rnum, in_nodal_coord_sys=None, nodes=None):
        """Returns the DOF solution for each node in the global
        cartesian coordinate system or nodal coordinate system.

        Solution may be nodal temperatures or nodal displacements
        depending on the type of the solution.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        in_nodal_coord_sys : bool, optional
            When ``True``, returns results in the nodal coordinate
            system.  Default ``False``.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : int np.ndarray
            Node numbers associated with the results.

        result : float np.ndarray
            Array of nodal displacements or nodal temperatures.  Array
            is (``nnod`` x ``sumdof``), the number of nodes by the
            number of degrees of freedom which includes ``numdof`` and
            ``nfldof``

        Examples
        --------
        Return the nodal soltuion (in this case, displacement) for the
        first result of ``"file.rst"``

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, data = rst.nodal_solution(0)

        Return the nodal solution just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, data = rst.nodal_solution(0, nodes='MY_COMPONENT')

        Return the nodal solution just for the nodes from 20 through 50.

        >>> nnum, data = rst.nodal_solution(0, nodes=range(20, 51))

        Notes
        -----
        Some solution results may not include results for each node.
        These results are removed by and the node numbers of the
        solution results are reflected in ``nnum``.
        """

        if hasattr(self.model.results, "displacement"):
            return self.nodal_displacement(rnum, in_nodal_coord_sys, nodes)
        elif hasattr(self.model.results, "displacement"):
            return self.nodal_temperature(rnum, nodes)
        else:
            raise ResultNotFound(
                "The current analysis does not have 'displacement' or 'temperature' results."
            )

    def nodal_temperature(self, rnum, nodes=None):
        """Retrieves the temperature for each node in the
        solution.

        The order of the results corresponds to the sorted node
        numbering.

        Equivalent MAPDL command: PRNSOL, TEMP

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : numpy.ndarray
            Node numbers of the result.

        temperature : numpy.ndarray
            Temperature at each node.

        Examples
        --------
        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, temp = rst.nodal_temperature(0)

        Return the temperature just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, temp = rst.nodal_stress(0, nodes='MY_COMPONENT')

        Return the temperature just for the nodes from 20 through 50.

        >>> nnum, temp = rst.nodal_solution(0, nodes=range(20, 51))

        """
        return self._get_nodes_result(rnum, "temperature", nodes)

    def nodal_voltage(self, rnum, in_nodal_coord_sys=None, nodes=None):
        """Retrieves the voltage for each node in the
        solution.

        The order of the results corresponds to the sorted node
        numbering.

        Equivalent MAPDL command: PRNSOL, VOLT

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : numpy.ndarray
            Node numbers of the result.

        voltage : numpy.ndarray
            voltage at each node.

        Examples
        --------
        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, temp = rst.nodal_voltage(0)

        Return the voltage just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, temp = rst.nodal_stress(0, nodes='MY_COMPONENT')

        """
        return self._get_nodes_result(
            rnum, "electric_potential", in_nodal_coord_sys, nodes
        )

    def element_stress(
        self, rnum, principal=None, in_element_coord_sys=None, elements=None, **kwargs
    ):
        """Retrieves the element component stresses.

        Equivalent ANSYS command: PRESOL, S

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        principal : bool, optional
            Returns principal stresses instead of component stresses.
            Default False.

        in_element_coord_sys : bool, optional
            Returns the results in the element coordinate system.
            Default False and will return the results in the global
            coordinate system.

        elements : str, sequence of int or str, optional
            Select a limited subset of elements.  Can be a element
            component or array of element numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        **kwargs : optional keyword arguments
            Hidden options for distributed result files.

        Returns
        -------
        enum : np.ndarray
            ANSYS element numbers corresponding to each element.

        element_stress : list
            Stresses at each element for each node for Sx Sy Sz Sxy
            Syz Sxz or SIGMA1, SIGMA2, SIGMA3, SINT, SEQV when
            principal is True.

        enode : list
            Node numbers corresponding to each element's stress
            results.  One list entry for each element.

        Examples
        --------
        Element component stress for the first result set.

        >>> rst.element_stress(0)

        Element principal stress for the first result set.

        >>> enum, element_stress, enode = result.element_stress(0, principal=True)

        Notes
        -----
        Shell stresses for element 181 are returned for top and bottom
        layers.  Results are ordered such that the top layer and then
        the bottom layer is reported.
        """
        if principal:
            op = self._get_elem_result(
                rnum,
                "stress",
                in_element_coord_sys=in_element_coord_sys,
                elements=elements,
                return_operator=True,
                **kwargs,
            )
            return self._get_principal(op)
        else:
            return self._get_elem_result(
                rnum, "stress", in_element_coord_sys, elements, **kwargs
            )

    def element_nodal_stress(
        self, rnum, principal=None, in_element_coord_sys=None, elements=None, **kwargs
    ):
        """Retrieves the nodal stresses for each element.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a list containing
            (step, substep) of the requested result.

        principal : bool, optional
            Returns principal stresses instead of component stresses.
            Default False.

        in_element_coord_sys : bool, optional
            Returns the results in the element coordinate system if ``True``.
            Else, it returns the results in the global coordinate system.
            Default False

        elements : str, sequence of int or str, optional
            Select a limited subset of elements.  Can be a element
            component or array of element numbers.  For example:

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        **kwargs : optional keyword arguments
            Hidden options for distributed result files.

        Returns
        -------
        enum : np.ndarray
            ANSYS element numbers corresponding to each element.

        element_stress : list
            Stresses at each element for each node for Sx Sy Sz Sxy
            Syz Sxz or SIGMA1, SIGMA2, SIGMA3, SINT, SEQV when
            principal is True.

        enode : list
            Node numbers corresponding to each element's stress
            results.  One list entry for each element.

        Examples
        --------
        Element component stress for the first result set.

        >>> rst.element_stress(0)

        Element principal stress for the first result set.

        >>> enum, element_stress, enode = result.element_stress(0, principal=True)

        Notes
        -----
        Shell stresses for element 181 are returned for top and bottom
        layers.  Results are ordered such that the top layer and then
        the bottom layer is reported.
        """
        if principal:
            op = self._get_elemnodal_result(
                rnum,
                "stress",
                in_element_coord_sys=in_element_coord_sys,
                elements=elements,
                return_operator=True,
                **kwargs,
            )
            return self._get_principal(op)
        else:
            return self._get_elemnodal_result(
                rnum, "stress", in_element_coord_sys, elements, **kwargs
            )

    def nodal_elastic_strain(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Nodal component elastic strains.  This record contains
        strains in the order ``X, Y, Z, XY, YZ, XZ, EQV``.

        Elastic strains can be can be nodal values extrapolated from
        the integration points or values at the integration points
        moved to the nodes.

        Equivalent MAPDL command: ``PRNSOL, EPEL``

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : np.ndarray
            MAPDL node numbers.

        elastic_strain : np.ndarray
            Nodal component elastic strains.  Array is in the order
            ``X, Y, Z, XY, YZ, XZ, EQV``.

            .. versionchanged:: 0.64
                The nodes with no values are now equals to zero.
                The results of the midnodes are also calculated and
                presented.

        Examples
        --------
        Load the nodal elastic strain for the first result.

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, elastic_strain = rst.nodal_elastic_strain(0)

        Return the nodal elastic strain just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, elastic_strain = rst.nodal_elastic_strain(0, nodes='MY_COMPONENT')

        Return the nodal elastic strain just for the nodes from 20 through 50.

        >>> nnum, elastic_strain = rst.nodal_elastic_strain(0, nodes=range(20, 51))

        Notes
        -----
        Nodes without a strain will be NAN.

        ..
        """
        return self._get_nodes_result(
            rnum, "elastic_strain", in_nodal_coord_sys=in_nodal_coord_sys, nodes=nodes
        )

    def nodal_plastic_strain(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Nodal component plastic strains.

        This record contains strains in the order:
        ``X, Y, Z, XY, YZ, XZ, EQV``.

        Plastic strains are always values at the integration points
        moved to the nodes.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : np.ndarray
            MAPDL node numbers.

        plastic_strain : np.ndarray
            Nodal component plastic strains.  Array is in the order
            ``X, Y, Z, XY, YZ, XZ, EQV``.

        Examples
        --------
        Load the nodal plastic strain for the first solution.

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, plastic_strain = rst.nodal_plastic_strain(0)

        Return the nodal plastic strain just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, plastic_strain = rst.nodal_plastic_strain(0, nodes='MY_COMPONENT')

        Return the nodal plastic strain just for the nodes from 20
        through 50.

        >>> nnum, plastic_strain = rst.nodal_plastic_strain(0, nodes=range(20, 51))

        """
        return self._get_nodes_result(rnum, "plastic_strain", in_nodal_coord_sys, nodes)

    def nodal_acceleration(self, rnum, in_nodal_coord_sys=None, nodes=None):
        """Nodal velocities for a given result set.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        in_nodal_coord_sys : bool, optional
            When ``True``, returns results in the nodal coordinate
            system.  Default False.

        Returns
        -------
        nnum : int np.ndarray
            Node numbers associated with the results.

        result : float np.ndarray
            Array of nodal accelerations.  Array is (``nnod`` x
            ``sumdof``), the number of nodes by the number of degrees
            of freedom which includes ``numdof`` and ``nfldof``

        Examples
        --------
        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, data = rst.nodal_acceleration(0)

        Notes
        -----
        Some solution results may not include results for each node.
        These results are removed by and the node numbers of the
        solution results are reflected in ``nnum``.
        """
        return self._get_nodes_result(
            rnum, "misc.nodal_acceleration", in_nodal_coord_sys, nodes
        )

    def nodal_reaction_forces(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Nodal reaction forces.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        Returns
        -------
        rforces : np.ndarray
            Nodal reaction forces for each degree of freedom.

        nnum : np.ndarray
            Node numbers corresponding to the reaction forces.  Node
            numbers may be repeated if there is more than one degree
            of freedom for each node.

        dof : np.ndarray
            Degree of freedom corresponding to each node using the
            MAPDL degree of freedom reference table.  See
            ``rst.result_dof`` for the corresponding degrees of
            freedom for a given solution.

        Examples
        --------
        Get the nodal reaction forces for the first result and print
        the reaction forces of a single node.

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> rforces, nnum, dof = rst.nodal_reaction_forces(0)
        >>> dof_ref = rst.result_dof(0)
        >>> rforces[:3], nnum[:3], dof[:3], dof_ref
        (array([  24102.21376091, -109357.01854005,   22899.5303263 ]),
         array([4142, 4142, 4142]),
         array([1, 2, 3], dtype=int32),
         ['UX', 'UY', 'UZ'])

        """
        return self._get_nodes_result(
            rnum, "misc.nodal_reaction_force", in_nodal_coord_sys, nodes
        )

    def nodal_stress(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Retrieves the component stresses for each node in the
        solution.

        The order of the results corresponds to the sorted node
        numbering.

        Computes the nodal stress by averaging the stress for each
        element at each node.  Due to the discontinuities across
        elements, stresses will vary based on the element they are
        evaluated from.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : numpy.ndarray
            Node numbers of the result.

        stress : numpy.ndarray
            Stresses at ``X, Y, Z, XY, YZ, XZ`` averaged at each corner
            node.

        Examples
        --------
        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, stress = rst.nodal_stress(0)

        Return the nodal stress just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, stress = rst.nodal_stress(0, nodes='MY_COMPONENT')

        Return the nodal stress just for the nodes from 20 through 50.

        >>> nnum, stress = rst.nodal_solution(0, nodes=range(20, 51))

        Notes
        -----
        Nodes without a stress value will be NAN.
        Equivalent ANSYS command: PRNSOL, S
        """
        return self._get_nodes_result(rnum, "stress", in_nodal_coord_sys, nodes)

    def nodal_thermal_strain(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Nodal component thermal strain.

        This record contains strains in the order X, Y, Z, XY, YZ, XZ,
        EQV, and eswell (element swelling strain).  Thermal strains
        are always values at the integration points moved to the
        nodes.

        Equivalent MAPDL command: PRNSOL, EPTH, COMP

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : np.ndarray
            MAPDL node numbers.

        thermal_strain : np.ndarray
            Nodal component plastic strains.  Array is in the order
            ``X, Y, Z, XY, YZ, XZ, EQV, ESWELL``

        Examples
        --------
        Load the nodal thermal strain for the first solution.

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, thermal_strain = rst.nodal_thermal_strain(0)

        Return the nodal thermal strain just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, thermal_strain = rst.nodal_thermal_strain(0, nodes='MY_COMPONENT')

        Return the nodal thermal strain just for the nodes from 20 through 50.

        >>> nnum, thermal_strain = rst.nodal_thermal_strain(0, nodes=range(20, 51))
        """
        return self._get_nodes_result(rnum, "thermal_strain", in_nodal_coord_sys, nodes)

    def nodal_velocity(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Nodal velocities for a given result set.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        in_nodal_coord_sys : bool, optional
            When ``True``, returns results in the nodal coordinate
            system.  Default False.

        Returns
        -------
        nnum : int np.ndarray
            Node numbers associated with the results.

        result : float np.ndarray
            Array of nodal velocities.  Array is (``nnod`` x
            ``sumdof``), the number of nodes by the number of degrees
            of freedom which includes ``numdof`` and ``nfldof``

        Examples
        --------
        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, data = rst.nodal_velocity(0)

        Notes
        -----
        Some solution results may not include results for each node.
        These results are removed by and the node numbers of the
        solution results are reflected in ``nnum``.
        """
        return self._get_nodes_result(
            rnum, "misc.nodal_velocity", in_nodal_coord_sys, nodes
        )

    def nodal_static_forces(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Return the nodal forces averaged at the nodes.

        Nodal forces are computed on an element by element basis, and
        this method averages the nodal forces for each element for
        each node.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        nodes : str, sequence of int or str, optional
            Select a limited subset of nodes.  Can be a nodal
            component or array of node numbers.  For example

            * ``"MY_COMPONENT"``
            * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
            * ``np.arange(1000, 2001)``

        Returns
        -------
        nnum : np.ndarray
            MAPDL node numbers.

        forces : np.ndarray
           Averaged nodal forces.  Array is sized ``[nnod x numdof]``
           where ``nnod`` is the number of nodes and ``numdof`` is the
           number of degrees of freedom for this solution.

        Examples
        --------
        Load the nodal static forces for the first result using the
        example hexahedral result file.

        >>> from ansys.mapdl import reader as pymapdl_reader
        >>> from ansys.mapdl.reader import examples
        >>> rst = pymapdl_reader.read_binary(examples.rstfile)
        >>> nnum, forces = rst.nodal_static_forces(0)

        Return the nodal static forces just for the nodal component
        ``'MY_COMPONENT'``.

        >>> nnum, forces = rst.nodal_static_forces(0, nodes='MY_COMPONENT')

        Return the nodal static forces just for the nodes from 20 through 50.

        >>> nnum, forces = rst.nodal_static_forces(0, nodes=range(20, 51))

        Notes
        -----
        Nodes without a a nodal will be NAN.  These are generally
        midside (quadratic) nodes.
        """
        return self._get_nodes_result(
            rnum, "misc.nodal_force", in_nodal_coord_sys, nodes
        )

    def principal_nodal_stress(self, rnum, in_nodal_coord_sys=False, nodes=None):
        """Computes the principal component stresses for each node in
        the solution.

        Parameters
        ----------
        rnum : int or list
            Cumulative result number with zero based indexing, or a
            list containing (step, substep) of the requested result.

        Returns
        -------
        nodenum : numpy.ndarray
            Node numbers of the result.

        pstress : numpy.ndarray
            Principal stresses, stress intensity, and equivalent stress.
            [sigma1, sigma2, sigma3, sint, seqv]

        Examples
        --------
        Load the principal nodal stress for the first solution.

        >>> from ansys.mapdl.core.reader import DPFResult as Result
        >>> rst = Result('file.rst')
        >>> nnum, stress = rst.principal_nodal_stress(0)

        Notes
        -----
        ANSYS equivalent of:
        PRNSOL, S, PRIN

        which returns:
        S1, S2, S3 principal stresses, SINT stress intensity, and SEQV
        equivalent stress.

        Internal averaging algorithm averages the component values
        from the elements at a common node and then calculates the
        principal using the averaged value.

        See the MAPDL ``AVPRIN`` command for more details.
        ``ansys-mapdl-reader`` uses the default ``AVPRIN, 0`` option.

        """
        op = self._get_nodes_result(
            rnum,
            "stress",
            in_nodal_coord_sys=in_nodal_coord_sys,
            nodes=nodes,
            return_operator=True,
        )
        return self._get_principal(op)

    @property
    def n_results(self):
        """Number of results"""
        return self.model.get_result_info().n_results

    @property
    def filename(self) -> str:
        """String form of the filename. This property is read-only."""
        return self._rst  # in the reader, this contains the complete path.

    @property
    def pathlib_filename(self) -> pathlib.Path:
        """Return the ``pathlib.Path`` version of the filename. This property can not be set."""
        return pathlib.Path(self._rst)

    def nsets(self):
        return self.metadata.time_freq_support.n_sets

    def parse_step_substep(self, user_input):
        """Converts (step, substep) to a cumulative index"""
        if isinstance(user_input, int):
            return self.metadata.time_freq_support.get_cumulative_index(
                user_input
            )  # 0 based indexing

        elif isinstance(user_input, (list, tuple)):
            return self.metadata.time_freq_support.get_cumulative_index(
                user_input[0], user_input[1]
            )

        else:
            raise TypeError("Input must be either an int or a list")

    @property
    def version(self):
        """The version of MAPDL used to generate this result file.

        Examples
        --------
        >>> mapdl.result.version
        20.1
        """
        return float(self.model.get_result_info().solver_version)

    @property
    def available_results(self):
        text = "Available Results:\n"
        for each_available_result in self.model.get_result_info().available_results:
            text += (
                each_available_result.native_location
                + " "
                + each_available_result.name
                + "\n"
            )

    @property
    def n_sector(self):
        """Number of sectors"""
        # TODO: Need to check when this is triggered.
        return self.model.get_result_info().has_cyclic

    @property
    def title(self):
        """Title of model in database"""
        return self.model.get_result_info().main_title

    @property
    def is_cyclic(self):  # Todo: DPF should implement this.
        return self.n_sector > 1

    @property
    def units(self):
        return self.model.get_result_info().unit_system_name

    def __repr__(self):
        if False or self.is_distributed:
            rst_info = ["PyMAPDL Reader Distributed Result"]
        else:
            rst_info = ["PyMAPDL Result"]

        rst_info.append("{:<12s}: {:s}".format("title".capitalize(), self.title))
        rst_info.append("{:<12s}: {:s}".format("subtitle".capitalize(), self.subtitle))
        rst_info.append("{:<12s}: {:s}".format("units".capitalize(), self.units))

        rst_info.append("{:<12s}: {:s}".format("Version", self.version))
        rst_info.append("{:<12s}: {:s}".format("Cyclic", self.is_cyclic))
        rst_info.append("{:<12s}: {:d}".format("Result Sets", self.nsets))

        rst_info.append("{:<12s}: {:d}".format("Nodes", self.model.mesh.nodes.n_nodes))
        rst_info.append(
            "{:<12s}: {:d}".format("Elements", self.model.mesh.elements.n_elements)
        )

        rst_info.append("\n")
        rst_info.append(self.available_results)
        return "\n".join(rst_info)

    def nodal_time_history(self, solution_type="NSL", in_nodal_coord_sys=None):
        """The DOF solution for each node for all result sets.

        The nodal results are returned returned in the global
        cartesian coordinate system or nodal coordinate system.

        Parameters
        ----------
        solution_type: str, optional
            The solution type.  Must be either nodal displacements
            (``'NSL'``), nodal velocities (``'VEL'``) or nodal
            accelerations (``'ACC'``).

        in_nodal_coord_sys : bool, optional
            When ``True``, returns results in the nodal coordinate system.
            Default ``False``.

        Returns
        -------
        nnum : int np.ndarray
            Node numbers associated with the results.

        result : float np.ndarray
            Nodal solution for all result sets.  Array is sized
            ``rst.nsets x nnod x Sumdof``, which is the number of
            time steps by number of nodes by degrees of freedom.
        """
        if not isinstance(solution_type, str):
            raise TypeError("Solution type must be a string")

        if solution_type == "NSL":
            func = self.nodal_solution
        elif solution_type == "VEL":
            func = self.nodal_velocity
        elif solution_type == "ACC":
            func = self.nodal_acceleration
        else:
            raise ValueError(
                "Argument 'solution type' must be either 'NSL', " "'VEL', or 'ACC'"
            )

        # size based on the first result
        nnum, sol = func(0, in_nodal_coord_sys)
        data = np.empty((self.nsets, sol.shape[0], sol.shape[1]), np.float64)
        for i in range(self.nsets):
            data[i] = func(i)[1]

        return nnum, data

    def element_components(self):
        """Dictionary of ansys element components from the result file.

        Examples
        --------
        >>> from ansys.mapdl import reader as pymapdl_reader
        >>> from ansys.mapdl.reader import examples
        >>> rst = pymapdl_reader.read_binary(examples.rstfile)
        >>> rst.element_components
        {'ECOMP1': array([17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40], dtype=int32),
        'ECOMP2': array([ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                14, 15, 16, 17, 18, 19, 20, 23, 24], dtype=int32),
        'ELEM_COMP': array([ 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                16, 17, 18, 19, 20], dtype=int32)}
        """
        element_components_ = {}
        for each_named_selection in self.model.mesh.available_named_selections:
            scoping = self.model.mesh.named_selection(each_named_selection)
            element_components_[each_named_selection] = scoping.ids

        return element_components_

    @property
    def time_values(self):
        "Values for the time/frequency"
        return self.metadata.time_freq_support.time_frequencies.data_as_list

    # def save_as_vtk(
    #     self, filename, rsets=None, result_types=["ENS"], progress_bar=True
    # ):
    #     """Writes results to a vtk readable file.

    #     Nodal results will always be written.

    #     The file extension will select the type of writer to use.
    #     ``'.vtk'`` will use the legacy writer, while ``'.vtu'`` will
    #     select the VTK XML writer.

    #     Parameters
    #     ----------
    #     filename : str, pathlib.Path
    #         Filename of grid to be written.  The file extension will
    #         select the type of writer to use.  ``'.vtk'`` will use the
    #         legacy writer, while ``'.vtu'`` will select the VTK XML
    #         writer.

    #     rsets : collections.Iterable
    #         List of result sets to write.  For example ``range(3)`` or
    #         [0].

    #     result_types : list
    #         Result type to write.  For example ``['ENF', 'ENS']``
    #         List of some or all of the following:

    #         - EMS: misc. data
    #         - ENF: nodal forces
    #         - ENS: nodal stresses
    #         - ENG: volume and energies
    #         - EGR: nodal gradients
    #         - EEL: elastic strains
    #         - EPL: plastic strains
    #         - ECR: creep strains
    #         - ETH: thermal strains
    #         - EUL: euler angles
    #         - EFX: nodal fluxes
    #         - ELF: local forces
    #         - EMN: misc. non-sum values
    #         - ECD: element current densities
    #         - ENL: nodal nonlinear data
    #         - EHC: calculated heat generations
    #         - EPT: element temperatures
    #         - ESF: element surface stresses
    #         - EDI: diffusion strains
    #         - ETB: ETABLE items
    #         - ECT: contact data
    #         - EXY: integration point locations
    #         - EBA: back stresses
    #         - ESV: state variables
    #         - MNL: material nonlinear record

    #     progress_bar : bool, optional
    #         Display a progress bar using ``tqdm``.

    #     Notes
    #     -----
    #     Binary files write much faster than ASCII, but binary files
    #     written on one system may not be readable on other systems.
    #     Binary can only be selected for the legacy writer.

    #     Examples
    #     --------
    #     Write nodal results as a binary vtk file.

    #     >>> rst.save_as_vtk('results.vtk')

    #     Write using the xml writer

    #     >>> rst.save_as_vtk('results.vtu')

    #     Write only nodal and elastic strain for the first result

    #     >>> rst.save_as_vtk('results.vtk', [0], ['EEL', 'EPL'])

    #     Write only nodal results (i.e. displacements) for the first result.

    #     >>> rst.save_as_vtk('results.vtk', [0], [])

    #     """
    #     # This should probably be included a part of the ansys.dpf.post.result_data.ResultData class
    #     raise NotImplementedError("To be implemented by DPF")

    # @property
    # def subtitle(self):
    #     raise NotImplementedError("To be implemented by DPF")

    # @property
    # def _is_distributed(self):
    #     raise NotImplementedError("To be implemented by DPF")

    # @property
    # def is_distributed(self):
    #     """True when this result file is part of a distributed result

    #     Only True when Global number of nodes does not equal the
    #     number of nodes in this file.

    #     Notes
    #     -----
    #     Not a reliabile indicator if a cyclic result.
    #     """
    #     return self._is_distributed

    # def cs_4x4(self, cs_cord, as_vtk_matrix=False):
    #     """return a 4x4 transformation array for a given coordinate system"""
    #     raise NotImplementedError("To be implemented by DPF.")

    # def cylindrical_nodal_stress(self):
    #     """Retrieves the stresses for each node in the solution in the
    #     cylindrical coordinate system as the following values:

    #     ``R``, ``THETA``, ``Z``, ``RTHETA``, ``THETAZ``, and ``RZ``

    #     The order of the results corresponds to the sorted node
    #     numbering.

    #     Computes the nodal stress by averaging the stress for each
    #     element at each node.  Due to the discontinuities across
    #     elements, stresses will vary based on the element they are
    #     evaluated from.

    #     Parameters
    #     ----------
    #     rnum : int or list
    #         Cumulative result number with zero based indexing, or a
    #         list containing (step, substep) of the requested result.

    #     nodes : str, sequence of int or str, optional
    #         Select a limited subset of nodes.  Can be a nodal
    #         component or array of node numbers.  For example

    #         * ``"MY_COMPONENT"``
    #         * ``['MY_COMPONENT', 'MY_OTHER_COMPONENT]``
    #         * ``np.arange(1000, 2001)``

    #     Returns
    #     -------
    #     nnum : numpy.ndarray
    #         Node numbers of the result.

    #     stress : numpy.ndarray
    #         Stresses at ``R, THETA, Z, RTHETA, THETAZ, RZ`` averaged
    #         at each corner node where ``R`` is radial.

    #     Examples
    #     --------
    #     >>> from ansys.mapdl.core.reader import DPFResult as Result
    #     >>> rst = Result('file.rst')
    #     >>> nnum, stress = rst.cylindrical_nodal_stress(0)

    #     Return the cylindrical nodal stress just for the nodal component
    #     ``'MY_COMPONENT'``.

    #     >>> nnum, stress = rst.cylindrical_nodal_stress(0, nodes='MY_COMPONENT')

    #     Return the nodal stress just for the nodes from 20 through 50.

    #     >>> nnum, stress = rst.cylindrical_nodal_stress(0, nodes=range(20, 51))

    #     Notes
    #     -----
    #     Nodes without a stress value will be NAN.
    #     Equivalent ANSYS commands:
    #     RSYS, 1
    #     PRNSOL, S
    #     """
    #     raise NotImplementedError("This should be implemented by DPF")

    # def element_lookup(self, element_id):
    #     """Index of the element within the result mesh"""
    #     # We need to get the mapping between the mesh.grid and the results.elements.
    #     # Probably DPF already has that mapping.
    #     raise NotImplementedError("This should be implemented by DPF")

    # def element_solution_data(self):
    #     pass

    # def materials(self):
    #     pass

    # def quadgrid(self):
    #     pass

    # def read_record(self):
    #     pass

    # def result_dof(self):
    #     pass

    # def section_data(self):
    #     pass

    # def solution_info(self):
    #     pass

    # def text_result_table(self):
    #     pass

    # def write_table(self):
    #     pass

    # def nodal_boundary_conditions(self):
    #     pass

    # def nodal_input_force(self):
    #     pass

    # def nodal_static_forces(self):
    #     pass

    # def node_components(self):
    #     pass

    # def parse_coordinate_system(self):
    #     pass


#### overwriting
# def overwrite_element_solution_record(self):
#     pass

# def overwrite_element_solution_records(self):
#     pass

### plotting

# def animate_nodal_displacement(self):
#     pass

# def animate_nodal_solution(self):
#     pass

# def animate_nodal_solution_set(self):
#     pass

# def plot(self):
#     pass

# def plot_cylindrical_nodal_stress(self):
#     pass

# def plot_element_result(self):
#     pass

# def plot_nodal_displacement(self,
#     rnum,
#     comp=None,
#     show_displacement=False,
#     displacement_factor=1.0,
#     node_components=None,
#     element_components=None,
#     **kwargs):
#     pass

#     if kwargs.pop("sel_type_all", None):
#         warn(f"The kwarg 'sel_type_all' is being deprecated.")

#     if kwargs.pop("treat_nan_as_zero", None):
#         warn(f"The kwarg 'treat_nan_as_zero' is being deprecated.")

#     if isinstance(rnum, list):
#         set_ = rnum[0]  # todo: implement subresults
#     elif isinstance(rnum, (int, float)):
#         set_ = rnum
#     else:
#         raise ValueError(f"Please use 'int', 'float' or  'list' for the parameter 'rnum'.")

#     disp = self.model.displacement(set=set_)
#     if not comp:
#         comp = 'norm'
#     disp_dir = getattr(disp, comp)
#     disp_dir.plot_contour(**kwargs)

# def plot_nodal_elastic_strain(self):
#     pass

# def plot_nodal_plastic_strain(self):
#     pass

# def plot_nodal_solution(self):
#     pass

# def plot_nodal_stress(self):
#     pass

# def plot_nodal_temperature(self):
#     pass

# def plot_nodal_thermal_strain(self):
#     pass

# def plot_principal_nodal_stress(self):
#     pass
