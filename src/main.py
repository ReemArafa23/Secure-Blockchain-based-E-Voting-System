import sys
from auth import register_user, login_user


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
                # Go to user menu after successful login
                user_menu(user)
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")


def user_menu(user):
    """
    Menu shown after login (we will expand it later).
    For now it only shows role and allows logout.
    """
    while True:
        print(f"\n=== Welcome, {user['username']} ({user['role']}) ===")
        print("1. Show role")
        print("2. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print(f"Your role is: {user['role']}")
        elif choice == "2":
            print("Logging out...")
            return  # go back to guest_menu
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    guest_menu()
