import networkx as nx
import matplotlib.pyplot as plt
from network.network import Network
from attestation.database import MultiChainDB

def experiment():
    db = MultiChainDB('databases/multichain_10000.db')
    net = Network.from_database(db)
    net.interaction_graph()

    nx.draw(net.IG, pos=nx.spring_layout(net.IG, k=.15), with_labels=True, font_color='g')
    plt.show()
