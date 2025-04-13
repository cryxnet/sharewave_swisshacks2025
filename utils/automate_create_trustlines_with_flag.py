#!/usr/bin/env python3
import json
import sys
import asyncio
from typing import List, Dict

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.requests import AccountLines
from xrpl.models.transactions import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import submit_and_wait
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet, AccountSet, AccountSetAsfFlag

# -------------------------------------------------------------------
# 1) XRPL Testnet URL
# -------------------------------------------------------------------
TESTNET_URL = "https://s.altnet.rippletest.net:51234"

# -------------------------------------------------------------------
# 2) Issuers and Token Symbols
# -------------------------------------------------------------------
# Hardcode the RLUSD issuer (no secret needed since that issuer doesn't trust itself).
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
RLUSD_TOKEN_SYMBOL = "RLUSD"

# Hardcode the WTAC issuer address + secret (we NEED the secret to sign a transaction from it).
WTAC_ISSUER_ADDRESS = "rLpXb2V556Mg3oYKVUqPgEaSqhK1LfcRZ1"
WTAC_ISSUER_SECRET = "sEdSbthHLmfku6P991zGacpGsh5biJ1"
COMPANY_TOKEN_SYMBOL = "ROAIC"

# -------------------------------------------------------------------
# 3) Trust Limits & Flags
# -------------------------------------------------------------------
TRUST_LIMIT = "1000000"       # The trust limit you desire
TRUSTSET_FLAGS = 262144       # Always use tfClearNoRipple (decimal 262144)

# -------------------------------------------------------------------
# 4) JSON File for All Other Wallets (Shareholders, etc.)
# -------------------------------------------------------------------
ACCOUNTS_FILE = "xrpl_testnet_wallets.json"


# -------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------
async def enable_default_ripple(client: AsyncJsonRpcClient, wallet_info: Dict):
    """
    Enables the Default Ripple flag on the issuer account.
    Required for AMM creation involving IOUs.
    """
    address = wallet_info.get("address")
    secret = wallet_info.get("secret")

    if not address or not secret:
        print(f"[!] Missing address or secret for enabling DefaultRipple.")
        return

    wallet = Wallet.from_seed(secret)
    tx = AccountSet(
        account=address,
        set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE  # or just `set_flag=8`
    )
    try:
        response = await submit_and_wait(tx, client, wallet)
        engine_result = response.result.get("engine_result")
        print(f"[✓] Enabled DefaultRipple for {address}: {engine_result}")
    except Exception as e:
        print(f"[x] Error enabling DefaultRipple for {address}: {e}")

def ascii_symbol_to_hex(symbol: str) -> str:
    """
    Convert an ASCII token symbol (e.g. "WTAC" or "RLUSD") into
    a 40-character HEX string required by the XRPL.
    """
    hex_str = symbol.encode("ascii").hex().upper()
    return hex_str.ljust(40, "0")


def load_wallets(filename: str) -> List[Dict]:
    """Load a list of wallets from the given JSON file."""
    try:
        with open(filename, "r") as f:
            wallets_data = json.load(f)
        if not isinstance(wallets_data, list):
            print(f"[x] The file {filename} must contain a list (array) of wallets.")
            sys.exit(1)
        return wallets_data
    except FileNotFoundError:
        print(f"[x] Could not find {filename}.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[x] Invalid JSON in {filename}.")
        sys.exit(1)


def list_wallets(wallets_data: List[Dict]) -> None:
    """Print out the available wallets for selection."""
    print("\nAvailable Wallets in JSON:")
    for w in wallets_data:
        w_num = w.get("wallet_number")
        addr = w.get("address")
        print(f"  Wallet Number: {w_num}, Address: {addr}")
    print()


def parse_selection(selection: str) -> List[int]:
    """
    Given a comma-separated string like "1,2,3",
    return a list of integers [1, 2, 3].
    """
    try:
        nums = [int(x.strip()) for x in selection.split(",") if x.strip()]
        return nums
    except ValueError:
        print("[x] Invalid input. Please enter wallet numbers like: 1,2,3")
        sys.exit(1)


async def trustline_exists(
    client: AsyncJsonRpcClient, address: str, issuer: str, currency_hex: str
) -> bool:
    """
    Return True if `address` already has a trustline to `issuer`
    for the specified `currency_hex`.
    """
    try:
        resp = await client.request(AccountLines(account=address))
        for line in resp.result.get("lines", []):
            if line["account"] == issuer and line["currency"] == currency_hex:
                return True
    except Exception as e:
        print(f"[!] Could not check trustline for {address}: {e}")
    return False


async def remove_trustline(
    client: AsyncJsonRpcClient,
    wallet_info: Dict,
    issuer: str,
    currency_hex: str,
    flags: int = TRUSTSET_FLAGS,
):
    """
    Remove an existing trustline by setting its limit to "0".
    (Removal will only succeed if the trustline’s balance is zero.)
    """
    address = wallet_info.get("address")
    secret = wallet_info.get("secret")
    if not secret:
        print(f"[!] Cannot remove trustline for {address}; missing secret.")
        return

    wallet = Wallet.from_seed(secret)
    removal_tx = TrustSet(
        account=address,
        flags=flags,
        limit_amount=IssuedCurrencyAmount(
            currency=currency_hex,
            issuer=issuer,
            value="0"
        ),
    )
    try:
        response = await submit_and_wait(removal_tx, client, wallet)
        engine_result = response.result.get("engine_result")
        print(f"[→] Removed existing trustline for {address} to {issuer}: {engine_result}")
    except Exception as e:
        print(f"[x] Error removing trustline for {address} to {issuer}: {e}")


