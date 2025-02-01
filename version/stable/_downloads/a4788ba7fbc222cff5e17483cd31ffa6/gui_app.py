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

import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from pyvistaqt import QtInteractor

from ansys.mapdl.core import Mapdl, launch_mapdl
from ansys.mapdl.core.plotting.theme import MapdlTheme


class MainWindow(QMainWindow):
    def __init__(self, mapdl: Mapdl, parent=None) -> None:
        super().__init__(parent)
        self._mapdl = mapdl
        self._setup_ui()

    def _setup_ui(self) -> None:
        # General settings for the window
        self.setWindowTitle("PyMAPDL example application")
        self.resize(1000, 500)
        self._widget = QWidget()
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Create the tabs
        self._tab_widget = QtWidgets.QTabWidget()

        self._tab_preprocessing = QtWidgets.QWidget()
        self._tab_widget.addTab(self._tab_preprocessing, "Preprocessing")
        self._setup_tab_preprocessing()

        self._tab_postprocessing = QtWidgets.QWidget()
        self._tab_widget.addTab(self._tab_postprocessing, "Postprocessing")
        self._setup_tab_postprocessing()

        self._layout.addWidget(self._tab_widget)
        self._widget.setLayout(self._layout)
        self.setCentralWidget(self._widget)

    def _setup_tab_preprocessing(self) -> None:
        container_layout = QGridLayout()
        max_qlineedit_width = 250
        self._tab_preprocessing.setLayout(container_layout)

        # Poisson's ration input
        poisson_ratio_label = QLabel("Poisson's ratio: ")
        container_layout.addWidget(poisson_ratio_label, 0, 0)
        self._poisson_ratio_input = QLineEdit()
        self._poisson_ratio_input.setText("0.3")
        self._poisson_ratio_input.setMaximumWidth(max_qlineedit_width)

        # Young modulus input
        young_modulus_label = QLabel("Young's modulus (N/m2): ")
        container_layout.addWidget(young_modulus_label, 1, 0)
        self._young_modulus_input = QLineEdit()
        self._young_modulus_input.setText("210e3")
        self._young_modulus_input.setMaximumWidth(max_qlineedit_width)

        # Beam length input
        length_label = QLabel("Length (m): ")
        container_layout.addWidget(length_label, 2, 0)
        self._length_input = QLineEdit()
        self._length_input.setText("1")
        self._length_input.setMaximumWidth(max_qlineedit_width)

        # Input for the force exerced on the beam
        force_label = QLabel("Force (N): ")
        container_layout.addWidget(force_label, 3, 0)
        self._force_input = QLineEdit()
        self._force_input.setText("100000")
        self._force_input.setMaximumWidth(max_qlineedit_width)

        # Slider for the number of nodes (between 3 and 9)
        number_of_nodes_label = QLabel("Number of nodes: ")
        container_layout.addWidget(number_of_nodes_label, 4, 0)
        self._number_of_nodes_input = QSlider(orientation=Qt.Orientation.Horizontal)
        self._number_of_nodes_input.setMinimum(3)
        self._number_of_nodes_input.setMaximum(9)
        self._number_of_nodes_input.setValue(5)
        self._number_of_nodes_input.setSingleStep(2)
        self._number_of_nodes_input.setPageStep(2)
        self._number_of_nodes_input.setMaximumWidth(max_qlineedit_width - 50)
        self._number_of_node_label = QLabel(
            f"{self._number_of_nodes_input.value()} nodes"
        )
        self._number_of_nodes_input.valueChanged.connect(self.update_pre_plot)

        container_layout.addWidget(self._poisson_ratio_input, 0, 1, 1, 2)
        container_layout.addWidget(self._young_modulus_input, 1, 1, 1, 2)
        container_layout.addWidget(self._length_input, 2, 1, 1, 2)
        container_layout.addWidget(self._force_input, 3, 1, 1, 2)
        container_layout.addWidget(self._number_of_nodes_input, 4, 1, 1, 1)
        container_layout.addWidget(self._number_of_node_label, 4, 2, 1, 1)
        # PyVista frame in the window
        self._preprocessing_plotter = QtInteractor(theme=MapdlTheme())
        container_layout.addWidget(self._preprocessing_plotter, 0, 4, 6, 50)

        # Generating the plot for the first time.
        self._run_preprocessor()

        # Solve button
        self._solve_button = QPushButton(text="Solve")
        self._solve_button.clicked.connect(self.run_solver)
        container_layout.addWidget(self._solve_button, 5, 0, 1, 3)

    def update_pre_plot(self):
        self._number_of_node_label.setText(
            f"{self._number_of_nodes_input.value()} nodes"
        )
        self._run_preprocessor()

    def _setup_tab_postprocessing(self) -> None:
        container_layout = QtWidgets.QVBoxLayout()
        self._tab_postprocessing.setLayout(container_layout)

        # Add a PyVista frame
        self._postprocessing_plotter = QtInteractor(theme=MapdlTheme())
        container_layout.addWidget(self._postprocessing_plotter)

        self._deflection_label = QLabel("Deflection: ")
        container_layout.addWidget(self._deflection_label)

    def _run_preprocessor(self) -> None:
        try:
            poisson_ratio = float(self._poisson_ratio_input.text())
            young_modulus = float(self._young_modulus_input.text())
            length = float(self._length_input.text())
            force = float(self._force_input.text())
        except Exception:
            msg_box = QMessageBox()
            msg_box.setText("Expecting a number")
            msg_box.exec()
            return

        poisson_ratio = float(self._poisson_ratio_input.text())
        young_modulus = float(self._young_modulus_input.text())
        nnodes = int(self._number_of_nodes_input.value())
        length = float(self._length_input.text())
        force = float(self._force_input.text())

        self.build_model(poisson_ratio, young_modulus, nnodes, length, force)

        # Get the pv.Plotter object from mapdl.eplot function
        # to plot in the window
        preprocessing_plotter = self._mapdl.eplot(
            show_node_numbering=True, show_edges=True, cpos="xy", return_plotter=True
        )

        self._preprocessing_plotter.GetRenderWindow().AddRenderer(
            preprocessing_plotter.scene.renderer
        )

        self._mapdl.finish()

    def build_model(self, poisson_ratio, young_modulus, nnodes, length, force):
        self._mapdl.clear()
        self._mapdl.verify()
        self._mapdl.prep7()
        self._mapdl.antype("STATIC")
        # create element type
        self._mapdl.et(1, "BEAM188")

        # Create material
        self._mapdl.mp("PRXY", 1, poisson_ratio)
        self._mapdl.mp("EX", 1, young_modulus)
        self._mapdl.sectype(1, "BEAM", "RECT")
        self._mapdl.secdata("10", "10")

        # Create the nodes
        for node_num in range(1, nnodes + 1):
            self._mapdl.n(node_num, (node_num - 1) * length / (nnodes - 1), 0, 0)

        # Create the elements
        for elem_num in range(1, nnodes):
            self._mapdl.e(elem_num, elem_num + 1)

        # Fix beam ends
        self._mapdl.d(1, lab="ALL")
        self._mapdl.d(nnodes, lab="ALL")

        #  Apply the force to the node in the middle
        self._mapdl.f(nnodes // 2 + 1, lab="FY", value=force)

    def run_solver(self) -> None:
        # solve
        self._mapdl.slashsolu()
        self._mapdl.solve()
        self._mapdl.finish()

        # run postprocessing
        self._mapdl.post1()
        self._mapdl.graphics("power")
        self._mapdl.eshape(1)
        self._mapdl.rgb("index", 100, 100, 100, 0)
        self._mapdl.rgb("index", 0, 0, 0, 15)

        mapdl.upcoord(2)

        nodal_disp_plotter = self._mapdl.post_processing.plot_nodal_displacement(
            "norm", show_node_numbering=True, cpos="xy", return_plotter=True
        )
        self._postprocessing_plotter.GetRenderWindow().AddRenderer(
            nodal_disp_plotter.scene.renderer
        )

        nnodes = len(mapdl.mesh.nodes)

        mid_node_uy = mapdl.get_value(
            entity="NODE", entnum=nnodes // 2 + 1, item1="u", it1num="y"
        )

        self._deflection_label.setText(f"Deflection: {mid_node_uy:.6f}")

    def closeEvent(self, event) -> None:
        self._preprocessing_plotter.close()
        self._postprocessing_plotter.close()
        event.accept()  # let the window close


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mapdl = launch_mapdl()
    window = MainWindow(mapdl)
    window.show()
    sys.exit(app.exec())
