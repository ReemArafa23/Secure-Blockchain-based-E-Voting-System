# 🗳️ Secure Blockchain-based E-Voting System  
A secure and transparent electronic voting system powered by **Python**, **Flask**, and a **custom blockchain implementation**.  
This project demonstrates how blockchain can ensure **vote integrity**, **tamper resistance**, and **transparency** in digital elections.

It includes:
- A **fully working backend** with JSON storage and blockchain hashing
- A Python **console application** for real voting operations
- A **beautiful web-based UI demo** (frontend only)
- Clean GitHub workflow (branches, issues, PRs, structure)

---

## 🚀 Overview

Electronic voting requires strict integrity, transparency, and security.  
This project implements:

- A simple blockchain where **each vote becomes a block**
- SHA-256 hashing for tamper prevention
- Admin features (create elections, open/close, add candidates)
- Voter features (view elections, cast votes, no double voting)
- A modern, user-friendly **web demo UI**

**Important Note:**  
The backend (Python) is the *real* implementation.  
The web UI is a **frontend demo** using browser `localStorage` — it does NOT modify backend JSON files.

---

## ⭐ Features

### 🔐 Authentication  
- Register users  
- Login with hashed passwords  
- First registered user becomes **ADMIN**  
- All later users become **VOTERS**

### 🧑‍💼 Admin Capabilities  
- Create elections  
- Add candidates  
- Open/Close elections  
- View blockchain ledger  
- Verify blockchain integrity  
- View final results

### 👤 Voter Capabilities  
- View active elections  
- Cast vote (double-voting blocked)  

### 🧱 Blockchain Features  
Every block includes:
- Voter Hash  
- Election ID  
- Candidate ID  
- Timestamp  
- Previous Block Hash  
- Current Hash (SHA-256)

Tampering with any block breaks the chain.

### 🌐 Web Frontend UI Demo  
Includes:
- Login/Register screen  
- Voter dashboard  
- Admin dashboard  
- Blockchain viewer  
- Results view  

**Used only for visualization** — does NOT write to backend JSON files.

---

## 📂 Project Architecture

📦 Secure-Blockchain-based-E-Voting-System
│
├── data/ # Real backend storage
│ ├── users.json
│ ├── elections.json
│ ├── votes.json
│ └── blockchain.json
│
├── src/ # Backend source code
│ ├── auth.py
│ ├── election.py
│ ├── voting.py
│ ├── blockchain.py
│ ├── reporting.py
│ └── main.py # Full console interface
│
├── web_frontend/ # UI demo files
│ ├── index.html
│
├── README.md # Main project documentation
└── api_server.py


---

## ⚙️ Installation

### **1. Install Python**
Python **3.10+** required.

### **2. Install dependencies**
pip install flask

---

## 🌐 Running the Web Frontend
### Start Flask:
python api_server.py

### Visit:
http://127.0.0.1:5000

The UI will load and store temporary demo data in localStorage.

---

## 📸 Screenshots
### 🔑 Login & Register
<img width="1420" height="697" alt="image" src="https://github.com/user-attachments/assets/576fe99a-57bb-4f86-a5f5-6c20fd383005" />

### 👤 Voter View
<img width="1401" height="628" alt="image" src="https://github.com/user-attachments/assets/3f2b7ce6-18c3-4409-836b-896e852d7a27" />

### 🧑‍💼 Admin View
<img width="1390" height="886" alt="image" src="https://github.com/user-attachments/assets/7f59c3d3-44d8-4b3d-bcb6-800aceebf353" />

---

##🧪 Blockchain Integrity
Run integrity check via admin menu or UI demo:
- Verifies every block’s SHA-256 hash
- Ensures no manipulation occurred
- Detects breaks in the chain instantly

---

# 🚀Thank You
