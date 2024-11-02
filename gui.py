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

from render_sep_gui import *
from trans_mesh_gui import *
from retrieval_sep_gui import *

# code based on example from vedo documentation on QT integration
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mesh_obj: MeshObject, pipeline: Pipeline, retriever: ShapeRetrieval, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()
        self.layout_all = QtWidgets.QVBoxLayout()
        self.button_layout_all = QtWidgets.QHBoxLayout()
        
        self.create_window()
        self.mesh_obj = mesh_obj
        self.pipeline = pipeline
        self.render_gui = RenderGUI(self)
        self.retrieval_gui = RetrievalGUI(retriever, self)
        self.trans_gui = TransformationGUI(pipeline, self)

        self.button_layout_all.addLayout(self.trans_gui.button_layout)
        self.button_layout_all.addLayout(self.render_gui.render_buttons_layout)
        self.layout_all.addLayout(self.button_layout_all)

        # connect transformations in TransformationGUI to camera changes in RenderGUI
        self.trans_gui.mesh_transformed.connect(self.render_gui.change_camera)

        self.layout_all.addWidget(self.render_gui)
        self.layout_all.addWidget(self.retrieval_gui)
    
        self.frame.setLayout(self.layout_all)
        self.setCentralWidget(self.frame)

        self.show()

    def onClose(self):
        self.close()

    def create_window(self):
        self.resize(1366, 1200)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(MeshObject(), Pipeline())
    app.aboutToQuit.connect(window.onClose)
    app.exec()