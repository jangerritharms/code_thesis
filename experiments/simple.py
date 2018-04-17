from base_experiment import BaseExperiment

class Experiment(BaseExperiment):
    """
    Test experiment to test functions.
    """
    def run(self):
        self.result = self.net.list_agents()

    def visualize(self):
        net_viz = self.viz.make_network_visualizer(self.net.interactions)
        net_viz.export('svg', 'network')
