import vedo
import numpy as np
from vedo import show, Plotter, Mesh

class MeshObject:
    def __init__(self, path_obj=None, visualize=False) -> None:
        if not path_obj:
            return
        
        self.load_mesh(path_obj)
        self.visualize = visualize
        
        if self.visualize:
            self.create_visualisation()

    def load_mesh(self, path_obj):
        self.vedo_mesh: Mesh = vedo.load(path_obj)
        self.vedo_mesh = self.vedo_mesh.color("grey").lw(1)

        # obj stats
        self.class_type, self.name = path_obj.split("/")[-2:] # assume path is of form: ../ShapeFolder/Type/obj
        self.face_type = self._determine_face_type()

        return self
        
    @property
    def coordinates(self):
        return self.vedo_mesh.coordinates

    @property
    def n_faces(self):
        return self.vedo_mesh.ncells

    @property
    def n_vertices(self):
        return self.vedo_mesh.nvertices
    
    @property
    def bounding_box(self):
        return self.vedo_mesh.bounds()

    def _determine_face_type(self):
        cell_type_map = {
            3: "triangle",
            4: "quad"
        }

        cell_types = set([cell_type_map[len(cell)] for cell in self.vedo_mesh.cells])
        return list(cell_types)[0] if len(cell_types) < 2 else "mixed"
        
    def create_visualisation(self):
        vedo.settings.default_backend = "vtk"
        self.plotter = Plotter()
        self.plotter += [self.vedo_mesh]

    def check_barycenter(self):
        # print(self.vedo_mesh.center_of_mass() - self.vedo_mesh.coordinates, self.vedo_mesh.center_of_mass())
        # assert np.all((self.vedo_mesh.center_of_mass() - self.vedo_mesh.coordinates) > 0)
        ...

    def show(self):
        if self.visualize:
            show(self.vedo_mesh, axes=1).close()
        else:
            print("Visualization not initialized")
            exit(-1) # switch to throw error instead