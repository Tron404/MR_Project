from Pipeline import *
import numpy as np
from vedo import *

def surface_area(mesh):
    return mesh.area()

def volume(mesh):
    vols = []
    for connected in mesh.cells:
        triangle = mesh.coordinates[connected]
        volume = signed_volume_triangle(triangle)
        vols += [volume]
    
    volume = abs(sum(vols))
    return volume

def compactness(mesh):
    return (surface_area(mesh) ** 3) / (36 * np.pi * (volume(mesh) ** 2))

def rectangularity(mesh):
    bb = mesh.bounding_box
    x = abs(bb[1] - bb[0])
    y = abs(bb[3] - bb[2])
    z = abs(bb[5] - bb[4])
    bb_volume = x*y*z
    return mesh.volume / bb_volume

def diameter(mesh):
    # TODO
    return None

def convexity(mesh):
    convex_hull = ConvexHull(mesh.vertices)
    return convex_hull

def eccentricity(mesh):
    eigenvalues, _ = Pipeline._eigen_vectors(None, mesh)
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