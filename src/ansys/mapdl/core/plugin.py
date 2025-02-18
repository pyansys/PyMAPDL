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

"""Contains the ansPlugin class."""
import json
import pathlib
import weakref

from ansys.api.mapdl.v0 import mapdl_pb2

from .common_grpc import ANSYS_VALUE_TYPE
from .errors import MapdlRuntimeError
from .misc import random_string


class ansPlugin:
    """
    ANSYS MAPDL Plugin Manager.

    Examples
    --------
    >>> from ansys.mapdl.core import launch_mapdl
    >>> mapdl = launch_mapdl()
    >>> plugin = mapdl.plugin

    Load a plugin in the MAPDL Session
    """

    def __init__(self, mapdl):
        """Initialize the class."""
        from ansys.mapdl.core.mapdl_grpc import MapdlGrpc

        if not isinstance(mapdl, MapdlGrpc):  # pragma: no cover
            raise TypeError("Must be initialized using MapdlGrpc class")

        self._mapdl_weakref = weakref.ref(mapdl)
        self._filename = None
        self._open = False

    @property
    def _mapdl(self):
        """Return the weakly referenced instance of mapdl."""
        return self._mapdl_weakref()

    def load(self, plugin_name: str, feature: str = "CMD") -> str:
        """
        Loads a plugin into MAPDL.

        Parameters
        ----------
        plugin_name : str
                Name of the plugin to load.
        feature : str
                Feature or module to activate in the plugin.

        Returns
        -------
        str
                Confirmation message about the loaded plugin.

        Raises
        ------
        PluginLoadError
                If the plugin fails to load.
        """

        command = f"*PLUG,LOAD,{plugin_name},{feature}"
        response = self._mapdl.run(command)
        if "error" in response.lower():
            raise PluginLoadError(
                f"Failed to load plugin '{plugin_name}' with feature '{feature}'."
            )
        return f"Plugin '{plugin_name}' with feature '{feature}' loaded successfully."

    def unload(self, plugin_name: str) -> str:
        """
        Unloads a plugin from MAPDL.

        Parameters
        ----------
        plugin_name : str
            Name of the plugin to unload.

        Returns
        -------
        str
            Confirmation message about the unloaded plugin.

        Raises
        ------
        PluginUnloadError
            If the plugin fails to unload.
        """

        command = f"*PLUG,UNLOAD,{plugin_name}"
        response = self._mapdl.run(command)
        if "error" in response.lower():
            raise PluginUnloadError(f"Failed to unload plugin '{plugin_name}'.")
        return f"Plugin '{plugin_name}' unloaded successfully."

    def list(self) -> list:
        """
        Lists all currently loaded plugins in MAPDL.

        Returns
        -------
        list
            A list of loaded plugin names.

        Raises
        ------
        RuntimeError
            If the plugin list cannot be retrieved.
        """

        command = "*PLUG,LIST"
        response = self._mapdl.run(command)
        if "error" in response.lower():
            raise RuntimeError("Failed to retrieve the list of loaded plugins.")
        # Parse response and extract plugin names (assuming response is newline-separated text)
        plugins = [line.strip() for line in response.splitlines() if line.strip()]
        return plugins
