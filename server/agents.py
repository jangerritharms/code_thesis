from twisted.web import resource

import json

class AgentsEndpoint(resource.Resource):

    def __init__(self, network):
        resource.Resource.__init__(self)
        self.network = network

    def getChild(self, path, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520)
        
        return AgentsSpecificEndpoint(self.network, path)

    def render_GET(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520)

        agents = self.network.list_agents()
        agents = [a.to_hex()[:12] for a in agents]
        return json.dumps(agents)

class AgentsSpecificEndpoint(resource.Resource):

    def __init__(self, network, path):
        self.network = network
        self.agent_query = path

    def render_GET(self, request):
        agent = self.network.get_agent(self.agent_query)

        return json.dumps(agent.to_dict())