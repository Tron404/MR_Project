import numpy as np
import vedo
import os
from tqdm import tqdm
from MeshObject import *
import pandas as pd
from Pipeline import *
from collections import defaultdict
import argparse

if __name__ == "__main__":

    df = pd.read_pickle("original_data_statistics.pickle")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--shape_class", type=str)
    args = arg_parser.parse_args()
    class_type = args.shape_class
    df = df[df["class"] == class_type]

    shape_path_orig = "../ShapeDatabase_INFOMR_orig"
    pipeline = Pipeline(pipeline_parameters={"subdivide": {"threshold": 5610}})

    new_path_shape = "../ShapeDatabase_INFOMR_norm"
    folder_name = os.path.join(new_path_shape, class_type)
    os.makedirs(folder_name, exist_ok=True)
    nontwomanifold_faces = defaultdict(list)
    obj_name = ""
    iterator = tqdm(zip(df["class"], df["name"]), total=len(df), desc=f"{class_type} - {obj_name}")
    ok = []
    print(class_type)
    for class_type, obj_name in iterator:
        iterator.set_description(f"{class_type} - {obj_name}")
        if obj_name in os.listdir(folder_name):
            continue
        path = os.path.join(shape_path_orig, class_type, obj_name)
        new_path = os.path.join(new_path_shape, class_type, obj_name)
        mesh = MeshObject(path, True, class_type=class_type, name=obj_name)
        if not mesh.is_manifold():
            nontwomanifold_faces[class_type] += [obj_name]
        mesh: MeshObject = pipeline.normalize_shape(mesh)

        vedo.save(mesh, new_path)
