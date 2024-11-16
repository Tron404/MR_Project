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
            "subdivision": self.resample_shape_pymeshlab,
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
            mesh: MeshObject = transformation(*args, **kwargs)
            mesh = mesh.compute_normals()
            return mesh
        return normals
    
    def sanitize_nonmanifoldness_pymesh(self, pymesh_set):
        operations_nonmanifoldness = [
            partial(pymesh_set.meshing_repair_non_manifold_edges, method=0),
            pymesh_set.meshing_repair_non_manifold_vertices,
        ]

        is_manifold = pymesh_set.get_topological_measures()["is_mesh_two_manifold"]
        while not is_manifold:
            for operation in operations_nonmanifoldness:
                operation()
            is_manifold = pymesh_set.get_topological_measures()["is_mesh_two_manifold"]

        return pymesh_set

    def sanitize_geometry_pymesh(self, pymesh_set):
        def remove_disconnected_components(pymesh_set, nbfaceratio=0.05, ratio_selected_faces = 0.1): # elbow method?
            pymesh_set.apply_filter("set_selection_all")
            all_faces_num = pymesh_set.current_mesh().selected_face_number()
            pymesh_set.set_selection_none()
            pymesh_set.compute_selection_by_small_disconnected_components_per_face(nbfaceratio=nbfaceratio)
            r = pymesh_set.current_mesh().selected_face_number()/all_faces_num
            if r < ratio_selected_faces: # if too many, dont
                pymesh_set.meshing_remove_selected_faces()
            pymesh_set.set_selection_none()

            return pymesh_set

        operations_cleaning = [
            pymesh_set.meshing_remove_duplicate_faces,
            partial(remove_disconnected_components, pymesh_set, nbfaceratio=0.05),
            pymesh_set.meshing_merge_close_vertices,
        ]

        for operation in operations_cleaning:
            operation()

        return pymesh_set

    def sanitize_mesh_pymesh(self, pymesh_set):       
        pymesh_set = self.sanitize_geometry_pymesh(pymesh_set)
        is_manifold = pymesh_set.get_topological_measures()["is_mesh_two_manifold"]
        if not is_manifold:
            pymesh_set = self.sanitize_nonmanifoldness_pymesh(pymesh_set)

        pymesh_set.meshing_close_holes(refinehole=True, refineholeedgelen=pymeshlab.PercentageValue(1), maxholesize=25)
        pymesh_set.set_selection_none()
        is_manifold = pymesh_set.get_topological_measures()["is_mesh_two_manifold"]
        if not is_manifold:
            pymesh_set = self.sanitize_nonmanifoldness_pymesh(pymesh_set)
       
        return pymesh_set
    
    def resample_shape_pymeshlab(self, vedo_mesh: MeshObject, threshold: int=5610):
        pymesh = vedo.utils.vedo2meshlab(vedo_mesh)
        pymesh_set = pymeshlab.MeshSet()
        pymesh_set.add_mesh(pymesh)

        if pymesh_set.current_mesh().vertex_number() > threshold:
            ### !!!! we dont need a manifold shape for decimation
            last_vertex_count = -1
            prev_meshset = pymeshlab.MeshSet()
            prev_meshset.add_mesh(pymesh_set.current_mesh())
            while pymesh_set.current_mesh().vertex_number() > threshold:
                pymesh_set.apply_filter("meshing_decimation_quadric_edge_collapse", targetperc=0.9, qualitythr=0.3, preserveboundary=True, preservetopology=True, planarquadric=True)
                
                if last_vertex_count == pymesh_set.current_mesh().vertex_number():
                    break
                last_vertex_count = pymesh_set.current_mesh().vertex_number()

            vedo_mesh = self.sanitize_mesh_pymesh(pymesh_set)

            return MeshObject(pymesh_set.current_mesh(), visualize=True)
        
        vedo_mesh = self.sanitize_mesh_pymesh(pymesh_set)

        # subdiv_method = partial(pymesh_set.apply_filter, filter_name="meshing_surface_subdivision_ls3_loop", loopweight=2, iterations=1)
        # if pymesh_set.current_mesh().vertex_number() < 100: # low vertex shapes' topology is heavily modified by any loop-adjacent subdivision algo
        subdiv_method = partial(pymesh_set.apply_filter, filter_name="meshing_surface_subdivision_midpoint", iterations=1)
        ##### LS3 INTRODUCES NANs !!!!!!
        ##### midpoint is vertex splitting, while ls3 loop is face splitting
        last_vertex_count = -1
        while pymesh_set.current_mesh().vertex_number() < threshold:
            subdiv_method()
            if last_vertex_count == pymesh_set.current_mesh().vertex_number():
                break
            last_vertex_count = pymesh_set.current_mesh().vertex_number()

        last_vertex_count = -1
        prev_meshset = pymeshlab.MeshSet()
        prev_meshset.add_mesh(pymesh_set.current_mesh())
        while pymesh_set.current_mesh().vertex_number() > threshold:
            pymesh_set.apply_filter("meshing_decimation_quadric_edge_collapse", targetperc=0.9, qualitythr=0.3, preserveboundary=True, preservetopology=True, planarquadric=True)
            if last_vertex_count == pymesh_set.current_mesh().vertex_number():
                break
            last_vertex_count = pymesh_set.current_mesh().vertex_number()

        return MeshObject(pymesh_set.current_mesh(), visualize=True)

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

    # @recompute_normals
    def _align_to_principal_axes(self, mesh: MeshObject) -> None:
        _, eigen_vectors = self._eigen_vectors(mesh)
        mesh.coordinates = np.dot(mesh.coordinates, eigen_vectors)

        return mesh

    # @recompute_normals
    def _flip_mass(self, mesh: MeshObject, return_sign=False) -> None:
        centre_coordinates = mesh.cell_centers
        f = np.sign(np.sum(np.sign(centre_coordinates) * (centre_coordinates ** 2), axis=0))
        flip_transformation = np.zeros((3,3))
        np.fill_diagonal(flip_transformation, f)

        mesh.coordinates = np.dot(mesh.coordinates, flip_transformation)
        if return_sign:
            return mesh, f
        else:
            return mesh


    @recompute_normals
    def normalize_shape(self, mesh: MeshObject) -> None:
        for component in list(self._pipeline_components.keys()):
            mesh = self._pipeline_components[component](mesh, **self.pipeline_parameters[component])

        return mesh
