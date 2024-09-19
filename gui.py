import sys
from PySide6 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter, Mesh, Text2D, printc
import vedo
import os

# code based on example from vedo documentation on QT integration
class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.create_window()
        self.setAcceptDrops(True)

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QStackedLayout()
        
        # create vedo renderer and add objects and callbacks
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.plt = Plotter(qt_widget=self.vtkWidget)
        self.cbid = self.plt.add_callback("key press", self.onKeypress)
        self.init_text = Text2D("Drag and drop a 3D mesh file to visualize it!", pos="center")

        self.layout.addWidget(self.vtkWidget)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        self.plt.show(self.init_text)
        self.show()

    def load_mesh_from_path(self, url):
        vedo_mesh = vedo.Mesh(url).lw(1).color("grey")
        return vedo_mesh

    def add_then_display(self, mesh):
        self.init_text.pos("top-left")
        self.plt.clear()
        self.plt.show(mesh) # build the vedo rendering

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

        mesh = self.load_mesh_from_path(file_path)
        self.add_then_display(mesh)

        event.acceptProposedAction()

    def create_window(self):
        self.resize(1366, 768)

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keypress, c='b')
        if evt.keypress=='q':
            self.plt.close()
            self.vtkWidget.close()
            exit()

    def onClose(self):
        self.vtkWidget.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose)
    app.exec()