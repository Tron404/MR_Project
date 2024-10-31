import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors
import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui
import pickle
from matplotlib.backend_bases import MouseEvent

sns.set_theme(style="whitegrid")

class TSNEPlot(QtWidgets.QWidget):
    point_hovered = QtCore.Signal(str)
    def __init__(self, figsize, dpi):
        super().__init__()
        self.shape_path = "../ShapeDatabase_INFOMR_norm"

        self.load_tsne_data()
        self.tsne_plot(figsize, dpi)

    def load_tsne_data(self):
        self.fv_df = pd.read_pickle("../ShapeDatabase_INFOMR_norm_features/feature_vector_df_normalized.pickle")
        self.tsne_components = pickle.load(open("../ShapeDatabase_INFOMR_norm_features/tsne_2d_components.pickle", "rb"))

        self.class_subset_1 = ["Ship", "House", "Tool", "Sign", "Door", "Car", "Monoplane", "Cellphone", "Knife", "Bus", "Humanoid", "Mug"]
        
        self.fv_df_aux = self.fv_df[self.fv_df["class_type"].isin(self.class_subset_1)]
        self.idx_aux = self.fv_df_aux.index.to_numpy()

        self.plot_labels = [f"{class_type}\n{obj_name}" for class_type, obj_name in zip(self.fv_df_aux.class_type.tolist(), self.fv_df_aux.obj_name.tolist())]
        self.class_labels = self.fv_df_aux.class_type.tolist()


    def tsne_plot(self, figsize, dpi):
        sns_colors = [
            "#FB5012", "#01FDF6", "#CBBAED", "#E9DF00", "#03FCBA", "#08415C",
            "#6610F2", "#E6AD29", "#187FC9", "#A85751", "#A6D9F7", "#57CC99"
        ]

        plt.figure(figsize=figsize, dpi=dpi)
        ax = sns.scatterplot(x=self.tsne_components[:,0][self.idx_aux], y=self.tsne_components[:,1][self.idx_aux], hue=self.class_labels, legend=True, palette=sns_colors)
        plt.legend(loc="upper center", bbox_to_anchor = (0.5, 1.1), frameon=False, ncols=len(self.class_subset_1)//2)

        self.highlight_kwargs = dict(
            # color="red",
            markeredgecolor="black",
            linewidth=1,
            markeredgewidth=3,
            # PathCollection.
            # facecolor="black",
            edgecolor="black",
        )

        self.annotation_kwargs = dict(
            bbox=dict(
                boxstyle="round,pad=.5",
                fc="orange",
                alpha=.7,
                ec="k",
            ),
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3",
                shrinkB=0,
                ec="k",
            ),
            ma="center"
        )
        
        self.plot = ax
        self.cursor_init()

    def cursor_init(self):
        self.cursor = mplcursors.cursor(self.plot, hover=mplcursors.HoverMode.Transient, highlight=True, highlight_kwargs=self.highlight_kwargs, annotation_kwargs=self.annotation_kwargs)
        self.cursor_click = mplcursors.cursor(self.plot, hover=mplcursors.HoverMode.NoHover, highlight=False, highlight_kwargs={}, annotation_kwargs={"alpha": 0})

        self.cursor.connect(
            "add", lambda x: x.annotation.set(text=self.plot_labels[x.index])
        )
        self.cursor_click.connect(
            "add", lambda x: x.annotation.set(text=self.plot_labels[x.index])
        )
        
        self.cursor_click.connect(
            "add", self.emit_hover_point
        )

    def reset(self):
        mouse_press_event = MouseEvent('button_press_event', self.plot.figure.canvas, 0, 0, button="LEFT")
        self.plot.figure.canvas.callbacks.process('button_press_event', mouse_press_event)

        mouse_release_event = MouseEvent('button_release_event', self.plot.figure.canvas, 0, 0, button="LEFT")
        self.plot.figure.canvas.callbacks.process('button_release_event', mouse_release_event)

        self.plot.figure.canvas.draw()

    def emit_hover_point(self, x):
        shape_class, shape_name = x.annotation.get_text().split("\n")
        shape_name = shape_name.removesuffix(".pickle")
        name = f"{self.shape_path}/{shape_class}/{shape_name}.obj"
        self.point_hovered.emit(name)