import json
import os
from datetime import datetime
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

BLOCKCHAIN_FILE = os.path.join(DATA_DIR, "blockchain.json")


def _load_chain_raw():
    """Load raw chain (list of dicts) from blockchain.json."""
    if not os.path.exists(BLOCKCHAIN_FILE):
        return []

    with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []


def _save_chain_raw(chain_list):
    """Save raw chain (list of dicts) to blockchain.json."""
    with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(chain_list, f, indent=2)


class Block:
    """
    Represents a single block in the chain.
    Fields:
      - index
      - timestamp
      - voter_hash (hashed username, not plain text)
      - election_id
      - candidate_id
      - previous_hash
      - hash
    """

    def __init__(self, index, timestamp, voter_hash, election_id, candidate_id, previous_hash, hash_):
        self.index = index
        self.timestamp = timestamp
        self.voter_hash = voter_hash
        self.election_id = election_id
        self.candidate_id = candidate_id
        self.previous_hash = previous_hash
        self.hash = hash_

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "voter_hash": self.voter_hash,
            "election_id": self.election_id,
            "candidate_id": self.candidate_id,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @staticmethod
    def from_dict(d):
        return Block(
            index=d["index"],
            timestamp=d["timestamp"],
            voter_hash=d["voter_hash"],
            election_id=d["election_id"],
            candidate_id=d["candidate_id"],
            previous_hash=d["previous_hash"],
            hash_=d["hash"],
        )


class Blockchain:
    """
    Simple blockchain to store votes.
    """

    def __init__(self):
        # Load existing chain or create a new one with a genesis block
        raw_chain = _load_chain_raw()
        if not raw_chain:
            # No chain yet, create genesis
            genesis = self._create_genesis_block()
            self.chain = [genesis]
            self._persist()
        else:
            self.chain = [Block.from_dict(b) for b in raw_chain]

    def _persist(self):
        """Save current chain to file."""
        _save_chain_raw([b.to_dict() for b in self.chain])

    @staticmethod
    def _calculate_hash(index, timestamp, voter_hash, election_id, candidate_id, previous_hash):
        """
        Calculate SHA-256 hash of block content.
        """
        content = f"{index}{timestamp}{voter_hash}{election_id}{candidate_id}{previous_hash}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_genesis_block(self):
        """
        First block in the chain. It doesn't represent a real vote.
        """
        index = 0
        timestamp = datetime.utcnow().isoformat()
        voter_hash = "GENESIS"
        election_id = -1
        candidate_id = -1
        previous_hash = "0"
        hash_ = self._calculate_hash(index, timestamp, voter_hash, election_id, candidate_id, previous_hash)
        return Block(index, timestamp, voter_hash, election_id, candidate_id, previous_hash, hash_)

    def get_last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash_username(username: str) -> str:
        """
        Hash the username so we don't store it in plain text in the blockchain.
        """
        return hashlib.sha256(username.encode("utf-8")).hexdigest()

    def add_vote_block(self, username: str, election_id: int, candidate_id: int) -> Block:
        """
        Create and append a new block representing a vote.
        """
        last_block = self.get_last_block()
        index = last_block.index + 1
        timestamp = datetime.utcnow().isoformat()
        voter_hash = self.hash_username(username)
        previous_hash = last_block.hash

        hash_ = self._calculate_hash(index, timestamp, voter_hash, election_id, candidate_id, previous_hash)

        new_block = Block(
            index=index,
            timestamp=timestamp,
            voter_hash=voter_hash,
            election_id=election_id,
            candidate_id=candidate_id,
            previous_hash=previous_hash,
            hash_=hash_,
        )

        self.chain.append(new_block)
        self._persist()
        return new_block

    def get_chain(self):
        """Return list of blocks."""
        return self.chain
    
    def is_valid(self):
        """
        Check that:
        - each block's hash is correct
        - each block's previous_hash matches the hash of the previous block
        Returns: (is_valid: bool, message: str)
        """
        if not self.chain:
            return False, "Blockchain is empty."

        for i, block in enumerate(self.chain):
            # Recalculate hash
            recalculated = self._calculate_hash(
                block.index,
                block.timestamp,
                block.voter_hash,
                block.election_id,
                block.candidate_id,
                block.previous_hash,
            )

            if block.hash != recalculated:
                return False, f"Invalid hash at block index {block.index}."

            # Check previous_hash linkage (skip for genesis block)
            if i > 0:
                prev_block = self.chain[i - 1]
                if block.previous_hash != prev_block.hash:
                    return False, f"Broken link between block {prev_block.index} and {block.index}."

        return True, "Blockchain is valid."




# Create a single global blockchain instance for the whole app
_blockchain_instance = Blockchain()


def add_vote_to_blockchain(username: str, election_id: int, candidate_id: int) -> Block:
    """
    Helper used by voting.py to add a vote block.
    """
    return _blockchain_instance.add_vote_block(username, election_id, candidate_id)


def get_blockchain():
    """
    Return the global blockchain instance (for reading / validation later).
    """
    return _blockchain_instance

def print_blockchain():
    """
    Pretty-print the blockchain to the console.
    """
    bc = get_blockchain()
    chain = bc.get_chain()

    if not chain:
        print("\nBlockchain is empty.")
        return

    print("\n=== BLOCKCHAIN ===")
    for block in chain:
        print(f"Index       : {block.index}")
        print(f"Timestamp   : {block.timestamp}")
        print(f"Voter Hash  : {block.voter_hash}")
        print(f"Election ID : {block.election_id}")
        print(f"Candidate ID: {block.candidate_id}")
        print(f"Prev Hash   : {block.previous_hash}")
        print(f"Hash        : {block.hash}")
        print("-" * 60)

def check_blockchain_integrity():
    """
    Run integrity check and print the result.
    Returns (is_valid, message).
    """
    bc = get_blockchain()
    is_valid, msg = bc.is_valid()
    if is_valid:
        print("\n✅ Blockchain integrity check PASSED.")
        print(f"   Details: {msg}")
    else:
        print("\n❌ Blockchain integrity check FAILED.")
        print(f"   Details: {msg}")
    return is_valid, msg
