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

# code based on example from vedo documentation on QT integration
class RetrievalGUI(QtWidgets.QFrame):
    def __init__(self, retriever: ShapeRetrieval, parent=None, plot_idx=0):
        super().__init__()

        # self.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")

        self.retriever = retriever
        # self.k = self.retriever.k # number of retrieved shapes
        # self.return_query = self.retriever.return_query
        self.k = 6 # number of retrieved shapes
        self.return_query = True

        self.retrieveal_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.retrieveal_layout)
        self.parent = parent

        self.plt_retrieval = self.parent.renderers
        self.plot_idx = plot_idx

        ##### retrieval buttons
        retrieve_button = QtWidgets.QPushButton("Retrieve similar shapes")
        retrieve_button.pressed.connect(self.retrieve_shapes)
        retrieve_button.setFixedSize(QtCore.QSize(250,50))
        self.retrieveal_layout.addWidget(retrieve_button)

        # ##### retrieval rendering
        for idx in self.plot_idx:
            self.text_retrieval = Text2D("", pos="center")
            self.plt_retrieval.at(idx)
            self.plt_retrieval.show(self.text_retrieval)

        self.show()

    ##### retrieval funcs
    def retrieve_shapes(self):
        retrieved_dict = self.retriever.find_similar_shapes(self.parent.mesh_obj.name, self.parent.mesh_obj.class_type, return_query=self.return_query)
        for idx_plot, obj in zip(self.plot_idx, retrieved_dict): # include the query item as well
            self.plt_retrieval.at(idx_plot)
            self.plt_retrieval.clear(deep=True)
            path = os.path.join(self.retriever.PATH, obj["class_type"], obj["obj_name"] + ".obj")
            text_str = f"class={obj['class_type']}\nname={obj['obj_name']}\ndist={round(obj['distance'],3)}"
            if self.return_query and idx_plot == 0: # == query item
                text_str = "(query)\n" + text_str
            text = Text2D(text_str, s=0.75)
            mesh = MeshObject(path, visualize=True)
            self.plt_retrieval.at(idx_plot).zoom(4)
            self.plt_retrieval += [mesh, text]
            self.plt_retrieval.show()

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.close()
            self.vtkWidget.close()
            exit()
        if evt.keypress=="Ctrl+z":
            self.mesh = self.old_mesh
            self.add_then_display()
        if evt.keypress=="+":
            self.plt.add_global_axes(axtype=(self.current_axis+1)%13)
        if evt.keypress=="-":
            self.plt.add_global_axes(axtype=(self.current_axis-1)%13)