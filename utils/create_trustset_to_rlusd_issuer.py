import json
import asyncio
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import AccountLines
from xrpl.asyncio.transaction import submit_and_wait
from xrpl.wallet import generate_faucet_wallet

# XRPL Testnet config
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
RLUSD_CURRENCY = "524C555344000000000000000000000000000000"
TRUST_LIMIT = "1000000"  # Set as needed

# Load wallets
with open("xrpl_testnet_wallets.json", "r") as f:
    wallet_data = json.load(f)

client = AsyncJsonRpcClient(TESTNET_URL)

async def trustline_exists(address):
    """Check if a trustline to RLUSD already exists for this address."""
    resp = await client.request(AccountLines(account=address))
    for line in resp.result.get("lines", []):
        if line["currency"] == RLUSD_CURRENCY and line["account"] == RLUSD_ISSUER:
            return True
    return False

async def create_trustline(wallet_info):
    address = wallet_info["address"]
    secret = wallet_info.get("secret")

    if not secret:
        print(f"[!] Missing secret for wallet {address}. Skipping.")
        return

    wallet = Wallet.from_seed(secret)  # Use secp256k1 if applicable

    if await trustline_exists(address):
        print(f"[✓] Trustline already exists for {address}")
        return

    trust_tx = TrustSet(
        account=address,
        limit_amount=IssuedCurrencyAmount(
            currency=RLUSD_CURRENCY,
            issuer=RLUSD_ISSUER,
            value=TRUST_LIMIT
        )
    )

    try:
        response = await submit_and_wait(trust_tx, client, wallet)
        print(f"[→] Trustline created for {address}: {response.result.get('engine_result')}")
    except Exception as e:
        print(f"[x] Error for {address}: {e}")

async def main():
    tasks = [create_trustline(w) for w in wallet_data]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
