from network.network import Network
from attestation.database import MultiChainDB

number_of_audits = 5

def experiment():
    db = MultiChainDB('databases/multichain_10000.db')
    net = Network.from_database(db)
    agents = net.list_agents()
    agent = net.get_agent('217dac55bdf709f408c')
    print [key.to_hex()[:10] for key in agent.get_hop_agents(1)]
    print [key.to_hex()[:10] for key in agent.get_hop_agents(2)]

    for i in range(number_of_audits):
        net.pairwise_audit(agent)
    
    print agent.contribution_accounting()

