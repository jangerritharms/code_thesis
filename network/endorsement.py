"""
Module describing the endorsement class.
"""

class Endorsement:
    """
    An endorsement is the outcome of a audit which checks the integrity of data
    and performs an exchange of private data between two agents.
    """
    def __init__(self, data):
        """
        Creates a new endorsement record from a list.
        """
        self.auditor = data[0]
        self.subject = data[1]
        self.outcome = data[2]
