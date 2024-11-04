from tqdm import tqdm
import pickle

import argparse

import vedo
from Pipeline import *
from MeshObject import *
from mesh_properties import *
import os

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--shape_class", type=str)
    args = arg_parser.parse_args()
    p = Pipeline()
    # mesh.show()

    shape_property_args = {
        "num_samples": 10000,
        "num_bins": 75,
        "return_unbinned": True
    }

    path = f"../ShapeDatabase_INFOMR_norm"
    path_features = f"../ShapeDatabase_INFOMR_norm_features"
    class_types = os.listdir(path)
    class_types = [class_type for class_type in class_types if os.path.isdir(path + "/" + class_type) and class_type != ".git"]
    replace_feature_file = False
    class_type = args.shape_class

    path_class = os.path.join(path, class_type)
    path_class_features = os.path.join(path_features, class_type)
    os.makedirs(os.path.join(path_class_features), exist_ok=True)
    for shape in tqdm(os.listdir(path_class), desc=class_type):
        shape_name = shape.removesuffix(".obj")
        feature_file_name = shape.removesuffix(".obj") + ".pickle"
        feature_file_name_path = os.path.join(path_class_features, feature_file_name) 
        if not replace_feature_file and feature_file_name in os.listdir(path_class_features):
            continue
        mesh = MeshObject(os.path.join(path_class, shape))
        f_vector, unbinned_shape_property = compute_feature_vector(mesh, shape_property_args)
        feature_dict = {
            "obj_name": shape_name,
            "class_type": class_type,
            "feature_vector": f_vector,
            "unbinned_shape_property": unbinned_shape_property
        }
        pickle.dump(feature_dict, open(feature_file_name_path, "wb"))