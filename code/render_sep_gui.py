import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PySide6 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from vedo import Plotter, Mesh, Text2D, printc
import vedo
from MeshObject import *
import os
from Pipeline import *
from shape_retrieval import *
from tsne_plot import *
from math import ceil
from vtk import vtkRenderer

# code based on example from vedo documentation on QT integration
class RenderGUI(QtWidgets.QFrame):
    class_checked = QtCore.Signal((bool, str))
    def __init__(self, parent=None, plot_idx=0):
        super().__init__()
        self.render_layout = QtWidgets.QVBoxLayout()
        self.render_buttons_layout = QtWidgets.QHBoxLayout()
        self.setParent(parent)

        self.setAcceptDrops(True)
        self.setLayout(self.render_layout)
        self.plot_idx = plot_idx

        ##### render buttons
        btn_save = QtWidgets.QPushButton("Screenshot", self)
        btn_save.pressed.connect(self.save_screenshot)

        btn_shader = QtWidgets.QPushButton("Shading", self)
        shader_menu = QtWidgets.QMenu(self)
        shader_menu.addAction("Flat").triggered.connect(self.change_shading_to_flat)
        shader_menu.addAction("Gouraud").triggered.connect(self.change_shading_to_gouraud)
        shader_menu.addAction("Phong").triggered.connect(self.change_shading_to_phong)
        btn_shader.setMenu(shader_menu)

        btn_save.setFixedSize(QtCore.QSize(250,50))
        btn_shader.setFixedSize(QtCore.QSize(250,50))

        self.render_buttons_layout.addWidget(btn_save)
        self.render_buttons_layout.addWidget(btn_shader)

        ##### create vedo renderer and add objects and callbacks
        self.render_plot_stacked_widget = QtWidgets.QStackedWidget(self)
        
        self.plt = self.parent().renderers

        self.init_text = Text2D("Drag and drop a 3D mesh file to visualize it!", pos="center")
        self.info_text_template = "Vertices={}\nFaces={}\nClass={}\nName={}"
        self.info_text = Text2D(self.info_text_template, pos="top-right")
        self.info_text.SetPosition((0.994,0.9))

        ##### change between tsne and 3d render
        self.tsne_3d_render_btn = QtWidgets.QPushButton("Change to\nT-SNE Plot")
        self.tsne_3d_render_btn.pressed.connect(self.change_render)
        self.render_buttons_layout.addWidget(self.tsne_3d_render_btn)

        ##### tsne representation
        self.tsne_plot = TSNEPlot(figsize=(12,5), dpi=100, num_bins=self.parent().num_bins, feature_weights=self.parent().feature_weights) 
        self.class_checked.connect(self.tsne_plot.update_tsne_plot)
        self.tsne_fig = FigureCanvasQTAgg(self.tsne_plot.plot.figure)
        self.tsne_fig.draw()
        self.tsne_plot.point_hovered.connect(self.load_mesh_from_path)
        self.render_plot_stacked_widget.addWidget(self.parent().vtk)
        self.render_plot_stacked_widget.addWidget(self.tsne_fig)
        # ##### tsne checkbox options
        self.class_checkboxes = []
        self.checked_boxes = 0
        self.checkbox_layout = QtWidgets.QGridLayout()
        self.checkbox_widget = QtWidgets.QWidget()
        class_types = self.tsne_plot.class_types
        n_cols = 6

        idx_row = 0
        idx_col = 0
        for idx in range(len(class_types)):
            widget = QtWidgets.QCheckBox(text=class_types[idx], parent=self.checkbox_widget)
            widget.stateChanged.connect(self.checkbox_update)
            self.class_checkboxes += [widget]
            self.checkbox_layout.addWidget(widget, idx_row, idx_col)

            idx_col = (idx_col+1) % n_cols
            idx_row += int(idx_col % n_cols == 0)

        self.checkbox_widget.setLayout(self.checkbox_layout)
        self.checkbox_widget.setFixedHeight(200)
        self.checkbox_widget.hide()
        self.render_layout.addWidget(self.checkbox_widget)
        self.render_layout.addWidget(self.render_plot_stacked_widget)

        self.plt.at(self.plot_idx).show(self.init_text)
        self.plt.at(self.plot_idx).show(self.info_text)

    def block_unblock_unchecked_checkboxes(self, checkable=True):
        for checkbox in self.class_checkboxes:
            if not checkbox.isChecked():
                checkbox.setCheckable(checkable)

    def checkbox_update(self):
        if self.sender().isChecked() and self.checked_boxes <= 12:
            self.checked_boxes += 1
            self.class_checked.emit(True, self.sender().text())
        else:
            self.checked_boxes -= 1
            self.class_checked.emit(False, self.sender().text())
            if self.checked_boxes + 1 <= 12:
                self.block_unblock_unchecked_checkboxes(checkable=True)
        self.tsne_fig.figure = self.tsne_plot.plot.figure
        self.tsne_fig.draw()
                
        if self.checked_boxes > 12:
            self.sender().setChecked(False)
            self.block_unblock_unchecked_checkboxes(checkable=False)

    def change_render(self):
        if self.render_plot_stacked_widget.currentIndex() == 0: # vtk render:
            self.checkbox_widget.show()
            self.tsne_3d_render_btn.setText("Change to\n3D Render")
            self.render_plot_stacked_widget.setCurrentIndex(1)
            self.tsne_fig.draw()
            self.tsne_plot.reset()
        elif self.render_plot_stacked_widget.currentIndex() == 1: # tsne
            self.checkbox_widget.hide()
            self.tsne_3d_render_btn.setText("Change to\nT-SNE Plot")
            self.render_plot_stacked_widget.setCurrentIndex(0)

    ###### render funcs
    def _change_shading(self, interpolation_mode):
        # 0=flat; 1=gouraud; 2=phong
        self.parent().mesh_obj = self.parent().mesh_obj.compute_normals(cells=False, points=True)
        self.parent().mesh_obj.properties.SetInterpolation(interpolation_mode)
        self.add_then_display()

    def change_shading_to_flat(self):
        self._change_shading(0)

    def change_shading_to_gouraud(self):
        self._change_shading(1)

    def change_shading_to_phong(self):
        self._change_shading(2)

    def change_camera(self):
        self.add_then_display()
        self.plt.at(self.plot_idx).reset_camera()
        self.plt.at(self.plot_idx).zoom(4)
        self.plt.at(self.plot_idx).fly_to([0,0])

    def load_mesh_from_path(self, url):
        self.plt.at(self.plot_idx).reset_camera()
        class_name, file_name = url.split("/")[-2:]
        self.parent().mesh_obj = MeshObject(url, class_type=class_name, name=file_name.removesuffix(".obj"))
        self.plt.at(self.plot_idx).fly_to(self.parent().mesh_obj.center_of_mass())
        if self.render_plot_stacked_widget.currentIndex() == 1: # tsne
            self.change_render()
        self.add_then_display()

    def save_screenshot(self):
        self.init_text.off()
        self.info_text.off()
        path = f"screenshots/{self.parent().mesh_obj.name}"
        self.plt.screenshot(path, scale=5)
        self.init_text.on()
        self.info_text.on()

    def add_then_display(self):
        self.plt.at(self.plot_idx).clear()
        self.init_text.pos("top-left")
        n_vertex = self.parent().mesh_obj.n_vertices
        n_face = self.parent().mesh_obj.n_faces
        class_type = self.parent().mesh_obj.class_type
        name = self.parent().mesh_obj.name
        self.info_text = self.info_text.text(self.info_text_template.format(n_vertex, n_face, class_type, name))
        self.plt.at(self.plot_idx).show(self.parent().mesh_obj) # build the vedo rendering

    def onKeypress(self, evt):
        self.vtkWidget.setFocus()

        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.at(self.plot_idx).close()
            self.vtkWidget.close()
            exit()
        if evt.keypress=="Ctrl+z":
            self.mesh = self.old_mesh
            self.add_then_display()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls(): # accept drag event iff it is a file with a path
            event.acceptProposedAction()  
        else:
            event.ignore()

    # event for when a file is dropped
    def dropEvent(self, event: QtGui.QDropEvent):
        mime_data = event.mimeData().urls()

        if len(mime_data) > 1:
            event.ignore()
            return

        file_path = mime_data[0].toLocalFile()  # local file path
        self.load_mesh_from_path(file_path)
        self.add_then_display()

        event.acceptProposedAction()
        
    def onClose(self):
        self.vtkWidget.close()