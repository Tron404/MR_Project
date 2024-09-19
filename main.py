from g import *
from MeshObject import *
from processing_functions import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mesh = MeshObject()
    gui = MainWindow(mesh)
    app.aboutToQuit.connect(gui.onClose)
    app.exec()