from base_experiment import BaseExperiment

class Experiment(BaseExperiment):
    """
    Text experiment to test functions.
    """
    def run(self):
        self.result = self.net.list_agents()

    def visualize(self):
        print self.result
