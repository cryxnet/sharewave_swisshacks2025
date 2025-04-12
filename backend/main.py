import math
import uuid
import asyncio
from typing import List
from collections import deque
import aiosqlite
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ------------------ Database File ------------------
DATABASE_FILE = "sharewave_db.sqlite"

# ------------------ FastAPI App ------------------
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # add production domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    """
    On startup, create the companies and shareholders tables if they don't exist.
    """
    app.state.db = await aiosqlite.connect(DATABASE_FILE)
    await app.state.db.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        _id TEXT PRIMARY KEY,
        name TEXT,
        symbol TEXT,
        total_supply INTEGER,
        total_valuation_usd REAL,
        liquidity_percent REAL,
        issuing_address TEXT,
        issuing_seed TEXT,
        state TEXT
    )
    """)

    await app.state.db.execute("""
    CREATE TABLE IF NOT EXISTS shareholders (
        id TEXT PRIMARY KEY,
        company_id TEXT,
        wallet_address TEXT,
        percent REAL,
        adjusted_percent REAL,
        required_rlusd REAL,
        has_paid BOOLEAN,
        has_trustline BOOLEAN,
        tokens_distributed BOOLEAN
    )
    """)
    await app.state.db.commit()


@app.on_event("shutdown")
async def shutdown():
    """
    Close the DB connection on shutdown.
    """
    await app.state.db.close()


# ------------------ XRPL Integration ------------------
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.asyncio.transaction import sign_and_submit
from xrpl.models.transactions import Payment, AMMCreate, TrustSet
from xrpl.models.requests import AccountTx, AccountLines
from xrpl.wallet import Wallet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import AccountObjects
from xrpl.models.requests import AMMInfo

XRPL_URL = "https://s.altnet.rippletest.net:51234"
XRPL_CLIENT = AsyncJsonRpcClient(XRPL_URL)

# This is the known test issuer for RLUSD on XRPL
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
# The 40-hex code for "RLUSD"
RLUSD_CURRENCY = "524C555344000000000000000000000000000000"


# ------------------ Data Models ------------------
class ShareholderInput(BaseModel):
    """Defines a single shareholder with wallet + percent ownership (excluding liquidity)."""
    wallet_address: str
    percent: float  # e.g. 20 => 20%


class CompanyInput(BaseModel):
    """
    Defines how to create a new company:
    - total_supply: total shares minted (int)
    - total_valuation_usd: how many USD needed in total
    - liquidity_percent: how many % of shares are allocated to AMM pool
    - shareholders: e.g. 4 people holding 90% collectively if liquidity is 10%
    """
    name: str
    symbol: str
    total_supply: int
    total_valuation_usd: float
    liquidity_percent: float
    shareholders: List[ShareholderInput]


# ------------------ Helper: Get Company + Shareholders ------------------
import datetime

RIPPLE_EPOCH_OFFSET = 946684800

# ------------------ Helper: Get Token Holding ------------------
# This helper queries XRPL for the account lines of a given shareholder,
# then searches for the trustline for the specified token (e.g. company token)
# issued by the company's issuing address. It returns a dict with:
#   - "exists": True/False if the trustline exists
#   - "balance": The balance from the trustline, as a string.
# Helper: Query on-chain trustline info for a given address.
# (This function uses the XRPL AccountLines request.)
async def get_token_holding(shareholder_addr: str, token_symbol: str, issuer_addr: str) -> dict:
    """
    Query the XRPL ledger for the given shareholder's trustline of the token
    issued by `issuer_addr`. Returns a dict with:
      - "exists": True if the trustline exists.
      - "balance": The current balance of the token for that address.
    """
    token_hex = currency_to_hex(token_symbol)
    from xrpl.models.requests import AccountLines
    req = AccountLines(account=shareholder_addr, ledger_index="validated")
    try:
        resp = await XRPL_CLIENT.request(req)
    except Exception as e:
        print(f"[!] Error querying account_lines for {shareholder_addr}: {e}")
        return {"exists": False, "balance": "0"}
    lines = resp.result.get("lines", [])
    for line in lines:
        if line.get("currency", "").upper() == token_hex and line.get("account") == issuer_addr:
            return {"exists": True, "balance": line.get("balance", "0")}
    return {"exists": False, "balance": "0"}

def ripple_date_to_datetime(ripple_date: int) -> datetime.datetime:
    """
    XRPL "date" is seconds since Ripple epoch (2000-01-01).
    Convert to standard Python datetime.
    """
    return datetime.datetime.utcfromtimestamp(ripple_date + RIPPLE_EPOCH_OFFSET)

