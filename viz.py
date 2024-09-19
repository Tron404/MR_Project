import vedo
import os
from vedo import show, Plotter
import numpy as np
from argparse import ArgumentParser

shape_path = "../ShapeDatabase_INFOMR"


arg_parse = ArgumentParser()
arg_parse.add_argument("-s", "--shape", choices=os.listdir(shape_path), type=str.title)
args = arg_parse.parse_args()

possible_shapes_path = os.path.join(shape_path, args.shape)
random_shape = np.random.choice(os.listdir(possible_shapes_path))

path = os.path.join(shape_path, args.shape, random_shape)
path = "../ShapeDatabase_INFOMR/City/m1660.obj"
obj = vedo.load_obj(path)[0]
obj = obj.color("grey").lw(1)

obj = obj.normalize()

def show_edges(widget, event):
    match widget.status():
        case "Show edges":
            obj.lw(1)
        case "Hide edges":
            obj.lw(0)
    widget.switch()

def make_orange(widget, event):
    match widget.status():
        case "Change to orange":
            obj.color("orange")
        case "Change to grey":
            obj.color("grey")
    widget.switch()

plt = Plotter()
plt += [obj]

plt.add_button(
    show_edges,
    states=("Hide edges","Show edges"),
    bc=("red4", "green4"),
    pos=(0.3,0.3)
)

plt.add_button(
    make_orange,
    states=("Change to orange", "Change to grey"),
    bc=("red4", "green4"),
    pos=(0.6,0.3)
)

show(obj, axes=1).close()