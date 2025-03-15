#!/usr/bin/env python3

import os
import json
import shutil
from pathlib import Path
import subprocess
from typing import Dict, List

# Where we store the info about multiple Signal profiles
MANAGER_CONFIG_DIR = Path.home() / ".config" / "signal_account_manager"
ACCOUNTS_JSON = MANAGER_CONFIG_DIR / "accounts.json"

DEFAULT_SIGNAL_DIR = Path.home() / ".config" / "Signal"  # The standard Signal Desktop config dir
DEFAULT_ACCOUNT_NAME = "Default"                        # Label for the automatically-detected default

def ensure_config_dir() -> None:
    """
    Ensure the config directory and accounts.json file exist.
    Creates the file if it does not exist.
    """
    MANAGER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not ACCOUNTS_JSON.exists():
        with open(ACCOUNTS_JSON, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_accounts() -> List[Dict[str, str]]:
    """
    Load the list of accounts from JSON.
    Returns a list of dictionaries with 'name' and 'profile_dir'.
    """
    with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_accounts(accounts: List[Dict[str, str]]) -> None:
    """
    Save the list of accounts to JSON.
    Each account is a Dict with at least 'name' and 'profile_dir'.
    """
    with open(ACCOUNTS_JSON, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

def is_signal_installed() -> bool:
    """
    Check if 'signal-desktop' is found on the PATH.
    Returns True if installed, False otherwise.
    """
    return shutil.which("signal-desktop") is not None

def auto_add_default_signal() -> None:
    """
    If the default Signal directory exists and is not in our accounts list,
    add it automatically as the 'Default' account.
    """
    if not DEFAULT_SIGNAL_DIR.exists():
        return  # Default directory doesn't exist, so nothing to do

    accounts = load_accounts()

    # Check if we already have an entry that uses ~/.config/Signal
    for acc in accounts:
        # Compare absolute paths
        if Path(acc["profile_dir"]).resolve() == DEFAULT_SIGNAL_DIR.resolve():
            return  # Already added

    # If we're here, ~/.config/Signal exists but isn't in the list
    new_account = {
        "name": DEFAULT_ACCOUNT_NAME,
        "profile_dir": str(DEFAULT_SIGNAL_DIR)
    }
    accounts.append(new_account)
    save_accounts(accounts)
    print(f"Detected existing default Signal directory and added it as '{DEFAULT_ACCOUNT_NAME}' account.")

def list_accounts() -> None:
    """
    Print the list of existing accounts to the console.
    """
    accounts = load_accounts()
    if not accounts:
        print("No accounts found.")
    else:
        print("Existing accounts:")
        for i, acc in enumerate(accounts, start=1):
            print(f"  {i}) {acc['name']} -> {acc['profile_dir']}")

def create_desktop_icon(account_name: str, profile_dir_str: str) -> None:
    """
    Create a .desktop file for the given account so the user can launch Signal
    with this profile directly from their application menu or desktop.
    """
    # Where we'll place the .desktop file (typical location in many Linux distros)
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)

    # File name might be "Signal-Work.desktop" for example
    sanitized_name = account_name.replace(" ", "_")
    desktop_path = applications_dir / f"Signal-{sanitized_name}.desktop"

    # .desktop file content
    desktop_file_content = f"""[Desktop Entry]
Name=Signal - {account_name}
Comment=Launch Signal for the '{account_name}' profile
Exec=signal-desktop --user-data-dir="{profile_dir_str}"
Terminal=false
Type=Application
Icon=signal-desktop
Categories=Network;InstantMessaging;"""

    # Write the .desktop file
    with open(desktop_path, "w", encoding="utf-8") as f:
        f.write(desktop_file_content)

    # Make it executable
    desktop_path.chmod(0o755)

    print(f"Created a desktop launcher: {desktop_path}")

def add_account() -> None:
    """
    Add a new account by creating a new profile directory and storing it in JSON.
    After adding, optionally create a desktop icon.
    """
    accounts = load_accounts()
    name = input("Enter a label for this new account (e.g., 'Work', 'Personal'): ").strip()

    profile_dir = Path.home() / f".config/Signal-{name.replace(' ', '_')}"
    profile_dir_str = str(profile_dir)

    if profile_dir.exists():
        print(f"Directory {profile_dir_str} already exists. "
              "If it’s a valid Signal profile, you can add it anyway or choose a different name.")
    else:
        profile_dir.mkdir(parents=True, exist_ok=True)

    accounts.append({"name": name, "profile_dir": profile_dir_str})
    save_accounts(accounts)
    print(f"Account '{name}' added. When you first launch it, you must link it with your phone.")

    # Ask if user wants to create a .desktop launcher
    create_icon = input("Create a new desktop launcher icon for this account? (y/n): ").lower()
    if create_icon == 'y':
        create_desktop_icon(name, profile_dir_str)
    else:
        print("Skipping desktop launcher creation.")

def select_account() -> None:
    """
    Allow the user to select an existing account and launch Signal with that profile.
    """
    accounts = load_accounts()
    if not accounts:
        print("No accounts to select.")
        return

    list_accounts()
    choice = input("Enter the number of the account you want to launch: ").strip()
    try:
        idx = int(choice) - 1
        acc = accounts[idx]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    profile_dir = acc["profile_dir"]
    print(f"Launching Signal for account '{acc['name']}' using directory {profile_dir} ...")
    subprocess.Popen(["signal-desktop", f"--user-data-dir={profile_dir}"])
    print("Signal launched. You can close this script or continue to manage other accounts.")

def get_desktop_file_path(account_name: str) -> Path:
    """
    Given an account name, return the expected path for its .desktop file in
    ~/.local/share/applications.
    """
    sanitized_name = account_name.replace(" ", "_")
    return Path.home() / ".local" / "share" / "applications" / f"Signal-{sanitized_name}.desktop"

def delete_account() -> None:
    """
    Delete an account from the manager, optionally removing its profile directory.
    Also remove the corresponding .desktop file if it was created.
    """
    accounts = load_accounts()
    if not accounts:
        print("No accounts to delete.")
        return

    list_accounts()
    choice = input("Enter the number of the account to delete: ").strip()
    try:
        idx = int(choice) - 1
        acc = accounts[idx]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    confirm = input(f"Are you sure you want to delete '{acc['name']}' from the manager? (y/n): ").lower()
    if confirm == 'y':
        # 1) Optionally remove the profile directory
        rm_dir = input("Remove the profile directory from disk as well? (y/n): ").lower()
        if rm_dir == 'y':
            try:
                shutil.rmtree(acc["profile_dir"])
                print(f"Removed directory: {acc['profile_dir']}")
            except Exception as e:
                print(f"Could not remove directory: {e}")

        # 2) Remove the desktop icon if it exists
        desktop_file_path = get_desktop_file_path(acc["name"])
        if desktop_file_path.exists():
            try:
                desktop_file_path.unlink()
                print(f"Removed desktop icon: {desktop_file_path}")
            except Exception as e:
                print(f"Could not remove desktop icon: {e}")

        # 3) Remove from our JSON store
        del accounts[idx]
        save_accounts(accounts)
        print(f"Account '{acc['name']}' removed.")
    else:
        print("Deletion cancelled.")

def main() -> None:
    """
    Main interactive menu that drives the script:
    1) Ensure config and check Signal installation
    2) Optionally auto-detect default config
    3) Show menu to list, add, select, or delete accounts
    """
    ensure_config_dir()

    if not is_signal_installed():
        print("Signal Desktop is not found on this system (signal-desktop not on PATH).")
        print("Please install Signal Desktop first.")
        return

    auto_add_default_signal()

    while True:
        print("\n=== Signal Multi Account Manager ===")
        print("1) List existing accounts")
        print("2) Add a new account")
        print("3) Select (launch) an account")
        print("4) Delete an account")
        print("5) Exit")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            list_accounts()
        elif choice == '2':
            add_account()
        elif choice == '3':
            select_account()
        elif choice == '4':
            delete_account()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
            
if __name__ == "__main__":
    main()