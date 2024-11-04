import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors
import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui
import pickle
import os
from matplotlib.backend_bases import MouseEvent
from sklearn.manifold import TSNE
from functools import partial
from distance import *
import warnings

sns.set_theme(style="whitegrid")

class TSNEPlot(QtWidgets.QWidget):
    point_hovered = QtCore.Signal(str)
    def __init__(self, figsize, dpi, num_bins, feature_weights):
        super().__init__()
        self.SHAPE_PATH = "../ShapeDatabase_INFOMR_norm"
        self.SHAPE_PATH_FEATURES = "../ShapeDatabase_INFOMR_norm_features"
        self.num_bins = num_bins
        self.feature_weights = feature_weights
        self.dpi = dpi
        self.figsize = figsize

        self.sns_colors = [
            "#FB5012", "#01FDF6", "#CBBAED", "#E9DF00", "#03FCBA", "#08415C",
            "#6610F2", "#E6AD29", "#187FC9", "#A85751", "#A6D9F7", "#57CC99"
        ]

        self.shown_classes = set()

        self.load_tsne_data()
        self.init_scatter()


    def init_scatter(self):
        # plt.figure(figsize=self.figsize, dpi=self.dpi)
        self.plot = sns.scatterplot()

    def create_tsne_data(self):
        fv = np.asarray(self.fv_df["feature_vector"].tolist())
        self.tsne_components = TSNE(n_components=2, metric=partial(distance, num_bins=self.num_bins, feature_weights=self.feature_weights)).fit_transform(fv)
        pickle.dump(self.tsne_components, open(f"{self.SHAPE_PATH_FEATURES}/tsne_2d_components.pickle", "wb"))

    def load_tsne_data(self):
        self.fv_df = pd.read_pickle(f"{self.SHAPE_PATH_FEATURES}/feature_vector_df_normalized.pickle")
        self.class_types = list(self.fv_df["class_type"].unique())
        self.class_types.sort()
        if "tsne_2d_components.pickle" not in os.listdir(self.SHAPE_PATH_FEATURES):
            warnings.warn("WARNING: No TSNE data found; creating, will take some time.")
            self.create_tsne_data()
        else:
            self.tsne_components = pickle.load(open(f"{self.SHAPE_PATH_FEATURES}/tsne_2d_components.pickle", "rb"))

    def update_tsne_plot(self, show_class, class_type):
        if show_class:
            self.shown_classes.add(class_type)
        else:
            self.shown_classes.remove(class_type)

        self.plot.clear()
        # plt.figure(figsize=self.figsize, dpi=self.dpi)
        self.fv_df_aux = self.fv_df[self.fv_df["class_type"].isin(self.shown_classes)]
        self.idx_aux = self.fv_df_aux.index.to_numpy()

        self.plot_labels = [f"{class_type}\n{obj_name}" for class_type, obj_name in zip(self.fv_df_aux.class_type.tolist(), self.fv_df_aux.obj_name.tolist())]
        self.class_labels = self.fv_df_aux.class_type.tolist()

        self.plot = sns.scatterplot(x=self.tsne_components[:,0][self.idx_aux], y=self.tsne_components[:,1][self.idx_aux], hue=self.class_labels, legend=True, palette=self.sns_colors)
        plt.legend(loc="upper center", bbox_to_anchor = (0.5, 1.15), frameon=False, ncols=len(self.shown_classes)//2)

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
        
        self.cursor_init()
        plt.savefig("Plots/tsne_plot.png", transparent=True)
        self.plot.figure.canvas.draw()

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
        name = f"{self.SHAPE_PATH}/{shape_class}/{shape_name}.obj"
        self.point_hovered.emit(name)