def parse_transaction(tx_envelope: dict) -> dict:
    """
    Adapts the user script to parse the structure returned by xrpl-py AccountTx,
    which can be either:
      {
        "tx_json": {
          "TransactionType": "...",
          "Account": "...",
          "Destination": "...",
          "Amount": "... or {...}",
          "date": 123456789,
          ...
        },
        "meta": {
          "delivered_amount": "... or {...}",
          ...
        },
        "validated": True,
        "close_time_iso": "...",
        ...
      }
    or in some cases:
      {
        "tx": {...},
        "meta": {...},
        ...
      }
    We'll look for tx_json first, then fallback to tx.
    """

    # 1) The transaction data might be in "tx_json" or "tx".
    tx_json = tx_envelope.get("tx_json")
    if not tx_json:
        tx_json = tx_envelope.get("tx", {})

    meta = tx_envelope.get("meta", {})

    # 2) The top-level "hash" can be in tx_json["hash"] or the outer envelope
    tx_hash = tx_json.get("hash") or tx_envelope.get("hash", "N/A")

    # 3) We might have close_time_iso or not
    close_time = tx_envelope.get("close_time_iso", "N/A")

    # 4) Basic fields from the transaction
    tx_type = tx_json.get("TransactionType", "N/A")
    sender = tx_json.get("Account", "N/A")
    receiver = tx_json.get("Destination", "N/A")

    # 5) The ledger "date" in XRPL is an integer in the tx
    ledger_date = tx_json.get("date")
    if ledger_date is not None:
        dt_obj = ripple_date_to_datetime(ledger_date)
        tx_date = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        tx_date = "N/A"

    # Payment vs TrustSet vs other
    amount_str = "N/A"
    token = "N/A"
    issue = "N/A"

    if tx_type == "Payment":
        # Check meta for delivered_amount
        delivered_amt = meta.get("delivered_amount")
        if isinstance(delivered_amt, dict):
            # IOU
            amount_str = delivered_amt.get("value", "N/A")
            token = delivered_amt.get("currency", "N/A")
            issue = delivered_amt.get("issuer", "N/A")
        elif isinstance(delivered_amt, str):
            # Possibly XRP in drops
            try:
                xrp_amount = float(delivered_amt) / 1_000_000
                amount_str = f"{xrp_amount:.6f}"
                token = "XRP"
            except:
                amount_str = delivered_amt

        # If delivered_amount was None or "N/A", fallback to raw "Amount"
        if amount_str == "N/A":
            raw_amt = tx_json.get("Amount")
            if isinstance(raw_amt, dict):
                amount_str = raw_amt.get("value", "N/A")
                token = raw_amt.get("currency", "N/A")
                issue = raw_amt.get("issuer", "N/A")
            elif isinstance(raw_amt, str):
                # Possibly XRP
                try:
                    xrp_amount = float(raw_amt) / 1_000_000
                    amount_str = f"{xrp_amount:.6f}"
                    token = "XRP"
                except:
                    amount_str = raw_amt

    elif tx_type == "TrustSet":
        limit_amount = tx_json.get("LimitAmount", {})
        if isinstance(limit_amount, dict):
            amount_str = limit_amount.get("value", "N/A")
            token = limit_amount.get("currency", "N/A")
            issue = limit_amount.get("issuer", "N/A")

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

async def get_company_with_shareholders(db: aiosqlite.Connection, company_id: str):
    """
    Fetches a single company row plus all its shareholders, returning a dict
    that mimics the original "document" structure.
    """
    company_cursor = await db.execute("""
        SELECT _id, name, symbol, total_supply, total_valuation_usd,
               liquidity_percent, issuing_address, issuing_seed, state
        FROM companies
        WHERE _id=?
    """, (company_id,))
    company_row = await company_cursor.fetchone()
    await company_cursor.close()

    if not company_row:
        return None

    (cid, name, symbol, total_supply, total_val, liq_percent,
     issuing_addr, issuing_seed, state) = company_row

    sh_cursor = await db.execute("""
        SELECT id, wallet_address, percent, adjusted_percent, required_rlusd,
               has_paid, has_trustline, tokens_distributed
        FROM shareholders
        WHERE company_id=?
    """, (company_id,))
    shareholders_rows = await sh_cursor.fetchall()
    await sh_cursor.close()

    shareholders = []
    for row in shareholders_rows:
        (sh_id, wallet_addr, percent, adj_percent, req_rlusd,
         has_paid, has_tl, tok_dist) = row
        shareholders.append({
            "id": sh_id,
            "wallet_address": wallet_addr,
            "percent": percent,
            "adjusted_percent": adj_percent,
            "required_rlusd": req_rlusd,
            "has_paid": bool(has_paid),
            "has_trustline": bool(has_tl),
            "tokens_distributed": bool(tok_dist)
        })

    doc = {
        "_id": cid,
        "name": name,
        "symbol": symbol,
        "total_supply": total_supply,
        "total_valuation_usd": total_val,
        "liquidity_percent": liq_percent,
        "issuing_address": issuing_addr,
        "issuing_seed": issuing_seed,
        "state": state,
        "shareholders": shareholders
    }
    return doc


