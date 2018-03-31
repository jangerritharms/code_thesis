"""
Module describing the PublicKey class.
"""

class PublicKey(object):
    """
    The public key is the identifier of an agent on the network.
    """

    def __init__(self, bin_key):
        """
        Creates a public key object from the binary string representation.
        """
        self.bin_key = bin_key

    def to_hex(self):
        """
        Returns the significant part of the public key in hex encoding.
        """

        return self.bin_key.encode('hex')

    def to_base64(self):
        """
        Returns the significant part of the public key in base64 encoding.
        """

        return self.bin_key.encode('base64')[13:]

    def __hash__(self):
        return hash(self.bin_key)

    def __eq__(self, other):
        return self.bin_key == other.bin_key

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return self.to_base64()[:8]
