import asyncio
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import submit_and_wait

# === Config ===
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
RLUSD_CURRENCY = "524C555344000000000000000000000000000000"  # "RLUSD" in hex
TRUST_LIMIT = "1000000"

# === Input your wallet info here ===
ADDRESS = "rPWhqXbvW5MTfABbzXfNYPgi1QB9EweBei"
SECRET = "sEdTvedy4451HwWu9GSJDm1XcCURWGp"

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
        result = await submit_and_wait(trust_tx, client, wallet)
        print(f"[✓] Trustline created. Result: {result.result['engine_result']}")
    except Exception as e:
        print(f"[x] Failed to create trustline: {e}")

if __name__ == "__main__":
    asyncio.run(create_trustline(ADDRESS, SECRET))
