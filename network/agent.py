"""
This module defines the Agent class.
"""
from ranking.temporal_page_rank import calculate_tpr
from chain import Chain
from messages import Message, MessageTypes

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
        self.blocks = []
        self.chain = Chain()
        self.public_key = public_key
        self.interface = network_interface
        self.messages = []

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

        if message.type == MessageTypes.PA_INDEX:
            print message.payload
            self.interface.send(message.sender, Message(MessageTypes.PA_INDEX_REPLY,
                                                        self.public_key, self.create_index()))
        if message.type == MessageTypes.PA_INDEX_REPLY:
            print message.payload
            reply = Message(MessageTypes.PA_BLOCKS,
                            self.public_key,
                            self.index_difference(self.create_index(), message.payload))
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.PA_BLOCKS:
            reply = Message(MessageTypes.PA_BLOCKS_REPLY,
                            self.public_key,
                            self.index_difference(self.create_index(), self.messages[-2].payload))
            print message.payload
            self.blocks += message.payload
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.PA_BLOCKS_REPLY:
            print message.payload
            self.blocks += message.payload
            reply = Message(MessageTypes.PA_SCORE,
                            self.public_key,
                            self.calculate_score(message.sender))
            self.interface.send(message.sender, reply)
        if message.type == MessageTypes.PA_SCORE:
            reply = Message(MessageTypes.PA_SCORE_REPLY,
                            self.public_key,
                            self.calculate_score(message.sender))

    def initiate_pairwise_auditing(self, public_key_responder):
        """
        Starts a pairwise auditing session with the agent corresponding to
        `public_key_responder`.
        """
        message = Message(MessageTypes.PA_INDEX, self.public_key, self.create_index())
        self.interface.send(public_key_responder, message)

    def create_index(self):
        """
        Create an index from the set of blocks.
        """
        index = {}

        for block in self.blocks:
            index.setdefault(block.public_key, []).append(block.sequence_number)

        return index

    def index_difference(self, own_index, other_index):
        """
        Calculates which blocks the agents own that the opposite does not own,
        and returns those blocks from the block storage.
        """

        blocks = []
        for key, block_list in own_index.iteritems():
            if not key in other_index:
                for block in block_list:
                    blocks.append(self.get_block(key, block))
                continue

            for block in block_list:
                if not block in other_index[key]:
                    blocks.append(self.get_block(key, block))

        return blocks

    def get_block(self, public_key, sequence_number):
        """
        Get a block given by the public_key and sequence number from the block
        storage.
        """
        for block in self.blocks:
            if block.public_key == public_key and block.sequence_number == sequence_number:
                return block

    def calculate_score(self, public_key):
        """
        Calculates a ranking of known agents and returns the score corresponding
        to the given public key.
        """

        rank = calculate_tpr(self.public_key, self.blocks)
        result = -1
        for key, score in rank.iteritems():
            if key == public_key:
                result = score 
        return result

    def add_transaction(self, halfblock):
        """
        Adds a transaction to the personal database.
        """
        self.blocks.append(halfblock)

        if halfblock.public_key == self.public_key:
            self.chain.add(halfblock)

    def get_blocks(self):
        """
        Returns the private database of the agent.
        """
        return self.blocks

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
