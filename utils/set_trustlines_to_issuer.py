#!/usr/bin/env python3
import json
import sys
import asyncio
from typing import List

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import submit_and_wait

# --- Helper Function: Convert a Currency Symbol to 40-Character HEX ---
def currency_to_hex(currency: str) -> str:
    """
    Convert an ASCII currency symbol (e.g., "ACRP") to its 40-character HEX representation.
    """
    hex_str = currency.encode("ascii").hex().upper()
    return hex_str.ljust(40, "0")

# --- Configuration ---
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
TOKEN_SYMBOL = "ATCO"  # The human-friendly token symbol.
TOKEN_HEX = currency_to_hex(TOKEN_SYMBOL)  # e.g. "ACRP" becomes "4143525000000000000000000000000000000000"
ISSUER_ADDRESS = "rptQwHDxLACEPw3pNmj6Tw5YvWHANdyj5S"  # Issuer for ACRP.
TRUST_LIMIT = "1000000"  # Trust limit for the trustline.

# JSON filename for the wallet accounts.
ACCOUNTS_FILE = "xrpl_testnet_wallets.json"

# --- Functions for Handling Wallet Accounts ---
def load_accounts(filename: str) -> List[dict]:
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

def list_wallets(accounts: List[dict]) -> None:
    print("Available Wallets:")
    for account in accounts:
        print(f"  Wallet Number: {account.get('wallet_number')}, Address: {account.get('address')}")
    print()

def get_wallet_by_number(accounts: List[dict], number: int) -> dict:
    for account in accounts:
        if account.get("wallet_number") == number:
            return account
    return None

def parse_wallet_selection(selection: str) -> List[int]:
    try:
        numbers = [int(num.strip()) for num in selection.split(",") if num.strip()]
        return numbers
    except ValueError:
        print("Invalid input; please enter wallet numbers separated by commas (e.g., 1,2,3).")
        sys.exit(1)

# --- Async Function to Process a Single Wallet's Trustline ---
async def process_wallet_trustline(wallet_dict: dict):
    address = wallet_dict.get("address")
    secret = wallet_dict.get("secret")
    wallet_number = wallet_dict.get("wallet_number")
    print(f"Setting trustline for wallet {wallet_number} ({address})...")
    
    client = AsyncJsonRpcClient(TESTNET_URL)
    # Create the wallet object (adjust algorithm if needed; default is ED25519)
    wallet_obj = Wallet.from_seed(secret)  # Add algorithm="secp256k1" if required.
    
    # Construct the TrustSet transaction using the IssuedCurrencyAmount class.
    trust_tx = TrustSet(
        account=wallet_obj.address,
        flags=262144,
        limit_amount=IssuedCurrencyAmount(
            currency=TOKEN_HEX,
            issuer=ISSUER_ADDRESS,
            value=TRUST_LIMIT
        )
    )
    
    try:
        response = await submit_and_wait(trust_tx, client, wallet_obj)
        result = response.result
        print(f"Wallet {wallet_number} trustline response:")
        # Use default=str to safely serialize any non-serializable objects.
        print(json.dumps(result, indent=2, default=str))
        print("-" * 40)
    except Exception as e:
        print(f"Error setting trustline for wallet {wallet_number} ({address}): {e}")

# --- Main Async Function ---
async def main():
    accounts = load_accounts(ACCOUNTS_FILE)
    if not accounts:
        print("No wallet accounts found in the file.")
        sys.exit(1)
    
    list_wallets(accounts)
    selection = input("Enter the wallet numbers to add the trustline for (comma separated): ").strip()
    selected_numbers = parse_wallet_selection(selection)
    selected_wallets = [get_wallet_by_number(accounts, num) for num in selected_numbers if get_wallet_by_number(accounts, num)]
    
    if not selected_wallets:
        print("No valid wallets were selected.")
        sys.exit(1)
    
    print("\nTrustline will be added to the following wallets:")
    for wallet in selected_wallets:
        print(f"  Wallet Number: {wallet.get('wallet_number')}, Address: {wallet.get('address')}")
    
    print("\nProcessing TrustSet transactions...\n")
    # Process wallets sequentially.
    for wallet_dict in selected_wallets:
        await process_wallet_trustline(wallet_dict)

if __name__ == "__main__":
    asyncio.run(main())
