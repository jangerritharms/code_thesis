from twisted.web import resource

import json

class AuditEndpoint(resource.Resource):

    def __init__(self, network):
        resource.Resource.__init__(self)
        self.network = network

    # def getChild(self, path, request):
    #     request.setHeader('Access-Control-Allow-Origin', '*')
    #     request.setHeader('Access-Control-Allow-Methods', 'GET')
    #     request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
    #     request.setHeader('Access-Control-Max-Age', 2520)
        
    #     return PagerankSpecificEndpoint(self.network, path)

    def render_GET(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520)

        node1 = request.args['node1']
        node2 = request.args['node2']
        print node1
        print node2
        agent1 = self.network.get_agent(node1[0])
        agent2 = self.network.get_agent(node2[0])
        
        print len(agent1.blocks)
        self.network.pairwise_audit(agent1, agent2)
        print len(agent1.blocks)

        return json.dumps([agent1.to_dict(), agent2.to_dict()])
