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

"""Module for miscellaneous functions and methods"""
from enum import Enum
from functools import cache, wraps
import importlib
import inspect
import os
import platform
import re
import socket
import string
import tempfile
from threading import Thread
from typing import Callable, Dict, Iterable, List, Tuple, Union
from warnings import warn

import numpy as np

from ansys.mapdl.core import _HAS_PYVISTA, LOG

# path of this module
MODULE_PATH = os.path.dirname(inspect.getfile(inspect.currentframe()))


class ROUTINES(Enum):
    """MAPDL routines."""

    BEGIN_LEVEL = 0
    PREP7 = 17
    SOLUTION = 21
    POST1 = 31
    POST26 = 36
    AUX2 = 52
    AUX3 = 53
    AUX12 = 62
    AUX15 = 65


def check_valid_routine(routine: ROUTINES) -> bool:
    """Check if a routine is valid.

    Acceptable aliases for "Begin level" include "begin".

    Parameters
    ----------
    routine : str
        Routine. For example "PREP7".

    Returns
    -------
    bool
        ``True`` when routine is valid.

    Raises
    ------
    ValueError
        Raised when a routine is invalid.

    """
    if routine.lower().startswith("/"):
        routine = routine[1:]

    if routine.lower().startswith("begin"):
        return True
    if not hasattr(ROUTINES, routine.upper()):
        valid_routines = []
        for item in dir(ROUTINES):
            if not item.startswith("_") and not item.startswith("BEGIN"):
                valid_routines.append(item)
        valid_routines.append("Begin level")
        valid_routines_str = "\n".join([f'\t- "{item}"' for item in valid_routines])
        raise ValueError(
            f"Invalid routine {routine}. Should be one of:\n{valid_routines_str}"
        )
    return True


def is_float(input_string: str) -> bool:
    """Returns true when a string can be converted to a float"""
    try:
        float(input_string)
        return True
    except ValueError:
        return False


def random_string(stringLength: int = 10, letters: str = string.ascii_lowercase) -> str:
    """Generate a random string of fixed length"""
    import secrets

    return "".join(secrets.choice(letters) for _ in range(stringLength))


def check_has_mapdl() -> bool:
    """Safely wraps check_valid_ansys

    Returns
    -------
    has_ansys : bool
        True when this local installation has ANSYS installed in a
        standard location.
    """
    from ansys.mapdl.core.launcher.tools import check_valid_ansys

    try:
        return check_valid_ansys()
    except Exception as err:
        LOG.error(
            f"An error was obtained when checking for a valid MAPDL installation:\n{str(err)}"
        )
        return False


def supress_logging(func: Callable) -> Callable:
    """Decorator to suppress logging for a MAPDL instance"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        from ansys.mapdl.core.mapdl import MapdlBase

        mapdl = args[0]
        if not issubclass(type(mapdl), (MapdlBase)):
            # Assuming we are on a module object.
            mapdl = mapdl._mapdl
            if not issubclass(type(mapdl), (MapdlBase)):
                raise Exception("This wrapper cannot access MAPDL object")

        prior_log_level = mapdl._log.level
        if prior_log_level != "CRITICAL":
            mapdl._set_log_level("CRITICAL")

        out = func(*args, **kwargs)

        if prior_log_level != "CRITICAL":
            mapdl._set_log_level(prior_log_level)

        return out

    return wrapper


def run_as(routine: ROUTINES):
    """Run a MAPDL method at PREP7 and always revert to the prior processor"""

    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            from ansys.mapdl.core.mapdl import MapdlBase

            mapdl = self
            if not issubclass(type(mapdl), (MapdlBase)):
                # Assuming we are on a module object.
                mapdl = mapdl._mapdl
                if not issubclass(type(mapdl), (MapdlBase)):
                    raise Exception("This wrapper cannot access MAPDL object")

            with mapdl.run_as_routine(routine.upper()):
                return function(self, *args, **kwargs)

        return wrapper

    return decorator


def threaded(func: Callable) -> Callable:
    """Decorator to call a function using a thread"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        name = kwargs.get("name", f"Threaded `{func.__name__}` function")
        thread = Thread(target=func, name=name, args=args, kwargs=kwargs)
        thread.start()
        LOG.debug(f"Thread started with name: {name}")
        return thread

    return wrapper


