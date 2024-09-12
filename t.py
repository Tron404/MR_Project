from MeshObject import *

mesh = MeshObject("../ShapeDatabase_INFOMR/Wheel/m748.obj", visualize=True)
mesh.vedo_mesh = mesh.vedo_mesh.normalize()
mesh.show()