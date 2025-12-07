import json
import os
from election import list_active_elections
from blockchain import add_vote_to_blockchain
from reporting import log_action

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

VOTES_FILE = os.path.join(DATA_DIR, "votes.json")

def _load_votes():
    if not os.path.exists(VOTES_FILE):
        return []
    with open(VOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_votes(votes):
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, indent=2)

def _next_vote_id(votes):
    """Return next integer ID for a new vote."""
    if not votes:
        return 1
    return max(v["id"] for v in votes) + 1


def has_user_voted_in_election(username: str, election_id: int) -> bool:
    """
    Check in votes.json if this user already voted in this election.
    """
    votes = _load_votes()
    for v in votes:
        if v["voter_username"] == username and v["election_id"] == election_id:
            return True
    return False


def cast_vote(user):
    """
    Main function for a voter to cast a vote in an active election.
    Steps:
    - Show active elections
    - Choose election
    - Check if user already voted in that election
    - Show candidates
    - Choose candidate
    - Save vote to votes.json
    (Later we will also write to the blockchain here.)
    """
    username = user["username"]

    # Get active elections
    active = list_active_elections()
    if not active:
        print("\nNo ACTIVE elections available to vote.")
        return

    print("\n=== Vote in an Election ===")
    print("Available active elections:")
    for e in active:
        print(f"- ID: {e['id']} | {e['title']}")

    # Choose election
    try:
        election_id = int(input("Enter election ID to vote in: ").strip())
    except ValueError:
        print("❌ Invalid election ID.")
        return

    # Find the chosen election in the active list
    election = next((e for e in active if e["id"] == election_id), None)
    if election is None:
        print("❌ Election not found or not active.")
        return

    # Prevent double voting
    if has_user_voted_in_election(username, election_id):
        print("❌ You have already voted in this election.")
        return

    candidates = election.get("candidates", [])
    if not candidates:
        print("❌ This election has no candidates configured. Contact the admin.")
        return

    print(f"\nCandidates for '{election['title']}':")
    for c in candidates:
        print(f"- [{c['id']}] {c['name']}")

    # Choose candidate
    try:
        candidate_id = int(input("Enter candidate ID to vote for: ").strip())
    except ValueError:
        print("❌ Invalid candidate ID.")
        return

    candidate = next((c for c in candidates if c["id"] == candidate_id), None)
    if candidate is None:
        print("❌ No such candidate in this election.")
        return

    # Save vote in votes.json
    votes = _load_votes()
    new_vote = {
        "id": _next_vote_id(votes),
        "election_id": election_id,
        "voter_username": username,
        "candidate_id": candidate_id
    }
    votes.append(new_vote)
    _save_votes(votes)

    # Also store the vote in the blockchain
    new_block = add_vote_to_blockchain(username, election_id, candidate_id)

    print(f"✅ Your vote for '{candidate['name']}' has been recorded.")
    print(f"   → Blockchain block index: {new_block.index}")
    log_action(username, "VOTE",
               f"election_id={election_id}, candidate_id={candidate_id}, block_index={new_block.index}")