def threaded_daemon(func: Callable) -> Callable:
    """Decorator to call a function using a daemon thread."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        name = kwargs.pop(
            "thread_name", f"Threaded (with Daemon) `{func.__name__}` function"
        )

        thread = Thread(target=func, name=name, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        LOG.debug(f"Thread demon started with name: {name}")
        return thread

    return wrapper


def unique_rows(arr: np.ndarray) -> Tuple[Union[np.ndarray, np.ndarray, np.ndarray]]:
    """Returns unique rows of `arr` and indices of those rows"""
    if not arr.flags.c_contiguous:
        arr = np.ascontiguousarray(arr)

    b = arr.view(np.dtype((np.void, arr.dtype.itemsize * arr.shape[1])))
    _, idx, idx2 = np.unique(b, True, True)

    return arr[idx], idx, idx2


def creation_time(path_to_file: str) -> float:
    """The file creation time.

    Try to get the date that a file was created, falling back to when
    it was last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return float(stat.st_birthtime)
        except AttributeError:
            LOG.debug(
                "We're probably on Linux. No easy way to get creation dates here, "
                "so we'll settle for when its content was last modified."
            )
            return stat.st_mtime


def last_created(filenames: List[str]) -> str:
    """Return the last created file given a list of filenames

    If all filenames have the same creation time, then return the last
    filename.
    """
    ctimes = [creation_time(filename) for filename in filenames]
    idx = np.argmax(ctimes)
    if len(set(ctimes)):
        return filenames[-1]

    return filenames[idx]


def create_temp_dir(tmpdir: str = None, name: str = None) -> str:
    """Create a new unique directory at a given temporary directory"""
    if tmpdir is None:
        tmpdir = tempfile.gettempdir()

    # Possible letters
    letters_ = string.ascii_lowercase.replace("n", "")

    def get_name():
        return random_string(10, letters_)

    name = name or get_name()
    while os.path.exists(os.path.join(tmpdir, name)):
        name = get_name()

    # create dir:
    path = os.path.join(tmpdir, name)

    if not os.path.isdir(path):
        os.makedirs(path)
        LOG.debug(f"Created run location at {path}")

    return path


