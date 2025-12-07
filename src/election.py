import json
import os
from reporting import log_action

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ELECTIONS_FILE = os.path.join(DATA_DIR, "elections.json")

def _load_elections():
    print("DEBUG ELECTIONS_FILE:", ELECTIONS_FILE)  # TEMP
    if not os.path.exists(ELECTIONS_FILE):
        print("DEBUG: elections.json does NOT exist")
        return []
    with open(ELECTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_elections(elections):
    with open(ELECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(elections, f, indent=2)


def _next_election_id(elections):
    """Get next integer ID for a new election."""
    if not elections:
        return 1
    return max(e["id"] for e in elections) + 1


def _next_candidate_id(election):
    """Get next candidate ID inside one election."""
    candidates = election.get("candidates", [])
    if not candidates:
        return 1
    return max(c["id"] for c in candidates) + 1


def create_election():
    """Interactive: admin creates a new election."""
    elections = _load_elections()

    print("\n=== Create New Election ===")
    title = input("Election title: ").strip()
    description = input("Description: ").strip()

    new_election = {
        "id": _next_election_id(elections),
        "title": title,
        "description": description,
        "is_active": False,  # initially closed
        "candidates": []
    }

    elections.append(new_election)
    _save_elections(elections)

    print(f"✅ Election created with ID {new_election['id']} (currently CLOSED).")


def list_elections(show_candidates=False):
    """Print all elections. If show_candidates=True, also print candidates."""
    elections = _load_elections()

    if not elections:
        print("\nNo elections found.")
        return

    print("\n=== Elections ===")
    for e in elections:
        status = "ACTIVE" if e.get("is_active") else "CLOSED"
        print(f"- ID: {e['id']} | {e['title']} [{status}]")
        print(f"  Description: {e['description']}")
        if show_candidates:
            candidates = e.get("candidates", [])
            if not candidates:
                print("  Candidates: (none yet)")
            else:
                print("  Candidates:")
                for c in candidates:
                    print(f"    [{c['id']}] {c['name']}")
        print()


def add_candidate_to_election():
    """Interactive: add candidate to an existing election."""
    elections = _load_elections()
    if not elections:
        print("\nNo elections exist. Create an election first.")
        return

    print("\n=== Add Candidate to Election ===")
    list_elections(show_candidates=False)
    try:
        election_id = int(input("Enter election ID: ").strip())
    except ValueError:
        print("❌ Invalid ID.")
        return

    # find election
    election = next((e for e in elections if e["id"] == election_id), None)
    if election is None:
        print("❌ Election not found.")
        return

    candidate_name = input("Candidate name: ").strip()
    if not candidate_name:
        print("❌ Candidate name cannot be empty.")
        return

    new_candidate = {
        "id": _next_candidate_id(election),
        "name": candidate_name
    }

    election.setdefault("candidates", []).append(new_candidate)
    _save_elections(elections)

    print(f"✅ Candidate '{candidate_name}' added to election '{election['title']}'.")


def toggle_election_status():
    """Open or close an election (toggle is_active)."""
    elections = _load_elections()
    if not elections:
        print("\nNo elections exist.")
        return

    print("\n=== Open/Close Election ===")
    list_elections(show_candidates=False)
    try:
        election_id = int(input("Enter election ID: ").strip())
    except ValueError:
        print("❌ Invalid ID.")
        return

    election = next((e for e in elections if e["id"] == election_id), None)
    if election is None:
        print("❌ Election not found.")
        return

    election["is_active"] = not election.get("is_active", False)
    _save_elections(elections)

    state = "ACTIVE" if election["is_active"] else "CLOSED"
    print(f"✅ Election '{election['title']}' is now {state}.")
    

def list_active_elections():
    """Helper for later (voting feature): return only active elections."""
    elections = _load_elections()
    return [e for e in elections if e.get("is_active")]

def print_active_elections(show_candidates=False):
    """Print only active elections, used by voters."""
    active = list_active_elections()

    if not active:
        print("\nNo ACTIVE elections at the moment.")
        return

    print("\n=== ACTIVE Elections ===")
    for e in active:
        print(f"- ID: {e['id']} | {e['title']} [ACTIVE]")
        print(f"  Description: {e['description']}")
        if show_candidates:
            candidates = e.get("candidates", [])
            if not candidates:
                print("  Candidates: (none yet)")
            else:
                print("  Candidates:")
                for c in candidates:
                    print(f"    [{c['id']}] {c['name']}")
        print()
