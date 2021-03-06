"""
This file contains everything related to persistence for MultiChain.
"""
import base64
import os
import sqlite3

from hashlib import sha256


DATABASE_DIRECTORY = os.path.join(u"sqlite")
# Path to the database location + dispersy._workingdirectory
DATABASE_PATH = os.path.join(DATABASE_DIRECTORY, u"multichain_09_02_18.db")
# Version to keep track if the db schema needs to be updated.
LATEST_DB_VERSION = 2
# Schema for the MultiChain DB.
schema = u"""
CREATE TABLE IF NOT EXISTS multi_chain(
 public_key_requester		TEXT NOT NULL,
 public_key_responder		TEXT NOT NULL,
 up                         INTEGER NOT NULL,
 down                       INTEGER NOT NULL,

 total_up_requester         UNSIGNED BIG INT NOT NULL,
 total_down_requester       UNSIGNED BIG INT NOT NULL,
 sequence_number_requester  INTEGER NOT NULL,
 previous_hash_requester	TEXT NOT NULL,
 signature_requester		TEXT NOT NULL,
 hash_requester		        TEXT PRIMARY KEY,

 total_up_responder         UNSIGNED BIG INT NOT NULL,
 total_down_responder       UNSIGNED BIG INT NOT NULL,
 sequence_number_responder  INTEGER NOT NULL,
 previous_hash_responder	TEXT NOT NULL,
 signature_responder		TEXT NOT NULL,
 hash_responder		        TEXT NOT NULL,

 insert_time                TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
 );

CREATE TABLE option(key TEXT PRIMARY KEY, value BLOB);
INSERT INTO option(key, value) VALUES('database_version', '""" + str(LATEST_DB_VERSION) + u"""');
"""

upgrade_to_version_2_script = u"""
DROP TABLE IF EXISTS multi_chain;
DROP TABLE IF EXISTS option;
"""