def no_return(func: Callable) -> Callable:
    """Decorator to return nothing from the wrapped function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    LOG.debug("Output has been suppressed.")
    return wrapper


def get_bounding_box(nodes_xyz: np.ndarray) -> np.ndarray:
    min_ = np.min(nodes_xyz, axis=0)
    max_ = np.max(nodes_xyz, axis=0)

    return max_ - min_


def load_file(mapdl: "Mapdl", fname: str, priority_mapdl_file: bool = None) -> str:
    """
    Provide a file to the MAPDL instance.

    Parameters
    ----------
    mapdl
      Mapdl instance

    fname : str, path
      Path to the file.

    priority_mapdl_file : bool
      In case of the file existing in the MAPDL environment and
      in the local Python environment, this parameter specifies
      which one has priority. Defaults to ``True``, meaning the MAPDL file
      has priority.

    Notes
    -----

    **When running MAPDL locally:**

    Checks if the file is reachable or is in the MAPDL directory,
    if not, it raises a ``FileNotFound`` exception.

    If:

    - The file is only the MAPDL directory, this function does nothing
      since the file is already accessible to the MAPDL instance.

    - If the file exists in both, the Python working directory and the MAPDL
      directory, this function does nothing, as the file in the MAPDL working
      directory has priority.

    **When in remote (not-local)**

    Check if the file exists locally or in the working directory, if not, it will raise a ``FileNotFound`` exception.
    If the file is local, it will be uploaded.

    """

    base_fname = os.path.basename(fname)
    if not os.path.exists(fname) and base_fname not in mapdl.list_files():
        raise FileNotFoundError(
            f"The file {fname} could not be found in the Python working directory ('{os.getcwd()}') "
            f"nor in the MAPDL working directory ('{mapdl.directory}')."
        )

    elif os.path.exists(fname) and base_fname in mapdl.list_files():
        if priority_mapdl_file is None:
            warn(
                f"The file '{base_fname}' is present in both, the python working directory ('{os.getcwd()}') "
                f"and in the MAPDL working directory ('{mapdl.directory}'). "
                "Using the one already in the MAPDL directory.\n"
                "If you prefer to use the file in the Python directory, you shall remove the file in the MAPDL directory."
            )
            priority_mapdl_file = True

        if not priority_mapdl_file:
            mapdl.upload(fname)

    elif os.path.exists(fname) and base_fname not in mapdl.list_files():
        mapdl._log.debug("File is in the Python working directory, uploading.")
        mapdl.upload(fname)

    elif not os.path.exists(fname) and base_fname in mapdl.list_files():
        mapdl._log.debug("File is already in the MAPDL working directory")

    # Simplifying name for MAPDL reads it.
    return os.path.basename(fname)


def check_valid_ip(ip: str) -> None:
    """Check for valid IP address"""
    if ip.lower() != "localhost":
        ip = ip.replace('"', "").replace("'", "")
        socket.inet_aton(ip)


def check_valid_port(
    port: int, lower_bound: int = 1000, high_bound: int = 60000
) -> None:
    if not isinstance(port, int):
        raise ValueError("The 'port' parameter should be an integer.")

    if not (lower_bound < port < high_bound):
        raise ValueError(
            f"'port' values should be between {lower_bound} and {high_bound}."
        )


def write_array(filename: Union[str, bytes], array: np.ndarray) -> None:
    """
    Write an array to a file.

    This function aim to replace
    ``ansys.mapdl.reader._reader write_array``.

    Parameters
    ----------
    filename : str
        Name of the file.
    array : numpy.ndarray
        Array.
    """
    if isinstance(filename, bytes):
        filename = filename.decode()
    np.savetxt(filename, array, fmt="%20.12f")


@cache
def is_package_installed_cached(package_name):
    try:
        importlib.import_module(package_name)
        return True

    except ModuleNotFoundError:
        return False


def requires_package(package_name: str, softerror: bool = False) -> Callable:
    """
    Decorator check whether a package is installed or not.

    If it is not, it will return None.

    Parameters
    ----------
    package_name : str
        Name of the package.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):

            if is_package_installed_cached(package_name):
                return function(self, *args, **kwargs)

            else:
                msg = (
                    f"To use the method '{function.__name__}', "
                    f"the package '{package_name}' is required.\n"
                    f"Please try to install '{package_name}' with:\n"
                    f"pip install {package_name.replace('.', '-') if 'ansys' in package_name else package_name}"
                )

                if softerror:
                    warn(msg)
                    return None
                else:
                    raise ModuleNotFoundError(msg)

        return wrapper

    return decorator


def _get_args_xsel(*args: Tuple[str], **kwargs: Dict[str, str]) -> Tuple[str]:
    type_ = kwargs.pop("type_", str(args[0]) if len(args) else "").upper()
    item = kwargs.pop("item", str(args[1]) if len(args) > 1 else "").upper()
    comp = kwargs.pop("comp", str(args[2]) if len(args) > 2 else "").upper()
    vmin = kwargs.pop("vmin", args[3] if len(args) > 3 else "")
    vmax = kwargs.pop("vmax", args[4] if len(args) > 4 else "")
    vinc = kwargs.pop("vinc", args[5] if len(args) > 5 else "")
    kabs = kwargs.pop("kabs", args[6] if len(args) > 6 else "")
    return type_, item, comp, vmin, vmax, vinc, kabs, kwargs


