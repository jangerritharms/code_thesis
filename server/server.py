from twisted.internet import reactor
from twisted.web import server

from root import RootEndpoint

class RESTManager(object):

    def __init__(self):
        self.root_endpoint = None
        self.network = None

    def start(self, network):
        self.network = network
        self.root_endpoint = RootEndpoint(network)
        site = server.Site(resource=self.root_endpoint)
        self.site = reactor.listenTCP(8088, site, interface="127.0.0.1")

    def run(self):
        reactor.run()