class MultiChainDB(object):
    """
    Persistence layer for the MultiChain Community.
    Connection layer to SQLiteDB.
    Ensures a proper DB schema on startup.
    """

    def __init__(self, path=DATABASE_PATH):
        """
        Sets up the persistence layer ready for use.
        :param dispersy: Dispersy stores the PK.
        :param working_directory: Path to the working directory
        that will contain the the db at working directory/DATABASE_PATH
        :return:
        """
        self._dbPath = os.path.join(os.getcwd(), path)
        self.blocks = None
        self.open()

    def add_block(self, block):
        """
        Persist a block
        :param block: The data that will be saved.
        """
        data = (buffer(block.public_key_requester), buffer(block.public_key_responder), block.up, block.down,
                block.total_up_requester, block.total_down_requester,
                block.sequence_number_requester, buffer(block.previous_hash_requester),
                buffer(block.signature_requester), buffer(block.hash_requester),
                block.total_up_responder, block.total_down_responder,
                block.sequence_number_responder, buffer(block.previous_hash_responder),
                buffer(block.signature_responder), buffer(block.hash_responder))

        self.execute(
            u"INSERT INTO multi_chain (public_key_requester, public_key_responder, up, down, "
            u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, "
            u"signature_requester, hash_requester, "
            u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, "
            u"signature_responder, hash_responder) "
            u"VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            data)
        self.commit()

    def get_stats(self):
        """
        Returns statistics about the database
        """
        stats = {}
        stats['unique_keys'] = len(self.get_unique_public_keys())
        stats['num_blocks'] = len(self.get_all_blocks())
        stats['first_block'] = self.get_all_blocks()[0].to_dictionary()
        stats['last_block'] = self.get_all_blocks()[-1].to_dictionary()

        return stats

    def update_block_with_responder(self, block):
        """
        Update an existing block
        :param block: The data that will be saved.
        """
        data = (
            block.total_up_responder, block.total_down_responder,
            block.sequence_number_responder, buffer(block.previous_hash_responder),
            buffer(block.signature_responder), buffer(block.hash_responder), buffer(block.hash_requester))

        self.execute(
            u"UPDATE multi_chain "
            u"SET total_up_responder = ?, total_down_responder = ?, "
            u"sequence_number_responder = ?, previous_hash_responder = ?, "
            u"signature_responder = ?, hash_responder = ? "
            u"WHERE hash_requester = ?",
            data)
        self.commit()

    def get_latest_hash(self, public_key):
        """
        Get the relevant hash of the latest block in the chain for a specific public key.
        Relevant means the hash_requester if the last block was a request,
        hash_responder if the last block was a response.
        :param public_key: The public_key for which the latest hash has to be found.
        :return: the relevant hash
        """
        public_key = buffer(public_key)
        db_query = u"SELECT block_hash FROM (" \
                   u"SELECT hash_requester AS block_hash, sequence_number_requester AS sequence_number " \
                   u"FROM multi_chain WHERE public_key_requester = ? " \
                   u"UNION " \
                   u"SELECT hash_responder AS block_hash, sequence_number_responder AS sequence_number " \
                   u"FROM multi_chain WHERE public_key_responder = ?) ORDER BY sequence_number DESC LIMIT 1"
        db_result = self.execute(db_query, (public_key, public_key)).fetchone()
        return str(db_result[0]) if db_result else None

    def get_latest_block(self, public_key):
        return self.get_by_hash(self.get_latest_hash(public_key))

    def get_by_hash_requester(self, hash_requester):
        """
        Returns a block saved in the persistence
        :param hash_requester: The hash_requester of the block that needs to be retrieved.
        :return: The block that was requested or None
        """
        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM `multi_chain` WHERE hash_requester = ? LIMIT 1"
        db_result = self.execute(db_query, (buffer(hash_requester),)).fetchone()
        # Create a DB Block or return None
        return self._create_database_block(db_result)

    def get_by_hash(self, hash):
        """
        Returns a block saved in the persistence, based on a hash that can be either hash_requester or hash_responder
        :param hash: The hash of the block that needs to be retrieved.
        :return: The block that was requested or None
        """
        if hash is None:
            return None

        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM `multi_chain` WHERE hash_requester = ? OR hash_responder = ? LIMIT 1"
        db_result = self.execute(db_query, (buffer(hash), buffer(hash))).fetchone()
        # Create a DB Block or return None
        return self._create_database_block(db_result)

    def get_by_public_key_and_sequence_number(self, public_key, sequence_number):
        """
        Returns a block saved in the persistence.
        :param public_key: The public key corresponding to the block
        :param sequence_number: The sequence number corresponding to the block.
        :return: The block that was requested or None"""
        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM (" \
                   u"SELECT *, sequence_number_requester AS sequence_number, " \
                   u"public_key_requester AS pk FROM `multi_chain` " \
                   u"UNION " \
                   u"SELECT *, sequence_number_responder AS sequence_number," \
                   u"public_key_responder AS pk FROM `multi_chain`) " \
                   u"WHERE sequence_number = ? AND pk = ? LIMIT 1"
        db_result = self.execute(db_query, (sequence_number, buffer(public_key))).fetchone()
        # Create a DB Block or return None
        return self._create_database_block(db_result)

    def get_blocks_since(self, public_key, sequence_number):
        """
        Returns database blocks with sequence number higher than or equal to sequence_number, at most 100 results
        :param public_key: The public key corresponding to the member id
        :param sequence_number: The linear block number
        :return A list of DB Blocks that match the criteria
        """
        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM (" \
                   u"SELECT *, sequence_number_requester AS sequence_number," \
                   u" public_key_requester AS public_key FROM `multi_chain` " \
                   u"UNION " \
                   u"SELECT *, sequence_number_responder AS sequence_number," \
                   u" public_key_responder AS public_key FROM `multi_chain`) " \
                   u"WHERE sequence_number >= ? AND public_key = ? " \
                   u"ORDER BY sequence_number ASC " \
                   u"LIMIT 100"
        db_result = self.execute(db_query, (sequence_number, buffer(public_key))).fetchall()
        return [self._create_database_block(db_item) for db_item in db_result]

    def get_blocks(self, public_key, limit=100):
        """
        Returns database blocks identified by a specific public key (either of the requester or the responder).
        Optionally limit the amount of blocks returned.
        :param public_key: The public key corresponding to the member id
        :param limit: The maximum number of blocks to return
        :return A list of DB Blocks that match the criteria
        """
        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM (" \
                   u"SELECT *, sequence_number_requester AS sequence_number," \
                   u" public_key_requester AS public_key FROM `multi_chain` " \
                   u"UNION " \
                   u"SELECT *, sequence_number_responder AS sequence_number," \
                   u" public_key_responder AS public_key FROM `multi_chain`) " \
                   u"WHERE public_key = ? " \
                   u"ORDER BY sequence_number DESC " \
                   u"LIMIT ?"
        db_result = self.execute(db_query, (buffer(public_key), limit)).fetchall()
        return [self._create_database_block(db_item) for db_item in db_result]

    def get_num_unique_interactors(self, public_key):
        """
        Returns the number of people you interacted with (either helped or that have helped you)
        :param public_key: The public key of the member of which we want the information
        :return: A tuple of unique number of interactors that helped you and that you have helped respectively
        """
        peers_you_helped = set()
        peers_helped_you = set()
        for block in self.get_blocks(public_key, limit=-1):
            if block.public_key_requester == public_key:
                if int(block.up) > 0:
                    peers_you_helped.add(block.public_key_responder)
                if int(block.down) > 0:
                    peers_helped_you.add(block.public_key_responder)
            else:
                if int(block.up) > 0:
                    peers_helped_you.add(block.public_key_requester)
                if int(block.down) > 0:
                    peers_you_helped.add(block.public_key_requester)
        return len(peers_you_helped), len(peers_helped_you)

    def _create_database_block(self, db_result):
        """
        Create a Database block or return None.
        :param db_result: The DB_result with the DatabaseBlock or None
        :return: DatabaseBlock if db_result else None
        """
        if db_result:
            return DatabaseBlock(db_result)
        else:
            return None

    def get_all_hash_requester(self):
        """
        Get all the hash_requester saved in the persistence layer.
        :return: list of hash_requester.
        """
        db_result = self.execute(u"SELECT hash_requester FROM multi_chain").fetchall()
        # Unpack the db_result tuples and decode the results.
        return [str(x[0]) for x in db_result]

    def contains(self, hash_requester):
        """
        Check if a block is existent in the persistence layer.
        :param hash_requester: The hash_requester that is queried
        :return: True if the block exists, else false.
        """
        db_query = u"SELECT hash_requester FROM multi_chain WHERE hash_requester = ? LIMIT 1"
        db_result = self.execute(db_query, (buffer(hash_requester),)).fetchone()
        return db_result is not None

    def get_latest_sequence_number(self, public_key):
        """
        Return the latest sequence number known for this public_key.
        If no block for the pk is know returns -1.
        :param public_key: Corresponding public key
        :return: sequence number (integer) or -1 if no block is known
        """
        public_key = buffer(public_key)
        db_query = u"SELECT MAX(sequence_number) FROM (" \
                   u"SELECT sequence_number_requester AS sequence_number " \
                   u"FROM multi_chain WHERE public_key_requester = ? UNION " \
                   u"SELECT sequence_number_responder AS sequence_number " \
                   u"FROM multi_chain WHERE public_key_responder = ? )"
        db_result = self.execute(db_query, (public_key, public_key)).fetchone()[0]
        return db_result if db_result is not None else -1

    def get_total(self, public_key):
        """
        Return the latest (total_up, total_down) known for this node.
        if no block for the pk is know returns (0,0)
        :param public_key: public_key of the node
        :return: (total_up (int), total_down (int)) or (0, 0) if no block is known.
        """
        public_key = buffer(public_key)
        db_query = u"SELECT total_up, total_down FROM (" \
                   u"SELECT total_up_requester AS total_up, total_down_requester AS total_down, " \
                   u"sequence_number_requester AS sequence_number FROM multi_chain " \
                   u"WHERE public_key_requester = ? UNION " \
                   u"SELECT total_up_responder AS total_up, total_down_responder AS total_down, " \
                   u"sequence_number_responder AS sequence_number FROM multi_chain WHERE public_key_responder = ? ) " \
                   u"ORDER BY sequence_number DESC LIMIT 1"
        db_result = self.execute(db_query, (public_key, public_key)).fetchone()
        return (db_result[0], db_result[1]) if db_result is not None and db_result[0] is not None \
                                               and db_result[1] is not None else (0, 0)

    def open(self, initial_statements=True, prepare_visioning=True):
        self._connection = sqlite3.connect(self._dbPath)
        self._cursor = self._connection.cursor()

    def close(self, commit=True):
        return super(MultiChainDB, self).close(commit)

    def check_database(self, database_version):
        """
        Ensure the proper schema is used by the database.
        :param database_version: Current version of the database.
        :return:
        """
        assert isinstance(database_version, unicode)
        assert database_version.isdigit()
        assert int(database_version) >= 0
        database_version = int(database_version)

        if database_version < LATEST_DB_VERSION:
            # Remove all previous data, since we have only been testing so far, and previous blocks might not be
            # reliable. In the future, we should implement an actual upgrade procedure
            self.executescript(upgrade_to_version_2_script)
            self.executescript(schema)
            self.commit()

        return LATEST_DB_VERSION

    def get_all_blocks(self, limit=-1):
        """
        Get all blocks in the database.
        :return: All blocks in the database
        """
        if self.blocks is None:
            db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                    u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                    u"signature_requester, hash_requester, " \
                    u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                    u"signature_responder, hash_responder, insert_time " \
                    u"FROM `multi_chain` " \
                    u"LIMIT ?"

            db_result = self.execute(db_query, (limit,)).fetchall()

            self.blocks = [self._create_database_block(db_item) for db_item in db_result]
        
        return self.blocks

    def get_unique_public_keys(self):
        """
        Compiles list of unique public keys used as either requester or responder.
        :return: list of unique public_keys
        """
        dbQuery = u"SELECT DISTINCT public_key FROM (" \
                  u"SELECT public_key_requester AS public_key FROM multi_chain " \
                  u"UNION " \
                  u"SELECT public_key_responder AS public_key FROM multi_chain)"

        db_result = self.execute(dbQuery).fetchall()
        return db_result

    def get_total_in_blocks(self, public_key):
        """
        Calculates the uploaded and downloaded data for a node proven in recorded blocks.
        :return: A tuple of (total_up, total_down)
        """
        public_key = buffer(public_key)
        db_query = u"SELECT SUM(total_up), SUM(total_down) FROM (" \
                   u"SELECT up AS total_up, down AS total_down " \
                   u"FROM multi_chain " \
                   u"WHERE public_key_requester = ? UNION " \
                   u"SELECT down AS total_up, up AS total_down " \
                   u"FROM multi_chain WHERE public_key_responder = ? ) " 
        db_result = self.execute(db_query, (public_key, public_key)).fetchone()

        return (db_result[0], db_result[1]) if db_result is not None and db_result[0] is not None \
                                               and db_result[1] is not None else (0, 0)

    def execute(self, statement, bindings=(), get_lastrowid=False):
        """
        Execute one SQL statement.

        A SQL query must be presented in unicode format.  This is to ensure that no unicode
        exeptions occur when the bindings are merged into the statement.

        Furthermore, the bindings may not contain any strings either.  For a 'string' the unicode
        type must be used.  For a binary string the buffer(...) type must be used.

        The SQL query may contain placeholder entries defined with a '?'.  Each of these
        placeholders will be used to store one value from bindings.  The placeholders are filled by
        sqlite and all proper escaping is done, making this the preferred way of adding variables to
        the SQL query.

        @param statement: the SQL statement that is to be executed.
        @type statement: unicode

        @param bindings: the values that must be set to the placeholders in statement.
        @type bindings: list, tuple, dict, or set

        @returns: unknown
        @raise sqlite.Error: unknown
        """
        if __debug__:
            assert self._cursor is not None, "Database.close() has been called or Database.open() has not been called"
            assert self._connection is not None, "Database.close() has been called or Database.open() has not been called"
            assert isinstance(statement, unicode), "The SQL statement must be given in unicode"
            assert isinstance(bindings, (tuple, list, dict, set)), "The bindings must be a tuple, list, dictionary, or set"

            # bindings may not be strings, text must be given as unicode strings while binary data,
            # i.e. blobs, must be given as a buffer(...)
            if isinstance(bindings, dict):
                tests = (not isinstance(binding, str) for binding in bindings.itervalues())
            else:
                tests = (not isinstance(binding, str) for binding in bindings)
            assert all(tests), "Bindings may not be strings.  Provide unicode for TEXT and buffer(...) for BLOB\n%s" % (statement,)
        
        result = self._cursor.execute(statement, bindings)
        if get_lastrowid:
            result = self._cursor.lastrowid
        return result

    def executescript(self, statements):
        assert self._cursor is not None, "Database.close() has been called or Database.open() has not been called"
        assert self._connection is not None, "Database.close() has been called or Database.open() has not been called"
        assert isinstance(statements, unicode), "The SQL statement must be given in unicode"

        return self._cursor.executescript(statements)
    
    def commit(self):
        """
        Write changes to the database.
        :return: 
        """
        self._connection.commit()

class DatabaseBlock:
    """ DataClass for a multichain block. """

    def __init__(self, data):
        """ Create a block from data """
        # Common part
        self.public_key_requester = str(data[0])
        self.public_key_responder = str(data[1])
        self.up = data[2]
        self.down = data[3]
        # Requester part
        self.total_up_requester = data[4]
        self.total_down_requester = data[5]
        self.sequence_number_requester = data[6]
        self.previous_hash_requester = str(data[7])
        self.signature_requester = str(data[8])
        self.hash_requester = str(data[9])
        # Responder part
        self.total_up_responder = data[10]
        self.total_down_responder = data[11]
        self.sequence_number_responder = data[12]
        self.previous_hash_responder = str(data[13])
        self.signature_responder = str(data[14])
        self.hash_responder = str(data[15])

        self.insert_time = data[16]

    def to_dictionary(self):
        """
        :return: (dict) a dictionary that can be sent over the internet.
        """
        return {
            "up": self.up,
            "down": self.down,
            "total_up_requester": self.total_up_requester,
            "total_down_requester": self.total_down_requester,
            "sequence_number_requester": self.sequence_number_requester,
            "previous_hash_requester": base64.encodestring(self.previous_hash_requester).strip(),
            "total_up_responder": self.total_up_responder,
            "total_down_responder": self.total_down_responder,
            "sequence_number_responder": self.sequence_number_responder,
            "previous_hash_responder": base64.encodestring(self.previous_hash_responder).strip(),
            "public_key_requester": base64.encodestring(self.public_key_requester).strip(),
            "signature_requester": base64.encodestring(self.signature_requester).strip(),
            "public_key_responder": base64.encodestring(self.public_key_responder).strip(),
            "signature_responder": base64.encodestring(self.signature_responder).strip(),
            "insert_time": self.insert_time
        }
