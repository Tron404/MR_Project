from gui import *
from MeshObject import *
from Pipeline import *
from shapre_retrieval import *

if __name__ == "__main__":
    pipeline_parameters = {
        "subdivision": {
            "sampling_type": "centroid",
            "threshold": 5610
        }
    }
    retrieval_parameters = {
        "k": 5,
        "num_bins": 150,
        "feature_weights": np.asarray([0.5, 0.5, 0.2, 0.7, 0.4, 0.7, 0.2, 0.9, 0.9, 0.5, 0.7], dtype=np.float32),
        "are_vectors_normalized": True,
        "distance_approach": "ann"
    }
    
    app = QtWidgets.QApplication(sys.argv)
    mesh = MeshObject()
    pipeline = Pipeline(pipeline_parameters=pipeline_parameters)
    retriever = ShapeRetrieval(**retrieval_parameters)
    gui = MainWindow(mesh, pipeline, retriever)
    app.aboutToQuit.connect(gui.onClose)
    app.exec()