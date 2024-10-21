from gui import *
from MeshObject import *
from Pipeline import *
import mesh_properties

if __name__ == "__main__":
    pipeline_parameters = {
        "subdivision": {
            "sampling_type": "centroid",
            "threshold": 5610
        }
    }
    
    app = QtWidgets.QApplication(sys.argv)
    mesh = MeshObject()
    pipeline = Pipeline(pipeline_parameters=pipeline_parameters)
    gui = MainWindow(mesh, pipeline)
    app.aboutToQuit.connect(gui.onClose)
    app.exec()