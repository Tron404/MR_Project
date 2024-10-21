import sys
from PySide6 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter, Mesh, Text2D, printc
import vedo
from MeshObject import *
import os
from Pipeline import *

# code based on example from vedo documentation on QT integration
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mesh_obj: MeshObject, pipeline: Pipeline, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.create_window()
        self.setAcceptDrops(True)

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        render_layout = QtWidgets.QStackedLayout()
        self.mesh_obj = mesh_obj
        self.pipeline = pipeline

        self.layout.addLayout(button_layout)
        self.layout.addLayout(render_layout)

        ##### render buttons
        btn_save = QtWidgets.QPushButton("Screenshot")
        btn_save.pressed.connect(self.save_screenshot)

        btn_shader = QtWidgets.QPushButton("Shading", parent=self)
        shader_menu = QtWidgets.QMenu(self)
        shader_menu.addAction("Flat").triggered.connect(self.change_shading_to_flat)
        shader_menu.addAction("Gouraud").triggered.connect(self.change_shading_to_gouraud)
        shader_menu.addAction("Phong").triggered.connect(self.change_shading_to_phong)
        btn_shader.setMenu(shader_menu)

        ##### mesh transformation buttons 
        btn1 = QtWidgets.QPushButton("Normalize shape")
        btn1.pressed.connect(self.normalize)

        btn_menu = QtWidgets.QPushButton("Normalization\nOperations", parent=self)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Decimation").triggered.connect(partial(self.resample_shape, sampling_type="decimation"))

        subdivision_types = ["centroid", "linear","loop", "butterfly", "adaptive"]
        subdivision_menu = menu.addMenu("Subdivision")
        for sub_type in subdivision_types:
            subdivision_menu.addAction(sub_type.title()).triggered.connect(partial(self.resample_shape, sampling_type=sub_type))
        
        menu.addAction("Barycenter translation").triggered.connect(self.translation_to_barycenter)
        menu.addAction("Principal axis alignment").triggered.connect(self.align_to_axes)
        menu.addAction("Flip shape").triggered.connect(self.flip_mass)
        menu.addAction("Scale shape").triggered.connect(self.scale_mesh)
        btn_menu.setMenu(menu)

        btn1.setFixedSize(QtCore.QSize(250,50))
        btn_save.setFixedSize(QtCore.QSize(250,50))
        btn_menu.setFixedSize(QtCore.QSize(250,50))
        btn_shader.setFixedSize(QtCore.QSize(250,50))

        button_layout.addWidget(btn1)
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_menu)
        button_layout.addWidget(btn_shader)

        # create vedo renderer and add objects and callbacks
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.plt = Plotter(qt_widget=self.vtkWidget)
        self.cbid = self.plt.add_callback("key press", self.onKeypress)
        self.init_text = Text2D("Drag and drop a 3D mesh file to visualize it!", pos="center")
        self.vertex_template = "Vertices={}"
        self.face_template = "Faces={}"
        self.vertex_text = Text2D(self.vertex_template, pos="top-right")
        self.face_text = Text2D(self.face_template, pos="center-right")
        self.face_text.SetPosition((0.994,0.9))
        render_layout.addWidget(self.vtkWidget)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        self.plt.show(self.init_text)
        self.plt.show(self.vertex_text)
        self.plt.show(self.face_text)
        self.show()

    ##### mesh transformation funcs
    def _apply_transformation_on_shape(self, transformation, **kwargs):
        move_camera = kwargs.pop("move_camera", False)
        self.old_mesh = self.mesh_obj
        self.mesh_obj = transformation(self.mesh_obj, **kwargs)
        if move_camera:
            self.plt.fly_to([0,0])
        self.add_then_display()

    def normalize(self):
        self._apply_transformation_on_shape(self.pipeline.normalize_shape, move_camera=True)

    def resample_shape(self, sampling_type="centroid"):
        self._apply_transformation_on_shape(self.pipeline._resample_shape, sampling_type=sampling_type)

    def translation_to_barycenter(self):
        self._apply_transformation_on_shape(self.pipeline._translate_to_barycenter, move_camera=True)
    
    ### create custom decorator for buttons?
    def align_to_axes(self):
        self._apply_transformation_on_shape(self.pipeline._align_to_principal_axes)

    def flip_mass(self):
        self._apply_transformation_on_shape(self.pipeline._flip_mass)

    def scale_mesh(self):
        self._apply_transformation_on_shape(self.pipeline._scale_mesh)

    ###### render funcs
    def _change_shading(self, interpolation_mode):
        # 0=flat; 1=gouraud; 2=phong
        self.mesh_obj = self.mesh_obj.compute_normals(cells=False, points=True)
        self.mesh_obj.properties.SetInterpolation(interpolation_mode)
        self.add_then_display()

    def change_shading_to_flat(self):
        self._change_shading(0)

    def change_shading_to_gouraud(self):
        self._change_shading(1)

    def change_shading_to_phong(self):
        self._change_shading(2)

    def load_mesh_from_path(self, url):
        class_name, file_name = url.split("/")[-2:]
        self.mesh_obj = MeshObject(url, class_type=class_name, name=file_name)
        self.plt.fly_to(self.mesh_obj.center_of_mass())

    def save_screenshot(self):
        self.init_text.off()
        self.face_text.off()
        self.vertex_text.off()
        path = f"screenshots/{self.mesh_obj.name}"
        self.plt.screenshot(path, scale=5)
        self.init_text.on()
        self.face_text.on()
        self.vertex_text.on()

    def add_then_display(self):
        self.init_text.pos("top-left")
        self.vertex_text = self.vertex_text.text(self.vertex_template.format(self.mesh_obj.n_vertices))
        self.face_text = self.face_text.text(self.face_template.format(self.mesh_obj.n_faces))
        self.plt.clear()
        self.plt.show(self.mesh_obj) # build the vedo rendering

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

    def create_window(self):
        self.resize(1366, 768)

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.close()
            self.vtkWidget.close()
            exit()
        if evt.keypress=="Ctrl+z":
            self.mesh = self.old_mesh
            self.add_then_display()
        
    def onClose(self):
        self.vtkWidget.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(MeshObject())
    app.aboutToQuit.connect(window.onClose)
    app.exec()