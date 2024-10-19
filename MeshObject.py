import vedo
import numpy as np
from vedo import show, Plotter, Mesh

class MeshObject(Mesh):
    def __init__(self, path_obj: any=None, visualize: bool=False, name: str="", class_type: str="") -> None:
        if not path_obj:
            return
        
        super(MeshObject, self).__init__(path_obj)
        self.set_mesh_colors()
        self.visualize = visualize
        self.face_type = self._determine_face_type()
        self.name = name
        self.class_type = class_type

        if self.visualize:
            self._create_visualisation()
    
    def set_mesh_colors(self):
        self.color("grey").lw(1)
    
    @property
    def n_faces(self):
        return self.ncells

    @property
    def n_vertices(self):
        return self.nvertices
    
    @property
    def bounding_box(self):
        return self.bounds()

    def _determine_face_type(self):
        cell_type_map = {
            3: "triangle",
            4: "quad"
        }

        cell_types = set([cell_type_map[len(cell)] for cell in self.cells])
        ##### CHECK WHICH SHAPE THROWS ERROR
        # return list(cell_types)[0] if len(cell_types) < 2 else "mixed"
        return "triangle"
        
    def _create_visualisation(self):
        vedo.settings.default_backend = "vtk"
        self.plotter = Plotter()
        self.plotter += [self]

    def check_barycenter(self):
        # print(self.vedo_mesh.center_of_mass() - self.vedo_mesh.coordinates, self.vedo_mesh.center_of_mass())
        # assert np.all((self.vedo_mesh.center_of_mass() - self.vedo_mesh.coordinates) > 0)
        ...

    def show(self):
        if self.visualize:
            self.plotter.clear(deep=True)
            show(self, axes=1).close()
        else:
            print("Visualization not initialized")
            exit(-1) # switch to throw error instead