"""
Module describing the Network class.
"""
import logging
import networkx as nx
from attestation.database import MultiChainDB
from attestation.public_key import PublicKey
from interaction_set import InteractionSet
from agent import Agent
from attestation.halfblock import Halfblock
from interface import NetworkInterface
from progress.bar import Bar

class Network(object):
    """
    The network class keeps track of the complete network data. It takes data
    from a database and automatically creates the known agents with their
    personal chains. The network object therefore has full knowledge of the
    interactions and can act as a reference.
    """

    def __init__(self, blocks):
        """
        Creates a new Network object.
        """
        self.agents = {}
        self.interactions = InteractionSet()
        self.interface = NetworkInterface(self)

        self.create_agents_from_blocks(blocks)

    def create_agents_from_blocks(self, blocks):
        """
        Populate the network with agents from the database.
        """
        progressbar = Bar('Creating agents', max=len(blocks))
        for block in blocks:
            public_key1 = PublicKey(block.public_key_requester)
            public_key2 = PublicKey(block.public_key_responder)

            agent_req = self.get_agent(public_key1)
            if agent_req is None:
                agent_req = self.add_agent(public_key1)
            agent_res = self.get_agent(public_key2)
            if agent_res is None:
                agent_res = self.add_agent(public_key2)

            block_req, block_res = Halfblock.from_old_block(block)
            agent_req.add_transaction(block_req)
            agent_res.add_transaction(block_res)
            self.interactions.add_blocks([block_req, block_res])
            progressbar.next()
        progressbar.finish()

    def set_accounting_policy(self, func):
        """
        Sets the accounting policy for agents to use.
        """
        for agent_key in self.agents:
            agent = self.get_agent(agent_key)
            agent.set_accounting_policy(func)


    @classmethod
    def from_database(cls, db_adapter):
        """
        Creates a network from a given database.

        :param db: A DatabaseAdapter object.
        """
        assert isinstance(db_adapter, MultiChainDB)
        blocks = db_adapter.get_all_blocks()

        return cls(blocks)

    @classmethod
    def from_file(cls, path):
        """
        Creates a network from a serialized network file.

        :param filename: Path to the network file.
        """
        pass

    def list_agents(self):
        """
        Returns the list of all agents in the network.
        """
        return self.agents

    def pairwise_audit(self, requester, responder=None):
        """
        Perform pairwise audit between two nodes.
        """
        assert isinstance(requester, Agent)

        if responder is not None:
            requester.initiate_pairwise_auditing(responder.public_key)
        else:
            requester.initiate_pairwise_auditing(None)

    def increase_data_to_hops(self, hops):
        """
        Increases the data to a certain amount of hops. Each agent
        will store at least all data from all agens `hops` hops away.
        """
        for agent_key in Bar('Increasing data').iter(self.agents):
            agent = self.get_agent(agent_key)
            agent.obtain_data_from_hops(hops)

    def add_agent(self, public_key):
        """
        Creates a new agent on the network.
        """
        assert isinstance(public_key, PublicKey)
        if self.get_agent(public_key) is not None:
            logging.warning("Agent already exists.")
            return None

        self.agents[public_key] = Agent(self.interface, public_key)

        return self.agents[public_key]

    def clean_data(self):
        """
        Clean network data such that only complete chains remain.
        """
        complete = 0
        removed_blocks = 0
        blocks_kept = 0
        for agent_key in Bar('Cleaning data').iter(self.agents):
            agent = self.get_agent(agent_key)
            if agent.chain.is_complete():
                complete += 1
                blocks_kept += len(agent.chain)
            else:
                removed_blocks += len(agent.chain)
                print agent.chain

        print complete
        print "Blocks kept: ", blocks_kept
        print "Removed blocks: ", removed_blocks

    def get_agent(self, public_key):
        """
        Tries to get an agent from the network. If it does not exist, it
        returns None.
        """
        if isinstance(public_key, str):
            results = []
            for key, agent in self.agents.iteritems():
                if public_key in key.to_hex() or public_key in key.to_base64():
                    results.append(agent)

            if len(results) == 1:
                return results[0]
            elif len(results) < 1:
                return None

            return results

        elif isinstance(public_key, PublicKey):
            return self.agents.get(public_key)
