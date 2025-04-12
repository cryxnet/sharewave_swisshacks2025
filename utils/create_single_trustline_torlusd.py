import asyncio
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import submit_and_wait

# === Config ===
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
RLUSD_CURRENCY = "524C555344000000000000000000000000000000"  # 20-byte hex = RLUSD
TRUST_LIMIT = "1000000"

# === Input your wallet info here ===
ADDRESS = "rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2"
SECRET = "sEdVqbuDfd1GWF7jCVVVLDtpGbGdnSj"

async def create_trustline(address: str, secret: str):
    client = AsyncJsonRpcClient(TESTNET_URL)
    wallet = Wallet.from_seed(secret)

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
        result = response.result

        # Print full result and extract engine_result safely
        print("Transaction submitted:")
        print(result)

        engine_result = result.get("engine_result") or result.get("meta", {}).get("TransactionResult")
        if engine_result:
            print(f"[✓] Trustline transaction result: {engine_result}")
        else:
            print("[!] Submitted, but no engine result found. Full result above.")

    except Exception as e:
        print(f"[x] Failed to create trustline: {e}")

if __name__ == "__main__":
    asyncio.run(create_trustline(ADDRESS, SECRET))
