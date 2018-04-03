"""
Module describing the Halfblock class.
"""
from attestation.public_key import PublicKey

class Halfblock(object):
    """
    Container for the TrustChain block information.
    """

    def __init__(self, data):
        """
        Creates a halfblock from a given data array.
        """
        self.contribution = data[0]
        self.net_contribution = data[1]
        self.public_key = PublicKey(data[2])
        self.sequence_number = data[3]
        self.link_public_key = PublicKey(data[4])
        self.link_sequence_number = data[5]
        self.previous_hash = data[6]
        self.signature = data[7]

    @classmethod
    def from_old_block(cls, block):
        """
        Creates two halfblocks from the original blocks.
        """

        block1 = cls([block.up, block.up-block.down, block.public_key_requester,
                      block.sequence_number_requester, block.public_key_responder,
                      block.sequence_number_responder, block.previous_hash_requester,
                      block.signature_requester])

        block2 = cls([block.down, block.down-block.up, block.public_key_responder,
                      block.sequence_number_responder, block.public_key_requester,
                      block.sequence_number_requester, block.previous_hash_responder,
                      block.signature_responder])

        return block1, block2

    def __lt__(self, other):
        return self.sequence_number < other.sequence_number

    def to_dict(self):
        """
        Returns json representation of the halfblock.
        """
        return {
            "contribution": self.contribution,
            "net_contribution": self.net_contribution,
            "public_key": self.public_key.to_hex(),
            "sequence_number": self.sequence_number,
            "link_public_key": self.link_public_key.to_hex(),
            "link_sequence_number": self.link_sequence_number,
            "previous_hash": self.previous_hash.encode('hex'),
            "signature": self.signature.encode('hex')
        }
