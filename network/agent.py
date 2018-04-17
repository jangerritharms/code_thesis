"""
This module defines the Agent class.
"""
from ranking.temporal_page_rank import calculate_tpr
from interaction_set import InteractionSet
from chain import Chain
from messages import Message, MessageTypes
from endorsement import Endorsement

class Agent(object):
    """
    An agent is the main entity that can attempt interactions. Agents have
    a personal hashchain which contains all their interactions of the past. Additionally
    they keep track of other interactions, together with their personal transactions
    this amounts to their private information set. Agents are identifiable by a public
    key, which we assume to be live-long.
    """

    def __init__(self, network_interface, public_key):
        """
        Creates a new agent with the given public_key.
        """
        self.interactions = InteractionSet()
        self.chain = Chain()
        self.public_key = public_key
        self.interface = network_interface
        self.messages = []
        self.accounting_policy = lambda *args: -1
        self.endorsements = []

    def subjective_interaction_graph(self):
        """
        Returns the subjective interaction graph of this agent.
        """
        pass

    def receive(self, message):
        """
        Handler for received messages.
        """

        self.messages.append(message)

        if message.type == MessageTypes.PA_BLOCKS:
            print "replying blocks"
            reply = Message(MessageTypes.PA_BLOCKS_REPLY,
                            self.public_key,
                            self.interactions.get_blocks())
            self.interactions.add_blocks(message.payload)
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.PA_BLOCKS_REPLY:
            print "sending score"
            self.interactions.add_blocks(message.payload)
            reply = Message(MessageTypes.PA_SCORE,
                            self.public_key,
                            True)
            self.interface.send(message.sender, reply)
            self.endorsements.append(Endorsement([self.public_key, message.sender, True]))
        if message.type == MessageTypes.PA_SCORE:
            print "replying score"
            reply = Message(MessageTypes.PA_SCORE_REPLY,
                            self.public_key,
                            True)
            self.endorsements.append(Endorsement([self.public_key, message.sender, True]))
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.CHAIN:
            reply = Message(MessageTypes.CHAIN_REPLY,
                            self.public_key,
                            self.chain)
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.CHAIN_REPLY:
            self.interactions.add_blocks(message.payload.get_blocks())

    def initiate_pairwise_auditing(self, public_key_responder):
        """
        Starts a pairwise auditing session with the agent corresponding to
        `public_key_responder`.
        """
        responder = public_key_responder
        if responder is None:
            responder = self.get_next_audit_partner()

        print "Starting audit with %s" % responder.to_hex()[:10]

        message = Message(MessageTypes.PA_BLOCKS, self.public_key, self.interactions.get_blocks())
        self.interface.send(responder, message)

    def get_endorsements_by_candidate(self, agent):
        """
        Returns a list of endorsements of an agent. If none exist,
        returns None.
        """

        result = []
        for endorsement in self.endorsements:
            if endorsement.subject == agent:
                result.append(endorsement)

        if len(result) == 0:
            return None

        return result

    def get_next_audit_partner(self):
        """
        Chooses a random audit partner that is close and has not been audited
        before.
        """

        hops = 1
        partner = None
        while not partner:
            hop_partners = self.get_hop_agents(hops)

            for candidate in hop_partners:
                if self.get_endorsements_by_candidate(candidate) is None:
                    return candidate

            hops += 1

    def set_accounting_policy(self, func):
        """
        Sets the accounting policy.
        """
        self.accounting_policy = func

    def request_data(self, public_key):
        """
        Requets chain from agent with public_key.
        """
        message = Message(MessageTypes.CHAIN, self.public_key)
        self.interface.send(public_key, message)

    def obtain_data_from_hops(self, hops):
        """
        Get the chains of all known agents.
        """
        if hops < 2:
            return

        partners = self.chain.get_partner_agents()
        for _ in range(1, hops):
            new_partners = []

            for partner in partners:
                self.request_data(partner)
                chain = self.messages[-1].payload
                new_partners += chain.get_partner_agents()

            partners += new_partners

    def get_hop_agents(self, hops):
        """
        Get all agents from a specific hop distance.
        """
        partners = self.chain.get_partner_agents()
        if hops == 1:
            return partners

        for i in range(1, hops):
            new_partners = []

            for partner in partners:
                self.request_data(partner)
                chain = self.messages[-1].payload
                print chain
                new_partners += chain.get_partner_agents()

            if i == hops:
                return new_partners
            else:
                partners += new_partners

        return []

    def calculate_ranking(self):
        """
        Calculates a ranking of known agents.
        """
        return calculate_tpr(self.public_key, self.interactions.get_blocks())

    def calculate_score(self, public_key):
        """
        Calculates a ranking of known agents and returns the score corresponding
        to the given public key.
        """

        rank = calculate_tpr(self.public_key, self.interactions.get_blocks())
        result = -1
        for key, score in rank.iteritems():
            if key == public_key:
                result = score
        return result

    def contribution_accounting(self):
        """
        Defines a simple accounting policy which takes into account only
        the contirbution of the known agents.
        """
        contributions = {}

        for agent_key in self.interactions.list_public_keys():
            contributions[agent_key] = self.interactions.get_known_contributions(agent_key)

        return contributions

    def add_transaction(self, halfblock):
        """
        Adds a transaction to the personal database.
        """
        self.interactions.add_block(halfblock)

        if halfblock.public_key == self.public_key:
            self.chain.add(halfblock)

    def get_interaction_set(self):
        """
        Returns the private database of the agent.
        """
        return self.interactions

    def get_personal_chain(self):
        """
        Returns the personal chain of the agent.
        """
        return self.chain

    def __str__(self):
        """
        String representation of an agent object.
        """
        return self.__repr__()

    def __repr__(self):
        """
        String representation of an agent object.
        """
        return "Agent<@%s>" % self.public_key.to_base64()[:8]

    def to_dict(self):
        """
        Python dictionary representation of the agent object.
        """
        return {
            "public_key": self.public_key.to_hex(),
            "chain_length": len(self.chain),
            "up": self.chain.up(),
            "down": self.chain.down(),
            "blocks": self.interactions.to_list(),
            "hop1": [key.to_hex() for key in self.get_hop_agents(1)],
            "hop2": [key.to_hex() for key in self.get_hop_agents(2)],
        }
