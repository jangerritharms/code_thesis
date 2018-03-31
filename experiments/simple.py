from network.network import Network
from attestation.database import MultiChainDB



def experiment():
    db = MultiChainDB('databases/multichain_1000.db')
    net = Network.from_database(db)
    agents = net.list_agents()

    net.pairwise_audit(agents.values()[0], agents.values()[1])
