#!/usr/bin/env python3
import asyncio
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.requests import AMMInfo

def currency_to_hex(currency: str) -> str:
    """
    Convert an ASCII currency symbol (e.g. "ACRP") to a
    40-character uppercase HEX string (padded with zeros).
    For example, "ACRP" becomes "4143525000000000000000000000000000000000".
    """
    hex_str = currency.encode("ascii").hex().upper()
    return hex_str.ljust(40, "0")

async def main():
    TESTNET_URL = "https://s.altnet.rippletest.net:51234"
    client = AsyncJsonRpcClient(TESTNET_URL)

    # Define your assets.
    # For your token, e.g., "ACRP". We assume its issuer is also rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2.
    token_symbol = "ACRP"
    token_symbol_hex = currency_to_hex(token_symbol)
    token_issuer = "rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2"

    # For RLUSD, we use its known 40-char hex and issuer.
    rlusd_currency = "524C555344000000000000000000000000000000"  # RLUSD in hex
    rlusd_issuer = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"

    # Construct the AMMInfo request.
    # Note: Do NOT include ledger_index; your xrpl-py version doesn't support that argument here.
    amm_request = AMMInfo(
         asset={
             "currency": token_symbol_hex,
             "issuer": token_issuer
         },
         asset2={
             "currency": rlusd_currency,
             "issuer": rlusd_issuer
         }
    )
    try:
        response = await client.request(amm_request)
        print("AMMInfo response:")
        print(response.result)
    except Exception as e:
        print("Error requesting AMMInfo:", e)

if __name__ == "__main__":
    asyncio.run(main())
