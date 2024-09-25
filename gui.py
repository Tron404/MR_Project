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

        btn1 = QtWidgets.QPushButton("Normalize shape")
        btn1.pressed.connect(self.process)
        button_layout.addWidget(btn1)
        
        # create vedo renderer and add objects and callbacks
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.plt = Plotter(qt_widget=self.vtkWidget)
        self.cbid = self.plt.add_callback("key press", self.onKeypress)
        self.init_text = Text2D("Drag and drop a 3D mesh file to visualize it!", pos="center")
        render_layout.addWidget(self.vtkWidget)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        self.plt.show(self.init_text)
        self.show()

    def process(self):
        self.mesh_obj = self.pipeline.normalize_shape(self.mesh_obj)
        self.plt.clear()
        self.plt.show(self.mesh_obj)
        self.plt.fly_to([0,0])

    def load_mesh_from_path(self, url):
        self.mesh_obj = MeshObject(url)
        self.plt.fly_to(self.mesh_obj.center_of_mass())

    def add_then_display(self):
        self.init_text.pos("top-left")
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
        print(self.mesh_obj.class_type)
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.close()
            self.vtkWidget.close()
            exit()

    def onClose(self):
        self.vtkWidget.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(MeshObject())
    app.aboutToQuit.connect(window.onClose)
    app.exec()