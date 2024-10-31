import sys
import matplotlib
from PySide6 import QtCore, QtWidgets, QtGui
import vedo
from MeshObject import *
import os
from Pipeline import *

# code based on example from vedo documentation on QT integration
class TransformationGUI(QtCore.QObject):
    mesh_transformed = QtCore.Signal(object)
    def __init__(self, mesh_obj: MeshObject, pipeline: Pipeline, parent=None):
        super().__init__(parent)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.mesh_obj = mesh_obj
        self.pipeline = pipeline
        self.parent = parent

        ###### mesh transformation buttons 
        self.btn1 = QtWidgets.QPushButton("Normalize shape")
        self.btn1.pressed.connect(self.normalize)

        self.btn_menu = QtWidgets.QPushButton("Normalization\nOperations")
        menu = QtWidgets.QMenu(self.btn_menu)
        menu.addAction("Decimation").triggered.connect(partial(self.resample_shape, sampling_type="decimation"))

        subdivision_types = ["centroid", "linear","loop", "butterfly", "adaptive"]
        subdivision_menu = menu.addMenu("Subdivision")
        for sub_type in subdivision_types:
            subdivision_menu.addAction(sub_type.title()).triggered.connect(partial(self.resample_shape, sampling_type=sub_type))
        
        menu.addAction("Barycenter translation").triggered.connect(self.translation_to_barycenter)
        menu.addAction("Principal axis alignment").triggered.connect(self.align_to_axes)
        menu.addAction("Flip shape").triggered.connect(self.flip_mass)
        menu.addAction("Scale shape").triggered.connect(self.scale_mesh)
        self.btn_menu.setMenu(menu)

        self.btn1.setFixedSize(QtCore.QSize(250,50))
        self.btn_menu.setFixedSize(QtCore.QSize(250,50))

        self.button_layout.addWidget(self.btn1)
        self.button_layout.addWidget(self.btn_menu)

    ##### mesh transformation funcs
    def _apply_transformation_on_shape(self, transformation, **kwargs):
        move_camera = kwargs.pop("move_camera", False)
        self.parent.mesh_obj = transformation(self.parent.mesh_obj, **kwargs)
        self.mesh_transformed.emit(move_camera)
        
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