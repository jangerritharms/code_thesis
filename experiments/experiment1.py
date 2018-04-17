from experiments.base_experiment import BaseExperiment

class Experiment(BaseExperiment):

    def run(self):
        agent = self.net.get_agent('217dac55bdf709f408c')

        amount_of_data = []
        for i in range(35):
            self.net.pairwise_audit(agent)
            amount_of_data.append(len(agent.interactions.get_blocks()))

        self.result = amount_of_data
    
    def visualize(self):
        print self.result
