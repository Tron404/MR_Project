from MeshObject import *
import pymeshlab

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

def scale_mesh(mesh: MeshObject) -> None:
    max_dim = np.max(mesh.bounding_box)
    mesh.vedo_mesh.coordinates /= max_dim
    

shape_path = "../ShapeDatabase_INFOMR"

mesh = MeshObject(shape_path + "/" + "City/" + "m1662.obj", True)
translate_to_barycenter(mesh)
scale_mesh(mesh)
mesh.check_barycenter()
mesh.show()