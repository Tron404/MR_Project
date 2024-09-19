from MeshObject import *
import pymeshlab
import numpy as np

def subdivide_shape(obj_path, subdivision_type, iterations=1, threshold=None):
    pymesh_set = pymeshlab.MeshSet()
    pymesh_set.load_new_mesh(obj_path)

    match subdivision_type:
        case "midpoint":
            subdivion_func = pymesh_set.meshing_surface_subdivision_midpoint
    
    subdivion_func(iterations=iterations)

    class_type, obj_name = obj_path.split("/")[-2:]
    pymesh_set.save_current_mesh(f"../ShapeDatabase_INFOMR/{class_type}/" + f"subdivided_{obj_name}.obj")

def translate_to_barycenter(mesh: MeshObject) -> None:
    bary_center = mesh.vedo_mesh.center_of_mass()
    mesh.vedo_mesh.coordinates = mesh.vedo_mesh.coordinates - bary_center
    mesh.check_barycenter()

def scale_mesh(mesh: MeshObject):
    max_dim = mesh.vedo_mesh.bounds()
    max_dim = np.max([max_dim[1]-max_dim[0], max_dim[3]-max_dim[2], max_dim[5]-max_dim[4]])
    mesh.vedo_mesh.coordinates /= max_dim

def _eigen_vectors(mesh: MeshObject):
    coordinates = mesh.vedo_mesh.vertices
    cov_matrix = np.cov(coordinates.T)

    e_vals, e_vectors = np.linalg.eig(cov_matrix)

    e_vectors = e_vectors[np.argsort(e_vals)[::-1][:3]]

    return e_vectors

def align_to_principal_axes(mesh: MeshObject):
    eigen_vectors = _eigen_vectors(mesh)
    mesh.vedo_mesh.coordinates = np.dot(mesh.vedo_mesh.coordinates, eigen_vectors)


def flip_mass(mesh: MeshObject):
    centre_coordinates = mesh.vedo_mesh.cell_centers
    f = np.sign(np.sum(np.sign(centre_coordinates) * (centre_coordinates ** 2), axis=0))
    flip_transformation = np.zeros((3,3))
    flip_transformation[0,0] = f[0]
    flip_transformation[1,1] = f[1]
    flip_transformation[2,2] = f[2]

    mesh.vedo_mesh.coordinates = np.dot(mesh.vedo_mesh.coordinates, flip_transformation)

def normalize_shape(mesh: MeshObject):
    translate_to_barycenter(mesh)
    align_to_principal_axes(mesh)
    flip_mass(mesh)
    scale_mesh(mesh)

if __name__ == "__main__":
    shape_path = "../ShapeDatabase_INFOMR"

    mesh = MeshObject(shape_path + "/" + "MultiSeat/" + "D00273.obj", True)
    normalize_shape(mesh)
    mesh.show()