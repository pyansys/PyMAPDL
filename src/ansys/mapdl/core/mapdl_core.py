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

"""Module to control interaction with MAPDL through Python"""

from functools import wraps
import glob
import logging
import os
import pathlib
import re
from shutil import copyfile, rmtree

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
from subprocess import DEVNULL, call  # nosec B404
import tempfile
import time
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union
from warnings import warn
import weakref

import numpy as np

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import LOG as logger
from ansys.mapdl.core import _HAS_VISUALIZER
from ansys.mapdl.core.commands import (
    CMD_BC_LISTING,
    CMD_LISTING,
    CMD_XSEL,
    XSEL_DOCSTRING_INJECTION,
    BoundaryConditionsListingOutput,
    CommandListingOutput,
    Commands,
    StringWithLiteralRepr,
    inject_docs,
)
from ansys.mapdl.core.errors import (
    ComponentNoData,
    MapdlCommandIgnoredError,
    MapdlExitedError,
    MapdlFileNotFoundError,
    MapdlInvalidRoutineError,
    MapdlRuntimeError,
)
from ansys.mapdl.core.information import Information
from ansys.mapdl.core.inline_functions import Query
from ansys.mapdl.core.mapdl_types import MapdlFloat
from ansys.mapdl.core.misc import (
    check_valid_routine,
    last_created,
    random_string,
    requires_package,
    run_as,
    supress_logging,
)

if TYPE_CHECKING:  # pragma: no cover
    from ansys.mapdl.reader import Archive

    from ansys.mapdl.core.component import ComponentManager
    from ansys.mapdl.core.mapdl import MapdlBase
    from ansys.mapdl.core.mapdl_geometry import Geometry, LegacyGeometry
    from ansys.mapdl.core.parameters import Parameters
    from ansys.mapdl.core.solution import Solution
    from ansys.mapdl.core.xpl import ansXpl
    from ansys.mapdl.core.plugin import ansPlugin

from ansys.mapdl.core.post import PostProcessing

MAX_PARAM_CHARS = 32

DEBUG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

VALID_DEVICES = ["PNG", "TIFF", "VRML", "TERM", "CLOSE"]
VALID_DEVICES_LITERAL = Literal[tuple(["PNG", "TIFF", "VRML", "TERM", "CLOSE"])]

VALID_FILE_TYPE_FOR_PLOT = VALID_DEVICES.copy()
VALID_FILE_TYPE_FOR_PLOT.remove("CLOSE")
VALID_FILE_TYPE_FOR_PLOT_LITERAL = Literal[tuple(VALID_FILE_TYPE_FOR_PLOT)]

_PERMITTED_ERRORS = [
    r"(\*\*\* ERROR \*\*\*).*(?:[\r\n]+.*)+highly distorted.",
    r"(\*\*\* ERROR \*\*\*).*[\r\n]+.*is turning inside out.",
    r"(\*\*\* ERROR \*\*\*).*[\r\n]+.*The distributed memory parallel solution does not support KRYLOV method",
]

_TMP_COMP = {
    "KP": "cmp_kp",
    "LINE": "cmp_line",
    "AREA": "cmp_area",
    "VOLU": "cmp_volu",
    "NODE": "cmp_node",
    "ELEM": "cmp_elem",
}

ENTITIES_TO_SELECTION_MAPPING = {
    "KP": "ksel",
    "LINE": "lsel",
    "AREA": "asel",
    "VOLU": "vsel",
    "NODE": "nsel",
    "ELEM": "esel",
}

# test for png file
PNG_IS_WRITTEN_TO_FILE = re.compile(
    "WRITTEN TO FILE"
)  # getting the file name is buggy.

VWRITE_MWRITE_REPLACEMENT = """
Cannot use *VWRITE/*MWRITE directly as a command in MAPDL
service mode.  Instead, run it as ``non_interactive``.

For example, in the *VWRITE case:

with self.non_interactive:
    self.vwrite('%s(1)' % parm_name)
    self.run('(F20.12)')

"""

## Invalid commands in interactive mode.
INVAL_COMMANDS = {
    "*VWR": VWRITE_MWRITE_REPLACEMENT,
    "*MWR": VWRITE_MWRITE_REPLACEMENT,
    "*CFO": "Run CFOPEN as ``non_interactive``",
    "*CRE": "Create a function within python or run as non_interactive",
    "*END": "Create a function within python or run as non_interactive",
    "/EOF": "Unsupported command.  Use ``exit`` to stop the server.",
    "*ASK": "Unsupported command.  Use python ``input`` instead.",
    "*IF": "Use a python ``if`` or run as non_interactive",
    "CMAT": "Run `CMAT` as ``non_interactive``.",
    "*REP": "Run '*REPEAT' in ``non_interactive``.",
    "LSRE": "Run 'LSREAD' in ``non_interactive``.",
}

## Soft-invalid commands
# Invalid commands in interactive mode but their execution is just ignored.
# The correspondent command is replaced by a comment using the command '\COM'
# and a warning is recorded in the logger
#
# This commands can still be executed in ``non_interactive`` mode or using
# ``Mapdl._run`` method.
#
# Format of the message:
# f"{CMD} is ignored: {INVAL_COMMANDS_SILENT[CMD]}.
#
# NOTE
# Obtain the command from the string supplied using
#
#    string.split(',')[0].upper()
#
# This way to get the command is different from the one used in ``INVAL_COMMANDS``.
#
INVAL_COMMANDS_SILENT = {
    "/NOPR": "Suppressing console output is not recommended, use ``Mute`` parameter instead. This command is disabled in interactive mode."
}

PLOT_COMMANDS = ["NPLO", "EPLO", "KPLO", "LPLO", "APLO", "VPLO", "PLNS", "PLES"]
MAX_COMMAND_LENGTH = 600  # actual is 640, but seems to fail above 620

VALID_SELECTION_TYPE_TP = Literal["S", "R", "A", "U"]
VALID_SELECTION_ENTITY_TP = Literal["VOLU", "AREA", "LINE", "KP", "ELEM", "NODE"]

GUI_FONT_SIZE = 15
LOG_APDL_DEFAULT_FILE_NAME = "apdl.log"

_ALLOWED_START_PARM = [
    "additional_switches",
    "check_parameter_names",
    "env_vars",
    "launched",
    "exec_file",
    "finish_job_on_exit",
    "hostname",
    "ip",
    "jobid",
    "jobname",
    "launch_on_hpc",
    "mode",
    "nproc",
    "override",
    "port",
    "print_com",
    "process",
    "ram",
    "run_location",
    "start_instance",
    "start_timeout",
    "timeout",
]


def parse_to_short_cmd(command):
    """Takes any MAPDL command and returns the first 4 characters of
    the command

    Examples
    --------
    >>> parse_to_short_cmd('K,,1,0,0,')
    'K'

    >>> parse_to_short_cmd('VPLOT, ALL')
    'VPLO'
    """
    try:
        short_cmd = command.split(",")[0]
        return short_cmd[:4].upper()
    except Exception:  # pragma: no cover
        return


def setup_logger(loglevel="INFO", log_file=True, mapdl_instance=None):
    """Setup logger"""

    # return existing log if this function has already been called
    if hasattr(setup_logger, "log"):
        return setup_logger.log
    else:
        setup_logger.log = logger.add_instance_logger("MAPDL", mapdl_instance)

    return setup_logger.log


def _sanitize_start_parm(start_parm):
    for each_key in start_parm:
        if each_key not in _ALLOWED_START_PARM:
            raise ValueError(f"The argument '{each_key}' is not recognaised.")


