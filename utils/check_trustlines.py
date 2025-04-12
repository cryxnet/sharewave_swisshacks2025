#!/usr/bin/env python3

import json
import sys
import asyncio
from typing import List

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.requests import AccountLines

################################################################################
# CONFIGURATION
################################################################################

ACCOUNTS_FILE = "xrpl_testnet_wallets.json"  # Update to your actual JSON filename
TESTNET_URL = "https://s.altnet.rippletest.net:51234"

# We assume the token symbol is "ACRP" and the issuer is rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2.
CURRENCY_SYMBOL = "ACRP"
ISSUER = "rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2"

def currency_to_hex(currency: str) -> str:
    """
    Convert an ASCII currency symbol (e.g. "ACRP") to a
    40-character HEX string (padded with zeros).
    """
    hex_str = currency.encode("ascii").hex().upper()
    return hex_str.ljust(40, "0")

# This is what we expect on-ledger for "ACRP" in 40-char hex form.
CURRENCY_HEX = currency_to_hex(CURRENCY_SYMBOL)

################################################################################
# HELPER FUNCTIONS FOR ACCOUNTS
################################################################################

def load_accounts(filename: str) -> List[dict]:
    """
    Load wallet accounts from a JSON file. Each entry should have at least:
      {
        "wallet_number": 1,
        "address": "rXXXX...",
        "secret": "sXXXX...",
        ...
      }
    """
    try:
        with open(filename, "r") as f:
            accounts = json.load(f)
        return accounts
    except FileNotFoundError:
        print(f"ERROR: Could not find JSON file '{filename}'!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in file '{filename}'!")
        sys.exit(1)

def list_wallets(accounts: List[dict]) -> None:
    """
    Print available wallets with their wallet_number and address.
    """
    print("Available Wallets:")
    for acc in accounts:
        print(f"  Wallet Number: {acc.get('wallet_number')}, Address: {acc.get('address')}")
    print()

def parse_wallet_selection(selection: str) -> List[int]:
    """
    Parse the user's input string (e.g., "1,2,3") into a list of integers.
    """
    try:
        return [int(num.strip()) for num in selection.split(",") if num.strip()]
    except ValueError:
        print("Invalid input format for wallet numbers. Please enter e.g. '1,2,3'.")
        sys.exit(1)

def get_wallet_by_number(accounts: List[dict], number: int) -> dict:
    """
    Retrieve a single wallet dictionary from the accounts list by its wallet_number.
    """
    for acc in accounts:
        if acc.get("wallet_number") == number:
            return acc
    return None

################################################################################
# XRPL-RELATED FUNCTIONS
################################################################################

async def check_trustline_for_wallet(wallet_dict: dict):
    """
    Perform an AccountLines request for one wallet.
    Print the entire response for debugging, then parse 'lines'
    to see if the (CURRENCY_HEX, ISSUER) trustline is present.
    """
    address = wallet_dict.get("address")
    w_number = wallet_dict.get("wallet_number")

    print(f"\n=== Checking trustline for wallet {w_number} (address={address}) ===")

    # Build the XRPL client for the testnet.
    client = AsyncJsonRpcClient(TESTNET_URL)

    # Construct and send the AccountLines request.
    try:
        req = AccountLines(account=address)
        response = await client.request(req)
    except Exception as e:
        print(f"Error retrieving trustlines for wallet {w_number}: {e}")
        return

    # 1) DEBUG PRINT: the ENTIRE response, so we know what the ledger returned.
    print("\n--- FULL AccountLines Response (DEBUG) ---")
    print(json.dumps(response.result, indent=2, default=str))

    # 2) Attempt to parse out the lines
    lines = response.result.get("lines", [])
    if not lines:
        print(f"\nNo trustlines found for wallet {w_number}. (lines array is empty)")
        return

    # 3) Now let's see if we find our specific trustline in lines.
    found_trustline = None
    for line in lines:
        # The line entry typically has:
        # {
        #   "account": "rISSUER...",     <--- the "other side" of the trust line
        #   "currency": "41435250....", <--- 40-char hex for ACRP
        #   "limit": "...",
        #   "balance": "0",
        #   ...
        # }
        currency_field = line.get("currency", "").upper()
        account_field = line.get("account", "")
        if currency_field == CURRENCY_HEX and account_field == ISSUER:
            found_trustline = line
            break

    if found_trustline:
        print(f"\n[✓] FOUND the trustline for currency={CURRENCY_SYMBOL} / {CURRENCY_HEX} (issuer={ISSUER}).")
        print("Trustline Details:")
        print(json.dumps(found_trustline, indent=2, default=str))
    else:
        print(f"\n[!] The trustline for {CURRENCY_SYMBOL} (hex={CURRENCY_HEX}) / issuer={ISSUER} was NOT found.")

################################################################################
# MAIN ASYNC WORKFLOW
################################################################################

async def main():
    # 1) Load all accounts from the JSON file
    accounts = load_accounts(ACCOUNTS_FILE)
    if not accounts:
        print("No accounts found in the JSON file.")
        sys.exit(1)

    # 2) Show the user which wallets exist
    list_wallets(accounts)

    # 3) Ask user which wallet(s) to check
    selection_str = input("Enter the wallet numbers to check (comma separated): ").strip()
    selected_nums = parse_wallet_selection(selection_str)

    # 4) Gather the wallet dicts
    selected_wallets = []
    for num in selected_nums:
        w = get_wallet_by_number(accounts, num)
        if w:
            selected_wallets.append(w)
        else:
            print(f"Warning: No wallet found with wallet_number={num}.")

    if not selected_wallets:
        print("No valid wallets were selected.")
        sys.exit(1)

    # 5) For each selected wallet, check if trustline is present
    for wallet_dict in selected_wallets:
        await check_trustline_for_wallet(wallet_dict)

################################################################################
# ENTRY POINT
################################################################################

if __name__ == "__main__":
    asyncio.run(main())
