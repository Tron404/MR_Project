import numpy as np
# generate a matrix (3, n_points) for 3D points
# row 0 == x-coordinate
# row 1 == y-coordinate
# row 2 == z-coordinate

n_points = 5000

x_coords = np.random.uniform(-10, 10, n_points)
y_coords = np.random.uniform(-3, 3, n_points)
z_coords = np.random.uniform(-1, 1, n_points)

A = np.zeros((3, n_points))
A[0] = x_coords
A[1] = y_coords
A[2] = z_coords

print(A.shape)

# compute the covariance matrix for A 
# see the documentation at 
# https://docs.scipy.org/doc/numpy/reference/generated/numpy.cov.html
# this function expects that each row of A represents a variable, 
# and each column a single observation of all those variables
A_cov = np.cov(A)  # 3x3 matrix

# computes the eigenvalues and eigenvectors for the 
# covariance matrix. See documentation at  
# https://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eig.html 
eigenvalues, eigenvectors = np.linalg.eig(A_cov)

print("==> eigenvalues for (x, y, z)")
print(eigenvalues)
print("\n==> eigenvectors")
print(eigenvectors)