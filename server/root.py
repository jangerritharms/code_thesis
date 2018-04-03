from twisted.web import resource

from agents import AgentsEndpoint
from pagerank import PagerankEndpoint
from audit import AuditEndpoint

class RootEndpoint(resource.Resource):

    def __init__(self, network):
        self.network = network
        resource.Resource.__init__(self)
        self.agents_endpoint = AgentsEndpoint(self.network)
        self.pagerank_endpoint = PagerankEndpoint(self.network)
        self.audit_endpoint = AuditEndpoint(self.network)
        self.putChild("agents", self.agents_endpoint)
        self.putChild("rank", self.pagerank_endpoint)
        self.putChild("audit", self.audit_endpoint)