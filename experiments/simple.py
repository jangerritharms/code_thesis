from network.network import Network
from attestation.database import MultiChainDB



def experiment():
    db = MultiChainDB('databases/multichain_09_02_18.db')
    net = Network.from_database(db)
    net.clean_data()
    # agents = net.list_agents()