# ------------------ XRPL Utility Functions ------------------
async def create_issuing_wallet():
    """
    Creates (funds) a brand-new wallet on the XRPL testnet using the faucet.
    Returns (address, seed).
    """
    wallet = await generate_faucet_wallet(XRPL_CLIENT, debug=False)
    return wallet.classic_address, wallet.seed


async def check_rlusd_payment(company_addr: str, shareholder_addr: str, amount_needed: float) -> bool:
    """
    Uses parse_transaction to decode each transaction from AccountTx,
    then checks if `shareholder_addr` has sent >= `amount_needed` RLUSD to `company_addr`.
    """
    print(f"\n🔎 Checking RLUSD Payment from {shareholder_addr} => {company_addr}, needed: {amount_needed}")

    req = AccountTx(account=company_addr, limit=200, forward=False)
    resp = await XRPL_CLIENT.request(req)
    txs = resp.result.get("transactions", [])
    print(f"  [Debug] Found {len(txs)} total ledger entries for {company_addr} from AccountTx.\n")

    total_found = 0.0
    for i, tx_entry in enumerate(txs, start=1):
        parsed = parse_transaction(tx_entry)
        print(f"  {i}) Hash={parsed['Transaction Hash']} | Type={parsed['Type']} | "
              f"Sender={parsed['Sender']} | Token={parsed['Token']} | Amount={parsed['Amount']} | "
              f"Issue={parsed['Issue']}")

        # Must be a Payment from the correct shareholder
        if parsed["Type"] == "Payment" and parsed["Sender"] == shareholder_addr:
            # Must match RLUSD hex or "RLUSD", plus known issuer
            token_match = parsed["Token"] in [RLUSD_CURRENCY, "RLUSD"]
            issuer_match = (parsed["Issue"] == RLUSD_ISSUER)
            if token_match and issuer_match:
                try:
                    val = float(parsed["Amount"])
                except ValueError:
                    val = 0.0
                if val > 0:
                    total_found += val
                    print(f"    ✅ Payment matched: +{val}, total_found={total_found}")
                else:
                    print("    ❌ Payment had non-numeric or zero amount.")
            else:
                print("    ❌ Not matching RLUSD issuer/currency.")
        else:
            print("    (Skipped - not a Payment from this shareholder)")

    # Compare to needed
    total_found_2dec = round(total_found, 2)
    needed_2dec = round(amount_needed, 2)
    print(f"==> Summed RLUSD from {shareholder_addr}: {total_found_2dec}, needed: {needed_2dec}")

    return total_found_2dec >= needed_2dec




def currency_to_hex(currency: str) -> str:
    """
    Convert an ASCII token symbol (e.g. "ACRP") to a
    40-character uppercase HEX string (padded with zeros).
    """
    hex_str = currency.encode("ascii").hex().upper()
    return hex_str.ljust(40, "0")

async def check_trustline(shareholder_addr: str, token_symbol: str, issuer_addr: str) -> bool:
    """
    Confirm if the shareholder set a trustline for (token_symbol, issuer_addr).
    We'll query account_lines for the shareholder and look for a line:
      {
        "currency": <40-char hex of token_symbol>,
        "account": issuer_addr,
        ...
      }
    """
    # 1) Convert your token symbol, e.g. "ACRP", to 40-char HEX.
    token_hex = currency_to_hex(token_symbol)

    # 2) Request the account lines.
    lines_req = AccountLines(account=shareholder_addr, ledger_index="validated")
    lines_resp = await XRPL_CLIENT.request(lines_req)
    lines = lines_resp.result.get("lines", [])

    # 3) Search for the matching trustline in "lines".
    for line in lines:
        # Example line:
        # {
        #   "account": "rDsM3HgETmGozgF9crnQ9kjHs7m5aGpej2",
        #   "balance": "0",
        #   "currency": "4143525000000000000000000000000000000000",
        #   "limit": "1000000",
        #   ...
        # }

        # Compare the uppercase line["currency"] to token_hex,
        # and line["account"] to the issuer address.
        if (line.get("currency", "").upper() == token_hex
                and line.get("account") == issuer_addr):
            return True

    # If none matched, return False.
    return False


