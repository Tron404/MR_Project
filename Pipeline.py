import vedo
from vedo import Mesh
from MeshObject import *
import pymeshlab
import numpy as np
from functools import partial

class Pipeline:
    def __init__(self, disable_components: list[str]=None, pipeline_parameters: dict={}) -> None:
        ## ORDER IS IMPORTANT
        self._pipeline_components = {
            "subdivision": self._resample_shape,
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
    
    def recompute_normals(transformation):
        def normals(*args, **kwargs):
            # first check if normal calculation is needed?
            mesh: MeshObject = transformation(*args, **kwargs)
            mesh = mesh.compute_normals()
            # print(mesh.is_manifold())
            return mesh
        return normals

    def _sanitize_mesh(self, vedo_mesh: MeshObject):
        pymesh = vedo.utils.vedo2meshlab(vedo_mesh)
        pymesh_set = pymeshlab.MeshSet()
        pymesh_set.add_mesh(pymesh)

        operations = [
            pymesh_set.meshing_remove_duplicate_faces,
            pymesh_set.meshing_remove_duplicate_vertices,
            partial(pymesh_set.meshing_repair_non_manifold_edges, method=0),
            pymesh_set.meshing_repair_non_manifold_vertices
        ]
        for operation in operations:
            operation()

        vedo_mesh = MeshObject(pymesh_set.current_mesh(), visualize=True)
        vedo_mesh.fill_holes()

        return vedo_mesh
    
    @recompute_normals
    def _resample_shape(self, vedo_mesh: MeshObject, sampling_type: str="centroid", threshold: int=5610):
        if not vedo_mesh.is_manifold():
            vedo_mesh = self._sanitize_mesh(vedo_mesh)
        
        match sampling_type:
            case "loop":
                sampling_type = 0
            case "linear":
                sampling_type = 1
            case "adaptive":
                sampling_type = 2
            case "butterfly":
                sampling_type = 3
            case "centroid":
                sampling_type = 4
            case "decimation":
                sampling_type = -1
            case "decimation_pro":
                sampling_type = -2
        if sampling_type != -1:
            last_vertex_count = -1
            while vedo_mesh.n_vertices < threshold:
                vedo_mesh = vedo_mesh.subdivide(1, method=sampling_type)
                if last_vertex_count == vedo_mesh.n_vertices:
                    break
                last_vertex_count = vedo_mesh.n_vertices
        match sampling_type:
            case -1:
                vedo_mesh.decimate(fraction=0.5, n=threshold)
            case -2:
                vedo_mesh.decimate_pro(fraction=0.5, n=threshold)

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

        # matrix of eigen values has the following form
        # [ e_1 e_2 e_3
        #   e_1 e_2 e_3
        #   e_1 e_2 e_3
        # ]    
        # to access the *correct* eigen vector, use this notation `e_vectors[:,i]` 
        # to select the column corresponding to the i-th eigen vector
        e_vectors = e_vectors[:,np.argsort(e_vals)[::-1]] 
        e_vals = np.sort(e_vals)[::-1] # sort e_vals from high to low

        e_vectors[:,2] = np.cross(e_vectors[:,0], e_vectors[:,1])

        return e_vals, e_vectors

    @recompute_normals
    def _align_to_principal_axes(self, mesh: MeshObject) -> None:
        _, eigen_vectors = self._eigen_vectors(mesh)
        mesh.coordinates = np.dot(mesh.coordinates, eigen_vectors)

        return mesh

    @recompute_normals
    def _flip_mass(self, mesh: MeshObject) -> None:
        centre_coordinates = mesh.cell_centers
        f = np.sign(np.sum(np.sign(centre_coordinates) * (centre_coordinates ** 2), axis=0))
        flip_transformation = np.zeros((3,3))
        np.fill_diagonal(flip_transformation, f)

        mesh.coordinates = np.dot(mesh.coordinates, flip_transformation)

        return mesh

    @recompute_normals
    def normalize_shape(self, mesh: MeshObject) -> None:
        for component in list(self._pipeline_components.keys()):
            mesh = self._pipeline_components[component](mesh, **self.pipeline_parameters[component])

        return mesh
