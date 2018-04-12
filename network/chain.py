"""
Module describing the chain class.
"""
import bisect

class Chain(object):
    """
    The chain class represents a hashchain of blocks of one agent. It is a
    convenience representation of all transactions of the agent.
    """

    def __init__(self, transactions = []):
        """
        Creates the chain from a set of transactions.
        """
        self.transactions = sorted(transactions, key=lambda x: x.sequence_number)

    def validate(self):
        """
        Checks the validity of a chain.
        """
        pass

    def get_blocks(self):
        """
        Returns the blocks the chain is made of.
        """
        return self.transactions

    def get_partner_agents(self):
        """
        Calculates the list of all agents that this agent has interacted with.
        """
        partners = []
        for block in self.transactions:
            if not block.link_public_key in partners:
                partners.append(block.link_public_key)
        return partners

    def is_complete(self):
        """
        Returns true if the chain is continuous and does not contain partly
        signed interactions.
        """
        j = 0
        while j < len(self) and self.transactions[j].sequence_number == -1:
            j = j + 1

        if j == len(self):
            return False

        for i in range(j, len(self)):
            if self.transactions[i].sequence_number != i-j:
                return False

        return True

    def up(self):
        """
        Returns the total amount of uploaded data.
        """
        return sum([t.contribution for t in self.transactions])

    def down(self):
        """
        Returns the total amount of downloaded data.
        """
        return sum([t.contribution - t.net_contribution for t in self.transactions])

    def add(self, transaction):
        """
        Adds a transaction to the chain.
        """
        bisect.insort(self.transactions, transaction)

    def net_contribution(self):
        """
        Calculates the net contribution of the agent.
        """
        return sum([t.net_contribution for t in self.transactions])

    def __len__(self):
        """
        Returns the length of the chain.
        """
        return len(self.transactions)

    def __repr__(self):
        """
        String representation of the chain.
        """
        return '\n'.join(['{}: @{} {}MB -> @{}'.format(x.sequence_number, x.public_key.to_base64()[:8],
                                                   x.net_contribution,
                                                   x.link_public_key.to_base64()[:8])
                          for x in self.transactions])
