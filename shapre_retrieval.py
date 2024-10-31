import numpy as np
import pickle
import pandas as pd
import os
from distance import *

class ShapeRetrieval:
    def __init__(self):
        self.PATH = "../ShapeDatabase_INFOMR_norm"
        self.load_features_into_memory()

    def load_features_into_memory(self):
        path_features = self.PATH + "_features"
        class_types = os.listdir(path_features)
        class_types = [class_type for class_type in class_types if os.path.isdir(path_features + "/" + class_type) and class_type != ".git"]

        feature_vectors = {
            "obj_name": [],
            "class_type": [],
            "feature_vector": []
        }
        for class_type in class_types:
            path_class_features = os.path.join(path_features, class_type)
            for obj_feature in os.listdir(path_class_features):
                path = os.path.join(path_class_features, obj_feature)
                feature_vector = pickle.load(open(path, "rb"))

                feature_vectors["obj_name"] += [obj_feature]
                feature_vectors["class_type"] += [class_type]
                feature_vectors["feature_vector"] += [feature_vector["feature_vector"]]
        
        fv_df = pd.DataFrame(feature_vectors)
        fv = np.asarray(pd.DataFrame(feature_vectors)["feature_vector"].tolist())
        fv = feature_normalization(fv, num_bins=50)
        fv_df["feature_vector"] = fv.tolist()
        fv_df["feature_vector"] = fv_df["feature_vector"].apply(np.asarray)

        self.feature_df: pd.DataFrame = fv_df

    def find_similar_shapes(self, obj_name):
        obj_name = obj_name.removesuffix(".obj")
        query_mesh = self.feature_df[self.feature_df["obj_name"].str.removesuffix(".pickle") == obj_name]
        feature_vectors = np.asarray(self.feature_df["feature_vector"].tolist())
        query_mesh_fv = query_mesh["feature_vector"].to_numpy()[0]

        dists = []
        for vec in feature_vectors:
            dists += [distance(query_mesh_fv, vec, num_bins=50, feature_weights=np.ones(11))]

        dists_idx = np.argsort(dists)
        retrieved_shapes_idx = np.argsort(dists_idx)[1:6]
        aux_df = self.feature_df.iloc[retrieved_shapes_idx]
        aux_df["distance_to_query"] = np.sort(dists)[1:6]
        return aux_df