async def create_trustline(
    client: AsyncJsonRpcClient,
    wallet_info: Dict,
    issuer: str,
    currency_hex: str,
    limit: str,
    flags: int,
):
    """
    For the wallet in `wallet_info`, remove any existing trustline
    (if found) to (issuer, currency_hex), then create a new trustline.
    """
    address = wallet_info.get("address")
    secret = wallet_info.get("secret")

    if not address or not secret:
        print(f"[!] Missing address or secret. Skipping: {wallet_info}")
        return

    # If trustline exists, remove it first.
    if await trustline_exists(client, address, issuer, currency_hex):
        print(f"[!] Trustline already exists for {address} to {issuer}. Removing it...")
        await remove_trustline(client, wallet_info, issuer, currency_hex, flags)

    # Now, create the new trustline.
    wallet = Wallet.from_seed(secret)
    trust_tx = TrustSet(
        account=address,
        flags=flags,
        limit_amount=IssuedCurrencyAmount(
            currency=currency_hex,
            issuer=issuer,
            value=limit,
        ),
    )
    try:
        response = await submit_and_wait(trust_tx, client, wallet)
        engine_result = response.result.get("engine_result")
        print(f"[→] Created new trustline for {address} to {issuer}: {engine_result}")
    except Exception as e:
        print(f"[x] Error creating trustline for {address} to {issuer}: {e}")


async def main():
    # ---------------- Load Shareholders from JSON ----------------
    wallets_data = load_wallets(ACCOUNTS_FILE)
    if not wallets_data:
        print("[!] No wallets found. Nothing to do.")
        sys.exit(0)

    list_wallets(wallets_data)
    selection = input("Enter the *shareholder* wallet numbers (e.g. 1,2,3): ").strip()
    selected_numbers = parse_selection(selection)

    # Filter the selected wallets from the JSON by wallet_number
    selected_shareholders = [w for w in wallets_data if w.get("wallet_number") in selected_numbers]

    # Convert ASCII token symbols to 40-char HEX
    rlusd_hex = ascii_symbol_to_hex(RLUSD_TOKEN_SYMBOL)
    wtac_hex = ascii_symbol_to_hex(COMPANY_TOKEN_SYMBOL)

    # ---------------- Summarize the plan ----------------
    print("\nSelected Shareholders:")
    for w in selected_shareholders:
        print(f" - Wallet #{w['wallet_number']}, Address: {w['address']}")

    # Build a wallet dict for the WTAC issuer (hardcoded in script):
    wtac_issuer_wallet = {
        "address": WTAC_ISSUER_ADDRESS,
        "secret": WTAC_ISSUER_SECRET
    }

    # Create the XRPL client
    client = AsyncJsonRpcClient(TESTNET_URL)

    # ---------------------------------------------
    # Step 1: Set RLUSD trustline for:
    #   - every selected shareholder
    #   - plus the WTAC issuer (so it trusts RLUSD)
    # ---------------------------------------------
    print("\n=== Setting RLUSD Trustlines (for shareholders + WTAC issuer) ===")

    # 1a) RLUSD trust for selected shareholders
    tasks = []
    for sh in selected_shareholders:
        tasks.append(
            create_trustline(
                client=client,
                wallet_info=sh,
                issuer=RLUSD_ISSUER,
                currency_hex=rlusd_hex,
                limit=TRUST_LIMIT,
                flags=TRUSTSET_FLAGS,
            )
        )
    # 1b) RLUSD trust for the WTAC issuer
    tasks.append(
        create_trustline(
            client=client,
            wallet_info=wtac_issuer_wallet,
            issuer=RLUSD_ISSUER,
            currency_hex=rlusd_hex,
            limit=TRUST_LIMIT,
            flags=TRUSTSET_FLAGS,
        )
    )
    await asyncio.gather(*tasks)

    # ✅ New: Enable Default Ripple on WTAC issuer
    print("\n=== Enabling Default Ripple on WTAC issuer ===")
    await enable_default_ripple(client, wtac_issuer_wallet)

    # ---------------------------------------------
    # Step 2: Set WTAC trustline for the selected shareholders
    # (the WTAC issuer does NOT need to trust itself).
    # ---------------------------------------------
    print("\n=== Setting WTAC Trustlines (for shareholders only) ===")
    tasks = []
    for sh in selected_shareholders:
        tasks.append(
            create_trustline(
                client=client,
                wallet_info=sh,
                issuer=WTAC_ISSUER_ADDRESS,
                currency_hex=wtac_hex,
                limit=TRUST_LIMIT,
                flags=TRUSTSET_FLAGS,
            )
        )
    await asyncio.gather(*tasks)

    print("\nAll done!")


if __name__ == "__main__":
    asyncio.run(main())
