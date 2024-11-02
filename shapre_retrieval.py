import numpy as np
import pickle
import pandas as pd
import os
from distance import *
from pynndescent import NNDescent
import warnings
from functools import partial
from sklearn.neighbors import KNeighborsClassifier

class ShapeRetrieval:
    def __init__(self, num_bins, feature_weights, k=5, are_vectors_normalized=False, distance_approach="ann"):
        self.feature_weights = feature_weights
        self.num_bins = num_bins
        self.distance_approach = distance_approach
        self.k = k

        self.PATH = "../ShapeDatabase_INFOMR_norm"
        self.PATH_FEATURES = "../ShapeDatabase_INFOMR_norm_features"
        if not are_vectors_normalized:
            warnings.warn("WARNING: feature vectors are not normalized; initiating normalization procedure")
            self.normalize_feature_vectors()

        self.load_features_into_memory()
        match distance_approach:
            case "ann":
                self.load_ann_mmap_index()
            case "knn":
                self.load_knn()

    def normalize_feature_vectors(self):
        class_types = os.listdir(self.PATH_FEATURES)
        class_types = [class_type for class_type in class_types if os.path.isdir(self.PATH_FEATURES + "/" + class_type) and class_type != ".git"]

        feature_vectors = {
            "obj_name": [],
            "class_type": [],
            "feature_vector": []
        }
        skips = 0
        total_items = 0
        for class_type in class_types:
            path_class_features = os.path.join(self.PATH_FEATURES, class_type)
            for obj_feature in os.listdir(path_class_features):
                total_items += len(os.listdir(path_class_features))
                if "normalized" in obj_feature:
                    skips += 1
                    continue

                path = os.path.join(path_class_features, obj_feature)
                feature_vector = pickle.load(open(path, "rb"))

                feature_vectors["obj_name"] += [obj_feature.removesuffix(".pickle")]
                feature_vectors["class_type"] += [class_type]
                feature_vectors["feature_vector"] += [feature_vector["feature_vector"]]

        if skips == total_items:
            warnings.warn("WARNING: feature vectors were already normalized.")
            return

        fv_df = pd.DataFrame(feature_vectors)
        fv = np.asarray(pd.DataFrame(feature_vectors)["feature_vector"].tolist())
        fv = feature_normalization(fv, num_bins=self.num_bins)
        fv_df["feature_vector"] = fv.tolist()
        fv_df["feature_vector"] = fv_df["feature_vector"].apply(np.asarray)

        for class_type, obj_name, norm_fv in zip(fv_df["class_type"], fv_df["obj_name"], fv_df["feature_vector"]):
            path = os.path.join(self.PATH_FEATURES, class_type, obj_name)
            to_save_obj = {
                "obj_name": obj_name,
                "class_type": class_type,
                "feature_vector": norm_fv,
            }
            pickle.dump(to_save_obj, open(path + "_normalized.pickle", "wb"))   

        fv_df.to_pickle(os.path.join(self.PATH_FEATURES, "feature_vector_df_normalized.pickle"))   

    def load_ann_mmap_index(self):
        path_ann = self.PATH_FEATURES + "/ann_index.pickle"
        if "ann_index.pickle" in os.listdir(self.PATH_FEATURES):
            self.ann_index = pickle.load(open(path_ann, "rb"))
            return
        
        warnings.warn("WARNING: no ANN indexing has been found; creating new one (this might take a while!)")
        fv = np.asarray(self.feature_df["feature_vector"].tolist())

        numbda_dist = distance_numba(num_bins=self.num_bins, feature_weights=self.feature_weights)
        self.ann_index = NNDescent(data=fv, metric=numbda_dist)
        self.ann_index.prepare()

        pickle.dump(self.ann_index, open(path_ann, "wb"))

    def load_knn(self):
        self.label_to_int = {label: id for id, label in enumerate(self.feature_df.class_type.tolist())}
        self.int_to_label = {id: label for label, id in self.label_to_int.items()}

        fv = np.asarray(self.feature_df["feature_vector"].tolist())

        self.int_labels = [self.label_to_int[label] for label in self.feature_df.class_type.tolist()]
        self.knn = KNeighborsClassifier(metric=partial(distance, num_bins=self.num_bins, feature_weights=self.feature_weights), algorithm="auto")
        self.knn.fit(fv, self.int_labels)

    def load_features_into_memory(self):
        class_types = os.listdir(self.PATH_FEATURES)
        if "feature_vector_df_normalized.pickle" in class_types:
            self.feature_df = pd.read_pickle(os.path.join(self.PATH_FEATURES, "feature_vector_df_normalized.pickle"))   
            return
        class_types = [class_type for class_type in class_types if os.path.isdir(self.PATH_FEATURES + "/" + class_type) and class_type != ".git"]

        feature_vectors = {
            "obj_name": [],
            "class_type": [],
            "feature_vector": []
        }
        for class_type in class_types:
            path_class_features = os.path.join(self.PATH_FEATURES, class_type)
            for obj_feature in os.listdir(path_class_features):
                if not ("_normalized" in obj_feature):
                    continue 
                path = os.path.join(path_class_features, obj_feature)
                feature_vector = pickle.load(open(path, "rb"))

                feature_vectors["obj_name"] += [obj_feature.removesuffix("_normalized.pickle")]
                feature_vectors["class_type"] += [class_type]
                feature_vectors["feature_vector"] += [feature_vector["feature_vector"]]

        self.feature_df: pd.DataFrame = pd.DataFrame(feature_vectors)
        self.feature_df.to_pickle(os.path.join(self.PATH_FEATURES, "feature_vector_df_normalized.pickle"))   

    def find_similar_shapes_nn(self, obj_name, class_type):
        ## find the feature vector of the given shape
        path = os.path.join(self.PATH_FEATURES, class_type, obj_name)
        query_mesh_fv = pickle.load(open(path + "_normalized.pickle", "rb"))["feature_vector"]

        # k+1 because the algorithms return the original item as well
        neighbours_idx, neighbours_dist = None, None
        match self.distance_approach:
            case "ann":
                neighbours_idx, neighbours_dist = self.ann_index.query([query_mesh_fv], k=self.k+1)
            case "knn":
                neighbours_idx, neighbours_dist = self.knn.kneighbors([query_mesh_fv], n_neighbors=self.k+1)
        
        # unpack, as they are given as lists within lists; also remove the first item, as it is the queried item
        neighbours_idx, neighbours_dist = neighbours_idx[0][1:], neighbours_dist[0][1:] 
        dict_return = self.feature_df.iloc[neighbours_idx]
        dict_return["distance"] = neighbours_dist

        return dict_return.to_dict(orient="records")

    def find_similar_shapes_manual(self, obj_name):
        obj_name = obj_name.removesuffix(".obj")
        query_mesh = self.feature_df[self.feature_df["obj_name"] == obj_name]
        feature_vectors = np.asarray(self.feature_df["feature_vector"].tolist())
        query_mesh_fv = query_mesh["feature_vector"].to_numpy()[0]

        dists = []
        for vec in feature_vectors:
            dists += [distance(query_mesh_fv, vec, num_bins=self.num_bins, feature_weights=self.feature_weights)]

        dists_idx = np.argsort(dists)
        retrieved_shapes_idx = np.argsort(dists_idx)[1:6]
        aux_df = self.feature_df.iloc[retrieved_shapes_idx]
        aux_df["distance"] = np.sort(dists)[1:6]

        return aux_df.to_dict(orient="records")
    
    def find_similar_shapes(self, obj_name, class_type):
        callable_similar_func = None

        if self.distance_approach == "manual":
            callable_similar_func = partial(self.find_similar_shapes_manual, obj_name=obj_name)
        elif "nn" in self.distance_approach:
            callable_similar_func = partial(self.find_similar_shapes_nn, obj_name=obj_name, class_type=class_type)

        similar_shapes_dict = callable_similar_func()

        return similar_shapes_dict

