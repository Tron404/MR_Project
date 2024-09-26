import vedo
from vedo import Mesh
from MeshObject import *
import pymeshlab
import numpy as np

class Pipeline:
    def __init__(self, disable_components: list[str]=None, pipeline_parameters: dict={}) -> None:
        ## ORDER IS IMPORTANT
        self._pipeline_components = {
            "subdivision": self._subdivide_shape,
            "barycenter_translation": self._translate_to_barycenter,
            "axis_alignment": self._align_to_principal_axes,
            "flip_moment": self._flip_mass,
            "scaling": self._scale_mesh
          }
        
        self.pipeline_parameters = {
            "subdivision": {},
            "barycenter_translation": {},
            "axis_alignment": {},
            "flip_moment": {},
            "scaling": {}
        }
        self.pipeline_parameters = {**self.pipeline_parameters, **pipeline_parameters}

        if disable_components:
            for component in disable_components:
                self._pipeline_components.pop(component)
                self.pipeline_parameters.pop(component)

    @property
    def pipeline_components(self):
        return " --> ".join(list(self._pipeline_components.keys()))

    def _subdivide_shape(self, vedo_mesh: MeshObject, subdivision_type: str="midpoint", threshold: float=100.0) -> MeshObject:
        pymesh = vedo.utils.vedo2meshlab(vedo_mesh)
        pymesh_set = pymeshlab.MeshSet()
        pymesh_set.add_mesh(pymesh)

        match subdivision_type:
            case "midpoint":
                subdivion_func = pymesh_set.meshing_surface_subdivision_midpoint
            case "loop":
                subdivion_func = pymesh_set.meshing_surface_subdivision_loop
        
        # face_number - number of faces
    # vertex_number - number of vertices
        if pymesh_set.get_topological_measures()["non_two_manifold_edges"] > 0:
            return vedo_mesh

        last_vertex_num = -1
        while pymesh_set.current_mesh().vertex_number() < threshold:
            subdivion_func(iterations=1)
            if last_vertex_num == pymesh_set.current_mesh().vertex_number():
                break
            last_vertex_num = pymesh_set.current_mesh().vertex_number()
        # # face_number - number of faces
        # # vertex_number - number of vertices
        # while pymesh_set.current_mesh().vertex_number() < threshold:
        #     subdivion_func(iterations=1)

        vedo_mesh = MeshObject(pymesh_set.current_mesh(), vedo_mesh.visualize, **{"name": vedo_mesh.name, "class_type": vedo_mesh.class_type})
        return vedo_mesh

    def _translate_to_barycenter(self, mesh: MeshObject) -> MeshObject:
        bary_center = mesh.center_of_mass()
        mesh.coordinates = mesh.coordinates - bary_center
        mesh.check_barycenter()

        return mesh

    def _scale_mesh(self, mesh: MeshObject) -> MeshObject:
        """
        In-place operation
        """
        max_dim = mesh.bounds()
        max_dim = np.max([max_dim[1]-max_dim[0], max_dim[3]-max_dim[2], max_dim[5]-max_dim[4]])
        mesh.coordinates /= max_dim

        return mesh

    def _eigen_vectors(self, mesh: MeshObject) -> np.ndarray:
        coordinates = mesh.vertices
        cov_matrix = np.cov(coordinates.T)

        e_vals, e_vectors = np.linalg.eig(cov_matrix) # eigen vectors are normalized!!
        e_vectors = e_vectors[np.argsort(e_vals)[::-1]] # sort e_vals from high to low then select their corresponding e vectors
        e_vectors[-1] = np.cros(e_vectors[0], e_vectors[1])

        return e_vals, e_vectors

    def _align_to_principal_axes(self, mesh: MeshObject) -> None:
        _, eigen_vectors = self._eigen_vectors(mesh)
        mesh.coordinates = np.dot(mesh.coordinates, eigen_vectors)

        return mesh

    def _flip_mass(self, mesh: MeshObject) -> None:
        centre_coordinates = mesh.cell_centers
        f = np.sign(np.sum(np.sign(centre_coordinates) * (centre_coordinates ** 2), axis=0))
        flip_transformation = np.zeros((3,3))
        np.fill_diagonal(flip_transformation, f)

        mesh.coordinates = np.dot(mesh.coordinates, flip_transformation)

        return mesh

    def normalize_shape(self, mesh: MeshObject) -> None:
        for component in list(self._pipeline_components.keys()):
            mesh = self._pipeline_components[component](mesh, **self.pipeline_parameters[component])

        mesh = mesh.compute_normals()
        return mesh
