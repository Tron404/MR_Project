import numpy as np
import scipy.spatial.distance as scy

def scalar_normalization(feature_column: np.ndarray):
    return (feature_column - np.mean(feature_column)) / np.std(feature_column)

def histogram_normalization(feature_histogram: np.ndarray):
    sum_vals = np.repeat(np.sum(feature_histogram, axis=1), feature_histogram.shape[1]).reshape(feature_histogram.shape)
    return feature_histogram / sum_vals

def scalar_distance(query: np.ndarray, candidate: np.ndarray, weights: np.ndarray):
    return np.linalg.norm((query - candidate) * weights)

def single_histogram_distance(query, candidate):
    return scy.jensenshannon(query, candidate)

def feature_normalization(all_feature_vectors, num_bins=50):
    for feature_column in range(6):
        all_feature_vectors[:,feature_column] = scalar_normalization(all_feature_vectors[:,feature_column])

    for feature_hisogram in range(5):
        idx_range_left = 6 + feature_hisogram * num_bins
        idx_range_right = 6 + (feature_hisogram + 1) * num_bins
        all_feature_vectors[:, idx_range_left:idx_range_right] = histogram_normalization(all_feature_vectors[:,idx_range_left:idx_range_right])

    return all_feature_vectors

def distance(query, candidate, num_bins, feature_weights):
    # first 6 = scalar
    # remaning 5 * bins = histogram
    dists = scalar_distance(query=query[:6], candidate=candidate[:6], weights=feature_weights[:6])
    histogram_dists = []
    for feature_hisogram in range(1,6):
        idx_range_left = 6 + feature_hisogram * num_bins
        idx_range_right = 6 + (feature_hisogram + 1) * num_bins
        histogram_dists += [single_histogram_distance(query[idx_range_left:idx_range_right], candidate[idx_range_left:idx_range_right])]

    dists = [dists]
    dists += histogram_dists * feature_weights[6:]
    dists = np.asarray(dists)
    return np.sum(dists).item()