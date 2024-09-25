from gui import *
from MeshObject import *
from Pipeline import *

if __name__ == "__main__":
    pipeline_parameters = {
        "subdivision": {
            "threshold": 5610
        }
    }
    
    app = QtWidgets.QApplication(sys.argv)
    mesh = MeshObject()
    pipeline = Pipeline(pipeline_parameters=pipeline_parameters)
    gui = MainWindow(mesh, pipeline)
    app.aboutToQuit.connect(gui.onClose)
    app.exec()