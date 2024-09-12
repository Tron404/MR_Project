import vedo
import numpy as np
from vedo import show, Plotter, Mesh
from functools import partial

class MeshObject:
    def __init__(self, path_obj, visualize=False) -> None:
        self.vedo_mesh: Mesh = vedo.load(path_obj)
        self.vedo_mesh = self.vedo_mesh.color("grey").lw(1)
        self.visualize = visualize

        if self.visualize:
            self.create_visualisation()

    def compute_stats(self):
        cell_t = set([cell_type[len(cell)] for cell in obj_mesh.cells])
        stats[obj] = {
            "class": class_type,
            "nfaces":obj_mesh.ncells,
            "nvertices":obj_mesh.nvertices,
            "types_of_faces": cell_t,
            "3D_bounding_box": obj_mesh.bounds() # more processing?
        }

    def create_visualisation(self):
        self.plotter = Plotter()
        self.plotter += [self.vedo_mesh]

    def show(self):
        if self.visualize:
            show(self.vedo_mesh, axes=1).close()
        else:
            print("Visualization not initialized")