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
        return '\n'.join(['@{} {}MB -> @{}'.format(x.public_key.to_base64()[:8],
                                                   x.net_contribution,
                                                   x.link_public_key.to_base64()[:8])
                          for x in self.transactions])