def allow_pickable_entities(
    entity: str = "node", plot_function: str = "nplot"
) -> Callable:
    """
    This wrapper opens a window with the NPLOT or KPLOT, and get the selected points (Nodes or kp),
    and feed them as a list to the NSEL.
    """

    def decorator(orig_entity_sel_function):
        @wraps(orig_entity_sel_function)
        def wrapper(self, *args, **kwargs):
            type_, item, comp, vmin, vmax, vinc, kabs, kwargs = _get_args_xsel(
                *args, **kwargs
            )
            from ansys.mapdl.core.plotting.consts import POINT_SIZE

            if item == "P" and _HAS_PYVISTA:
                if type_ not in ["S", "R", "A", "U"]:
                    raise ValueError(
                        f"The 'item_' argument ('{item}') together with the 'type_' argument ('{type_}') are not allowed."
                    )

                previous_picked_entities = set(self._get_selected_(entity))

                if type_ in ["S", "A"]:  # selecting all the entities
                    orig_entity_sel_function(self, "all")

                plotting_function = getattr(self, plot_function)
                if entity == "area":
                    # To overwrite the quality argument
                    pl = plotting_function(return_plotter=True, quality=1)
                elif entity in ["node", "nodes", "kp"]:
                    pl = plotting_function(return_plotter=True, point_size=POINT_SIZE)
                else:
                    pl = plotting_function(return_plotter=True)

                vmin = self._enable_picking_entities(
                    entity, pl, type_, previous_picked_entities, **kwargs
                )

                if len(vmin) == 0:
                    # aborted picking
                    orig_entity_sel_function(
                        self, "S", entity, "", previous_picked_entities, **kwargs
                    )
                    return []

                item = entity
                comp = ""

                # to make return the array of entity when using P
                kwargs["Used_P"] = True

                return orig_entity_sel_function(
                    self, "S", item, comp, vmin, vmax, vinc, kabs, **kwargs
                )

            else:
                return orig_entity_sel_function(
                    self, type_, item, comp, vmin, vmax, vinc, kabs, **kwargs
                )

        return wrapper

    return decorator


def allow_iterables_vmin(entity: str = "node") -> Callable:
    def decorator(original_sel_func: Callable) -> Callable:
        """
        This function wraps a NSEL or KSEL function to allow using a list/tuple/array for vmin argument.

        This allows for example:

        >>> mapdl.nsel("S", "node", "", [1, 2, 3])  # select nodes 1, 2, and 3.
        """

        @wraps(original_sel_func)
        def wrapper(self, *args, **kwargs):
            type_, item, comp, vmin, vmax, vinc, kabs, kwargs = _get_args_xsel(
                *args, **kwargs
            )

            if isinstance(vmin, (set, tuple, list, np.ndarray)):
                if kwargs.get("Used_P", False) and (
                    (isinstance(vmin, np.ndarray) and vmin.size != 0) or len(vmin) == 0
                ):
                    # edge case where during the picking we have selected nothing.
                    # In that case, we just silently quit NSEL command. We do **not**
                    # want to unselect everything (case in scripting where
                    # ``mapdl.nsel("S","node", "", [])`` unselect everything).
                    return

                self.run(
                    f"/com, Selecting {entity}s from an iterable (i.e. set, list, tuple, or array)"
                )  # To have a clue in the apdl log file

                if vmax or vinc:
                    raise ValueError(
                        "If an iterable is used as 'vmin' argument, "
                        "it is not allowed to use 'vmax' or 'vinc' arguments."
                    )

                if len(vmin) == 0 and type_ == "S":
                    # assuming you want to select nothing because you supplied an empty list/tuple/array
                    return original_sel_func(self, "none")

                with self.non_interactive:  # to speed up
                    self._perform_entity_list_selection(
                        entity, original_sel_func, type_, item, comp, vmin, kabs
                    )

                if kwargs.pop("Used_P", False):
                    # we want to return the
                    return np.array(vmin)
                else:
                    return
            else:
                return original_sel_func(
                    self,
                    type_,
                    item,
                    comp,
                    vmin,
                    vmax,
                    vinc,
                    kabs,  # ksel, esel, nsel uses kabs, but lsel, asel, vsel uses kswp
                    **kwargs,
                )

        return wrapper

    return decorator


def only_numbers_and_dots(st: str) -> bool:
    """Return if a string contains only numbers and dots"""
    return bool(re.fullmatch(r"[0-9.]+", st))


def stack(*decorators: Iterable[Callable]) -> Callable:
    """Stack multiple decorators on top of each other"""

    def deco(f):
        for dec in reversed(decorators):
            f = dec(f)
        return f

    return deco
