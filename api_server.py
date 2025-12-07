from flask import Flask, request, jsonify, send_from_directory, session
from flask import redirect
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import auth
import election
import voting
import blockchain
import reporting

app = Flask(__name__, static_folder="web_frontend", static_url_path="")
app.secret_key = "change-me-in-real-app"   # for sessions (ok for local demo)

@app.get("/api/ping")
def api_ping():
    print("DEBUG: /api/ping was called")
    return jsonify({"ok": True, "msg": "Hello from Python API"})

# ---------- helpers ----------

def current_user():
    username = session.get("username")
    role = session.get("role")
    if not username or not role:
        return None
    return {"username": username, "role": role}


def require_logged_in():
    user = current_user()
    if not user:
        return None, jsonify({"ok": False, "error": "Not logged in"}), 401
    return user, None, None


def require_admin():
    user = current_user()
    if not user:
        return None, jsonify({"ok": False, "error": "Not logged in"}), 401
    if user["role"] != "admin":
        return None, jsonify({"ok": False, "error": "Admin only"}), 403
    return user, None, None


# ---------- static front-end ----------

@app.route("/")
def index():
    # serve index.html from web_frontend folder
    return send_from_directory(app.static_folder, "index.html")


# ---------- auth endpoints ----------

@app.post("/api/register")
def api_register():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"ok": False, "error": "username and password required"}), 400

    users = auth._load_users()
    if any(u["username"] == username for u in users):
        return jsonify({"ok": False, "error": "username already exists"}), 400

    has_admin = any(u.get("role") == "admin" for u in users)
    role = "admin" if not has_admin else "voter"

    salt = auth._generate_salt()
    password_hash = auth._hash_password(password, salt)

    new_user = {
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "role": role,
    }
    users.append(new_user)
    auth._save_users(users)

    reporting.log_action(username, "REGISTER_API", f"role={role}")

    return jsonify({"ok": True, "role": role})


@app.post("/api/login")
def api_login():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    users = auth._load_users()
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        return jsonify({"ok": False, "error": "No such user"}), 400

    entered_hash = auth._hash_password(password, user["salt"])
    if entered_hash != user["password_hash"]:
        return jsonify({"ok": False, "error": "Incorrect password"}), 400

    session["username"] = user["username"]
    session["role"] = user["role"]

    reporting.log_action(username, "LOGIN_API", f"role={user['role']}")
    return jsonify({"ok": True, "username": user["username"], "role": user["role"]})


@app.post("/api/logout")
def api_logout():
    user = current_user()
    if user:
        reporting.log_action(user["username"], "LOGOUT_API", "")
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"ok": True, "user": None})
    return jsonify({"ok": True, "user": user})


# ---------- elections (admin) ----------

@app.get("/api/elections")
def api_list_elections():
    els = election._load_elections()
    return jsonify({"ok": True, "elections": els})


@app.post("/api/elections")
def api_create_election():
    user, resp, code = require_admin()
    if resp:
        return resp, code

    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    desc = (data.get("description") or "").strip()
    if not title:
        return jsonify({"ok": False, "error": "title required"}), 400

    els = election._load_elections()
    new_id = election._next_election_id(els)
    new_e = {
        "id": new_id,
        "title": title,
        "description": desc,
        "is_active": False,
        "candidates": [],
    }
    els.append(new_e)
    election._save_elections(els)
    reporting.log_action(user["username"], "CREATE_ELECTION_API", f"id={new_id}")
    return jsonify({"ok": True, "election": new_e})


@app.post("/api/elections/<int:eid>/candidates")
def api_add_candidate(eid):
    user, resp, code = require_admin()
    if resp:
        return resp, code

    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    els = election._load_elections()
    e = next((x for x in els if x["id"] == eid), None)
    if not e:
        return jsonify({"ok": False, "error": "Election not found"}), 404
    if not name:
        return jsonify({"ok": False, "error": "name required"}), 400

    cid = election._next_candidate_id(e)
    e.setdefault("candidates", []).append({"id": cid, "name": name})
    election._save_elections(els)
    reporting.log_action(user["username"], "ADD_CANDIDATE_API", f"election_id={eid}")
    return jsonify({"ok": True, "election": e})


@app.post("/api/elections/<int:eid>/toggle")
def api_toggle_election(eid):
    user, resp, code = require_admin()
    if resp:
        return resp, code

    els = election._load_elections()
    e = next((x for x in els if x["id"] == eid), None)
    if not e:
        return jsonify({"ok": False, "error": "Election not found"}), 404

    e["is_active"] = not e.get("is_active", False)
    election._save_elections(els)
    reporting.log_action(
        user["username"],
        "TOGGLE_ELECTION_API",
        f"election_id={eid}, active={e['is_active']}",
    )
    return jsonify({"ok": True, "election": e})


@app.get("/api/elections/active")
def api_active_elections():
    active = election.list_active_elections()
    return jsonify({"ok": True, "elections": active})


# ---------- voting ----------

@app.post("/api/vote")
def api_vote():
    user, resp, code = require_logged_in()
    if resp:
        return resp, code

    data = request.get_json(force=True)
    try:
        election_id = int(data.get("election_id"))
        candidate_id = int(data.get("candidate_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "invalid ids"}), 400

    # reuse your helpers
    if voting.has_user_voted_in_election(user["username"], election_id):
        return jsonify({"ok": False, "error": "Already voted in this election"}), 400

    votes = voting._load_votes()
    new_vote = {
        "id": voting._next_vote_id(votes),
        "election_id": election_id,
        "voter_username": user["username"],
        "candidate_id": candidate_id,
    }
    votes.append(new_vote)
    voting._save_votes(votes)

    block = blockchain.add_vote_to_blockchain(
        user["username"], election_id, candidate_id
    )

    reporting.log_action(
        user["username"],
        "VOTE_API",
        f"election_id={election_id}, candidate_id={candidate_id}, block={block.index}",
    )

    return jsonify({"ok": True, "block_index": block.index})


# ---------- blockchain + results ----------

@app.get("/api/blockchain")
def api_blockchain():
    bc = blockchain.get_blockchain()
    chain_dicts = [b.to_dict() for b in bc.get_chain()]
    return jsonify({"ok": True, "chain": chain_dicts})


@app.get("/api/blockchain/verify")
def api_blockchain_verify():
    bc = blockchain.get_blockchain()
    valid, msg = bc.is_valid()
    return jsonify({"ok": True, "valid": valid, "message": msg})


@app.get("/api/results")
def api_results():
    elections = election._load_elections()
    votes = voting._load_votes()
    out = []

    for e in elections:
        counts = {}
        for v in votes:
            if v["election_id"] == e["id"]:
                cid = v["candidate_id"]
                counts[cid] = counts.get(cid, 0) + 1
        out.append({"election": e, "counts": counts})

    return jsonify({"ok": True, "results": out})


if __name__ == "__main__":
    # static folder "web_frontend" must contain your index.html
    app.run(debug=True)
