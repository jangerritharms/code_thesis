"""
Module defining the Visualization handler.
"""
from visualization.network import NetworkVisualizer

class VisualizationHandler(object):
    """
    The visualization handler object keeps a handle to the network instance
    and defines functions for visualizing different information.
    """

    def __init__(self, network):
        """
        Creates the visualization handler instance.
        """
        self.network = network

    def make_network_visualizer(self, graph):
        """
        Creates a network visualizer.
        """
        return NetworkVisualizer(graph)
