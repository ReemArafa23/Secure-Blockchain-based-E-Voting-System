import sys
from auth import register_user, login_user
from election import (
    create_election,
    list_elections,
    add_candidate_to_election,
    toggle_election_status,
    print_active_elections,
)
from voting import cast_vote
from blockchain import print_blockchain, check_blockchain_integrity


def guest_menu():
    """
    Menu shown when no one is logged in.
    """
    while True:
        print("\n=== Secure Blockchain-based E-Voting System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                user_menu(user)
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")


def user_menu(user):
    """
    Decide which menu to show based on role.
    """
    if user["role"] == "admin":
        admin_menu(user)
    else:
        voter_menu(user)


def admin_menu(user):
    """
    Admin-only functions: manage elections, candidates, and blockchain.
    """
    while True:
        print(f"\n=== ADMIN MENU ({user['username']}) ===")
        print("1. List elections")
        print("2. Create new election")
        print("3. Add candidate to election")
        print("4. Open/Close election")
        print("5. View blockchain")
        print("6. Verify blockchain integrity")
        print("7. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_elections(show_candidates=True)
        elif choice == "2":
            create_election()
        elif choice == "3":
            add_candidate_to_election()
        elif choice == "4":
            toggle_election_status()
        elif choice == "5":
            print_blockchain()
        elif choice == "6":
            check_blockchain_integrity()
        elif choice == "7":
            print("Logging out...")
            return
        else:
            print("Invalid choice, please try again.")


def voter_menu(user):
    """
    Voter functions: see active elections and cast a vote.
    """
    while True:
        print(f"\n=== VOTER MENU ({user['username']}) ===")
        print("1. List ACTIVE elections")
        print("2. Cast a vote")
        print("3. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print_active_elections(show_candidates=True)
        elif choice == "2":
            cast_vote(user)
        elif choice == "3":
            print("Logging out...")
            return
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    guest_menu()
