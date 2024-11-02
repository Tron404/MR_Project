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
from shapre_retrieval import *
from tsne_plot import *

# code based on example from vedo documentation on QT integration
class RenderGUI(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.render_layout = QtWidgets.QStackedLayout()
        self.render_buttons_layout = QtWidgets.QHBoxLayout()
        self.parent = parent

        self.setAcceptDrops(True)
        self.setLayout(self.render_layout)

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
        self.render_plot_stacked_widget = QtWidgets.QStackedWidget()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.plt = Plotter(qt_widget=self.vtkWidget)
        self.cbid = self.plt.add_callback("key press", self.onKeypress)
        self.init_text = Text2D("Drag and drop a 3D mesh file to visualize it!", pos="center")
        self.vertex_template = "Vertices={}"
        self.face_template = "Faces={}"
        self.vertex_text = Text2D(self.vertex_template, pos="top-right")
        self.face_text = Text2D(self.face_template, pos="center-right")
        self.face_text.SetPosition((0.994,0.9))
        self.render_layout.addWidget(self.vtkWidget)

        self.render_plot_stacked_widget.addWidget(self.vtkWidget)

        ##### change between tsne and 3d render
        self.tsne_3d_render_btn = QtWidgets.QPushButton("Change to\nT-SNE Plot")
        self.tsne_3d_render_btn.pressed.connect(self.change_render)
        self.render_buttons_layout.addWidget(self.tsne_3d_render_btn)

        ##### tsne representation
        
        self.tsne_plot = TSNEPlot(figsize=(12,5), dpi=100) 
        self.tsne_fig = FigureCanvasQTAgg(self.tsne_plot.plot.figure)
        self.tsne_fig.draw()
        self.tsne_plot.point_hovered.connect(self.load_mesh_from_path)

        self.render_plot_stacked_widget.addWidget(self.tsne_fig)

        self.render_layout.addWidget(self.render_plot_stacked_widget)

        self.plt.show(self.init_text)
        self.plt.show(self.vertex_text)
        self.plt.show(self.face_text)

    def change_render(self):
        if self.render_plot_stacked_widget.currentIndex() == 0: # vtk render:
            self.tsne_3d_render_btn.setText("Change to\n3D Render")
            self.render_plot_stacked_widget.setCurrentIndex(1)
            self.tsne_fig.draw()
            self.tsne_plot.reset()
        elif self.render_plot_stacked_widget.currentIndex() == 1: # tsne
            self.tsne_3d_render_btn.setText("Change to\nT-SNE Plot")
            self.render_plot_stacked_widget.setCurrentIndex(0)

    ###### render funcs
    def _change_shading(self, interpolation_mode):
        # 0=flat; 1=gouraud; 2=phong
        self.parent.mesh_obj = self.parent.mesh_obj.compute_normals(cells=False, points=True)
        self.parent.mesh_obj.properties.SetInterpolation(interpolation_mode)
        self.add_then_display()

    def change_shading_to_flat(self):
        self._change_shading(0)

    def change_shading_to_gouraud(self):
        self._change_shading(1)

    def change_shading_to_phong(self):
        self._change_shading(2)

    def change_camera(self):
        self.plt.reset_camera()
        self.plt.fly_to([0,0])
        self.add_then_display()

    def load_mesh_from_path(self, url):
        self.plt.reset_camera()
        class_name, file_name = url.split("/")[-2:]
        self.parent.mesh_obj = MeshObject(url, class_type=class_name, name=file_name.removesuffix(".obj"))
        self.plt.fly_to(self.parent.mesh_obj.center_of_mass())
        if self.render_plot_stacked_widget.currentIndex() == 1: # tsne
            self.change_render()
        self.add_then_display()

    def save_screenshot(self):
        self.init_text.off()
        self.face_text.off()
        self.vertex_text.off()
        path = f"screenshots/{self.parent.mesh_obj.name}"
        self.plt.screenshot(path, scale=5)
        self.init_text.on()
        self.face_text.on()
        self.vertex_text.on()

    def add_then_display(self):
        self.init_text.pos("top-left")
        self.vertex_text = self.vertex_text.text(self.vertex_template.format(self.parent.mesh_obj.n_vertices))
        self.face_text = self.face_text.text(self.face_template.format(self.parent.mesh_obj.n_faces))
        self.plt.clear()
        self.plt.show(self.parent.mesh_obj) # build the vedo rendering

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.close()
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