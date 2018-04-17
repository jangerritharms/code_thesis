"""
Module defining the InteractionSet class.
"""
import networkx as nx

from chain import Chain

class InteractionSet(object):
    """
    An interaction set is the database of known interaction records.
    """

    def __init__(self):
        """
        Creates a new interaction set from the block records.
        """
        self.halfblocks = set([])
        self.graph = None

    def add_block(self, block):
        """
        Adds a new block to the interaction set.

        :param block: A single halfblock
        """
        self.halfblocks |= set([block])

    def add_blocks(self, blocks):
        """
        Adds multiple blocks to the interaction set.

        :param blocks: List of halfblocks
        """
        assert isinstance(blocks, list)
        self.halfblocks |= set(blocks)

    def list_public_keys(self):
        """
        Returns the list of all known public keys in the network.
        """
        responders = [block.public_key for block in self.halfblocks]
        requesters = [block.link_public_key for block in self.halfblocks]
        responders.extend(requesters)

        return set(responders)

    def build_graph(self):
        """
        Returns an interaction graph of the complete network.
        """
        self.graph = nx.DiGraph()

        def update_graph(graph, pubkey1, pubkey2, contrib):
            """
            Adds an edge to a graph
            """
            try:
                old = graph[pubkey1][pubkey2]['capacity']
                graph.add_edge(pubkey1, pubkey2, capacity=(old+contrib))
            except KeyError:
                graph.add_edge(pubkey1, pubkey2, capacity=contrib)

        for block in self.halfblocks:

            pubkey_req = block.public_key.to_hex()[:10]
            pubkey_res = block.link_public_key.to_hex()[:10]
            up_data = block.contribution

            update_graph(self.graph, pubkey_req, pubkey_res, up_data)

        return self.graph

    def get_known_contributions(self, agent):
        """
        Calculates the known contributions for a known agent.
        """
        agent_blocks = [block for block in self.halfblocks if block.public_key == agent]
        agent_chain = Chain(agent_blocks)

        return agent_chain.up()

    def get_block(self, public_key, sequence_number):
        """
        Get a block given by the public_key and sequence number from the block
        storage.
        """
        for block in self.halfblocks:
            if block.public_key == public_key and block.sequence_number == sequence_number:
                return block

    def get_blocks(self):
        """
        Returns all blocks contained in the set.
        """
        return list(self.halfblocks)

    def to_list(self):
        """
        Returns a list of dicts which represent the data contained in the
        interaction set.
        """
        return [block.to_dict() for block in self.halfblocks]
