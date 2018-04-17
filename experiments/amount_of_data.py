from progress.bar import Bar
from base_experiment import BaseExperiment
import matplotlib.pyplot as plt

class Experiment(BaseExperiment):
    """
    Test experiment to test functions.
    """
    def run(self):
        agents = self.net.list_agents()

        data_length = []
        for a in agents:
            agent = self.net.get_agent(a)
            data_length.append(len(agent.interactions.list_public_keys())/float(len(agents)))

        self.result = [sorted(data_length)]

        self.net.increase_data_to_hops(2)

        data_length_after = []
        for a in Bar('getting data length').iter(agents):
            agent = self.net.get_agent(a)
            data_length_after.append(len(agent.interactions.list_public_keys())/float(len(agents)))

        self.result.append(sorted(data_length_after))

    def visualize(self):
        agents = self.net.list_agents()
        plt.scatter(range(len(agents)), self.result[0])
        plt.scatter(range(len(agents)), self.result[1], c='r')
        plt.savefig('datalength_full.png')

