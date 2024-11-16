from shapre_retrieval import ShapeRetrieval
import numpy as np
import pandas as pd
from collections import defaultdict
import pickle
from tqdm import tqdm
from argparse import ArgumentParser
import time
import os

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--k", type=int)
    argparser.add_argument("--distance_approach", type=str)
    args = argparser.parse_args()
    k = args.k if args.k else 5
    distance_approach = args.distance_approach if args.distance_approach else "ann"
    retrieval_parameters = {
            "k": k,
            "num_bins": 75,
            "feature_weights": [0.5, 0.5, 0.2, 0.7, 0.4, 0.7, 0.2, 0.9, 0.9, 0.5, 0.7],
            "are_vectors_normalized": True,
            "distance_approach": distance_approach
        }

    retriever = ShapeRetrieval(**retrieval_parameters)

    feature_vector_queries = np.asarray(retriever.feature_df["feature_vector"].tolist())
    if distance_approach == "manual":
        retrieve_func = retriever.find_similar_shapes_manual_vector_list
    else:
        retrieve_func = retriever.find_similar_shapes_nn_vector

    similar_list, query_time = retrieve_func(feature_vector_queries, return_query=True)

    class_performance = defaultdict(list)
    for idx_query, query in tqdm(enumerate(similar_list), total=len(similar_list)):
        query_item = query[0]
        class_query = query_item["class_type"]
        
        retrieved_items = query[1:]
        class_retrieved = [retrieved["class_type"] for retrieved in retrieved_items]
        names_retrieved = [retrieved["obj_name"] for retrieved in retrieved_items]
        successes = [int(class_r == class_query) for class_r in class_retrieved]

        class_performance[class_query] += [{
            "query_name": query_item["obj_name"],
            "query_id": idx_query,
            "query_class": class_query,
            "retrieved_item_names": names_retrieved,
            "retrieved_item_classes": class_retrieved,
            "successes": successes
        }]

    class_performance["time"] = query_time
    os.makedirs(distance_approach, exist_ok=True)
    pickle.dump(class_performance, open(f"{distance_approach}/class_performance_top{k}.pickle", "wb"))