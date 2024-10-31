from Pipeline import *
import numpy as np
from vedo import *
from collections import defaultdict
from functools import partial

def surface_area(mesh_obj):
    return mesh_obj.area()

def volume(mesh_obj):
    vols = []
    for connected in mesh_obj.cells:
        triangle = mesh_obj.coordinates[connected]
        volume = signed_volume_triangle(triangle)
        vols += [volume]
    
    volume = abs(sum(vols))
    return volume

def compactness(mesh_obj):
    return (surface_area(mesh_obj) ** 3) / (36 * np.pi * (volume(mesh_obj) ** 2))

def rectangularity(mesh_obj):
    bb = mesh_obj.bounding_box
    x = abs(bb[1] - bb[0])
    y = abs(bb[3] - bb[2])
    z = abs(bb[5] - bb[4])
    bb_volume = x*y*z
    return (mesh_obj.volume() / bb_volume)

def diameter(mesh_obj: MeshObject, return_points=False):
    convex_hull = create_convex_hull(mesh_obj)
    max_distance = -1
    max_distance_points = (None, None)
    for point1_idx in range(0,len(convex_hull.vertices)):
        for point2_idx in range(point1_idx,len(convex_hull.vertices)):
            distance = np.linalg.norm(convex_hull.vertices[point1_idx] - convex_hull.vertices[point2_idx])
            if distance > max_distance:
                max_distance = distance
                max_distance_points = (convex_hull.vertices[point1_idx], convex_hull.vertices[point2_idx])
    if return_points:
        return_items = max_distance, max_distance_points
    else:
        return_items = max_distance
    return return_items

def create_convex_hull(mesh_obj: MeshObject):
    coordinates = mesh_obj.coordinates
    convex_hull = ConvexHull(coordinates)
    return convex_hull

def convexity(mesh_obj: MeshObject):
    coordinates = mesh_obj.coordinates
    convex_hull = ConvexHull(coordinates)
    return mesh_obj.volume() / convex_hull.volume()

def eccentricity(mesh_obj):
    eigenvalues, _ = Pipeline._eigen_vectors(None, mesh_obj)
    eigenvalues = abs(eigenvalues)
    return eigenvalues[0] / eigenvalues[2]

def signed_volume_triangle(triangle):
    p1 = triangle[0]
    p2 = triangle[1]
    p3 = triangle[2]

    vol321 = p3[0] * p2[1] * p1[2]
    vol231 = p2[0] * p3[1] * p1[2]
    vol312 = p3[0] * p1[1] * p2[2]
    vol132 = p1[0] * p3[1] * p2[2]
    vol213 = p2[0] * p1[1] * p3[2]
    vol123 = p1[0] * p2[1] * p3[2]

    vol = (1/6) * (-vol321 + vol231 + vol312 - vol132 - vol213 + vol123)
    return vol

########### SHAPE-PROPERTY DESCRIPTORS

"""
p2       p3
 \      /
  \    /
   \  /
    p1
"""
def a3(p1, p2, p3, in_radians=True):
    diff_p2p1 = (p2 - p1)
    diff_p3p1 = (p3 - p1)
    angle = np.atan2(np.linalg.norm(np.cross(diff_p2p1, diff_p3p1)), np.dot(diff_p2p1, diff_p3p1))
    if not in_radians:
        angle = angle * (180/np.pi)
    return angle

def d1(p1): # double check!!!
    return np.linalg.norm(np.zeros(p1.shape)-p1)

def d2(p1, p2):
    return np.linalg.norm(p2-p1)

def d3(p1, p2, p3): # normalized by sqrt
    p2 -= p1
    p3 -= p1
    aux = np.cross(p2, p3)
    return np.sqrt(np.dot(aux, aux)/2)

# show diagram proof!
def d4(p1, p2, p3, p4):
    # consider p1 to be the point where the tetrahedron comes down from
    p2 -= p1
    p3 -= p1
    p4 -= p1
    return np.cbrt(1/6 * abs(np.dot(np.cross(p2, p3),p4)))

def shape_property_computation(mesh: MeshObject, num_samples=1, num_bins=25, return_unbinned=False):
    properties_map = {"d1": d1, 
                      "d2": d2, 
                      "d3": d3, 
                      "d4": d4, 
                      "a3": partial(a3, in_radians=True)}
    feature_map = defaultdict(list)
    for prop, func in properties_map.items():
        size = (num_samples,int(prop[-1])) if prop[-1] != "1" else (num_samples,1)
        subsample_points = np.random.choice(range(len(mesh.vertices)), size=size)
        subsample_points = mesh.vertices[subsample_points]
        for points in subsample_points:
            # print(points)
            feature_map[prop] += [func(*points)]
        if return_unbinned:
            feature_map[prop + "_unbinned"] = feature_map[prop]
        feature_map[prop] = np.histogram(feature_map[prop], bins=num_bins-1)[1].tolist() # -1 bcs func returns bins+1 (i.e. limits of a bin)

    return feature_map
        
########### feature vectors
def compute_feature_vector(mesh: MeshObject, shape_property_kwargs: dict):
    feature_vector = []
    scalar_feature_computations = [
        surface_area,
        compactness,
        rectangularity,
        diameter,
        convexity,
        eccentricity,
    ]

    for f_computation in scalar_feature_computations:
        feature = f_computation(mesh)
        feature_vector += [feature]


    return_unbinned = shape_property_kwargs["return_unbinned"]
    shape_property_features = shape_property_computation(mesh, **shape_property_kwargs)
    unbinned_features = {}
    for feature_name, feature_values in shape_property_features.items():
        if "unbinned" not in feature_name:
            feature_vector += feature_values
        if return_unbinned:
            unbinned_features[feature_name] = feature_values

    if return_unbinned:
        return_items = np.asarray(feature_vector), unbinned_features
    else:
        return_items = np.asarray(feature_vector)
    return return_items 