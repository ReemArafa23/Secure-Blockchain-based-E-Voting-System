import json
import os
from datetime import datetime

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ELECTIONS_FILE = os.path.join(BASE_DIR, "data", "elections.json")
VOTES_FILE = os.path.join(BASE_DIR, "data", "votes.json")

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "actions.log")


# ---------- Helpers for reading data ----------

def _load_json_list(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []


def _load_elections():
    return _load_json_list(ELECTIONS_FILE)


def _load_votes():
    return _load_json_list(VOTES_FILE)


# ---------- Logging ----------

def log_action(username, action, details=""):
    """
    Append a simple log entry to logs/actions.log.
    Format: [timestamp] username | ACTION | details
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.utcnow().isoformat()
    user_display = username if username is not None else "-"
    line = f"[{ts}] {user_display} | {action} | {details}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ---------- Results / Reporting ----------

def _count_votes_for_election(election_id):
    """
    Return a dict: {candidate_id: count} for one election.
    """
    votes = _load_votes()
    counts = {}
    for v in votes:
        if v["election_id"] == election_id:
            cid = v["candidate_id"]
            counts[cid] = counts.get(cid, 0) + 1
    return counts


def show_results():
    """
    Print vote results for all elections.
    """
    elections = _load_elections()
    if not elections:
        print("\nNo elections configured yet.")
        return

    print("\n=== ELECTION RESULTS ===")
    for e in elections:
        print(f"\nElection ID {e['id']}: {e['title']}")
        print(f"Description: {e['description']}")
        counts = _count_votes_for_election(e["id"])

        candidates = e.get("candidates", [])
        if not candidates:
            print("  No candidates.")
            continue

        total_votes = sum(counts.get(c["id"], 0) for c in candidates)
        print(f"  Total votes: {total_votes}")
        print("  Candidates:")
        for c in candidates:
            c_votes = counts.get(c["id"], 0)
            print(f"    - {c['name']}: {c_votes} vote(s)")


def export_election_results_to_file():
    """
    Ask for an election ID, then write its results to a text file in /reports.
    """
    elections = _load_elections()
    if not elections:
        print("\nNo elections configured yet.")
        return

    try:
        election_id = int(input("Enter election ID to export results for: ").strip())
    except ValueError:
        print("❌ Invalid election ID.")
        return

    election = next((e for e in elections if e["id"] == election_id), None)
    if election is None:
        print("❌ Election not found.")
        return

    counts = _count_votes_for_election(election_id)
    candidates = election.get("candidates", [])

    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"election_{election_id}_results.txt"
    path = os.path.join(REPORTS_DIR, filename)

    total_votes = sum(counts.get(c["id"], 0) for c in candidates)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Election ID: {election['id']}\n")
        f.write(f"Title      : {election['title']}\n")
        f.write(f"Description: {election['description']}\n")
        f.write(f"Total votes: {total_votes}\n\n")
        f.write("Candidates:\n")
        for c in candidates:
            c_votes = counts.get(c["id"], 0)
            f.write(f"  - {c['name']}: {c_votes} vote(s)\n")

    print(f"\n✅ Results exported to: {path}")
    log_action(None, "EXPORT_RESULTS", f"election_id={election_id}, file={filename}")


# ---------- Security Info ----------

def show_security_info():
    """
    Print a simple explanation of the security mechanisms of this tool.
    Good for the discussion in the lab.
    """
    print("\n=== SECURITY INFORMATION ===")
    print("\n1) Authentication & Access Control")
    print("   - Users must register and login.")
    print("   - Passwords are never stored in plain text;")
    print("     we store a salted SHA-256 hash instead.")
    print("   - Each user has a role: ADMIN or VOTER.")
    print("   - Only admins can create elections or manage candidates.")

    print("\n2) Vote Integrity & Double-Voting Protection")
    print("   - Each voter can cast at most one vote per election.")
    print("   - Before saving a vote, the system checks if this user")
    print("     already voted in the same election.")

    print("\n3) Blockchain-based Storage of Votes")
    print("   - Every vote is also written into a simple blockchain.")
    print("   - Each block contains: election ID, candidate ID,")
    print("     a hash of the voter's username, and the previous block hash.")
    print("   - This creates an immutable chain: if someone changes")
    print("     a past block, its hash changes and the chain becomes invalid.")

    print("\n4) Blockchain Verification")
    print("   - Admin can run an integrity check over the whole chain.")
    print("   - The system recomputes all hashes and verifies the links")
    print("     between blocks to detect any tampering.")

    print("\n5) Logging & Audit Trail")
    print("   - Important actions (registration, login, voting,")
    print("     exporting results) are recorded in logs/actions.log.")
    print("   - Logs help investigate suspicious behaviour.")
