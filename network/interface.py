"""
Module describing the interface for communicating on the network.
"""

class NetworkInterface(object):
    """
    The network interface through which agents can communicate.
    """

    def __init__(self, network):
        """
        Creates a new network interface.
        """
        self.network = network

    def send(self, public_key_receiver, message):
        """
        Send a message to an agent.
        """
        receiver = self.network.get_agent(public_key_receiver)
        receiver.receive(message)
