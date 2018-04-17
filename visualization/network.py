"""
Module defining the Network visualizer.
"""
import networkx as nx

from bokeh.io import show, output_file, export_png, export_svgs
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, WheelZoomTool, PanTool, SaveTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4

class NetworkVisualizer(object):
    """
    The NetworkVisualizer provides convenient functions for creating visualizations
    of the network.
    """

    def __init__(self, interactions):
        """
        Creates the NetworkVisualizer from a given network.
        """
        self.interactions = interactions
        self.title = "Network"
        self.plot = None

    def build_plot(self):
        """
        Creates the plot of the network.
        """
        self.graph = self.interactions.build_graph()
        self.plot = Plot(plot_width=1200, plot_height=800,
                         x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1),
                         output_backend="svg")
        self.plot.title.text = self.title

        self.plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool(), WheelZoomTool(), PanTool(), SaveTool())

        graph_renderer = from_networkx(self.graph, nx.spring_layout, scale=1, center=(0, 0))

        graph_renderer.node_renderer.glyph = Circle(size=3, fill_color=Spectral4[0])
        graph_renderer.node_renderer.selection_glyph = Circle(size=3, fill_color=Spectral4[2])
        graph_renderer.node_renderer.hover_glyph = Circle(size=3, fill_color=Spectral4[1])

        graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
        graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
        graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

        graph_renderer.selection_policy = NodesAndLinkedEdges()
        graph_renderer.inspection_policy = EdgesAndLinkedNodes()

        self.plot.renderers.append(graph_renderer)


    def interactive(self):
        """
        Creates an interactive network to be viewed in the browser.
        """
        output_file("interactive_graphs.html")
        show(self.plot)

    def export(self, export_format, filename):
        """
        Exports the graph in the given export_format and filename.
        """
        if self.plot == None:
            self.build_plot()

        if export_format == 'png':
            export_png(self.plot, filename=filename+'.'+export_format)
        elif export_format == 'svg':
            export_svgs(self.plot, filename=filename+'.'+export_format)
        else:
            print 'unknown format'
