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
class RetrievalGUI(QtWidgets.QFrame):
    def __init__(self, mesh_obj: MeshObject, pipeline: Pipeline, parent=None):
        super().__init__()

        self.k = 5 # number of retrieved shapes
        self.retriever = ShapeRetrieval()

        self.retrieveal_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.retrieveal_layout)
        self.parent = parent

        ##### retrieval buttons
        retrieve_button = QtWidgets.QPushButton("Retrieve similar shapes")
        retrieve_button.pressed.connect(self.retrieve_shapes)
        retrieve_button.setFixedSize(QtCore.QSize(250,50))
        self.retrieveal_layout.addWidget(retrieve_button)

        # ##### retrieval rendering
        self.vtkWidget_retrieval = QVTKRenderWindowInteractor(self)
        self.plt_retrieval = Plotter(qt_widget=self.vtkWidget_retrieval, shape=(1,self.k), sharecam=False)
        self.plt_retrieval.add_callback("key press", self.onKeypress)
        self.text_retrieval = Text2D("", pos="center")
        for idx in range(self.k):
            self.plt_retrieval.at(idx)
            self.plt_retrieval.show(self.text_retrieval)
        self.retrieveal_layout.addWidget(self.vtkWidget_retrieval)
        self.vtkWidget_retrieval.hide()

        self.show()

    ##### retrieval funcs
    def retrieve_shapes(self):
        retrieved_df = self.retriever.find_similar_shapes(self.parent.mesh_obj.name).to_numpy()
        for idx_plot, obj in zip(range(self.k), retrieved_df):
            # 0=name; 1=class; 2=features; 3=dist
            self.plt_retrieval.at(idx_plot)
            self.plt_retrieval.clear(deep=True)
            path = os.path.join(self.retriever.PATH, obj[1], obj[0].removesuffix(".pickle") + ".obj")
            print(path)
            text = Text2D(f"class={obj[1]}\ndist={round(obj[3],3)}")
            mesh = MeshObject(path, visualize=True)
            self.plt_retrieval += [mesh, text]
        self.vtkWidget_retrieval.show()
        self.plt_retrieval.show()

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt_retrieval.close()
            self.vtkWidget_retrieval.close()
            exit()
