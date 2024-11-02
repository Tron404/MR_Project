import numpy as np
import scipy.stats as scystats
import numba

####################### FEATURE NORMALIZATION
def scalar_normalization(feature_column: np.ndarray):
    return (feature_column - np.mean(feature_column)) / np.std(feature_column)

def histogram_normalization(feature_histogram: np.ndarray):
    # sum_vals = np.sqrt(np.repeat(np.sum(feature_histogram ** 2, axis=1), feature_histogram.shape[1]).reshape(feature_histogram.shape)) # angle normalization
    sum_vals = np.sum(feature_histogram) # area normalization
    return feature_histogram / sum_vals

def feature_normalization(all_feature_vectors, num_bins=50):
    for feature_column in range(6):
        all_feature_vectors[:,feature_column] = scalar_normalization(all_feature_vectors[:,feature_column])

    for feature_hisogram in range(5):
        idx_range_left = 6 + feature_hisogram * num_bins
        idx_range_right = 6 + (feature_hisogram + 1) * num_bins
        all_feature_vectors[:, idx_range_left:idx_range_right] = histogram_normalization(all_feature_vectors[:,idx_range_left:idx_range_right])

    return all_feature_vectors

####################### NUMBA-SPECIFIC METHODS
@numba.jit
# manual implementation of l2 norm
def scalar_distance_numba(query: np.ndarray, candidate: np.ndarray, feature_weights: np.ndarray):
    sum_val = 0
    for idx in range(6): # 6 scalar features
        sum_val += ((query[idx] - candidate[idx]) ** 2) * feature_weights[idx]
    
    return np.sqrt(sum_val)

# using l1 distance
# implemented based on scypy and the book chapter
@numba.jit
def emd_numba(x:np.ndarray,y:np.ndarray):
    ##### If x and y are equal weight, then the minimum work to 
    # transform one distribution into the other is the area 
    # between the graphs of the CDFs of x and y . 

    # sort vals by position - ch on EMD, section 4.3.2
    x_idx_sort = np.argsort(x)
    y_idx_sort = np.argsort(y)

    all = np.concatenate((x,y))
    all.sort()

    # diff between adjancent bins (combined and sorted x and y)
    all_dist = np.diff(all) # change between bins
    # searchsorted - indices in "x" where to insert values from "all" 
    # s.t. order is preserved
    # right side comparison a[i-1] <= v < a[i]
    # index is first position where insertion could be done; done for all elements of "all"
    x_cdf_indices = np.searchsorted(x[x_idx_sort], all[:-1], 'right')
    x_cdf = x_cdf_indices / x.size # convert idx to cumulative "probs"

    y_cdf_indices = np.searchsorted(y[y_idx_sort], all[:-1], 'right')
    y_cdf = y_cdf_indices / y.size
    
    # Math: \sum_{i=0}^{B}|x_{cdf_i}-y_{cdf_i}|\cdot d_i(a_i,a_{i+1}) 
    return np.sum(np.multiply(np.abs(x_cdf - y_cdf), all_dist))

@numba.jit
def single_histogram_distance_numba(query, candidate):
    return emd_numba(query, candidate)

@numba.jit
def mean_numbda(x):
    sum_val = 0
    for x_val in x:
        sum_val += x_val

    mean = sum_val / len(x)
    return np.float32(mean)

# first create the callable, then apply it
def distance_numba(num_bins, feature_weights):
    @numba.jit(fastmath=True)
    def distance_numba_comp(query, candidate):
        ### first 6 = scalar
        ### remaning 5 * bins = histogram
        dists = scalar_distance_numba(query=query[:6], candidate=candidate[:6], feature_weights=feature_weights[:6])
        histogram_dists = np.zeros(6, dtype=np.float32)
        for feature_hisogram in range(5):
            idx_range_left = 6 + feature_hisogram * num_bins
            idx_range_right = 6 + (feature_hisogram + 1) * num_bins
            histogram_dists[feature_hisogram+1] = single_histogram_distance_numba(query[idx_range_left:idx_range_right], candidate[idx_range_left:idx_range_right]) * feature_weights[6 + feature_hisogram]
            # histogram_dists[feature_hisogram+1] = single_histogram_distance(query[idx_range_left:idx_range_right], candidate[idx_range_left:idx_range_right])

        histogram_dists[0] = dists # change to have 6 distances instead of 1?

        return mean_numbda(histogram_dists)
    return distance_numba_comp

####################### STANDARD METHODS
# l2
def scalar_distance(query: np.ndarray, candidate: np.ndarray, weights: np.ndarray):
    return np.linalg.norm((query - candidate) * weights)

def single_histogram_distance(query, candidate):
    # return scydist.jensenshannon(query, candidate) # not a metric (mathematically = doesnt fulfill the triangle inequality)!
    # print(query, candidate)
    return scystats.wasserstein_distance(query, candidate)

def distance(query, candidate, num_bins, feature_weights):
    ### first 6 = scalar
    ### remaning 5 * bins = histograms
    dists = scalar_distance(query=query[:6], candidate=candidate[:6], weights=feature_weights[:6])
    histogram_dists = []
    for feature_hisogram in range(5):
        idx_range_left = 6 + feature_hisogram * num_bins
        idx_range_right = 6 + (feature_hisogram + 1) * num_bins
        histogram_dists += [single_histogram_distance(query[idx_range_left:idx_range_right], candidate[idx_range_left:idx_range_right]) * feature_weights[6 + feature_hisogram]]

    dists = [dists]
    dists += histogram_dists
    dists = np.asarray(dists)
    return np.mean(dists).item()