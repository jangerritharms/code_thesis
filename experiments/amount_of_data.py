from network.network import Network
from attestation.database import MultiChainDB
import matplotlib.pyplot as plt
from progress.bar import Bar

def experiment():
    db = MultiChainDB('databases/multichain_09_02_18.db')
    net = Network.from_database(db)
    agents = net.list_agents()

    data_length = []
    for a in agents:
        agent = net.get_agent(a)
        data_length.append(len(agent.get_known_agents())/float(len(agents)))

    sorted_data_length = sorted(data_length)
    
    plt.scatter(range(len(agents)), sorted_data_length)
    
    net.increase_data_to_hops(2)

    data_length = []
    for a in Bar('getting data length').iter(agents):
        agent = net.get_agent(a)
        data_length.append(len(agent.get_known_agents())/float(len(agents)))

    sorted_data_length = sorted(data_length)
    
    plt.scatter(range(len(agents)), sorted_data_length, c='r')

    plt.savefig('datalength_full.png')
