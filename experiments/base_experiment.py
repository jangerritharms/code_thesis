"""
This module defines the BaseExperiment class of which all Experiments are derived.
"""
from network.network import Network
from attestation.database import MultiChainDB
from visualization.handler import VisualizationHandler

class BaseExperiment(object):
    """
    The BaseExperiment defines the interface for an experiment.
    """

    def __init__(self, database):
        """
        Creates an experiment.
        """
        self.database = MultiChainDB(database)
        self.net = Network.from_database(self.database)
        self.viz = VisualizationHandler(self.net)
        self.result = None

    def _preprocessing(self):
        """
        Preprocess data.
        """
        pass

    def _run(self):
        """
        Runs the experiment and calculates the result.
        """
        self.run()

    def run(self):
        """
        Specific running function for the experiment.
        """

    def _visualize(self):
        """
        Visualizes the result of the experiment.
        """
        assert self.result is not None
        self.visualize()

    def visualize(self):
        """
        Specific visualization depending on the experiment.
        """
        pass
