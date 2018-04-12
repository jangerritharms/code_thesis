import networkx as nx
import matplotlib.pyplot as plt
from network.network import Network
from attestation.database import MultiChainDB

from bokeh.io import show, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, ZoomInTool, WheelZoomTool, PanTool, SaveTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4

def experiment():
    db = MultiChainDB('databases/multichain_09_02_18.db')
    net = Network.from_database(db)
    net.interaction_graph()

    G = net.IG
    plot = Plot(plot_width=1200, plot_height=800,
            x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
    plot.title.text = "Graph Interaction Demonstration"

    plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool(), WheelZoomTool(), PanTool(), SaveTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0,0))

    graph_renderer.node_renderer.glyph = Circle(size=3, fill_color=Spectral4[0])
    graph_renderer.node_renderer.selection_glyph = Circle(size=3, fill_color=Spectral4[2])
    graph_renderer.node_renderer.hover_glyph = Circle(size=3, fill_color=Spectral4[1])

    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
    graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
    graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = EdgesAndLinkedNodes()

    plot.renderers.append(graph_renderer)

    output_file("interactive_graphs.html")
    show(plot)

