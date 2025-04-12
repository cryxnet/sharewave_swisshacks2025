#!/usr/bin/env python3
import json
import sys
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait

# Constants for RLUSD issued currency.
# RLUSD is represented in a 40-character hex string.
RLUSD_HEX = "524C555344000000000000000000000000000000"
# Issuer address for RLUSD – update this if needed.
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"

# JSON filename containing wallet information.
ACCOUNTS_FILE = "xrpl_testnet_wallets.json"

def load_accounts(filename):
    try:
        with open(filename, "r") as f:
            accounts = json.load(f)
        return accounts
    except FileNotFoundError:
        print(f"Accounts file '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{filename}'.")
        sys.exit(1)

def list_wallets(accounts):
    print("Available Wallets:")
    for account in accounts:
        print(f"  Wallet Number: {account['wallet_number']}, Address: {account['address']}")
    print()

def get_wallet_by_number(accounts, number):
    for account in accounts:
        if account.get("wallet_number") == number:
            return account
    return None

def main():
    # Load wallets from JSON file.
    accounts = load_accounts(ACCOUNTS_FILE)
    if not accounts:
        print("No wallet accounts found in the file.")
        sys.exit(1)

    # List available wallets.
    list_wallets(accounts)

    # Prompt user to select a wallet.
    try:
        wallet_num = int(input("Enter the wallet number you wish to use: ").strip())
    except ValueError:
        print("Invalid wallet number.")
        sys.exit(1)

    selected_wallet = get_wallet_by_number(accounts, wallet_num)
    if not selected_wallet:
        print(f"Wallet number {wallet_num} not found.")
        sys.exit(1)

    # Prompt user for destination address.
    destination = input("Enter the destination address: ").strip()
    if not destination:
        print("Destination address cannot be empty.")
        sys.exit(1)

    # Prompt user for the RLUSD amount.
    amount_rlusd = input("Enter the RLUSD amount to send: ").strip()
    try:
        float_amount = float(amount_rlusd)
    except ValueError:
        print("Invalid RLUSD amount.")
        sys.exit(1)

    # Connect to the XRP Ledger Testnet.
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

    # Create a Payment transaction for RLUSD (for issued currencies, the Amount field is a dict).
    payment_tx = Payment(
        account=selected_wallet["address"],
        destination=destination,
        amount={
            "currency": RLUSD_HEX,
            "value": str(float_amount),
            "issuer": RLUSD_ISSUER
        },
        # You may omit sequence to allow autofill.
    )

    # Create a Wallet instance from the secret.
    # Use Wallet.from_seed with algorithm="secp256k1" if your keys were generated with the older scheme.
    wallet = Wallet.from_seed(selected_wallet["secret"])
    # You can now access the wallet address as wallet.address.

    # Display transaction details.
    print("\nTransaction Details:")
    print(f"  From:      {wallet.address}")
    print(f"  To:        {destination}")
    print(f"  Amount:    {float_amount} RLUSD")
    print(f"  Issuer:    {RLUSD_ISSUER}")
    print("\nSubmitting transaction...\n")

    try:
        # Sign, autofill, submit, and wait for the transaction using the new submit_and_wait function.
        final_response = submit_and_wait(payment_tx, client, wallet)
        print("Transaction submitted successfully!")
        print("Transaction result:")
        print(json.dumps(final_response, indent=2))
    except Exception as e:
        print("Error during transaction submission:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