async def distribute_tokens(
    issuer_seed: str,
    issuer_addr: str,
    token_symbol: str,
    total_supply: int,
    shareholder_addr: str,
    shareholder_percent: float
):
    tokens_to_send = math.floor(total_supply * (shareholder_percent / 100.0))
    wallet = Wallet.from_seed(issuer_seed)

    # Convert the ASCII symbol to 40-char hex if it's an IOU:
    token_symbol_hex = currency_to_hex(token_symbol)

    pay_tx = Payment(
        account=issuer_addr,
        destination=shareholder_addr,
        amount=IssuedCurrencyAmount(
            currency=token_symbol_hex,
            issuer=issuer_addr,
            value=str(tokens_to_send),
        ),
    )

    result = await sign_and_submit(pay_tx, XRPL_CLIENT, wallet)
    return {
        "shareholder": shareholder_addr,
        "tokens_sent": tokens_to_send,
        "tx_result": result.result
    }


from decimal import Decimal

def safe_issued_value(value: float, max_decimals: int = 8) -> str:
    from decimal import Decimal, ROUND_DOWN
    d = Decimal(value)
    quantized = d.quantize(Decimal(f"1.{'0'*max_decimals}"), rounding=ROUND_DOWN)
    return str(quantized.normalize())

async def create_amm_pool(
    issuer_seed: str,
    issuer_addr: str,
    token_symbol: str,
    token_amount: float,
    rlusd_amount: float
):
    wallet = Wallet.from_seed(issuer_seed)

    token_symbol_hex = currency_to_hex(token_symbol)  # If you haven't already

    amount1 = IssuedCurrencyAmount(
        currency=token_symbol_hex,
        issuer=issuer_addr,
        value=safe_issued_value(token_amount, 8),  # e.g. round to 8 decimals
    )
    amount2 = IssuedCurrencyAmount(
        currency=RLUSD_CURRENCY,
        issuer=RLUSD_ISSUER,
        value=safe_issued_value(rlusd_amount, 8),  # e.g. round to 8 decimals
    )

    amm_create_tx = AMMCreate(
        account=issuer_addr,
        amount=amount1,
        amount2=amount2,
        trading_fee=500,
    )
    result = await sign_and_submit(amm_create_tx, XRPL_CLIENT, wallet)
    return result.result


# ------------------ 1) CREATE COMPANY ------------------
@app.post("/companies")
async def create_company_endpoint(data: CompanyInput):
    """
    Creates a company with:
      - total_supply
      - liquidity_percent => e.g. 10% for an AMM
      - shareholders => sum of these + liquidity_percent == 100
    We store:
      - The company's XRPL issuing wallet (address + seed)
      - Each shareholder's required RLUSD payment (rounded to 2 decimals)
    """
    # 1) Validate sum of shareholder % + liquidity % = 100
    sum_sh = sum(s.percent for s in data.shareholders)
    total_ = sum_sh + data.liquidity_percent
    if round(total_, 2) != 100.0:
        raise HTTPException(
            status_code=400,
            detail="(sum of shareholders + liquidity_percent) must equal 100."
        )

    # 2) Create an issuing wallet for the company
    issuing_addr, issuing_seed = await create_issuing_wallet()

    # 3) Calculate each shareholder's required RLUSD
    new_shareholders = []
    for sh in data.shareholders:
        portion_of_liquidity = (sh.percent / sum_sh) * data.liquidity_percent
        adjusted_percent = sh.percent + portion_of_liquidity
        required_rlusd = round(
            data.total_valuation_usd * (adjusted_percent / 100.0),
            2
        )

        new_shareholders.append({
            "id": str(uuid.uuid4()),
            "wallet_address": sh.wallet_address,
            "percent": float(sh.percent),
            "adjusted_percent": float(adjusted_percent),
            "required_rlusd": required_rlusd,
            "has_paid": False,
            "has_trustline": False,
            "tokens_distributed": False
        })

    db = app.state.db
    company_id = str(uuid.uuid4())
    await db.execute("""
        INSERT INTO companies (
            _id, name, symbol, total_supply, total_valuation_usd,
            liquidity_percent, issuing_address, issuing_seed, state
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        data.name,
        data.symbol.upper(),
        data.total_supply,
        data.total_valuation_usd,
        data.liquidity_percent,
        issuing_addr,
        issuing_seed,
        "waiting_funds"
    ))

    # 5) Insert shareholders
    for sh in new_shareholders:
        await db.execute("""
            INSERT INTO shareholders (
                id, company_id, wallet_address,
                percent, adjusted_percent, required_rlusd,
                has_paid, has_trustline, tokens_distributed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sh["id"],
            company_id,
            sh["wallet_address"],
            sh["percent"],
            sh["adjusted_percent"],
            sh["required_rlusd"],
            int(sh["has_paid"]),
            int(sh["has_trustline"]),
            int(sh["tokens_distributed"])
        ))

    await db.commit()

    return {
        "message": "Company created successfully!",
        "company_id": company_id,
        "issuing_address": issuing_addr,
        "note": "Shareholders must now send their required RLUSD to this address + set trustline. Then call /companies/{id}/check_and_distribute."
    }