class _MapdlCore(Commands):
    """Contains methods in common between all Mapdl subclasses"""

    def __init__(
        self,
        loglevel: DEBUG_LEVELS = "DEBUG",
        use_vtk: Optional[bool] = None,
        log_apdl: Optional[str] = None,
        log_file: Union[bool, str] = False,
        local: bool = True,
        print_com: bool = False,
        file_type_for_plots: VALID_FILE_TYPE_FOR_PLOT_LITERAL = "PNG",
        **start_parm,
    ):
        """Initialize connection with MAPDL."""
        self._show_matplotlib_figures = True  # for testing
        self._query = None
        self._exited: bool = False
        self._ignore_errors: bool = False
        self._apdl_log = None
        self._store_commands: bool = False
        self._stored_commands = []
        self._response = None
        self._mode = start_parm.get("mode", None)
        self._mapdl_process = None
        self._launched: bool = start_parm.get("launched", False)
        self._stderr = None
        self._stdout = None
        self._file_type_for_plots = file_type_for_plots
        self._default_file_type_for_plots = file_type_for_plots
        self._version = None  # cached version
        self._mute = False
        self._save_selection_obj = None

        if _HAS_VISUALIZER:
            if use_vtk is not None:  # pragma: no cover
                self._use_vtk = use_vtk
            else:
                self._use_vtk = True
        else:  # pragma: no cover
            if use_vtk:
                raise ModuleNotFoundError(
                    "Using the keyword argument 'use_vtk' requires having "
                    "'ansys-tools-visualization_interface' installed."
                )
            else:
                self._use_vtk = False

        self._log_filehandler = None
        self._local: bool = local
        self._cleanup: bool = True
        self._vget_arr_counter = 0
        self._cached_routine = None
        self._geometry = None
        self.legacy_geometry: bool = False
        self._math = None
        self._krylov = None
        self._on_docker = None
        self._platform = None
        self._print_com: bool = print_com  # print the command /COM input.

        # Start_parameters
        _sanitize_start_parm(start_parm)
        self._start_parm: Dict[str, Any] = start_parm
        self._jobname: str = start_parm.get("jobname", "file")
        self._path: Union[str, pathlib.Path] = start_parm.get("run_location", None)
        self._check_parameter_names = start_parm.get("check_parameter_names", True)

        # Setting up loggers
        self._log: logger = logger.add_instance_logger(
            self.name, self, level=loglevel
        )  # instance logger
        # adding a file handler to the logger
        if log_file:
            if not isinstance(log_file, str):
                log_file = "instance.log"
            self._log.log_to_file(filename=log_file, level=loglevel)

        self._log.debug("Logging set to %s", loglevel)

        # Modules
        from ansys.mapdl.core.parameters import Parameters

        self._parameters: Parameters = Parameters(self)

        from ansys.mapdl.core.solution import Solution

        self._solution: Solution = Solution(self)

        self._xpl: Optional[ansXpl] = None  # Initialized in mapdl_grpc

        self._plugin: Optional[ansPlugin] = None  # Initialized in mapdl_grpc

        from ansys.mapdl.core.component import ComponentManager

        self._componentmanager: ComponentManager = ComponentManager(self)

        if isinstance(log_apdl, bool) and log_apdl:
            log_apdl = LOG_APDL_DEFAULT_FILE_NAME

        if log_apdl:
            self.open_apdl_log(log_apdl, mode="w")

        self._post = PostProcessing(self)

        # Wrapping listing functions for "to_array" methods
        self._wrap_listing_functions()

        # Wrapping XSEL commands to return ids.
        self._xsel_mapdl_output = False
        self._wrap_xsel_commands()

        self._info = Information(self)

    def _after_run(self, _command: str) -> None:
        pass

    @property
    def allow_ignore(self):
        """Invalid commands will be ignored rather than exceptions

        A command executed in the wrong processor will raise an
        exception when ``allow_ignore=False``.  This is the default
        behavior.

        Examples
        --------
        >>> mapdl.post1()
        >>> mapdl.k(1, 0, 0, 0)
        Exception:  K is not a recognized POST1 command, abbreviation, or macro.

        Ignore these messages by setting allow_ignore=True

        >>> mapdl.allow_ignore = True
        2020-06-08 21:39:58,094 [INFO] : K is not a
        recognized POST1 command, abbreviation, or macro.  This
        command will be ignored.

        *** WARNING *** CP = 0.372 TIME= 21:39:58
        K is not a recognized POST1 command, abbreviation, or macro.
        This command will be ignored.

        """
        warn(
            "'allow_ignore' is being deprecated and will be removed in a future release. "
            "Use ``mapdl.ignore_errors`` instead.",
            DeprecationWarning,
        )
        return self._ignore_errors

    @allow_ignore.setter
    def allow_ignore(self, value):
        """Set allow ignore"""
        warn(
            "'allow_ignore' is being deprecated and will be removed in a future release. "
            "Use ``mapdl.ignore_errors`` instead.",
            DeprecationWarning,
        )
        self._ignore_errors = bool(value)

    def _before_run(self, _command: str) -> None:
        pass

    @property
    def chain_commands(self):
        """Chain several mapdl commands.

        Commands can be separated with ``"$"`` in MAPDL rather than
        with a line break, so you could send multiple commands to
        MAPDL with:

        ``mapdl.run("/PREP7$K,1,1,2,3")``

        This method is merely a convenience context manager to allow
        for easy chaining of PyMAPDL commands to speed up sending
        commands to MAPDL.

        View the response from MAPDL with :attr:`Mapdl.last_response`.

        Notes
        -----
        Distributed Ansys cannot properly handle condensed data input
        and chained commands are not permitted in distributed ansys.

        Examples
        --------
        >>> with mapdl.chain_commands:
            mapdl.prep7()
            mapdl.k(1, 1, 2, 3)

        """
        if self._distributed:
            raise MapdlRuntimeError(
                "Chained commands are not permitted in distributed ansys."
            )
        return self._chain_commands(self)

    @property
    def check_status(self):
        """Return MAPDL status.
        * 'exited' if MAPDL is exited
        * 'exiting' if MAPDL is exiting
        * Otherwise returns 'OK'.
        """
        if self.exited:
            return "exited"
        elif self.exiting:
            return "exiting"
        else:
            return "OK"

    @property
    def components(self) -> "ComponentManager":
        """MAPDL Component manager.

        Returns
        -------
        :class:`ansys.mapdl.core.component.ComponentManager`

        Examples
        --------
        Check if a solution has converged.

        >>> mapdl.solution.converged
        """
        if self.exited:  # pragma: no cover
            raise MapdlRuntimeError("MAPDL exited.")
        return self._componentmanager

    @property
    def connection(self):
        """Return the type of connection to the instance, namely: grpc, corba or console."""
        return self._mode

    @property
    def default_file_type_for_plots(self):
        """Default file type for plots.

        Use when device is not properly set, for instance when the device is closed."""
        return self._default_file_type_for_plots

    @default_file_type_for_plots.setter
    def default_file_type_for_plots(self, value: VALID_FILE_TYPE_FOR_PLOT_LITERAL):
        """Set default file type for plots.

        Used when device is not properly set, for instance when the device is closed."""
        if not isinstance(value, str) or value.upper() not in VALID_FILE_TYPE_FOR_PLOT:
            raise ValueError(f"'{value}' is not allowed as file output for plots.")
        return self._default_file_type_for_plots

    @property
    @supress_logging
    def directory(self) -> str:
        """
        Current MAPDL directory.

        Examples
        --------
        Directory on Linux

        >>> mapdl.directory
        '/tmp/ansys'

        Directory on Windows

        >>> mapdl.directory
        'C:/temp_directory/'

        Setting the directory

        >>> mapdl.directory = 'C:/temp_directory/'
        None

        In case the directory does not exist or it is not
        accessible, ``cwd`` (:func:`MapdlBase.cwd`) will raise
        a warning.
        """
        # Inside inquire there is already a retry mechanisim
        path = None
        try:
            path = self.inquire("", "DIRECTORY")
        except MapdlExitedError:
            # Let's return the cached path
            pass

        # os independent path format
        if path:  # self.inquire might return ''.
            path = path.replace("\\", "/")
            # new line to fix path issue, see #416
            path = repr(path)[1:-1]
            self._path = path

        elif not self._path:
            raise MapdlRuntimeError(
                f"MAPDL could provide a path using /INQUIRE or the cached path ('{self._path}')."
            )

        return self._path

    @directory.setter
    @supress_logging
    def directory(self, path: Union[str, pathlib.Path]) -> None:
        """Change the directory using ``Mapdl.cwd``"""
        self.cwd(path)
        self._path = path

    @property
    def exited(self):
        """Return true if the MAPDL session exited"""
        return self._exited

    @property
    def file_type_for_plots(self):
        """Returns the current file type for plotting."""
        if not self._file_type_for_plots:
            self._run("/show, PNG")
            self._file_type_for_plots = "PNG"
        return self._file_type_for_plots

    @file_type_for_plots.setter
    def file_type_for_plots(self, value: VALID_DEVICES_LITERAL):
        """Modify the current file type for plotting."""
        if isinstance(value, str) and value.upper() in VALID_DEVICES:
            self._run(
                f"/show, {value.upper()}"
            )  # To avoid recursion we need to use _run.
            self._file_type_for_plots = value.upper()
        else:
            raise ValueError(f"'{value}' is not allowed as file output for plots.")

    @property
    def force_output(self):
        """Force text output globally by turning the ``Mapdl.mute`` attribute to False
        and activating text output (``/GOPR``)

        You can still do changes to those inside this context.

        """
        return self._force_output(self)

    @property
    def geometry(self) -> "Geometry":
        """Geometry information.

        See :class:`ansys.mapdl.core.mapdl_geometry.Geometry`

        Examples
        --------
        Print the current status of the geometry.

        >>> print(mapdl.geometry)
        MAPDL Selected Geometry
        Keypoints:  8
        Lines:      12
        Areas:      6
        Volumes:    1

        Return the number of lines.

        >>> mapdl.geometry.n_line
        12

        Return the number of areas.

        >>> mapdl.geometry.n_area
        6

        Select a list of keypoints.

        >>> mapdl.geometry.keypoint_select([1, 5, 10])

        Append to an existing selection of lines.

        >>> mapdl.geometry.line_select([1, 2, 3], sel_type='A')

        Reselect from the existing selection of lines.

        >>> mapdl.geometry.line_select([3, 4, 5], sel_type='R')

        """
        if self._geometry is None:
            self._geometry = self._create_geometry()
        return self._geometry

    @property
    def ignore_errors(self) -> bool:
        """Invalid commands will be ignored rather than exceptions

        Normally, any string containing "*** ERROR ***" from MAPDL
        will trigger a ``MapdlRuntimeError``.  Set this to ``True`` to
        ignore these errors.

        For example, a command executed in the wrong processor will
        raise an exception when ``ignore_errors=False``.
        This is the default behavior.

        Examples
        --------
        >>> mapdl.post1()
        >>> mapdl.k(1, 0, 0, 0)
        Exception:  K is not a recognized POST1 command, abbreviation, or macro.

        Ignore these messages by setting ignore_errors=True

        >>> mapdl.ignore_errors = True
        2020-06-08 21:39:58,094 [INFO] : K is not a
        recognized POST1 command, abbreviation, or macro.  This
        command will be ignored.

        *** WARNING *** CP = 0.372 TIME= 21:39:58
        K is not a recognized POST1 command, abbreviation, or macro.
        This command will be ignored.

        """
        return self._ignore_errors

    @ignore_errors.setter
    def ignore_errors(self, value):
        self._ignore_errors = bool(value)

    @property
    def info(self):
        """General information"""
        return self._info

    @property
    def is_console(self):
        """Return true if using console to connect to the MAPDL instance."""
        return self._mode == "console"

    @property
    def is_corba(self):
        """Return true if using corba to connect to the MAPDL instance."""
        return self._mode == "corba"

    @property
    def is_grpc(self):
        """Return true if using grpc to connect to the MAPDL instance."""
        return self._mode == "grpc"

    @property
    def is_local(self):
        """Check if the instance is running locally or remotely."""
        return self._local

    @property
    def jobname(self) -> str:
        """
        MAPDL job name.

        This is requested from the active mapdl instance.
        """
        try:
            self._jobname = self.inquire("", "JOBNAME")
        except Exception as e:
            logger.warning(f"Failed to get the jobname due to the following error: {e}")
        return self._jobname

    @jobname.setter
    def jobname(self, new_jobname: str):
        """Set the jobname"""
        self.finish(mute=True)
        self.filname(new_jobname)
        self._jobname = new_jobname

    @property
    def on_docker(self):
        """Check if MAPDL is running on docker."""
        if self._on_docker is None:
            self._on_docker = self._check_on_docker()
        return self._on_docker

    @property
    def last_response(self):
        """Returns the last response from MAPDL.

        Examples
        --------
        >>> mapdl.last_response
        'KEYPOINT      1   X,Y,Z=   1.00000       1.00000       1.00000'
        """
        return self._response

    @property
    def launched(self):
        """Check if the MAPDL instance has been launched by PyMAPDL."""
        return self._launched

    @property
    def check_parameter_names(self):
        """Whether check if the name which is given to the parameter is allowed or not"""
        return self._check_parameter_names

    @check_parameter_names.setter
    def check_parameter_names(self, value: bool):
        """Whether check if the name which is given to the parameter is allowed or not"""
        self._check_parameter_names = value

    @property
    def logger(self) -> logging.Logger:
        """MAPDL Python-based logger"""
        return self._log

    @property
    def mesh(self):
        """Mesh information.

        Returns
        -------
        :class:`Mapdl.Mesh <ansys.mapdl.core.mesh_grpc.Mesh>`

        Examples
        --------
        Return an array of the active nodes

        >>> mapdl.mesh.nodes
        array([[ 1.,  0.,  0.],
               [ 2.,  0.,  0.],
               [ 3.,  0.,  0.],
               [ 4.,  0.,  0.],
               [ 5.,  0.,  0.],
               [ 6.,  0.,  0.],
               [ 7.,  0.,  0.],
               [ 8.,  0.,  0.],
               [ 9.,  0.,  0.],
               [10.,  0.,  0.]])

        Return an array of the node numbers of the active nodes

        >>> mapdl.mesh.nnum
        array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10], dtype=int32)

        Simply query and print the geometry

        >>> print(mapdl.mesh)
          ANSYS Mapdl Mesh
          Number of Nodes:              321
          Number of Elements:           40
          Number of Element Types:      1
          Number of Node Components:    2
          Number of Element Components: 2

        Access the geometry as a VTK object

        >>> mapdl.mesh.grid

        """
        return self._mesh

    @property
    def name(self) -> str:
        raise NotImplementedError("Implemented by child classes.")

    @name.setter
    def name(self, name) -> None:
        raise AttributeError("The name of an instance cannot be changed.")

    @property
    def non_interactive(self):
        """Non-interactive context manager.

        Allow to execute code without user interaction or waiting
        between PyMAPDL responses.
        It can also be used to execute some commands which are not
        supported in interactive mode. For a complete list of commands
        visit :ref:`ref_unsupported_interactive_commands`.

        View the last response with :attr:`Mapdl.last_response` method.

        Notes
        -----
        All the commands executed inside this context manager are not
        executed until the context manager exits which then execute them
        all at once in the MAPDL instance.

        This command uses :func:`Mapdl.input() <ansys.mapdl.core.Mapdl.input>`
        method.

        Examples
        --------
        Use the non-interactive context manager for the VWRITE (
        :func:`Mapdl.vwrite() <ansys.mapdl.core.Mapdl.vwrite>`)
        command.

        >>> with mapdl.non_interactive:
        ...    mapdl.run("*VWRITE,LABEL(1),VALUE(1,1),VALUE(1,2),VALUE(1,3)")
        ...    mapdl.run("(1X,A8,'   ',F10.1,'  ',F10.1,'   ',1F5.3)")
        >>> mapdl.last_response

        """
        return self._non_interactive(self)

    @property
    def parameters(self) -> "Parameters":
        """Collection of MAPDL parameters.

        Notes
        -----
        See :ref:`ref_special_named_param` for additional notes regarding parameter naming in MAPDL.

        Examples
        --------
        Simply list all parameters except for MAPDL MATH parameters.

        >>> mapdl.parameters
        ARR                              : ARRAY DIM (3, 1, 1)
        PARM_FLOAT                       : 20.0
        PARM_INT                         : 10.0
        PARM_LONG_STR                    : "stringstringstringstringstringst"
        PARM_STR                         : "string"
        PORT                             : 50052.0

        Get a parameter

        >>> mapdl.parameters['PARM_FLOAT']
        20.0

        Get an array parameter

        >>> mapdl.parameters['ARR']
        array([1., 2., 3.])

        """
        return self._parameters

    @property
    def platform(self):
        """Return the platform where MAPDL is running."""
        if self._platform is None:
            self._check_mapdl_os()
        return self._platform

    @property
    def post_processing(self) -> "PostProcessing":
        """Post-process an active MAPDL session.

        Examples
        --------
        Get the nodal displacement in the X direction for the first
        result set.

        >>> mapdl.set(1, 1)
        >>> disp_x = mapdl.post_processing.nodal_displacement('X')
        array([1.07512979e-04, 8.59137773e-05, 5.70690047e-05, ...,
               5.70333124e-05, 8.58600402e-05, 1.07445726e-04])
        """
        if self.exited:
            raise MapdlRuntimeError(
                "MAPDL exited.\n\nCan only postprocess a live " "MAPDL instance."
            )
        return self._post

    @property
    def print_com(self):
        """Whether to print or not to the console the
        :meth:`mapdl.com ("/COM") <ansys.mapdl.core.Mapdl.com>` calls."""
        return self._print_com

    @print_com.setter
    def print_com(self, value):
        if isinstance(value, bool):
            status = "activated" if value else "deactivated"
            self._log.debug(f"The print of '/COM' commands has been {status}.")
            self._print_com = value
        else:
            raise ValueError(
                f"The property ``print_com`` only allows booleans, but type {type(value)} was supplied."
            )

    @property
    def queries(self):
        """Get instance of Query class containing inline functions of APDL.

        Most of the results of these methods are shortcuts for specific
        combinations of arguments supplied to :func:`ansys.mapdl.core.Mapdl.get`.

        Currently implemented functions:

        - ``centrx(e)`` - get the centroid x-coordinate of element `e`
        - ``centry(e)`` - get the centroid y-coordinate of element `e`
        - ``centrz(e)`` - get the centroid z-coordinate of element `e`
        - ``nx(n)`` - get the x-coordinate of node `n`
        - ``ny(n)`` - get the y-coordinate of node `n`
        - ``nz(n)`` - get the z-coordinate of node `n`
        - ``kx(k)`` - get the x-coordinate of keypoint `k`
        - ``ky(k)`` - get the y-coordinate of keypoint `k`
        - ``kz(k)`` - get the z-coordinate of keypoint `k`
        - ``lx(n, lfrac)`` - X-coordinate of line ``n`` at length fraction ``lfrac``
        - ``ly(n, lfrac)`` - Y-coordinate of line ``n`` at length fraction ``lfrac``
        - ``lz(n, lfrac)`` - Z-coordinate of line ``n`` at length fraction ``lfrac``
        - ``lsx(n, lfrac)`` - X-slope of line ``n`` at length fraction ``lfrac``
        - ``lsy(n, lfrac)`` - Y-slope of line ``n`` at length fraction ``lfrac``
        - ``lsz(n, lfrac)`` - Z-slope of line ``n`` at length fraction ``lfrac``
        - ``ux(n)`` - get the structural displacement at node `n` in x
        - ``uy(n)`` - get the structural displacement at node `n` in y
        - ``uz(n)`` - get the structural displacement at node `n` in z
        - ``rotx(n)`` - get the rotational displacement at node `n` in x
        - ``roty(n)`` - get the rotational displacement at node `n` in y
        - ``rotz(n)`` - get the rotational displacement at node `n` in z
        - ``nsel(n)`` - get the selection status of node `n`
        - ``ksel(k)`` - get the selection status of keypoint `k`
        - ``lsel(n)`` - get the selection status of line `n`
        - ``asel(a)`` - get the selection status of area `a`
        - ``esel(n)`` - get the selection status of element `e`
        - ``vsel(v)`` - get the selection status of volume `v`
        - ``ndnext(n)`` - get the next selected node with a number greater than `n`.
        - ``kpnext(k)`` - get the next selected keypoint with a number greater than `k`.
        - ``lsnext(n)`` - get the next selected line with a number greater than `n`.
        - ``arnext(a)`` - get the next selected area with a number greater than `a`.
        - ``elnext(e)`` - get the next selected element with a number greater than `e`.
        - ``vlnext(v)`` - get the next selected volume with a number greater than `v`.
        - ``node(x, y, z)`` - get the node closest to coordinate (x, y, z)
        - ``kp(x, y, z)`` - get the keypoint closest to coordinate (x, y, z)

        Returns
        -------
        :class:`ansys.mapdl.core.inline_functions.Query`
            Instance of the Query class

        Examples
        --------
        In this example we construct a solid box and mesh it. Then we use
        the ``Query`` methods ``nx``, ``ny``, and ``nz`` to find the
        cartesian coordinates of the first node.

        >>> from ansys.mapdl.core import launch_mapdl
        >>> mapdl = launch_mapdl()
        >>> mapdl.prep7()
        >>> mapdl.et(1, 'SOLID5')
        >>> mapdl.block(0, 10, 0, 20, 0, 30)
        >>> mapdl.esize(2)
        >>> mapdl.vmesh('ALL')
        >>> q = mapdl.queries
        >>> q.nx(1), q.ny(1), q.nz(1)
        0.0 20.0 0.0


        """
        if self._query is None:
            self._query = Query(self)
        return self._query

    @property
    def save_selection(self):
        """Save selection

        Save the current selection (nodes, elements, keypoints, lines, areas,
        volumes and components) before entering in the context manager, and
        when exit returns to that selection.

        """
        if self._save_selection_obj is None:
            self._save_selection_obj = self._save_selection(self)
        return self._save_selection_obj

    @property
    def solution(self) -> "Solution":
        """Solution parameters of MAPDL.

        Returns
        -------
        :class:`ansys.mapdl.core.solution.Solution`

        Examples
        --------
        Check if a solution has converged.

        >>> mapdl.solution.converged
        """
        if self.exited:
            raise MapdlRuntimeError("MAPDL exited.")
        return self._solution

    @property
    def use_vtk(self):
        """Returns if using VTK by default or not."""
        return self._use_vtk

    @use_vtk.setter
    def use_vtk(self, value: bool):
        """Set VTK to be used by default or not."""
        self._use_vtk = value

    @property
    @requires_package("ansys.mapdl.reader", softerror=True)
    def result(self):
        """Binary interface to the result file using :class:`ansys.mapdl.reader.rst.Result`.

        Returns
        -------
        :class:`ansys.mapdl.reader.rst.Result`.
            Result reader class.  See `Legacy PyMAPDL Reader <https://readerdocs.pyansys.com/>`.

        Examples
        --------
        >>> mapdl.solve()
        >>> mapdl.finish()
        >>> result = mapdl.result
        >>> print(result)
        PyMAPDL-Reader Result file object
        Units       : User Defined
        Version     : 18.2
        Cyclic      : False
        Result Sets : 1
        Nodes       : 3083
        Elements    : 977
        ...
        Available Results:
        EMS : Miscellaneous summable items (normally includes face pressures)
        ENF : Nodal forces
        ENS : Nodal stresses
        ENG : Element energies and volume
        EEL : Nodal elastic strains
        ETH : Nodal thermal strains (includes swelling strains)
        EUL : Element euler angles
        EMN : Miscellaneous nonsummable items
        EPT : Nodal temperatures
        NSL : Nodal displacements
        RF  : Nodal reaction forces
        """
        from ansys.mapdl.reader import read_binary
        from ansys.mapdl.reader.rst import Result

        if not self._local:
            # download to temporary directory
            save_path = os.path.join(tempfile.gettempdir())
            result_path = self.download_result(save_path)
        else:
            if self._distributed_result_file and self._result_file:
                result_path = self._distributed_result_file
                result = Result(result_path, read_mesh=False)
                if result._is_cyclic:
                    result_path = self._result_file
                else:  # pragma: no cover
                    # return the file with the last access time
                    filenames = [
                        self._distributed_result_file,
                        self._result_file,
                    ]
                    result_path = last_created(filenames)
                    if result_path is None:  # if same return result_file
                        result_path = self._result_file

            elif self._distributed_result_file:
                result_path = self._distributed_result_file
                result = Result(result_path, read_mesh=False)
                if result._is_cyclic:
                    if not os.path.isfile(self._result_file):
                        raise MapdlRuntimeError(
                            "Distributed Cyclic result not supported"
                        )
                    result_path = self._result_file
            else:
                result_path = self._result_file

        if result_path is None:
            raise FileNotFoundError("No result file(s) at %s" % self.directory)
        if not os.path.isfile(result_path):
            raise FileNotFoundError("No results found at %s" % result_path)

        return read_binary(result_path)

    @property
    def result_file(self):
        """Return the RST file path."""
        return self._result_file

    @property
    def version(self) -> float:
        """
        MAPDL build version.

        Examples
        --------
        >>> mapdl.version
        20.2
        """
        if not self._version:
            self._version = self.parameters.revision
        return self._version

    @property
    def _distributed_result_file(self):
        """Path of the distributed result file"""
        try:
            filename = self.inquire("", "RSTFILE")
            if not filename:
                filename = self.jobname
        except Exception:
            filename = self.jobname

        # ansys decided that a jobname ended in a number needs a bonus "_"
        if filename[-1].isnumeric():
            filename += "_"

        rth_basename = "%s0.%s" % (filename, "rth")
        rst_basename = "%s0.%s" % (filename, "rst")

        rth_file = os.path.join(self.directory, rth_basename)
        rst_file = os.path.join(self.directory, rst_basename)
        if os.path.isfile(rth_file) and os.path.isfile(rst_file):
            return last_created([rth_file, rst_file])
        elif os.path.isfile(rth_file):
            return rth_file
        elif os.path.isfile(rst_file):
            return rst_file

    @property
    def _distributed(self):
        """MAPDL is running in distributed mode."""
        return "-smp" not in self._start_parm.get("additional_switches", "")

    @property
    def _has_matplotlib(self):
        try:
            import matplotlib  # noqa: F401

            return True
        except ModuleNotFoundError:
            return False

    @property
    def _lockfile(self):
        """Lockfile path"""
        path = self.directory
        if path is not None:
            return os.path.join(path, self.jobname + ".lock").replace("\\", "/")

    @property
    @supress_logging
    def _mesh(self) -> "Archive":
        """Write entire archive to ASCII and read it in as an
        ``ansys.mapdl.core.Archive``"""
        from ansys.mapdl.reader import Archive

        if self._archive_cache is None:
            # write database to an archive file
            arch_filename = os.path.join(self.directory, "_tmp.cdb")
            nblock_filename = os.path.join(self.directory, "nblock.cdb")

            # must have all nodes elements are using selected
            if hasattr(self, "mute"):
                old_mute = self.mute
                self.mute = True

            self.cm("__NODE__", "NODE", mute=True)
            self.nsle("S", mute=True)
            self.cdwrite("db", arch_filename, mute=True)
            self.cmsel("S", "__NODE__", "NODE", mute=True)

            self.cm("__ELEM__", "ELEM", mute=True)
            self.esel("NONE", mute=True)
            self.cdwrite("db", nblock_filename, mute=True)
            self.cmsel("S", "__ELEM__", "ELEM", mute=True)

            if hasattr(self, "mute"):
                self.mute = old_mute

            self._archive_cache = Archive(arch_filename, parse_vtk=False, name="Mesh")
            grid = self._archive_cache._parse_vtk(additional_checking=True)
            self._archive_cache._grid = grid

            # rare bug
            if grid is not None:
                if grid.n_points != self._archive_cache.n_node:
                    self._archive_cache = Archive(
                        arch_filename, parse_vtk=True, name="Mesh"
                    )

            # overwrite nodes in archive
            nblock = Archive(nblock_filename, parse_vtk=False)
            self._archive_cache._nodes = nblock._nodes
            self._archive_cache._nnum = nblock._nnum
            self._archive_cache._node_coord = None

        return self._archive_cache

    @property
    def _png_mode(self):
        """Returns True when MAPDL is set to write plots as png to file."""
        with self.force_output:
            return "PNG" in self.show(mute=False)

    @property
    def _result_file(self):
        """Path of the non-distributed result file"""
        try:
            with self.run_as_routine("POST1"):
                filename = self.inquire("", "RSTFILE")
        except Exception:  # pragma: no cover
            filename = self.jobname

        try:
            with self.run_as_routine("POST1"):
                ext = self.inquire("", "RSTEXT")
        except Exception:  # pragma: no cover
            ext = "rst"

        if self._local:
            if ext == "":
                # Case where there is RST extension because it is thermal for example
                filename = self.jobname

                rth_file = os.path.join(self.directory, f"{filename}.rth")
                rst_file = os.path.join(self.directory, f"{filename}.rst")

                if self._prioritize_thermal and os.path.isfile(rth_file):
                    return rth_file

                if os.path.isfile(rth_file) and os.path.isfile(rst_file):
                    return last_created([rth_file, rst_file])
                elif os.path.isfile(rth_file):
                    return rth_file
                elif os.path.isfile(rst_file):
                    return rst_file
            else:
                filename = os.path.join(self.directory, f"{filename}.{ext}")
                if os.path.isfile(filename):
                    return filename
        else:
            return f"{filename}.{ext}"

    def _wrap_listing_functions(self):
        # Wrapping LISTING FUNCTIONS.
        def wrap_listing_function(func):
            # Injecting doc string modification
            if hasattr(func, "__func__"):
                func.__func__.__doc__ = inject_docs(func.__func__.__doc__)
            else:  # pragma: no cover
                func.__doc__ = inject_docs(func.__doc__)

            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                return CommandListingOutput(func(*args, **kwargs))

            return inner_wrapper

        def wrap_bc_listing_function(func):
            # Injecting doc string modification
            if hasattr(func, "__func__"):
                func.__func__.__doc__ = inject_docs(func.__func__.__doc__)
            else:  # pragma: no cover
                func.__doc__ = inject_docs(func.__doc__)

            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                return BoundaryConditionsListingOutput(func(*args, **kwargs))

            return inner_wrapper

        for name in dir(self):
            if name[0:4].upper() in CMD_LISTING and name in dir(
                Commands
            ):  # avoid matching Mapdl properties which starts with same letters as MAPDL commands.
                func = self.__getattribute__(name)
                setattr(self, name, wrap_listing_function(func))

            if name[0:4].upper() in CMD_BC_LISTING and name in dir(Commands):
                func = self.__getattribute__(name)
                setattr(self, name, wrap_bc_listing_function(func))

    def _wrap_xsel_commands(self):
        # Wrapping XSEL commands.
        if self.is_console:
            return

        def wrap_xsel_function(func):
            if hasattr(func, "__func__"):
                func.__func__.__doc__ = inject_docs(
                    func.__func__.__doc__, XSEL_DOCSTRING_INJECTION
                )
            else:  # pragma: no cover
                func.__doc__ = inject_docs(func.__doc__, XSEL_DOCSTRING_INJECTION)

            def wrap_xsel_function_output(method):
                # Injecting doc string modification
                name = method.__func__.__name__.upper()
                if not self.geometry:
                    # Cases where the geometry module is not loaded
                    return None

                if name == "NSEL":
                    return self.mesh.nnum
                elif name == "ESEL":
                    return self.mesh.enum
                elif name == "KSEL":
                    return self.geometry.knum
                elif name == "LSEL":
                    return self.geometry.lnum
                elif name == "ASEL":
                    return self.geometry.anum
                elif name == "VSEL":
                    return self.geometry.vnum
                elif name == "ESLN":
                    return self.mesh.enum
                elif name == "NSLE":
                    return self.mesh.nnum
                else:
                    return None

            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                # in interactive mode (item='p'), the output is not suppressed
                if self._store_commands:
                    # In non-interactive mode, we do not need to check anything.
                    return

                is_interactive_arg = (
                    True
                    if len(args) >= 2
                    and isinstance(args[1], str)
                    and args[1].upper() == "P"
                    else False
                )
                is_interactive_kwarg = (
                    True
                    if "item" in kwargs and kwargs["item"].upper() == "P"
                    else False
                )

                return_mapdl_output = kwargs.pop(
                    "return_mapdl_output", self._xsel_mapdl_output
                )
                if is_interactive_arg or is_interactive_kwarg:
                    return_mapdl_output = True

                output = func(*args, **kwargs)
                if not return_mapdl_output:
                    output = wrap_xsel_function_output(func)
                return output

            return inner_wrapper

        for name in dir(self):
            if name[0:4].upper() in CMD_XSEL and name in dir(
                Commands
            ):  # avoid matching Mapdl properties which starts with same letters as MAPDL commands.
                method = self.__getattribute__(name)
                setattr(self, name, wrap_xsel_function(method))

    def _chain_stored(self):
        """Send a series of commands to MAPDL"""
        # there's to be an limit to 640 characters per command, so
        # when chaining commands they must be shorter than 640 (minus
        # some overhead).
        c = 0
        chained_commands = []
        chunk = []
        for command in self._stored_commands:
            len_command = len(command) + 1  # include sep var
            if len_command + c > MAX_COMMAND_LENGTH:
                chained_commands.append("$".join(chunk))
                chunk = [command]
                c = 0
            else:
                chunk.append(command)
                c += len_command

        # join the last
        chained_commands.append("$".join(chunk))
        self._stored_commands = []

        responses = [self._run(command) for command in chained_commands]
        self._response = "\n".join(responses)

    class _non_interactive:
        """Allows user to enter commands that need to run non-interactively."""

        def __init__(self, parent):
            self._parent = weakref.ref(parent)

        def __enter__(self):
            self._parent()._log.debug("Entering in non-interactive mode")
            if self._parent().logger.logger.level <= logging.DEBUG:
                # only commenting if on debug mode
                self._parent().com("Entering in non_interactive mode")
            self._parent()._store_commands = True

        def __exit__(self, *args):
            self._parent()._store_commands = False

            if args[0] is not None:
                # An exception was raised, let's exit now without flushing
                self._parent()._log.debug(
                    "An exception was found in the `non_interactive` environment. "
                    "Hence the commands are not flushed."
                )
                return None
            else:
                # No exception so let's flush.
                self._parent()._log.debug("Exiting non-interactive mode")
                self._parent()._flush_stored()

    class _save_selection:
        """Save the selection and returns to it when exiting"""

        def __init__(self, parent):
            self._parent = weakref.ref(parent)
            self.selection = []

        def __enter__(self):
            self._parent()._log.debug("Entering saving selection context")
            mapdl = self._parent()

            # Storing components
            selection = {
                "cmsel": mapdl.components._comp,
            }
            id_ = random_string(5)
            for each_type, each_name in _TMP_COMP.items():
                each_name = f"__{each_name}{id_}__"
                selection[each_type] = each_name
                mapdl.cm(
                    each_name, each_type, mute=True
                )  # to hide ComponentNoData error

            self.selection.append(selection)

        def __exit__(self, *args):
            self._parent()._log.debug("Exiting saving selection context")

            mapdl = self._parent()
            mapdl.allsel()
            mapdl.cmsel("None")

            selection = self.selection.pop()
            cmps = selection.pop("cmsel")

            if cmps:
                for each_name, each_value in cmps.items():
                    mapdl.cmsel("a", each_name, each_value, mute=True)

            for each_type, each_name in selection.items():
                mapdl.cmsel("a", each_name, each_type, mute=True)

                selfun = getattr(
                    mapdl, ENTITIES_TO_SELECTION_MAPPING[each_type.upper()]
                )
                selfun("s", vmin=each_name, mute=True)

                mapdl.cmdele(each_name, mute=True)

    class _chain_commands:
        """Store MAPDL commands and send one chained command."""

        def __init__(self, parent):
            self._parent = weakref.ref(parent)

        def __enter__(self):
            self._parent()._log.debug("Entering chained command mode")
            self._parent()._store_commands = True

        def __exit__(self, *args):
            self._parent()._log.debug("Exiting chained command mode")
            self._parent()._chain_stored()
            self._parent()._store_commands = False

    class _RetainRoutine:
        """Store MAPDL's routine when entering and reverts it when exiting."""

        def __init__(self, parent, routine):
            self._parent = weakref.ref(parent)
            self._requested_routine = routine

        def __enter__(self):
            """Store the current routine and enter the requested routine."""
            self._parent()._cache_routine()
            self._parent()._log.debug(f"Caching routine {self._cached_routine}")

            if (
                self._requested_routine.lower().strip()
                != self._cached_routine.lower().strip()
            ):
                self._parent()._enter_routine(self._requested_routine)

        def __exit__(self, *args):
            """Restore the original routine."""
            self._parent()._log.debug(f"Restoring routine '{self._cached_routine}'")
            self._parent()._resume_routine()

        @property
        def _cached_routine(self):
            return self._parent()._cached_routine

    def run_as_routine(self, routine):
        """
        Runs a command or commands at a routine and then revert to the prior routine.

        This can be useful to avoid constantly changing between routines.

        Parameters
        ----------
        routine : str
            A MAPDL routine. For example, ``"PREP7"`` or ``"POST1"``.

        Examples
        --------
        Enter ``PREP7`` and run ``numvar``, which requires ``POST26``, and
        revert to the prior routine.

        >>> mapdl.prep7()
        >>> mapdl.parameters.routine
        'PREP7'
        >>> with mapdl.run_as_routine('POST26'):
        ...     mapdl.numvar(200)
        >>> mapdl.parameters.routine
        'PREP7'

        """
        return self._RetainRoutine(self, routine)

    @supress_logging
    def __str__(self):
        return self.info.__str__()

    def _create_geometry(self) -> Union["Geometry", "LegacyGeometry"]:
        """Return geometry cache"""

        if self.legacy_geometry:
            from ansys.mapdl.core.mapdl_geometry import LegacyGeometry

            return LegacyGeometry
        else:
            from ansys.mapdl.core.mapdl_geometry import Geometry

            return Geometry(self)

    def _reset_cache(self):
        """Reset cached items"""
        self._archive_cache = None

    def open_apdl_log(
        self, filename: Union[str, pathlib.Path], mode: Literal["w", "a", "x"] = "w"
    ) -> None:
        """Start writing all APDL commands to an MAPDL input file.

        Parameters
        ----------
        filename : str
            Filename of the log.
        mode : str, optional
            Python file modes (for example, ``'a'``, ``'w'``).  Should
            be either write or append.

        Examples
        --------
        Begin writing APDL commands to ``"log.inp"``.

        >>> mapdl.open_apdl_log("log.inp")
        """
        if self._apdl_log is not None:
            raise MapdlRuntimeError("APDL command logging already enabled")

        self._log.debug("Opening ANSYS log file at %s", filename)

        if mode not in ["w", "a", "x"]:
            raise ValueError(
                "File mode should either be write, append, or exclusive"
                " creation ('w', 'a', or 'x')."
            )

        self._apdl_log = open(filename, mode=mode, buffering=1)  # line buffered
        self._apdl_log.write(
            f"! APDL log script generated using PyMAPDL (ansys.mapdl.core {pymapdl.__version__})\n"
        )

    @supress_logging
    @run_as("PREP7")
    def _generate_iges(self):
        """Save IGES geometry representation to disk"""
        filename = os.path.join(self.directory, "_tmp.iges")
        self.igesout(filename, att=1, mute=True)
        return filename

    def open_gui(self, include_result=None, inplace=None):  # pragma: no cover
        """Save the existing database and open it up in the MAPDL GUI.

        Parameters
        ----------
        include_result : bool, optional
            Allow the result file to be post processed in the GUI.  It is
            ignored if ``inplace`` is ``True``.  By default, ``True``.

        inplace : bool, optional
            Open the GUI on the current MAPDL working directory, instead of
            creating a new temporary directory and coping the results files
            over there.  If ``True``, ignores ``include_result`` parameter.  By
            default, this ``False``.

        Examples
        --------
        >>> from ansys.mapdl.core import launch_mapdl
        >>> mapdl = launch_mapdl()

        Create a square area using keypoints.

        >>> mapdl.prep7()
        >>> mapdl.k(1, 0, 0, 0)
        >>> mapdl.k(2, 1, 0, 0)
        >>> mapdl.k(3, 1, 1, 0)
        >>> mapdl.k(4, 0, 1, 0)
        >>> mapdl.l(1, 2)
        >>> mapdl.l(2, 3)
        >>> mapdl.l(3, 4)
        >>> mapdl.l(4, 1)
        >>> mapdl.al(1, 2, 3, 4)

        Open up the gui.

        >>> mapdl.open_gui()

        Resume where you left off.

        >>> mapdl.et(1, 'MESH200', 6)
        >>> mapdl.amesh('all')
        >>> mapdl.eplot()
        """
        # lazy load here to avoid circular import
        from ansys.mapdl.core.launcher import get_mapdl_path

        if not self._local:
            raise MapdlRuntimeError(
                "``open_gui`` can only be called from a local MAPDL instance."
            )

        if inplace and include_result:
            raise ValueError(
                "'inplace' and 'include_result' kwargs are not compatible."
            )

        if inplace and include_result is None:
            include_result = False

        if include_result is None:
            include_result = True

        if not inplace:
            inplace = False

        name = self.jobname

        # specify a path for the temporary database if any.
        if inplace:
            run_dir = self._start_parm["run_location"]

        else:
            temp_dir = tempfile.gettempdir()
            run_dir = os.path.join(temp_dir, f"ansys_{random_string(10)}")

            # Sanity checks
            if os.path.isdir(run_dir):
                rmtree(run_dir)
            os.mkdir(run_dir)

        database_file = os.path.join(run_dir, f"{name}.db")
        if os.path.isfile(database_file) and not inplace:
            os.remove(database_file)

        # cache result file, version, and routine before closing
        resultfile = self._result_file
        version = self.version
        self._cache_routine()

        # finish, save and exit the server
        self.finish(mute=True)
        self.save(database_file, mute=True)

        # Exit and do not remove the temporary directory. This is backwards
        # compatible with CONSOLE and CORBA modes.
        remove_tmp = False
        if hasattr(self, "_remove_tmp"):
            remove_tmp = self._remove_tmp
        self._remove_tmp = False
        self.exit()

        # copy result file to temp directory
        if not inplace:
            if include_result and self._result_file is not None:
                if os.path.isfile(resultfile):
                    tmp_resultfile = os.path.join(run_dir, "%s.rst" % name)
                    copyfile(resultfile, tmp_resultfile)

        # write temporary input file
        start_file = os.path.join(run_dir, f"start{version}.ans")
        with open(start_file, "w") as f:
            f.write("RESUME\n")

        # some versions of ANSYS just look for "start.ans" when starting
        other_start_file = os.path.join(run_dir, "start.ans")
        with open(other_start_file, "w") as f:
            f.write("RESUME\n")

        # issue system command to run ansys in GUI mode
        cwd = os.getcwd()
        os.chdir(run_dir)
        exec_file = self._start_parm.get("exec_file", get_mapdl_path(allow_input=False))
        nproc = self._start_parm.get("nproc", 2)
        add_sw = self._start_parm.get("additional_switches", "")

        if inplace:
            warn(
                "MAPDL GUI has been opened using 'inplace' kwarg. "
                f"The changes you make will overwrite the files in {run_dir}."
            )
        add_sw = add_sw.split()

        # Ensure exec_file is a file
        try:
            pathlib.Path(exec_file).is_file()
        except FileNotFoundError:
            raise FileNotFoundError("The executable file for ANSYS was not found. ")

        exec_array = [
            f"{exec_file}",
            "-g",
            "-j",
            f"{name}",
            "-np",
            f"{nproc}",
            *add_sw,
        ]

        # exec_array is controlled by the library. Excluding bandit check.
        call(
            exec_array,
            stdout=DEVNULL,
            cwd=run_dir,
        )  # nosec B603

        # Going back
        os.chdir(cwd)

        # Clearing
        os.remove(start_file)
        os.remove(other_start_file)

        # reattach to a new session and reload database
        self._launch(self._start_parm)
        self.resume(database_file, mute=True)

        # restore remove tmp state
        self._remove_tmp = remove_tmp

    def _enter_routine(self, routine):
        # check the routine is valid since we're muting the output
        check_valid_routine(routine)

        if routine.lower() in ["begin level", "finish"]:
            self.finish(mute=True)
        else:
            if not routine.startswith("/"):
                routine = f"/{routine}"

            self.run(f"{routine}", mute=True)

    def _cache_routine(self):
        """Cache the current routine."""
        self._cached_routine = self.parameters.routine

    def _resume_routine(self):
        """Resume the cached routine."""
        if self._cached_routine is not None:
            self._enter_routine(self._cached_routine)
            self._cached_routine = None

    def _launch(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Implemented by child class")

    def _close_apdl_log(self):
        """Closes the APDL log"""
        if self._apdl_log is not None:
            self._apdl_log.close()
        self._apdl_log = None

    @supress_logging
    def _enable_interactive_plotting(self, pixel_res: int = 1600):
        """Enables interactive plotting.  Requires matplotlib

        Parameters
        ----------
        pixel_res : int
            Pixel resolution.  Valid values are from 256 to 2400.
            Lowering the pixel resolution produces a "fuzzier" image.
            Increasing the resolution produces a "sharper" image but
            takes longer to render.
        """
        return self.WithInterativePlotting(self, pixel_res)

    class WithInterativePlotting:
        """Allows to redirect plots to MAPDL plots."""

        def __init__(self, parent: "MapdlBase", pixel_res: int) -> None:
            self._parent = weakref.ref(parent)
            self._pixel_res = pixel_res

        def __enter__(self) -> None:
            self._parent()._log.debug("Entering in 'WithInterativePlotting' mode")

            if not self._parent()._has_matplotlib:  # pragma: no cover
                raise ModuleNotFoundError(
                    "Install matplotlib to display plots from MAPDL ,"
                    "from Python.  Otherwise, plot with vtk with:\n"
                    "``vtk=True``"
                )

            if not self._parent()._store_commands:
                if not self._parent()._png_mode:
                    self._parent().show("PNG", mute=True)
                    self._parent().gfile(self._pixel_res, mute=True)

                self.previous_device = self._parent().file_type_for_plots

                if self._parent().file_type_for_plots not in [
                    "PNG",
                    "TIFF",
                    "PNG",
                    "VRML",
                ]:
                    self._parent().show(self._parent().default_file_type_for_plots)

        def __exit__(self, *args) -> None:
            self._parent()._log.debug("Exiting in 'WithInterativePlotting' mode")
            self._parent().show("close", mute=True)

            if not self._parent()._store_commands:
                if not self._parent()._png_mode:
                    self._parent().show("PNG", mute=True)
                    self._parent().gfile(self._pixel_res, mute=True)

                self._parent().file_type_for_plots = self.previous_device

    def set_log_level(self, loglevel: DEBUG_LEVELS) -> None:
        """Sets log level

        Parameters
        ----------
        loglevel : str, int
            Log level.  Must be one of: ``'DEBUG', 'INFO', 'WARNING', 'ERROR'``.

        Examples
        --------
        Set the log level to debug

        >>> mapdl.set_log_level('DEBUG')

        Set the log level to info

        >>> mapdl.set_log_level('INFO')

        Set the log level to warning

        >>> mapdl.set_log_level('WARNING')

        Set the log level to error

        >>> mapdl.set_log_level('ERROR')
        """
        if isinstance(loglevel, str):
            loglevel = loglevel.upper()
        setup_logger(loglevel=loglevel)

    def _list(self, command):
        """Replaces *LIST command"""
        items = command.split(",")
        filename = os.path.join(self.directory, ".".join(items[1:]))
        if os.path.isfile(filename):
            self._response = open(filename).read()
            response_ = "\n".join(self._response.splitlines()[:10])
            self._log.info(response_)
        else:
            raise Exception("Cannot run:\n{command}\n\nFile does not exist")

    def _get(self, *args, **kwargs) -> MapdlFloat:
        """Simply use the default get method"""
        return self.get(*args, **kwargs)

    def add_file_handler(self, filepath, append=False, level="DEBUG"):
        """Add a file handler to the mapdl log.  This allows you to
        redirect the APDL logging to a file.

        Parameters
        ----------
        filepath : str
            Filename of the log.

        append : bool
            When ``True``, appends to an existing log file.  When
            ``False``, overwrites the log file if it already exists.

        level : str
            Log level.  Must be one of: ``'DEBUG', 'INFO', 'WARNING', 'ERROR'``.

        Examples
        --------
        Start writing the log to a new file named "mapdl.log"

        >>> mapdl.add_file_handler('mapdl.log')

        """
        if append:
            mode = "a"
        else:
            mode = "w"

        self._log_filehandler = logging.FileHandler(filepath)
        formatstr = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

        self._log_filehandler = logging.FileHandler(filepath, mode=mode)
        self._log_filehandler.setFormatter(logging.Formatter(formatstr))
        if isinstance(level, str):
            level = level.upper()
        self._log_filehandler.setLevel(level)
        self._log.logger.addHandler(self._log_filehandler)
        self._log.info("Added file handler at %s", filepath)

    def remove_file_handler(self):
        """Removes the filehander from the log"""
        self._log.removeHandler(self._log_filehandler)
        self._log.info("Removed file handler")

    def _flush_stored(self):
        """Writes stored commands to an input file and runs the input file.

        Used with ``non_interactive``.

        Overridden by gRPC.

        """
        if not self._stored_commands:
            self._log.debug("There is no commands to be flushed.")
            self._store_commands = False
            return

        self._log.debug("Flushing stored commands")

        rnd_str = random_string()
        tmp_out = os.path.join(tempfile.gettempdir(), f"tmp_{rnd_str}.out")
        self._stored_commands.insert(0, f"/OUTPUT, {tmp_out}")
        self._stored_commands.append("/OUTPUT")
        commands = "\n".join(self._stored_commands)
        if self._apdl_log:
            self._apdl_log.write(commands + "\n")

        self._store_commands = False
        self._stored_commands = []

        # write to a temporary input file
        self._log.debug(
            "Writing the following commands to a temporary " "apdl input file:\n%s",
            commands,
        )

        tmp_inp = os.path.join(tempfile.gettempdir(), f"tmp_{random_string()}.inp")
        with open(tmp_inp, "w") as f:
            f.writelines(commands)

        # interactive result
        _ = self.input(tmp_inp, write_to_log=False)

        time.sleep(0.1)  # allow MAPDL to close the file
        if os.path.isfile(tmp_out):
            self._response = "\n" + open(tmp_out).read()

        if self._response is None:  # pragma: no cover
            self._log.warning("Unable to read response from flushed commands")
        else:
            response_ = "\n".join(self._response.splitlines()[:10])
            self._log.debug(f"Printing truncated response: {response_}")

    def run_multiline(self, commands) -> str:
        """Run several commands as a single block

        .. deprecated:: 0.61.0
           This function is being deprecated. Please use `input_strings`
           instead.

        Allows to run multiple mapdl commands in different lines in one go.

        Parameters
        ----------
        commands : str
            Commands separated by new lines.  See example.

        Returns
        -------
        str
            Command output from MAPDL.  Includes the output from
            running every command, as if it was an input file.

        Examples
        --------
        Run several commands from Python multi-line string.

        >>> cmd = '''/prep7
        ! Mat
        MP,EX,1,200000
        MP,NUXY,1,0.3
        MP,DENS,1,7.85e-09
        ! Elements
        et,1,186
        et,2,154
        ! Geometry
        BLC4,0,0,1000,100,10
        ! Mesh
        esize,5
        vmesh,all
        nsel,s,loc,x,0
        d,all,all
        nsel,s,loc,x,999,1001
        type,2
        esurf
        esel,s,type,,2
        nsle
        sfe,all,3,pres,,-10
        allsel
        /solu
        antype,0
        solve
        /post1
        set,last
        plnsol,u,sum
        '''
        >>> resp = mapdl.run_multiline(cmd)
        >>> resp
        MATERIAL          1     EX   =   200000.0
        MATERIAL          1     NUXY =  0.3000000
        MATERIAL          1     DENS =  0.7850000E-08
        ELEMENT TYPE          1 IS SOLID186     3-D 20-NODE STRUCTURAL SOLID
         KEYOPT( 1- 6)=        0      0      0        0      0      0
         KEYOPT( 7-12)=        0      0      0        0      0      0
         KEYOPT(13-18)=        0      0      0        0      0      0
        output continues...

        """

        warn(
            "'run_multiline()' is being deprecated in future versions.\n Please use 'input_strings'.",
            DeprecationWarning,
        )
        return self.input_strings(commands=commands)

    def input_strings(self, commands) -> str:
        """
        Run several commands as a single block.

        These commands are all in a single string or in list of strings.

        Parameters
        ----------
        commands : str or list of str
            Commands separated by new lines, or a list of commands strings.
            See example.

        Returns
        -------
        str
            Command output from MAPDL.  Includes the output from
            running every command, as if it was an input file.

        Examples
        --------
        Run several commands from Python multi-line string.

        >>> cmd = '''/prep7
        ! Mat
        MP,EX,1,200000
        MP,NUXY,1,0.3
        MP,DENS,1,7.85e-09
        ! Elements
        et,1,186
        et,2,154
        ! Geometry
        BLC4,0,0,1000,100,10
        ! Mesh
        esize,5
        vmesh,all
        '''
        >>> resp = mapdl.input_strings(cmd)
        >>> resp
        MATERIAL          1     EX   =   200000.0
        MATERIAL          1     NUXY =  0.3000000
        MATERIAL          1     DENS =  0.7850000E-08
        ELEMENT TYPE          1 IS SOLID186     3-D 20-NODE STRUCTURAL SOLID
         KEYOPT( 1- 6)=        0      0      0        0      0      0
         KEYOPT( 7-12)=        0      0      0        0      0      0
         KEYOPT(13-18)=        0      0      0        0      0      0

        """
        if isinstance(commands, str):
            commands = commands.splitlines()

        self._stored_commands.extend(commands)
        if self._store_commands:
            return None
        else:
            self._flush_stored()
            return self._response

    def run(
        self,
        command: str,
        write_to_log: bool = True,
        mute: Optional[bool] = None,
        **kwargs,
    ) -> str:
        """
        Run single APDL command.

        For multiple commands, use :func:`Mapdl.input_strings()
        <ansys.mapdl.core.Mapdl.input_strings>`.

        Parameters
        ----------
        command : str
            ANSYS APDL command.

        write_to_log : bool, optional
            Overrides APDL log writing.  Default ``True``.  When set
            to ``False``, will not write command to log, even if APDL
            command logging is enabled.

        kwargs : dict, optional
            These keyword arguments are interface specific or for
            development purposes.

            avoid_non_interactive : :class:`bool`
              *(Development use only)*
              Avoids the non-interactive mode for this specific command.
              Defaults to ``False``.

            verbose : :class:`bool`
              Prints the command to the screen before running it.
              Defaults to ``False``.

        Returns
        -------
        str
            Command output from MAPDL.

        Notes
        -----

        **Running non-interactive commands**

        When two or more commands need to be run non-interactively
        (i.e. ``*VWRITE``) use

        >>> with mapdl.non_interactive:
        ...     mapdl.run("*VWRITE,LABEL(1),VALUE(1,1),VALUE(1,2),VALUE(1,3)")
        ...     mapdl.run("(1X,A8,'   ',F10.1,'  ',F10.1,'   ',1F5.3)")

        Alternatively, you can simply run a block of commands with:

        >>> mapdl.input_strings(cmd)

        Examples
        --------
        >>> mapdl.run('/PREP7')

        Equivalent Pythonic method:

        >>> mapdl.prep7()

        """
        if self.exited:
            raise MapdlExitedError(
                f"The MAPDL instance has been exited before running the command: {command}"
            )

        # check if multiline
        if "\n" in command or "\r" in command:
            raise ValueError("Use ``input_strings`` for multi-line commands")

        if len(command) > 639:  # CMD_MAX_LENGTH
            # If using mapdl_grpc, this check is redundant on purpose.
            # Console probably do not have this limitation, but I'm not certain.
            raise ValueError("Maximum command length must be less than 640 characters")

        # Check kwargs
        verbose = kwargs.pop("verbose", False)
        save_fig = kwargs.pop("savefig", False)

        # Check if you want to avoid the current non-interactive context.
        avoid_non_interactive = kwargs.pop("avoid_non_interactive", False)

        # Check if there is an unused keyword argument. If there is, it
        # might be because you wrote a wrong argument name.
        #
        # Remove empty string kwargs
        for key, value in list(kwargs.items()):
            if value == "":
                kwargs.pop(key)

        if kwargs:
            warn(
                "The following keyword arguments are not used:\n"
                f"{', '.join(kwargs.keys())}\n"
                "Make sure you are using the intended keyword arguments.",
                UserWarning,
            )

        # Early exit if on non-interactive.
        if self._store_commands and not avoid_non_interactive:
            # If you are using NBLOCK on input, you should not strip the string
            self._stored_commands.append(command)
            return

        if mute is None:
            if hasattr(self, "mute"):
                mute = self.mute
            else:  # if not gRPC
                mute = False

        command = command.strip()

        is_comment = command.startswith("!") or command.upper().startswith("/COM")

        # always reset the cache
        self._reset_cache()

        # address MAPDL /INPUT level issue
        if command[:4].upper() == "/CLE":
            # Address gRPC issue
            # https://github.com/ansys/pymapdl/issues/380
            command = "/CLE,NOSTART"

        # Tracking output device
        if command[:4].upper() == "/SHO" and "," in command:
            self._file_type_for_plots = command.split(",")[1].upper()

        # Invalid commands silently ignored.
        cmd_ = command.split(",")[0].upper()
        if cmd_ in INVAL_COMMANDS_SILENT:
            msg = f"{cmd_} is ignored: {INVAL_COMMANDS_SILENT[cmd_]}."
            self._log.info(msg)

            # This, very likely, won't be recorded anywhere.
            # But just in case, I'm adding info as /com
            command = (
                f"/com, PyMAPDL: {msg}"  # Using '!' makes the output of '_run' empty
            )

        if command[:3].upper() in INVAL_COMMANDS:
            exception = MapdlRuntimeError(
                'Invalid PyMAPDL command "%s"\n\n%s'
                % (command, INVAL_COMMANDS[command[:3].upper()])
            )
            raise exception
        elif command[:4].upper() in INVAL_COMMANDS:
            exception = MapdlRuntimeError(
                'Invalid PyMAPDL command "%s"\n\n%s'
                % (command, INVAL_COMMANDS[command[:4].upper()])
            )
            raise exception
        elif write_to_log and self._apdl_log is not None:
            if not self._apdl_log.closed:
                self._apdl_log.write("%s\n" % command)

        if command[:4].upper() == "/LIS":
            # simply return the contents of the file
            return self.list(*command.split(",")[1:])

        if "=" in command and not is_comment:
            # We are storing a parameter.
            param_name = command.split("=")[0].strip()

            if "/COM" not in cmd_ and "/TITLE" not in cmd_:
                # Edge case. `\title, 'par=1234' `
                self._check_parameter_name(param_name)

        self._before_run(command)

        short_cmd = parse_to_short_cmd(command)
        self._log.debug(f"Running (verbose: {verbose}, mute={mute}): '{command}'")
        text = self._run(command, verbose=verbose, mute=mute)

        if (
            "Display device has not yet been specified with the /SHOW command" in text
            and short_cmd in PLOT_COMMANDS
        ):
            # Reissuing the command to make sure we get output.
            self.show(self.default_file_type_for_plots)
            text = self._run(command, verbose=verbose, mute=mute)

        self._after_run(command)

        if mute:
            return

        text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
        if text:
            self._response = StringWithLiteralRepr(text.strip())
            response_ = "\n".join(self._response.splitlines()[:20])
            self._log.info(response_)
        else:
            self._response = None
            return self._response

        if not self.ignore_errors:
            self._raise_errors(text)

        # special returns for certain geometry commands
        if short_cmd in PLOT_COMMANDS:
            self._log.debug("It is a plot command.")
            plot_path = self._get_plot_name(text)

            if save_fig:
                return self._download_plot(plot_path, save_fig)
            elif self._has_matplotlib:
                return self._display_plot(plot_path)
            else:
                self._log.debug(
                    "Since matplolib is not installed, images are not shown."
                )

        return self._response

    def _run(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Implemented by child class")

    def exit(self):  # pragma: no cover
        """Exit from MAPDL"""
        raise NotImplementedError("Implemented by child class")

    def __del__(self):
        """Kill MAPDL when garbage cleaning"""
        self.exit()

    def _cleanup_loggers(self):
        """Clean up all the loggers"""
        # Detached from ``__del__`` for easier testing
        # if not hasattr(self, "_log"):
        #     return  # Early exit if logger has been already cleaned.

        logger = self._log
        logger.setLevel(logging.CRITICAL + 1)

        if logger.hasHandlers():
            for each_handler in logger.logger.handlers:
                if each_handler.stream and not each_handler.stream.closed:
                    logger.logger.removeHandler(each_handler)

        if logger.file_handler:
            logger.file_handler.close()
            logger.file_handler = None

        if logger.std_out_handler:
            logger.std_out_handler.close()
            logger.std_out_handler = None

    def is_png_found(self, text: str) -> bool:
        # findall returns None if there is no match
        return PNG_IS_WRITTEN_TO_FILE.findall(text) is not None

    def _get_plot_name(self, text: str) -> str:
        """Obtain the plot filename."""
        self._log.debug(f"Output from terminal used to find plot name: {text}")

        if self.is_png_found(text):
            # flush graphics writer
            previous_device = self.file_type_for_plots
            self.show("CLOSE", mute=True)
            # self.show("PNG", mute=True)

            filename = self._screenshot_path()
            self.show(previous_device)
            self._log.debug(f"Screenshot at: {filename}")

            if os.path.isfile(filename):
                return filename
            else:  # pragma: no cover
                raise MapdlRuntimeError("Unable to find screenshot at %s", filename)
        else:
            raise MapdlRuntimeError(
                "Unable to find plotted file in MAPDL command output. "
                "One possible reason is that the graphics device is not correct. "
                "Please check you are using FULL graphics device. "
                "For example:\n"
                ">>> mapdl.graphics('FULL')"
                f"\nThe text output from MAPDL is:\n{text}"
            )

    def _display_plot(self, filename: str) -> None:
        """Display the last generated plot (*.png) from MAPDL"""
        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt

        def in_ipython():
            # from scooby.in_ipython
            # to avoid dependency here.
            try:
                __IPYTHON__
                return True
            except NameError:  # pragma: no cover
                return False

        self._log.debug("A screenshot file has been found.")
        img = mpimg.imread(filename)
        plt.imshow(img)
        plt.axis("off")

        if self._show_matplotlib_figures:  # pragma: no cover
            self._log.debug("Using Matplotlib to plot")
            plt.show()  # consider in-line plotting

        if in_ipython():
            self._log.debug("Using ipython")
            from IPython.display import display

            display(plt.gcf())

    def _download_plot(self, filename: str, plot_name: str) -> None:
        """Copy the temporary download plot to the working directory."""
        if isinstance(plot_name, str):
            provided = True
            path_ = pathlib.Path(plot_name)
            plot_name = path_.name
            plot_stem = path_.stem
            plot_ext = path_.suffix
            plot_path = str(path_.parent)
            if not plot_path or plot_path == ".":
                plot_path = os.getcwd()

        elif isinstance(plot_name, bool):
            provided = False
            plot_name = "plot.png"
            plot_stem = "plot"
            plot_ext = ".png"
            plot_path = os.getcwd()
        else:  # pragma: no cover
            raise ValueError("Only booleans and str are allowed.")

        id_ = 0
        plot_path_ = os.path.join(plot_path, plot_name)
        while os.path.exists(plot_path_) and not provided:
            id_ += 1
            plot_path_ = os.path.join(plot_path, f"{plot_stem}_{id_}{plot_ext}")
        else:
            copyfile(filename, plot_path_)

        self._log.debug(
            f"Copy plot file from temp directory to working directory as: {plot_path}"
        )

    def _screenshot_path(self):
        """Return last filename based on the current jobname"""
        filenames = glob.glob(os.path.join(self.directory, f"{self.jobname}*.png"))
        filenames.sort()
        return filenames[-1]

    def _set_log_level(self, level):
        """Alias for set_log_level"""
        self.set_log_level(level)

    def _check_parameter_name(self, param_name):
        """Checks if a parameter name is allowed or not."""
        if not self.check_parameter_names:
            return

        param_name = param_name.strip()

        match_valid_parameter_name = (
            r"^[a-zA-Z_][a-zA-Z\d_\(\),\s\%]{0," + f"{MAX_PARAM_CHARS-1}" + r"}$"
        )
        # Using % is allowed, because of substitution, but it is very likely MAPDL will complain.
        if not re.search(match_valid_parameter_name, param_name):
            raise ValueError(
                f"The parameter name `{param_name}` is an invalid parameter name. "
                f"Only letters, numbers and `_` are permitted, up to {MAX_PARAM_CHARS} characters long. "
                "It cannot start with a number either."
            )

        if "(" in param_name or ")" in param_name:
            if param_name.count("(") != param_name.count(")"):
                raise ValueError(
                    "The parameter name should have all the parenthesis in pairs (closed)."
                )

            if param_name[-1] != ")":
                raise ValueError(
                    "If using parenthesis (indexing), you cannot use any character after the closing parenthesis."
                )

            # Check recursively the parameter name without parenthesis.
            # This is the real parameter name, however it must already exists to not raise an error.
            sub_param_name = re.findall(r"^(.*)\(", param_name)
            if sub_param_name:
                self._check_parameter_name(sub_param_name[0])
                return  # Following checks should not run against the parenthesis

        # Using leading underscored parameters
        match_reserved_leading_underscored_parameter_name = (
            r"^_[a-zA-Z\d_\(\),\s_]{1," + f"{MAX_PARAM_CHARS}" + r"}[a-zA-Z\d\(\),\s]$"
        )
        # If it also ends in underscore, this won't be triggered.
        if re.search(match_reserved_leading_underscored_parameter_name, param_name):
            raise ValueError(
                "It is discouraged the use of parameters starting with underscore ('_'). "
                "This convention is reserved for parameters used by the GUI and/or Mechanical APDL-provided macros."
            )

        # invalid parameter (using ARGXX or ARXX)
        match_reserved_arg_parameter_name = r"^(AR|ARG)(\d{1,3})$"
        if re.search(
            match_reserved_arg_parameter_name, param_name
        ):  # invalid parameter (using ARGXX or ARXX)
            raise ValueError(
                "The parameters 'ARGXX' and 'ARXX' where 'XX' are integers, are reserved for functions and macros local parameters."
                "Hence its use is not recommended outside them."
                "You might run in unexpected behaviours, for example, parameters not being show in `mapdl.parameters`."
            )

    def _get_selected_(self, entity):
        """Get list of selected entities."""
        allowed_values = ["NODE", "ELEM", "KP", "LINE", "AREA", "VOLU"]
        if entity.upper() not in allowed_values:
            raise ValueError(
                f"The value '{entity}' is not allowed."
                f"Only {allowed_values} are allowed"
            )

        entity = entity.upper()

        if entity == "NODE":
            return self.mesh.nnum.copy()
        elif entity == "ELEM":
            return self.mesh.enum.copy()
        elif entity == "KP":
            return self.geometry.knum
        elif entity == "LINE":
            return self.geometry.lnum
        elif entity == "AREA":
            return self.geometry.anum
        elif entity == "VOLU":
            return self.geometry.vnum

    def _enable_picking_entities(
        self, entity, pl, type_, previous_picked_entities, **kwargs
    ):
        """Show a plot and get the selected entity."""
        _debug = kwargs.pop("_debug", False)  # for testing purposes
        previous_picked_entities = set(previous_picked_entities)

        PICKING_USING_LEFT_CLICKING = False

        q = self.queries
        picked_entities = []
        picked_ids = []
        entity = entity.lower()

        if entity in ["kp", "node"]:
            selector = getattr(q, entity)
        else:
            # We need to come out with a different thing.
            pass

        # adding selection inversor
        pl.scene._inver_mouse_click_selection = False

        selection_text = {
            "S": "New selection",
            "A": "Adding to selection",
            "R": "Reselecting from the selection",
            "U": "Unselecting",
        }

        def gen_text(picked_entities=None):
            """Generate helpful text for the render window."""
            sel_ = (
                "Unselecting" if pl.scene._inver_mouse_click_selection else "Selecting"
            )
            type_text = selection_text[type_]
            button_ = "left" if PICKING_USING_LEFT_CLICKING else "right"
            text = (
                f"Please use the {button_} mouse button to pick the {entity}s.\n"
                f"Press the key 'u' to change between mouse selecting and unselecting.\n"
                f"Type: {type_} - {type_text}\n"
                f"Mouse selection: {sel_}\n"
            )

            picked_entities_str = ""
            if picked_entities:
                # reverse picked point order, exclude the brackets, and limit
                # to 40 characters
                picked_entities_str = str(picked_entities[::-1])[1:-1]
                if len(picked_entities_str) > 40:
                    picked_entities_str = picked_entities_str[:40]
                    idx = picked_entities_str.rfind(",") + 2
                    picked_entities_str = picked_entities_str[:idx] + "..."

            return text + f"Current {entity} selection: {picked_entities_str}"

        def callback_points(mesh, id_):
            from ansys.mapdl.core.plotting.consts import POINT_SIZE

            point = mesh.points[id_]
            node_id = selector(
                point[0], point[1], point[2]
            )  # This will only return one node. Fine for now.

            if not pl.scene._inver_mouse_click_selection:
                # Updating MAPDL entity mapping
                if node_id not in picked_entities:
                    picked_entities.append(node_id)
                # Updating pyvista entity mapping
                if id_ not in picked_ids:
                    picked_ids.append(id_)
            else:
                # Updating MAPDL entity mapping
                if node_id in picked_entities:
                    picked_entities.remove(node_id)
                # Updating pyvista entity mapping
                if id_ in picked_ids:
                    picked_ids.remove(id_)

            # remov etitle and update text
            pl.scene.remove_actor("title")
            pl.scene._picking_text = pl.scene.add_text(
                gen_text(picked_entities),
                font_size=GUI_FONT_SIZE,
                name="_entity_picking_message",
            )
            if picked_ids:
                pl.scene.add_mesh(
                    mesh.points[picked_ids],
                    color="red",
                    point_size=POINT_SIZE + 10,
                    name="_picked_entities",
                    pickable=False,
                    reset_camera=False,
                )
            else:
                pl.scene.remove_actor("_picked_entities")

        def callback_mesh(mesh):
            def get_entnum(mesh):
                return int(np.unique(mesh.cell_data["entity_num"])[0])

            mesh_id = get_entnum(mesh)

            # Getting meshes with that entity_num.
            meshes = pl.get_meshes_from_plotter()

            meshes = [each for each in meshes if get_entnum(each) == mesh_id]

            if not pl.scene._inver_mouse_click_selection:
                # Updating MAPDL entity mapping
                if mesh_id not in picked_entities:
                    picked_entities.append(mesh_id)
                    for i, each in enumerate(meshes):
                        pl.scene.add_mesh(
                            each,
                            color="red",
                            point_size=10,
                            name=f"_picked_entity_{mesh_id}_{i}",
                            pickable=False,
                            reset_camera=False,
                        )

            else:
                # Updating MAPDL entity mapping
                if mesh_id in picked_entities:
                    picked_entities.remove(mesh_id)

                    for i, each in enumerate(meshes):
                        pl.scene.remove_actor(f"_picked_entity_{mesh_id}_{i}")

            # Removing only-first time actors
            pl.scene.remove_actor("title")
            pl.scene.remove_actor("_point_picking_message")

            if "_entity_picking_message" in pl.actors:
                pl.scene.remove_actor("_entity_picking_message")

            pl._picking_text = pl.add_text(
                gen_text(picked_entities),
                font_size=GUI_FONT_SIZE,
                name="_entity_picking_message",
            )

        if entity in ["kp", "node"]:
            lines_pl = self.lplot(return_plotter=True, color="w")
            lines_meshes = lines_pl.get_meshes_from_plotter()

            for each_mesh in lines_meshes:
                pl.scene.add_mesh(
                    each_mesh,
                    pickable=False,
                    color="w",
                    # name="lines"
                )

            # Picking points
            pl.scene.enable_point_picking(
                callback=callback_points,
                use_mesh=True,
                show_message=gen_text(),
                show_point=True,
                left_clicking=PICKING_USING_LEFT_CLICKING,
                font_size=GUI_FONT_SIZE,
                tolerance=kwargs.get("tolerance", 0.025),
            )
        else:
            # Picking meshes
            pl.scene.enable_mesh_picking(
                callback=callback_mesh,
                use_mesh=True,
                show=False,  # This should be false to avoid a warning.
                show_message=gen_text(),
                left_clicking=PICKING_USING_LEFT_CLICKING,
                font_size=GUI_FONT_SIZE,
            )

        def callback_u():
            # inverting bool
            pl.scene._inver_mouse_click_selection = not pl._inver_mouse_click_selection
            pl.scene.remove_actor("_entity_picking_message")

            pl.scene._picking_text = pl.add_text(
                gen_text(picked_entities),
                font_size=GUI_FONT_SIZE,
                name="_entity_picking_message",
            )

        pl.scene.add_key_event("u", callback_u)

        if not _debug:  # pragma: no cover
            pl.scene.show()
        else:
            _debug(pl)

        picked_entities = set(
            picked_entities
        )  # removing duplicates (although there should be none)

        if type_ == "S":
            pass
        elif type_ == "R":
            picked_entities = previous_picked_entities.intersection(picked_entities)
        elif type_ == "A":
            picked_entities = previous_picked_entities.union(picked_entities)
        elif type_ == "U":
            picked_entities = previous_picked_entities.difference(picked_entities)

        return list(picked_entities)

    def _perform_entity_list_selection(
        self, entity, selection_function, type_, item, comp, vmin, kabs
    ):
        """Select entities using CM, and the supplied selection function."""
        # Getting new selection
        for id_, each_ in enumerate(vmin):
            if type_ == "S" or not type_:
                type__ = "S" if id_ == 0 else "A"
            # R is an issue, because first iteration will clean up the rest.
            elif type_ == "R":
                raise NotImplementedError("Mode R is not supported.")
            else:
                type__ = type_

            selection_function(self, type__, item, comp, each_, "", "", kabs)

    def _raise_errors(self, text):
        # to make sure the following error messages are caught even if a breakline is in between.
        flat_text = " ".join([each.strip() for each in text.splitlines()])
        base_error_msg = "\n\nIgnore these messages by setting 'ignore_errors'=True.\n"

        if "unable to open file" in flat_text or (
            "unable to open" in flat_text and "file" in flat_text
        ):
            text += base_error_msg
            raise MapdlFileNotFoundError(text)

        if "is not a recognized" in flat_text:
            text = text.replace("This command will be ignored.", "")
            text += base_error_msg
            raise MapdlInvalidRoutineError(text)

        if "command is ignored" in flat_text:
            text += base_error_msg
            raise MapdlCommandIgnoredError(text)

        if (
            "The component definition of" in flat_text
            and "contains no data." in flat_text
        ):
            text += base_error_msg
            raise ComponentNoData(text)

        if "is not part of the currently active set." in flat_text:
            text += base_error_msg
            raise MapdlCommandIgnoredError(text)

        if "No nodes defined." in flat_text:
            text += base_error_msg
            raise MapdlCommandIgnoredError(text)

        if "For element type = " in flat_text and "is invalid." in flat_text:
            if "is normal behavior when a CDB file is used." in flat_text:
                warn(text, UserWarning)
            else:
                text += base_error_msg
                raise MapdlCommandIgnoredError(text)

        if "Cannot create another with the same name" in flat_text:
            # When overriding constitutive models. See 'test_tbft'
            warn(text, UserWarning)

        # flag errors
        if "*** ERROR ***" in flat_text:
            self._raise_output_errors(text)

    def _raise_output_errors(self, response):
        """Raise errors in the MAPDL response.

        Parameters
        ----------
        response : str
            Response from MAPDL.

        Raises
        ------
        MapdlRuntimeError
            For most of the errors.
        """
        # The logic is to iterate for each line. If the error header is found,
        # we analyse the following 'lines_number' in other to get the full error method.
        # Then with regex, we collect the error message, and raise it.
        for index, each_line in enumerate(response.splitlines()):
            if "*** ERROR ***" in each_line:
                error_is_fine = False

                # Extracting only the first 'lines_number' lines.
                # This is important. Regex has problems parsing long messages.
                lines_number = 20
                if len(response.splitlines()) <= lines_number:
                    partial_output = response
                else:
                    partial_output = "\n".join(
                        response.splitlines()[index : (index + lines_number)]
                    )

                # Find the error message.
                # Either ends with the beginning of another error message or with double empty line.
                error_message = re.search(
                    r"(\*\*\* ERROR \*\*\*.*?).*(?=\*\*\*|.*\n\n)",  # we might consider to use only one \n.
                    partial_output,
                    re.DOTALL,
                )

                if not error_message:
                    # Since we couldn't find an error message, the full partial message (10 lines) is analysed
                    self._log.debug(
                        f"PyMAPDL could not identify the error message, the full partial message ({lines_number} lines) is analysed"
                    )
                    error_message = partial_output
                else:
                    # Catching only the first error.
                    error_message = error_message.group(0)

                # Trimming empty lines
                error_message = "\n".join(
                    [each for each in error_message.splitlines() if each]
                )

                # Checking for permitted error.
                for each_error in _PERMITTED_ERRORS:
                    permited_error_message = re.search(each_error, error_message)

                    if permited_error_message:
                        error_is_fine = True
                        break

                # Raising errors
                if error_is_fine:
                    self._log.warn("PERMITTED ERROR: " + permited_error_message.string)
                    continue
                else:
                    # We don't need to log exception because they already included in the main logger.
                    # logger.error(response)
                    # However, exceptions are recorded in the global logger which do not record
                    # information of the instances name, hence we edit the error message.
                    raise MapdlRuntimeError(
                        f"\n\nError in instance {self.name}\n\n" + error_message
                    )

    def _check_mapdl_os(self):
        platform = self.get_value("active", 0, "platform").strip()
        if "l" in platform.lower():
            self._platform = "linux"
        elif "w" in platform.lower():  # pragma: no cover
            self._platform = "windows"
        else:  # pragma: no cover
            raise MapdlRuntimeError("Unknown platform: {}".format(platform))
        self.logger.debug(f"MAPDL is running on {self._platform} OS.")

    def _check_on_docker(self):
        """Check if MAPDL is running on docker."""
        # self.get_mapdl_envvar("ON_DOCKER") # for later
        if not self.is_grpc:  # pragma: no cover
            return False

        if self.platform == "linux":
            self.sys(
                r"if grep -sq 'docker\|lxc' /proc/1/cgroup; then echo 'true' > __outputcmd__.txt; else echo 'false' > __outputcmd__.txt;fi;"
            )
        elif self.platform == "windows":  # pragma: no cover
            return False  # TODO: check if it is running a windows docker container. So far it is not supported.

        if not self.is_local:
            sys_output = self._download_as_raw("__outputcmd__.txt").decode().strip()

        else:
            file_ = os.path.join(self.directory, "__outputcmd__.txt")
            with open(file_, "r") as f:
                sys_output = f.read().strip()

        self._log.debug(f"The output of sys command is: '{sys_output}'.")
        self.slashdelete("__outputcmd__.txt")  # cleaning
        return sys_output == "true"

    def _decompose_fname(self, fname: str) -> Tuple[str, str, str]:
        """Decompose a file name (with or without path) into filename and extension.

        Parameters
        ----------
        fname : str
            File name with or without path.

        Returns
        -------
        str
            File name (without extension or path)

        str
            File extension (without dot)

        str
            File path
        """
        fname = pathlib.Path(fname)
        return (fname.stem, fname.suffix.replace(".", ""), fname.parent)

    class _force_output:
        """Allows user to enter commands that need to run with forced text output."""

        def __init__(self, parent: "MapdlBase"):
            self._parent: "MapdlBase" = weakref.ref(parent)

        def __enter__(self):
            self._parent()._log.debug("Entering force-output mode")

            if self._parent().wrinqr(1) != 1:  # using wrinqr is more reliable than *get
                self._in_nopr = True
                self._parent()._run("/gopr")  # Going to PR mode
            else:
                self._in_nopr = False

            self._previous_mute, self._parent()._mute = self._parent()._mute, False

        def __exit__(self, *args):
            self._parent()._log.debug("Exiting force-output mode")
            if self._in_nopr:
                self._parent()._run("/nopr")
            self._parent()._mute = self._previous_mute

    def _parse_cmlist(self, cmlist: Optional[str] = None) -> Dict[str, Any]:
        from ansys.mapdl.core.component import _parse_cmlist

        if not cmlist:
            cmlist = self.cmlist()

        return _parse_cmlist(cmlist)

    def _parse_cmlist_indiv(
        self, cmname: str, cmtype: str, cmlist: Optional[str] = None
    ) -> List[int]:
        from ansys.mapdl.core.component import _parse_cmlist_indiv

        if not cmlist:
            cmlist = self.cmlist(cmname, 1)

        return _parse_cmlist_indiv(cmname, cmtype, cmlist)
