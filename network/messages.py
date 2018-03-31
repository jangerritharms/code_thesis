"""
Module defining messages that agents can send to each other.
"""

class MessageTypes(object):
    PA_INDEX = 1
    PA_INDEX_REPLY = 2
    PA_BLOCKS = 3
    PA_BLOCKS_REPLY = 4
    PA_SCORE = 5
    PA_SCORE_REPLY = 6

class Message(object):
    """
    Message class defining an exchange of data between two agents.
    """

    def __init__(self, message_type, sender, payload):
        """
        Creates a message of given type and with the given payload.
        """

        self.type = message_type
        self.payload = payload
        self.sender = sender 
