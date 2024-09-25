import vedo
import vedo.plotter
from MeshObject import *
import pymeshlab
import numpy as np

## ORDER IS IMPORTANT
def subdivide_shape(vedo_mesh, subdivision_type, threshold=None):
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
    while pymesh_set.current_mesh().vertex_number() < threshold:
        subdivion_func(iterations=1)

    return vedo.Mesh(pymesh_set.current_mesh())


def translate_to_barycenter(mesh: MeshObject) -> None:
    bary_center = mesh.center_of_mass()
    mesh.coordinates = mesh.coordinates - bary_center
    mesh.check_barycenter()

def scale_mesh(mesh: MeshObject):
    max_dim = mesh.bounds()
    max_dim = np.max([max_dim[1]-max_dim[0], max_dim[3]-max_dim[2], max_dim[5]-max_dim[4]])
    mesh.coordinates /= max_dim

def _eigen_vectors(mesh: MeshObject):
    coordinates = mesh.vertices
    cov_matrix = np.cov(coordinates.T)

    e_vals, e_vectors = np.linalg.eig(cov_matrix)

    # print(np.sort(e_vals)[::-1])
    # e_vectors = e_vectors[np.argsort(e_vals)[::-1]]

    return e_vectors

def align_to_principal_axes(mesh: MeshObject):
    eigen_vectors = _eigen_vectors(mesh)
    mesh.coordinates = np.dot(mesh.coordinates, eigen_vectors)


def flip_mass(mesh: MeshObject):
    centre_coordinates = mesh.cell_centers
    f = np.sign(np.sum(np.sign(centre_coordinates) * (centre_coordinates ** 2), axis=0))
    flip_transformation = np.zeros((3,3))
    np.fill_diagonal(flip_transformation, f)

    mesh.coordinates = np.dot(mesh.coordinates, flip_transformation)

def normalize_shape(mesh: MeshObject):
    mesh = subdivide_shape(mesh, "midpoint", 5600)
    return mesh
    # translate_to_barycenter(mesh)
    # align_to_principal_axes(mesh)
    # flip_mass(mesh)
    # scale_mesh(mesh)

if __name__ == "__main__":
    shape_path = "../ShapeDatabase_INFOMR"

    mesh = MeshObject("../ShapeDatabase_INFOMR_orig/Bed/D00735.obj", True)
    print(mesh.n_vertices)
    mesh = normalize_shape(mesh)
    print(mesh.nvertices)
    vedo.show().close()
    mesh.show()