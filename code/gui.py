import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PySide6 import QtWidgets
from MeshObject import MeshObject
from Pipeline import Pipeline
from shape_retrieval import ShapeRetrieval

from render_sep_gui import RenderGUI
from trans_mesh_gui import TransformationGUI
from retrieval_sep_gui import RetrievalGUI
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter
from PySide6 import QtCore, QtWidgets, QtGui


# code based on example from vedo documentation on QT integration
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mesh_obj: MeshObject, pipeline: Pipeline, retriever: ShapeRetrieval, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()
        self.layout_all = QtWidgets.QVBoxLayout()
        self.button_layout_all = QtWidgets.QHBoxLayout()
        self.k = retriever.k
        self.num_bins = retriever.num_bins
        self.feature_weights = retriever.feature_weights

        k = self.k + 1
        size = 1/k
        custom_shape = [dict(bottomleft=(0.0,size), topright=(1.00,1.00), bg='wheat', bg2=None )]# ren0
        for idx in range(k):
            if idx == 0:
                bg1= "wheat"
                bg2 = None
            else:
                bg1= "white"
                bg2 = None
            c = dict(bottomleft=(size*idx ,0.0), topright=(size*(idx+1),size), bg=bg1, bg2=bg2, axes=3)
            custom_shape += [c]

        self.vtk = QVTKRenderWindowInteractor()
        self.renderers = Plotter(qt_widget=self.vtk, axes=0, shape=custom_shape, sharecam=False, size=(2000,2000))

        self.create_window()
        self.mesh_obj = mesh_obj
        self.render_gui = RenderGUI(self, plot_idx=0)
        self.retrieval_gui = RetrievalGUI(retriever, self, plot_idx=list(range(1,k+1)))
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