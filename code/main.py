from gui import MainWindow
from PySide6.QtWidgets import QApplication
from MeshObject import MeshObject
from Pipeline import Pipeline
import sys
from shape_retrieval import ShapeRetrieval

if __name__ == "__main__":
    pipeline_parameters = {
        "subdivision": {
            "threshold": 5610
        }
    }
    retrieval_parameters = {
        "k": 5,
        "num_bins": 75,
        "feature_weights": [0.5, 0.5, 0.2, 0.7, 0.4, 0.7, 0.2, 0.9, 0.9, 0.5, 0.7],
        "are_vectors_normalized": True,
        "distance_approach": "ann",
        "return_query": True
    }
    
    app = QApplication(sys.argv)
    mesh = MeshObject()
    pipeline = Pipeline(pipeline_parameters=pipeline_parameters)
    retriever = ShapeRetrieval(**retrieval_parameters)
    gui = MainWindow(mesh, pipeline, retriever)
    app.aboutToQuit.connect(gui.onClose)
    app.exec()