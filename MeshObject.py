import vedo
import numpy as np
# import Pipeline
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

    @property
    def surface_area(self):
        return self.area()
    
    @property
    def volume(self):
        vols = []
        for connected in self.cells:
            triangle = self.coordinates[connected]
            volume = self.signed_volume_triangle(triangle)
            vols += [volume]
        
        volume = abs(sum(vols))
        return volume
    
    @property
    def compactness(self):
        return (self.surface_area ** 3) / (36 * np.pi * (self.volume ** 2))
    
    @property
    def rectangularity(self):
        bb = self.bounding_box
        x = abs(bb[1] - bb[0])
        y = abs(bb[3] - bb[2])
        z = abs(bb[5] - bb[4])
        bb_volume = x*y*z
        return self.volume / bb_volume
    
    @property
    def diameter(self):
        # TODO
        return None
    
    @property
    def convexity(self):
        eigenvalues, _ = Pipeline._eigen_vectors(None, self)
        print(eigenvalues)
        return None
    
    @property
    def eccentricity(self):
        # TODO
        return None

    def signed_volume_triangle(triangle):
        p1 = triangle[0]
        p2 = triangle[1]
        p3 = triangle[2]

        vol321 = p3[0] * p2[1] * p1[2]
        vol231 = p2[0] * p3[1] * p1[2]
        vol312 = p3[0] * p1[1] * p2[2]
        vol132 = p1[0] * p3[1] * p2[2]
        vol213 = p2[0] * p1[1] * p3[2]
        vol123 = p1[0] * p2[1] * p3[2]

        vol = (1/6) * (-vol321 + vol231 + vol312 - vol132 - vol213 + vol123)
        return vol

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