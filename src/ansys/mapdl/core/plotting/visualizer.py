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

"""Module for the MapdlPlotter class."""
from collections import OrderedDict
from typing import Any, Dict, Iterable, Optional, Union

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackendInterface
import numpy as np
from numpy.typing import NDArray

from ansys.mapdl.core import LOG as logger
from ansys.mapdl.core import _HAS_VISUALIZER
from ansys.mapdl.core.misc import get_bounding_box
from ansys.mapdl.core.plotting.consts import (
    ALLOWED_TARGETS,
    BC_D,
    BC_F,
    BCS,
    FIELDS,
    FIELDS_ORDERED_LABELS,
    POINT_SIZE,
)
from ansys.mapdl.core.plotting.theme import MapdlTheme

if _HAS_VISUALIZER:
    import pyvista as pv

    from ansys.mapdl.core.plotting.plotting_defaults import DefaultSymbol

    BC_plot_settings = DefaultSymbol()


class MapdlPlotterBackend(PyVistaBackendInterface):
    """Provides the plotter for PyMAPDL.

    This class is an implementation of the ``PlotterInterface`` class from the ``ansys-visualizer`` package.
    Picker is implemented in PyMAPDL-specific classes due to the characteristics of the library.

    Parameters
    ----------
    use_trame : bool, optional
        Whether to use the Trame interface or not. The default is ``False``.
    theme : pv.DefaultTheme, optional
        Theme to use for the plotter. The default is ``None``.
    """

    def __init__(
        self, use_trame: bool = False, plot_picked_names: bool = True, **plotter_kwargs
    ):
        """Initialize the ``MapdlPlotter`` class."""
        super().__init__(
            use_trame=use_trame, plot_picked_names=plot_picked_names, **plotter_kwargs
        )

    def plot_iter(
        self, plottable_object: Any, name_filter: str = None, **plotting_options
    ):
        pass

    def plot(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        pass

    @property
    def scene(self):
        """Return the scene."""
        return self.pv_interface.scene

    @scene.setter
    def scene(self, scene):
        """Set the scene."""
        self.pv_interface._scene = scene

    @property
    def meshes(self):
        """Return the meshes."""
        return self.scene.meshes


class MapdlPlotter(Plotter):
    """Plotter class for PyMAPDL.

    This class is an implementation of the ``PlotterInterface`` class from the `Visualization Interface Tool <https://github.com/ansys/ansys-tools-visualization-interface>`_.
    The picker is implemented in PyMAPDL-specific classes due to the characteristics of the library.

    Parameters
    ----------
    use_trame : bool, optional
        Whether to use the Trame visualizer. The default is ``False``.
    theme : pv.DefaultTheme, optional
        Theme to use for the plotter. The default is ``None``.
    """

    def __init__(
        self, use_trame: bool = False, theme: pv.Plotter.theme = None, **plotter_kwargs
    ):
        """Initialize the ``MapdlPlotter`` class."""
        self._backend = MapdlPlotterBackend(use_trame=use_trame, **plotter_kwargs)
        super().__init__(backend=self._backend)
        self._theme = theme
        if theme is None:
            self._theme = MapdlTheme()
        self._off_screen = None
        self._notebook = None
        self._savefig = None
        self._title = None

    def _bc_labels_checker(self, bc_labels):
        """Make sure we have allowed parameters and data types for ``bc_labels``"""
        if not isinstance(bc_labels, (str, list, tuple)):
            raise ValueError(
                "The parameter 'bc_labels' can be only a string, a list of strings or tuple of strings."
            )

        if isinstance(bc_labels, str):
            bc_labels = bc_labels.upper()
            if bc_labels not in BCS and bc_labels not in FIELDS:
                raise ValueError(
                    f"The parameter '{bc_labels}' in 'bc_labels' is not supported.\n"
                    "Please use any of the following:\n"
                    f"{FIELDS}\nor any combination of:\n{BCS}"
                )
            bc_labels = [bc_labels]

        elif isinstance(bc_labels, (list, tuple)):
            if not all([isinstance(each, str) for each in bc_labels]):
                raise ValueError(
                    "The parameter 'bc_labels' can be a list or tuple, but it should only contain strings inside them."
                )

            if not all([each.upper() in BCS for each in bc_labels]):
                raise ValueError(
                    f"One or more parameters in 'bc_labels'({bc_labels}) are not supported.\n"
                    f"Please use any combination of the following:\n{BCS}"
                )

            bc_labels = [
                each.upper() for each in set(bc_labels)
            ]  # Removing duplicates too

        # Replacing field by equivalent fields.
        for each_field in FIELDS:
            if each_field in bc_labels:
                bc_labels.remove(each_field)
                bc_labels.extend(FIELDS[each_field])

        return bc_labels

    def _bc_target_checker(self, bc_target):
        """Make sure we have allowed parameters and data types for ``bc_labels``"""
        if not isinstance(bc_target, (str, list, tuple)):
            raise ValueError(
                "The parameter 'bc_target' can be only a string, a list of strings or tuple of strings."
            )

        if isinstance(bc_target, str):
            if bc_target.upper() not in ALLOWED_TARGETS:
                raise ValueError(
                    f"The parameter '{bc_target}' in 'bc_target' is not supported.\n"
                    f"At the moments only the following are supported:\n{ALLOWED_TARGETS}"
                )
            bc_target = [bc_target.upper()]

        if isinstance(bc_target, (list, tuple)):
            if not all([each.upper() in ALLOWED_TARGETS for each in bc_target]):
                raise ValueError(
                    "One or more parameters in 'bc_target' are not supported.\n"
                    f"Please use any combination of the following:\n{ALLOWED_TARGETS}"
                )
            if not all([isinstance(each, str) for each in bc_target]):
                raise ValueError(
                    "The parameter 'bc_target' can be a list or tuple, but it should only contain strings inside them."
                )

            bc_target = [each.upper() for each in bc_target]

        return bc_target

    def _bc_labels_default(self, mapdl):
        """Get the labels from the MAPDL database."""
        flist = list(
            set(
                [
                    each[1].upper()
                    for each in mapdl.get_nodal_loads()
                    if each[1].upper() in BCS
                ]
            )
        )
        dlist = list(
            set(
                [
                    each[1].upper()
                    for each in mapdl.get_nodal_constrains()
                    if each[1].upper() in BCS
                ]
            )
        )
        return flist + dlist

    def get_meshes_from_plotter(self):
        """Get the meshes plotted in the plotter.

        Returns
        -------
        list[pv.PolyData]
            Plotted meshes.
        """
        datasets = []
        for actor in self.scene.actors.values():
            if hasattr(actor, "mapper"):
                datasets.append(actor.mapper.dataset)

        return [
            actor.mapper.dataset
            for actor in self.scene.actors.values()
            if hasattr(actor, "mapper")
        ]

    def add_labels(
        self, points: Iterable[float], labels: Iterable[str], **plotting_options
    ) -> None:
        """Add labels to the plotter.

        Parameters
        ----------
        points : List[float]
            List of points for the labels.
        labels : List[str]
            List of labels to add.
        """
        self.scene.add_point_labels(points, labels, **plotting_options)

    def add_points(self, points: Iterable[float], **plotting_options) -> None:
        """Add points to the plotter.

        Parameters
        ----------
        points : List[float]
            List of points to add to the plotter.
        """
        _ = self.scene.add_points(points, **plotting_options)

    def plot_iter(
        self,
        plotting_list: Iterable[Any],
        name_filter: str = None,
        **plotting_options,
    ) -> None:
        """Add a list of objects to the plotter.

        Parameters
        ----------
        plotting_list : Iterable[Any]
            Iterable of objects to add to the plotter.
        name_filter : str, optional
            Filter to apply to the objects. The default is ``None``.
        """
        for plottable_object in plotting_list:
            self.plot(plottable_object, name_filter, **plotting_options)

    def add_mesh(
        self,
        meshes: Union[pv.PolyData, Dict[str, Any]] = [],
        points=[],
        labels=[],
        *,
        cpos=None,
        show_bounds=False,
        show_axes=True,
        background=None,
        # add_mesh kwargs:
        style=None,
        color="w",
        show_edges=None,
        edge_color=None,
        point_size=POINT_SIZE,
        line_width=None,
        opacity=1.0,
        flip_scalars=False,
        lighting=None,
        n_colors=256,
        interpolate_before_map=True,
        cmap=None,
        render_points_as_spheres=False,
        render_lines_as_tubes=False,
        scalar_bar_args=None,
        smooth_shading=None,
        feature_angle=30.0,
        show_scalar_bar=None,
        split_sharp_edges=None,
        # labels kwargs
        font_size=None,
        font_family=None,
        text_color=None,
        theme=None,
        add_points_kwargs=None,
        add_mesh_kwargs=None,
        add_point_labels_kwargs=None,
        plotter_kwargs=None,
    ):
        """Adds a mesh to the plotter.

        Parameters
        ----------
        meshes : pv.PolyData
            The mesh to add to the plotter.
        points : pv.PolyData
            The points to add to the plotter.
        labels : pv.PolyData
            The labels to add to the plotter.
        plotter_kwargs : dict, optional
            Extra kwargs, by default {}
        """
        if not meshes and not points and not labels:
            logger.warning("No meshes, points or labels to plot.")
            return

        if theme is None:
            theme = MapdlTheme()

        if not cmap:
            cmap = "bwr"

        if background:
            self.scene.set_background(background)
        else:
            self.scene.set_background("paraview")

        # Making sure that labels are visible in dark backgrounds
        if not text_color and background:
            bg = self.scene.background_color.float_rgb
            # from: https://graphicdesign.stackexchange.com/a/77747/113009
            gamma = 2.2
            threshold = (
                0.2126 * bg[0] ** gamma
                + 0.7152 * bg[1] ** gamma
                + 0.0722 * bg[2] ** gamma
                > 0.5 * gamma
            )
            if threshold:
                text_color = "black"
            else:
                text_color = "white"

        for point in points:
            self.add_points(
                point["points"],
                # scalars=point.get("scalars", None),
                color=color,
                show_edges=show_edges,
                edge_color=edge_color,
                point_size=point_size,
                line_width=line_width,
                opacity=opacity,
                flip_scalars=flip_scalars,
                lighting=lighting,
                n_colors=n_colors,
                interpolate_before_map=interpolate_before_map,
                cmap=cmap,
                render_points_as_spheres=render_points_as_spheres,
                render_lines_as_tubes=render_lines_as_tubes,
                **(add_points_kwargs or {}),
            )

        if isinstance(meshes, pv.PolyData):
            meshes = [meshes]
        for mesh in meshes:
            rgb = False
            if isinstance(mesh, Dict):
                scalars: Optional[NDArray[Any]] = mesh.get("scalars")

                if (
                    "scalars" in mesh
                    and scalars.ndim == 2
                    and (scalars.shape[1] == 3 or scalars.shape[1] == 4)
                ):
                    # for the case we are using scalars for plotting
                    rgb = True

                # To avoid index error.
                mesh_ = mesh["mesh"]
                if not isinstance(mesh_, list):
                    mesh_ = [mesh_]
            else:
                scalars = None
                mesh_ = meshes
            for each_mesh in mesh_:
                self.scene.add_mesh(
                    each_mesh,
                    scalars=scalars,
                    scalar_bar_args=scalar_bar_args,
                    color=(
                        mesh.get("color", color)
                        if isinstance(mesh, Dict) and "color" in mesh
                        else color
                    ),
                    style=(
                        mesh.get("style", style)
                        if isinstance(mesh, Dict) and "style" in mesh
                        else style
                    ),
                    show_edges=show_edges,
                    edge_color=edge_color,
                    smooth_shading=smooth_shading,
                    split_sharp_edges=split_sharp_edges,
                    feature_angle=feature_angle,
                    point_size=point_size,
                    line_width=line_width,
                    show_scalar_bar=show_scalar_bar,
                    opacity=opacity,
                    flip_scalars=flip_scalars,
                    lighting=lighting,
                    n_colors=n_colors,
                    interpolate_before_map=interpolate_before_map,
                    cmap=cmap,
                    render_points_as_spheres=render_points_as_spheres,
                    render_lines_as_tubes=render_lines_as_tubes,
                    rgb=rgb,
                    **(add_mesh_kwargs or {}),
                )

        for label in labels:
            # Pyvista does not support plotting two labels with the same point.
            # It does handle that case by keeping only the first label.

            self.add_labels(
                label["points"],
                label["labels"],
                show_points=False,
                shadow=False,
                font_size=font_size,
                font_family=font_family,
                text_color=text_color,
                always_visible=True,
                **(add_point_labels_kwargs or {}),
            )

        if cpos:
            self.scene.camera_position = cpos

        if show_bounds:
            self.scene.show_bounds()

    def bc_plot(
        self,
        mapdl=None,
        bc_labels=None,
        bc_target=None,
        plot_bc_labels=False,
        plot_bc_legend=None,
        bc_glyph_size=None,
        bc_labels_font_size=16,
    ):
        """Plot boundary conditions.

        Parameters
        ----------
        mapdl : Mapdl, optional
            Mapdl instance, by default None
        bc_labels : optional
            Labels to plot, by default None
        bc_target : optional
            Targets to plot, by default None
        plot_bc_labels : bool, optional
            Whether to plot the labels or not, by default False
        plot_bc_legend : optional
            Legend to plot, by default None
        bc_glyph_size : optional
            Size of the gliph, by default None
        bc_labels_font_size : int, optional
            Size of the labels font, by default 16
        """
        if bc_labels:
            bc_labels = self._bc_labels_checker(bc_labels)
        else:
            bc_labels = self._bc_labels_default(mapdl)

        if bc_target:
            bc_target = self._bc_target_checker(bc_target)
        else:
            bc_target = ["NODES"]  # bc_target_default()

        # We need to scale the glyphs, otherwise, they will be plot sized 1.
        # We are going to calculate the distance between the closest points,
        # so we will scaled to a percentage of this distance.
        # This might create very small points in cases there are a concentration of points.
        #
        # Later can find a way to plot them and keep their size constant independent of the zoom.

        ratio = 0.075  # Because a glyph of 1 is too big.
        if bc_glyph_size is None:
            bc_glyph_size = get_bounding_box(mapdl.mesh.nodes)
            bc_glyph_size = bc_glyph_size[bc_glyph_size != 0]

            if bc_glyph_size.size != 0:
                bc_glyph_size = bc_glyph_size.mean() * ratio
            else:  # Case were there is only one node
                bc_glyph_size = ratio

        if not isinstance(bc_glyph_size, (int, float)):
            raise ValueError(
                "The 'bc_glyph_size' parameter can be only an int or float."
            )

        if "NODES" in bc_target:
            self.bc_nodes_plot(
                mapdl=mapdl,
                bc_labels=bc_labels,
                plot_bc_labels=plot_bc_labels,
                bc_glyph_size=bc_glyph_size,
                plot_bc_legend=plot_bc_legend,
                bc_labels_font_size=bc_labels_font_size,
            )

        # Add next things
        if "ELEM" in bc_target:
            pass

    def bc_nodes_plot(
        self,
        mapdl,
        bc_labels,
        plot_bc_labels=False,
        bc_glyph_size=1,
        plot_bc_legend=None,
        bc_labels_font_size=16,
    ):
        """Plot nodes BC given a list of labels."""
        nodes_xyz = mapdl.mesh.nodes
        nodes_num = mapdl.mesh.nnum

        bc_point_labels = None

        for each_label in bc_labels:
            if each_label in BC_D:
                bc = mapdl.get_nodal_constrains(each_label)

            elif each_label in BC_F:
                bc = mapdl.get_nodal_loads(each_label)

            else:
                raise Exception(f"The label '{each_label}' is not supported.")

            if bc.size == 0:  # There is no nodes with such label
                return

            bc_num = bc[:, 0].astype(int)
            bc_nodes = nodes_xyz[np.isin(nodes_num, bc_num), :]
            bc_values = bc[:, 1:].astype(float)
            bc_scale = abs(bc_values[:, 0])

            if bc_scale.max() != bc_scale.min():
                bc_scale = (bc_scale - bc_scale.min()) / (
                    bc_scale.max() - bc_scale.min()
                ) + 0.5  # Normalization around 0.5
            else:
                bc_scale = (
                    np.ones(bc_scale.shape) * 0.5
                )  # In case all the values are the same

            pcloud = pv.PolyData(bc_nodes)
            pcloud["scale"] = bc_scale * bc_glyph_size

            # Specify tolerance in terms of fraction of bounding box length.
            # Float value is between 0 and 1. Default is None.
            # If absolute is True then the tolerance can be an absolute distance.
            # If None, points merging as a preprocessing step is disabled.
            glyphs = pcloud.glyph(
                orient=False,
                scale="scale",
                # tolerance=0.05,
                geom=BC_plot_settings(each_label)["glyph"],
            )
            name_ = f"{each_label}"
            self.scene.add_mesh(
                glyphs,
                # name_filter=None,
                color=BC_plot_settings(each_label)["color"],
                style="surface",
                # style='wireframe',
                # line_width=3,
                name=name_,
                label=name_,
                opacity=0.40,
            )

            if plot_bc_labels:
                if bc_point_labels is None:
                    bc_point_labels = {each: "" for each in nodes_num}

                for id_, values in zip(bc_num, bc_values):
                    if not bc_point_labels[id_]:
                        bc_point_labels[id_] = (
                            f"Node: {id_}\n{each_label}: {values[0]:6.3f}, {values[1]:6.3f}"
                        )
                    else:
                        bc_point_labels[id_] = (
                            f"{bc_point_labels[id_]}\n{each_label}: {values[0]:6.3f}, {values[1]:6.3f}"
                        )

        if plot_bc_labels:
            pcloud = pv.PolyData(nodes_xyz)
            pcloud["labels"] = list(bc_point_labels.values())
            self.add_labels(
                pcloud.points,
                pcloud["labels"],
                shape_opacity=0.25,
                font_size=bc_labels_font_size,
                # There is a conflict here. See
                # To do not hide the labels, even when the underlying nodes
                # are hidden, we set "always_visible"
                always_visible=True,
                show_points=False,  # to not have node duplicity
                font_family="arial",
            )

        if plot_bc_legend:
            # Reorder labels to keep a consistent order
            sorted_dict = OrderedDict()
            labels_ = self.scene.renderer._labels.copy()

            # sorting the keys
            for symbol in FIELDS_ORDERED_LABELS:
                for key, value in labels_.items():
                    # taking advantage and overriding the legend glyph with
                    # something it can be seen properly in the legend
                    label_ = value[1]
                    if "U" in label_:
                        value = [BC_plot_settings("UY")["glyph"], label_, value[2]]
                    elif "F" in label_:
                        value = [BC_plot_settings("FX")["glyph"], label_, value[2]]
                    else:
                        value = [BC_plot_settings(label_)["glyph"], label_, value[2]]

                    if symbol == value[1]:
                        sorted_dict[key] = value

            # moving the not added labels (just in case)
            for key, value in labels_.items():
                if label_ not in FIELDS_ORDERED_LABELS:
                    sorted_dict[key] = value

            # overwriting labels
            self.scene.renderer._labels = sorted_dict
            self.scene.theme.font.family = "arial"
            self.scene.add_legend(bcolor=None)

    def plot(
        self,
        meshes: Union[pv.PolyData, Dict[str, Any]] = [],
        points=[],
        labels=[],
        *,
        title="",
        cpos=None,
        show_bounds=False,
        show_axes=True,
        background=None,
        # add_mesh kwargs:
        style=None,
        color="w",
        show_edges=None,
        edge_color=None,
        point_size=5.0,
        line_width=None,
        opacity=1.0,
        flip_scalars=False,
        lighting=None,
        n_colors=256,
        interpolate_before_map=True,
        cmap=None,
        render_points_as_spheres=False,
        render_lines_as_tubes=False,
        scalar_bar_args=None,
        smooth_shading=None,
        show_scalar_bar=None,
        split_sharp_edges=None,
        # labels kwargs
        font_size=None,
        font_family=None,
        text_color=None,
        theme=None,
        return_plotter=False,
        return_cpos=False,
        mapdl=None,
        plot_bc=False,
        plot_bc_legend=None,
        plot_bc_labels=None,
        bc_labels=None,
        bc_target=None,
        bc_glyph_size=None,
        bc_labels_font_size=16,
        add_points_kwargs=None,
        add_mesh_kwargs=None,
        add_point_labels_kwargs=None,
        plotter_kwargs=None,
        **kwargs,
    ) -> None:
        """Add an object to the plotter.

        Parameters
        ----------
        object : Any
            Object to add to the plotter.
        name_filter : str, optional
            Filter to apply to the object. The default is ``None``.
        """

        # Getting the plotter
        self.add_mesh(
            meshes,
            points,
            labels,
            cpos=cpos,
            show_bounds=show_bounds,
            show_axes=show_axes,
            background=background,
            # add_mesh kwargs:
            style=style,
            color=color,
            show_edges=show_edges,
            edge_color=edge_color,
            point_size=point_size,
            line_width=line_width,
            opacity=opacity,
            flip_scalars=flip_scalars,
            lighting=lighting,
            n_colors=n_colors,
            interpolate_before_map=interpolate_before_map,
            cmap=cmap,
            render_points_as_spheres=render_points_as_spheres,
            render_lines_as_tubes=render_lines_as_tubes,
            scalar_bar_args=scalar_bar_args,
            smooth_shading=smooth_shading,
            show_scalar_bar=show_scalar_bar,
            split_sharp_edges=split_sharp_edges,
            # labels kwargs
            font_size=font_size,
            font_family=font_family,
            text_color=text_color,
            theme=theme,
            add_points_kwargs=add_points_kwargs,
            add_mesh_kwargs=add_mesh_kwargs,
            add_point_labels_kwargs=add_point_labels_kwargs,
            plotter_kwargs=plotter_kwargs,
        )

        if plot_bc:
            if not mapdl:
                raise ValueError(
                    "An instance of `ansys.mapdl.core.mapdl.MapdlBase` "
                    "should be passed using `mapdl` keyword if you are aiming "
                    "to plot the boundary conditions (`plot_bc` is `True`)."
                )
            self.bc_plot(
                mapdl=mapdl,
                plot_bc_legend=plot_bc_legend,
                plot_bc_labels=plot_bc_labels,
                bc_labels=bc_labels,
                bc_target=bc_target,
                bc_glyph_size=bc_glyph_size,
                bc_labels_font_size=bc_labels_font_size,
            )

        if title:  # Added here to avoid labels overlapping title
            self.scene.add_title(title, color=text_color)

        if return_cpos and return_plotter:
            raise ValueError(
                "'return_cpos' and 'return_plotter' cannot be both 'True' at the same time."
            )

    def switch_scene(self, pl: Union["pv.Plotter", "MapdlPlotter"]) -> "MapdlPlotter":
        """Switches the backend scene to the given plotter.

        Parameters
        ----------
        pl : Union["pv.Plotter", "MapdlPlotter"]
            Plotter to change the scene to.

        Returns
        -------
        MapdlPlotter
            The MapdlPlotter instance.
        """
        if isinstance(pl, pv.Plotter):
            self._backend.scene = pl
            self._backend.enable_widgets()
            return self
        elif isinstance(pl, MapdlPlotter):
            return pl
        elif pl is None:
            return self
        else:
            raise TypeError(
                f"Expected a ``MapdlPlotter`` or ``pv.Plotter`` instance, but got {type(pl)}"
            )

    def show(
        self,
        window_size=None,
        return_plotter=False,
        return_cpos=False,
        notebook=None,
        savefig=None,
        off_screen=None,
        **kwargs,
    ) -> None:
        """Show the plotter."""

        self._off_screen = off_screen
        if notebook:
            self._off_screen = True  # pragma: no cover

        if savefig:
            self._off_screen = True
            self._notebook = False

        # permit user to save the figure as a screenshot
        if self._savefig or savefig:
            self._backend.show(
                auto_close=False,
                window_size=window_size,
                screenshot=savefig,
                **kwargs,
            )
            self.scene.screenshot(self._savefig)

            # return unclosed plotter
            if return_plotter:
                return self

            # if plotter.scene.set_background("paraview") not returning plotter, close right away
            self.scene.close()

        else:
            if not return_plotter:
                self._backend.show()

        if return_plotter:
            return self
        elif return_cpos:
            return self.scene.camera_position
        else:
            return None

    @property
    def scene(self):
        """Return the scene."""
        return self._backend.scene

    @property
    def meshes(self):
        """Return the meshes."""
        return self.scene.meshes
