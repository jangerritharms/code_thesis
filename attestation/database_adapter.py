"""
Module defining the DatabaseAdapter class.
"""
import os

from attestation.database import MultiChainDB

class DatabaseAdapter:
    """
    The DatabaseAdapter can access transaction stored in a SQLite database.
    """

    def __init__(self, path):
        """
        Creates a new DatabaseAdapter from a given sqlite file.

        :param path: Path to sqlite database.
        """
        self.db = MultiChainDB(os.path.join("databases", path))