# ------------------ 2) CHECK & DISTRIBUTE + CREATE AMM ------------------
@app.post("/companies/{company_id}/check_and_distribute")
async def check_and_distribute(company_id: str):
    """
    Verifies if all shareholders have:
      - Sent >= required_rlusd
      - Set trustline
    If yes:
      1) Distribute tokens to each shareholder.
      2) Create an AMM pool with the 'liquidity_percent' portion of tokens + RLUSD in the company's wallet.
    If not all are ready, returns who hasn't paid or hasn't trustlined.
    """
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    if company["state"] == "distributed":
        return {"message": "Tokens already distributed and AMM created."}

    total_supply = company["total_supply"]
    symbol = company["symbol"]
    issuing_addr = company["issuing_address"]
    issuing_seed = company["issuing_seed"]
    liquidity_percent = company["liquidity_percent"]

    updated_shareholders = []
    for sh in company["shareholders"]:
        # Check Payment
        if not sh["has_paid"]:
            payment_ok = await check_rlusd_payment(
                company_addr=issuing_addr,
                shareholder_addr=sh["wallet_address"],
                amount_needed=sh["required_rlusd"]
            )
            if payment_ok:
                sh["has_paid"] = True

        # Check Trustline
        if not sh["has_trustline"]:
            trustline_ok = await check_trustline(
                shareholder_addr=sh["wallet_address"],
                token_symbol=symbol,
                issuer_addr=issuing_addr
            )
            if trustline_ok:
                sh["has_trustline"] = True

        updated_shareholders.append(sh)

    # Update DB with new has_paid / has_trustline
    for sh in updated_shareholders:
        await db.execute("""
            UPDATE shareholders
            SET has_paid=?, has_trustline=?
            WHERE id=?
        """, (
            int(sh["has_paid"]),
            int(sh["has_trustline"]),
            sh["id"]
        ))
    await db.commit()

    # Identify who is still not paid or not trustlined
    not_paid = []
    not_trustlined = []
    for sh in updated_shareholders:
        if not sh["has_paid"]:
            not_paid.append({
                "wallet_address": sh["wallet_address"],
                "still_owed_rlusd": sh["required_rlusd"]
            })
        if not sh["has_trustline"]:
            not_trustlined.append({
                "wallet_address": sh["wallet_address"],
                "token_symbol": symbol
            })

    if not_paid or not_trustlined:
        return {
            "message": "Not all shareholders have paid + trustlined. Distribution not performed.",
            "not_paid": not_paid,
            "not_trustlined": not_trustlined
        }

    # Everyone paid + trustlined => distribute
    sum_shareholder_percent = sum(s["percent"] for s in updated_shareholders)
    non_liquidity_supply = total_supply * ((100 - liquidity_percent) / 100.0)
    distribution_results = []

    for sh in updated_shareholders:
        if not sh["tokens_distributed"]:
            share_of_non_liq = (sh["percent"] / sum_shareholder_percent) * non_liquidity_supply
            dist_res = await distribute_tokens(
                issuer_seed=issuing_seed,
                issuer_addr=issuing_addr,
                token_symbol=symbol,
                total_supply=total_supply,
                shareholder_addr=sh["wallet_address"],
                shareholder_percent=(share_of_non_liq / total_supply * 100.0)
            )
            sh["tokens_distributed"] = True
            distribution_results.append(dist_res)

    # Create AMM for the liquidity portion
    liquidity_tokens = total_supply * (liquidity_percent / 100.0)
    liquidity_usd_value = company["total_valuation_usd"] * (liquidity_percent / 100.0)

    amm_result = await create_amm_pool(
        issuer_seed=issuing_seed,
        issuer_addr=issuing_addr,
        token_symbol=symbol,
        token_amount=liquidity_tokens,
        rlusd_amount=liquidity_usd_value
    )

    # Mark the company as distributed
    for sh in updated_shareholders:
        await db.execute("""
            UPDATE shareholders
            SET tokens_distributed=?
            WHERE id=?
        """, (
            int(sh["tokens_distributed"]),
            sh["id"]
        ))
    await db.execute("""
        UPDATE companies
        SET state=?
        WHERE _id=?
    """, ("distributed", company["_id"]))
    await db.commit()

    return {
        "message": "All shareholders paid & trustlined. Tokens distributed + AMM created!",
        "distribution": distribution_results,
        "amm_result": amm_result
    }


