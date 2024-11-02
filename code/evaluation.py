from shapre_retrieval import ShapeRetrieval
import numpy as np
import pandas as pd
from collections import defaultdict
import pickle
from tqdm import tqdm
retrieval_parameters = {
        "k": 5,
        "num_bins": 150,
        "feature_weights": [0.5, 0.5, 0.2, 0.7, 0.4, 0.7, 0.2, 0.9, 0.9, 0.5, 0.7],
        "are_vectors_normalized": True,
        "distance_approach": "ann"
    }

retriever = ShapeRetrieval(**retrieval_parameters)

feature_vector_queries = np.asarray(retriever.feature_df["feature_vector"].tolist())
similar_list = retriever.find_similar_shapes_nn_vector(feature_vector_queries, return_query=True)

pickle.dump(similar_list, open("what.pickle", "wb"))

class_performance = defaultdict(list)
for idx_query, query in tqdm(enumerate(similar_list)):
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

pickle.dump(class_performance, open("class_performance.pickle", "wb"))