#!/usr/bin/env python3
import datetime
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx

# Ripple epoch starts 2000-01-01, so we add that offset to ledger "date".
RIPPLE_EPOCH_OFFSET = 946684800

def ripple_date_to_datetime(ripple_date: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ripple_date + RIPPLE_EPOCH_OFFSET)

def parse_transaction(tx_envelope: dict) -> dict:
    """
    tx_envelope looks like:
      {
        "hash": "8EC50F...",
        "ledger_index": 12345,
        "meta": {...},
        "tx_json": {...},  <-- actual transaction fields
        "validated": True,
        "close_time_iso": "2025-04-12T10:40:50Z",
        ...
      }
    """

    # For the transaction data, look under "tx_json"
    tx_json = tx_envelope.get("tx_json", {})
    tx_hash = tx_envelope.get("hash", "N/A")  # Outer level
    close_time = tx_envelope.get("close_time_iso", "N/A")  # Outer-level close time
    meta = tx_envelope.get("meta", {})

    # Grab fields from "tx_json"
    tx_type = tx_json.get("TransactionType", "N/A")
    sender = tx_json.get("Account", "N/A")

    # Not all transactions have a "Destination"
    receiver = tx_json.get("Destination", "N/A")

    # The ledger "date" is in tx_json, but some transactions might not have it
    # Also you can rely on close_time_iso for a human-readable date/time
    ledger_date = tx_json.get("date", None)
    if ledger_date is not None:
        tx_date = ripple_date_to_datetime(ledger_date).strftime('%Y-%m-%d %H:%M:%S')
    else:
        tx_date = "N/A"

    # Payment vs TrustSet vs Something else
    amount_str = "N/A"
    token = "N/A"
    issue = "N/A"

    if tx_type == "Payment":
        # The final delivered amount is in the "meta" dictionary with key "delivered_amount"
        # That often tells you exactly what was delivered, after pathfinding or partial payments.
        delivered_amt = meta.get("delivered_amount")
        # delivered_amount might be a string (XRP drops) or a dictionary (IOU).
        if isinstance(delivered_amt, dict):
            # It's an IOU
            # e.g. {"currency": "...", "issuer": "...", "value": "..."}
            amount_str = delivered_amt.get("value", "N/A")
            token = delivered_amt.get("currency", "N/A")
            issue = delivered_amt.get("issuer", "N/A")
        elif isinstance(delivered_amt, str):
            # It's probably XRP in drops
            try:
                xrp_amount = float(delivered_amt) / 1_000_000
                amount_str = f"{xrp_amount:.6f}"
                token = "XRP"
            except:
                amount_str = delivered_amt

        # Some Payment TXs use "Amount" or "DeliverMax" inside tx_json.
        # But "delivered_amount" from meta is the final official amount delivered.

    elif tx_type == "TrustSet":
        # For a TrustSet, there is no direct "Amount" or "Destination"
        # But you might see "LimitAmount" for the trust line details
        limit_amount = tx_json.get("LimitAmount", {})
        if limit_amount and isinstance(limit_amount, dict):
            # Example: {'currency': 'USD', 'issuer': '...', 'value': '1000000'}
            amount_str = limit_amount.get("value", "N/A")
            token = limit_amount.get("currency", "N/A")
            issue = limit_amount.get("issuer", "N/A")

    # Add any other transaction types you want to parse here...

    return {
        "Transaction Hash": tx_hash,
        "Type": tx_type,
        "Sender": sender,
        "Receiver": receiver,
        "Amount": amount_str,
        "Token": token,
        "Issue": issue,
        "Date": tx_date,
        "Close Time (ISO)": close_time,
    }

def main():
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    address = "rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2"

    # Pull the last N transactions from the testnet
    req = AccountTx(
        account=address,
        ledger_index_min=-1,
        ledger_index_max=-1,
        limit=7,
        binary=False
    )
    response = client.request(req)

    if not response.is_successful():
        print("AccountTx request failed:", response.result)
        return

    result = response.result
    txs = result.get("transactions", [])
    if not txs:
        print("No transactions found for this address on the testnet.")
        return

    print(f"Last {len(txs)} transactions for account {address}:\n")
    for tx_envelope in txs:
        parsed = parse_transaction(tx_envelope)
        print(f"Transaction Hash: {parsed['Transaction Hash']}")
        print(f"Type:             {parsed['Type']}")
        print(f"Sender:           {parsed['Sender']}")
        print(f"Receiver:         {parsed['Receiver']}")
        print(f"Amount:           {parsed['Amount']}")
        print(f"Token:            {parsed['Token']}")
        print(f"Issue:            {parsed['Issue']}")
        print(f"Date (Ledger):    {parsed['Date']}")
        print(f"Close Time (ISO): {parsed['Close Time (ISO)']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