# ------------------ 3) GET COMPANY INFO ------------------
@app.get("/companies/{company_id}")
async def get_company_info(company_id: str):
    """
    Returns the current state of a company from SQLite,
    including each shareholder's payment/trustline/distribution status.
    """
    db = app.state.db
    doc = await get_company_with_shareholders(db, company_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Company not found.")

    # Omit the private seed
    safe_doc = {
        "company_id": doc["_id"],
        "name": doc["name"],
        "symbol": doc["symbol"],
        "total_supply": doc["total_supply"],
        "total_valuation_usd": doc["total_valuation_usd"],
        "liquidity_percent": doc["liquidity_percent"],
        "issuing_address": doc["issuing_address"],
        "state": doc["state"],
        "shareholders": [
            {
                "wallet_address": s["wallet_address"],
                "percent": s["percent"],
                "adjusted_percent": s["adjusted_percent"],
                "required_rlusd": s["required_rlusd"],
                "has_paid": s["has_paid"],
                "has_trustline": s["has_trustline"],
                "tokens_distributed": s["tokens_distributed"]
            }
            for s in doc["shareholders"]
        ]
    }
    return safe_doc


@app.get("/companies/{company_id}/shareholders")
async def get_shareholder_info(company_id: str, wallet: str = Query(None)):
    """
    Fetch a company's shareholders info, optionally filtered by a specific wallet.
    """
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    all_shareholders = company["shareholders"]
    if wallet:
        filtered = [s for s in all_shareholders if s["wallet_address"] == wallet]
        if not filtered:
            raise HTTPException(status_code=404, detail="Shareholder not found.")
        shareholders_to_return = filtered
    else:
        shareholders_to_return = all_shareholders

    return {
        "company_name": company["name"],
        "symbol": company["symbol"],
        "issuing_address": company["issuing_address"],
        "shareholders": [
            {
                "wallet_address": sh["wallet_address"],
                "required_rlusd": sh["required_rlusd"],
                "has_paid": sh["has_paid"],
                "has_trustline": sh["has_trustline"],
                "tokens_distributed": sh["tokens_distributed"]
            }
            for sh in shareholders_to_return
        ]
    }

@app.get("/debug/issuer_transactions")
async def debug_issuer_transactions(issuer_addr: str):
    """
    Returns a list of all Payment transactions whose destination is the given issuer address.
    This helps you debug all incoming payments to the company issuer wallet.
    """
    req = AccountTx(account=issuer_addr, limit=200)
    resp = await XRPL_CLIENT.request(req)
    txs = resp.result.get("transactions", [])
    
    debug_list = []
    for tx_entry in txs:
        tx = tx_entry.get("tx", {})
        # We want transactions that are Payment and whose Destination == issuer_addr
        if tx.get("TransactionType") == "Payment" and tx.get("Destination") == issuer_addr:
            debug_list.append({
                "tx_hash": tx.get("hash"),
                "Account": tx.get("Account"),  # sender
                "Amount": tx.get("Amount"),
                "Destination": tx.get("Destination"),
                "date": tx.get("date")  # if available
            })
    return {"issuer_transactions": debug_list}

@app.get("/companies/{company_id}/token_holdings")
async def get_token_holdings_endpoint(company_id: str):
    """
    Returns a list of all addresses holding this company's token,
    based on the issuer's AccountLines. For each trustline entry:

      - "account": the holder's address
      - "balance": from the issuer's perspective
         * A negative balance => the holder actually owns that positive amount.
         * A zero or positive balance => the holder doesn't own the token (they owe tokens to the issuer).
      - We compute the holder's actual token balance as -balance_float if negative, else 0.

    Then we calculate the percentage of total supply as:
      (holder_balance / total_supply) * 100

    Only non-zero holders are returned.
    """

    # 1) Fetch the company's details from your DB
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    # Issuer info from DB
    issuing_addr = company["issuing_address"]
    token_symbol = company["symbol"]  # e.g. "WTAC"
    total_supply = company["total_supply"]

    # Convert ASCII symbol to 40-char hex
    token_hex = currency_to_hex(token_symbol)

    # 2) Query all trustlines from the issuer's perspective
    try:
        req = AccountLines(account=issuing_addr, ledger_index="validated")
        resp = await XRPL_CLIENT.request(req)
    except Exception as e:
        print(f"[!] Error in AccountLines for {issuing_addr}: {e}")
        raise HTTPException(status_code=500, detail="Error querying XRPL for issuer trustlines.")

    lines = resp.result.get("lines", [])
    if not lines:
        return {"token_holdings": []}  # No trustlines at all

    # 3) Parse each trustline
    holdings_table = []
    for line in lines:
        # Filter only lines matching our token
        if line.get("currency", "").upper() != token_hex:
            continue

        holder_addr = line.get("account")
        balance_str = line.get("balance", "0")

        # The "balance" is from the issuer's perspective:
        # A negative issuer balance => the holder actually owns a positive amount.
        try:
            issuer_balance = float(balance_str)
        except ValueError:
            issuer_balance = 0.0

        # The holder's actual token holdings:
        holder_balance = 0.0
        if issuer_balance < 0:
            holder_balance = -issuer_balance  # invert sign

        # Skip if the holder's actual balance is zero
        if holder_balance <= 0:
            continue

        # Compute percent ownership
        if total_supply > 0:
            percent_ownership = (holder_balance / total_supply) * 100.0
        else:
            percent_ownership = 0.0

        # Add row to results
        holdings_table.append({
            "Wallet Address": holder_addr,
            "Token Balance": str(holder_balance),
            "Percent Ownership": round(percent_ownership, 2),
            "Trustline Active": True  # obviously they have an active trustline if they're in lines
        })

    # Return the final array of non-zero holders
    return {"token_holdings": holdings_table}

# ------------------ Endpoint 2: Initial Stakeholder Check ------------------
@app.get("/companies/{company_id}/initial_stakeholder_check")
async def initial_stakeholder_check(company_id: str):
    """
    Returns a checklist for all stakeholders (from the company registration) showing for each:
      - Wallet Address
      - Required RLUSD (the amount they must pay)
      - Has Paid (boolean from the DB)
      - Has Trustline (boolean from the DB)
      - Status: a string that is "Ready" if both are complete, or mentions what is missing.
      
    The frontend may display this information as a table.
    """
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    
    check_table = []
    for sh in company["shareholders"]:
        status = []
        if not sh["has_paid"]:
            status.append("Missing Payment")
        if not sh["has_trustline"]:
            status.append("Missing Trustline")
        status_str = "Ready" if not status else ", ".join(status)
        
        check_table.append({
            "Wallet Address": sh["wallet_address"],
            "Required RLUSD": sh["required_rlusd"],
            "Has Paid": sh["has_paid"],
            "Has Trustline": sh["has_trustline"],
            "Status": status_str
        })
    
    return {"initial_stakeholder_check": check_table}


@app.get("/companies/{company_id}/amm_info")
async def get_amm_info_endpoint(
    company_id: str,
    account: str = Query(
        None,
        description="Optional: an account id (e.g. a wallet address) to be used as the amm_account for the query."
    )
):
    """
    Retrieves AMM pool information using the AMMInfo request for a token pair consisting of:
      - Asset 1 (RLUSD): defined by RLUSD_CURRENCY and RLUSD_ISSUER.
      - Asset 2 (Company token): defined by the company’s token symbol (converted to 40-character hex)
        and the company’s issuing address.
    
    The company record is obtained from the database using company_id.
    If the optional query parameter "account" is provided, that account is used as amm_account.
    
    Returns a JSON object containing the AMM pool information.
    """
    # Retrieve company details from the database.
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    
    issuing_addr = company["issuing_address"]
    token_symbol = company["symbol"]

    # Build asset objects with both currency and issuer.
    rlusd_asset = {"currency": RLUSD_CURRENCY, "issuer": RLUSD_ISSUER}
    company_token_asset = {"currency": currency_to_hex(token_symbol), "issuer": issuing_addr}

    try:
        if account:
            req = AMMInfo(
                amm_account=account,
                asset=rlusd_asset,
                asset2=company_token_asset,
            )
        else:
            req = AMMInfo(
                asset=rlusd_asset,
                asset2=company_token_asset,
            )
        resp = await XRPL_CLIENT.request(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying AMM info: {e}")

    return {"amm_info": resp.result}

@app.get("/companies/{company_id}/full_info")
async def get_full_company_info(company_id: str):
    """
    Gathers and returns:
    - Company details
    - Shareholders and their status (paid, trustlined, tokens_distributed)
    - Token holders (actual trustline balances)
    - AMM info if available
    - Calculated stats like market cap, price, and AMM liquidity split
    """
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    total_supply = company["total_supply"]
    token_symbol = company["symbol"]
    issuing_addr = company["issuing_address"]

    # --------------------- Token Holders ---------------------
    token_hex = currency_to_hex(token_symbol)
    try:
        lines_resp = await XRPL_CLIENT.request(AccountLines(account=issuing_addr, ledger_index="validated"))
        lines = lines_resp.result.get("lines", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching token trustlines: {e}")

    token_holders = []
    total_holder_tokens = 0.0
    for line in lines:
        if line.get("currency", "").upper() != token_hex:
            continue
        balance_str = line.get("balance", "0")
        try:
            bal = float(balance_str)
        except:
            bal = 0.0
        if bal < 0:
            owned = -bal
            total_holder_tokens += owned
            token_holders.append({
                "wallet_address": line.get("account"),
                "balance": owned
            })

    # --------------------- AMM Info ---------------------
    amm_info = {}
    try:
        req = AMMInfo(
            asset={"currency": RLUSD_CURRENCY, "issuer": RLUSD_ISSUER},
            asset2={"currency": token_hex, "issuer": issuing_addr}
        )
        resp = await XRPL_CLIENT.request(req)
        amm_info = resp.result
    except Exception as e:
        amm_info = {"error": f"AMM not found or not active: {e}"}

    # --------------------- Calculated Stats ---------------------
    liquidity_usd = company["total_valuation_usd"] * (company["liquidity_percent"] / 100.0)
    market_cap = (company["total_valuation_usd"] if total_holder_tokens == total_supply else None)
    price_per_token = (company["total_valuation_usd"] / total_supply) if total_supply else None

    stats = {
        "price_per_token_usd": round(price_per_token, 6) if price_per_token else "N/A",
        "market_cap_usd": round(market_cap, 2) if market_cap else "N/A",
        "liquidity_usd": round(liquidity_usd, 2),
        "liquidity_token_amount": total_supply * (company["liquidity_percent"] / 100.0)
    }

    # --------------------- Shareholder Checklist ---------------------
    stakeholder_check = []
    for sh in company["shareholders"]:
        status = []
        if not sh["has_paid"]:
            status.append("Missing Payment")
        if not sh["has_trustline"]:
            status.append("Missing Trustline")
        stakeholder_check.append({
            "wallet_address": sh["wallet_address"],
            "required_rlusd": sh["required_rlusd"],
            "has_paid": sh["has_paid"],
            "has_trustline": sh["has_trustline"],
            "tokens_distributed": sh["tokens_distributed"],
            "status": "Ready" if not status else ", ".join(status)
        })

    return {
        "company": {
            "id": company["_id"],
            "name": company["name"],
            "symbol": company["symbol"],
            "total_supply": total_supply,
            "total_valuation_usd": company["total_valuation_usd"],
            "liquidity_percent": company["liquidity_percent"],
            "issuing_address": issuing_addr,
            "state": company["state"],
        },
        "stats": stats,
        "stakeholders": stakeholder_check,
        "token_holders": token_holders,
        "amm_info": amm_info
    }


@app.post("/companies/{company_id}/check_stakeholders")
async def check_stakeholders(company_id: str):
    """
    Performs the stakeholder check: 
    - Verifies if each shareholder has paid their required RLUSD.
    - Verifies if they have set the trustline.
    - Updates DB to reflect new has_paid and has_trustline flags.
    - Returns status of each shareholder.
    
    This does NOT perform token distribution or create AMM.
    """
    db = app.state.db
    company = await get_company_with_shareholders(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    symbol = company["symbol"]
    issuing_addr = company["issuing_address"]

    updated_shareholders = []
    for sh in company["shareholders"]:
        # Check Payment
        if not sh["has_paid"]:
            payment_ok = await check_rlusd_payment(
                company_addr=issuing_addr,
                shareholder_addr=sh["wallet_address"],
                amount_needed=sh["required_rlusd"]
            )
            if payment_ok:
                sh["has_paid"] = True

        # Check Trustline
        if not sh["has_trustline"]:
            trustline_ok = await check_trustline(
                shareholder_addr=sh["wallet_address"],
                token_symbol=symbol,
                issuer_addr=issuing_addr
            )
            if trustline_ok:
                sh["has_trustline"] = True

        updated_shareholders.append(sh)

    # Update the database
    for sh in updated_shareholders:
        await db.execute("""
            UPDATE shareholders
            SET has_paid=?, has_trustline=?
            WHERE id=?
        """, (
            int(sh["has_paid"]),
            int(sh["has_trustline"]),
            sh["id"]
        ))
    await db.commit()

    # Identify missing ones
    not_paid = []
    not_trustlined = []
    for sh in updated_shareholders:
        if not sh["has_paid"]:
            not_paid.append({
                "wallet_address": sh["wallet_address"],
                "still_owed_rlusd": sh["required_rlusd"]
            })
        if not sh["has_trustline"]:
            not_trustlined.append({
                "wallet_address": sh["wallet_address"],
                "token_symbol": symbol
            })

    # Final output
    if not_paid or not_trustlined:
        return {
            "message": "Some shareholders are still missing payment and/or trustline.",
            "not_paid": not_paid,
            "not_trustlined": not_trustlined
        }

    return {
        "message": "All shareholders have paid and set trustlines. Ready for distribution.",
        "not_paid": [],
        "not_trustlined": []
    }

# We're going to include the AI part in one single app
from match_endpoints import router as matching_router
app.include_router(matching_router)