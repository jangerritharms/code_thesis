from network.network import Network
from attestation.database import MultiChainDB
from server.server import RESTManager

db = MultiChainDB('databases/multichain_09_02_18.db')
net = Network.from_database(db)
rm = RESTManager()
rm.start(net)
rm.run()