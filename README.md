# SMAM 
The SMAM, or Signal Multi Account Manager, is a simple CLI tool for creating and managing multiple Signal accounts for the Signal desktop client on Linux.

It allows you to check existing accounts, add new accounts (with or without desktop icons), and remove existing accounts.

If you're looking for something similar for Windows or macOS, try this: https://github.com/kmille/signal-account-switcher

## Installation

**With pip**
Fetch the package:
```
pip install -i https://test.pypi.org/simple/ smam==0.0.1
```
Run:
```
python3 -m smam_package.smam
```
## Usage
When executed, you will be presented with an interactive menu:
```
=== Signal Multi Account Manager ===
1) List existing accounts
2) Add a new account
3) Select (launch) an account
4) Delete an account
5) Exit
Enter choice:
```

## Requirements

**Python:** 3.7 or higher.
