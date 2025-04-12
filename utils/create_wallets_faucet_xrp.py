import xrpl
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from xrpl.account import get_balance
import json
import time

# XRPL Testnet client
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(TESTNET_URL)

# Store wallet data
wallets_data = []

print("Creating and funding 10 XRPL testnet wallets...")
for i in range(10):
    print(f"Creating wallet {i+1}...")
    wallet = generate_faucet_wallet(client, debug=True)
    address = wallet.classic_address
    secret = wallet.seed

    # Wait a bit to ensure the funding is processed
    time.sleep(2)

    # Get balance
    balance = get_balance(address, client)

    wallets_data.append({
        "wallet_number": i + 1,
        "address": address,
        "secret": secret,
        "balance": balance
    })

# Save to JSON file
with open("xrpl_testnet_wallets.json", "w") as f:
    json.dump(wallets_data, f, indent=4)

print("Wallets created and saved to 'xrpl_testnet_wallets.json'")
