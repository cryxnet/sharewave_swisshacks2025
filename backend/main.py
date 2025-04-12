import math
import uuid
import asyncio
from typing import List

import aiosqlite
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ------------------ Database File ------------------
DATABASE_FILE = "sharewave_db.sqlite"

# ------------------ FastAPI App ------------------
app = FastAPI()

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
from xrpl.models import requests
from xrpl.wallet import Wallet

XRPL_URL = "https://s.altnet.rippletest.net:51234"
XRPL_CLIENT = AsyncJsonRpcClient(XRPL_URL)

# This is the known test issuer for RLUSD on XRPL:
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
# We'll just use "RLUSD" as the 3-5 letter currency code:
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


# ------------------ Helper to retrieve a company doc from SQLite ------------------
async def get_company_with_shareholders(db: aiosqlite.Connection, company_id: str):
    """
    Fetches a single company row plus all its shareholders, returning a dict
    that mimics the original "document" structure.
    """
    # 1) Company row
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

    # 2) Shareholders
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
    Returns True if `shareholder_addr` has sent >= `amount_needed` RLUSD to `company_addr`.
    Otherwise returns False.

    NOTE: If two different shareholders share the same XRPL address,
    they'd both appear paid once that one address paid enough. 
    So ensure each shareholder has a unique address.
    """
    print(f"🔍 Checking RLUSD Payment for {shareholder_addr} => {company_addr}. Needed: {amount_needed}")

    # Retrieve the last 200 transactions for the company account
    req = AccountTx(account=company_addr, limit=200, forward=False)
    resp = await XRPL_CLIENT.request(req)
    txs = resp.result.get("transactions", [])

    total_found = 0.0

    for tx_entry in txs:
        tx = tx_entry.get("tx", {})
        tx_type = tx.get("TransactionType")
        tx_sender = tx.get("Account")

        if tx_type == "Payment" and tx_sender == shareholder_addr:
            # "Amount" is a dict for IOU, or a string for XRP
            amount_dict = tx.get("Amount")
            if isinstance(amount_dict, dict):
                currency = amount_dict.get("currency")
                issuer   = amount_dict.get("issuer")
                value_str= amount_dict.get("value", "0")

                print(f"  → Found Payment TX {tx.get('hash')}. currency={currency}, issuer={issuer}, value={value_str}")

                # Match the RLUSD issuer and currency (hex or short code)
                if issuer == RLUSD_ISSUER and currency in [RLUSD_CURRENCY, "RLUSD"]:
                    try:
                        val = float(value_str)
                    except ValueError:
                        val = 0.0
                    if val > 0:
                        total_found += val
                        print(f"    ✅ Payment matched: +{val}. total_found={total_found}")
                else:
                    print("    ❌ Mismatch currency or issuer.")
            else:
                print(f"  ❌ Payment in XRP or malformed? amount={amount_dict}")

    total_found_2dec = round(total_found, 2)
    needed_2dec = round(amount_needed, 2)
    print(f"==> Final total from {shareholder_addr}: {total_found_2dec}, needed: {needed_2dec}")
    return total_found_2dec >= needed_2dec


async def check_trustline(shareholder_addr: str, token_symbol: str, issuer_addr: str) -> bool:
    """
    Confirm if the shareholder set a trustline for (token_symbol, issuer_addr).
    We'll query account_lines for the shareholder.
    """
    lines_req = requests.AccountLines(account=shareholder_addr, ledger_index="validated")
    lines_resp = await XRPL_CLIENT.request(lines_req)
    lines = lines_resp.result.get("lines", [])
    for line in lines:
        if line.get("currency") == token_symbol and line.get("account") == issuer_addr:
            return True
    return False


async def distribute_tokens(
    issuer_seed: str,
    issuer_addr: str,
    token_symbol: str,
    total_supply: int,
    shareholder_addr: str,
    shareholder_percent: float
):
    """
    Sends the correct portion of total_supply from the issuer to a shareholder.
    Example: total_supply=10000, shareholder_percent=20 => 2000 tokens
    """
    tokens_to_send = math.floor(total_supply * (shareholder_percent / 100.0))
    wallet = Wallet.from_seed(issuer_seed)

    pay_tx = Payment(
        account=issuer_addr,
        destination=shareholder_addr,
        amount={
            "currency": token_symbol,
            "issuer": issuer_addr,
            "value": str(tokens_to_send)
        }
    )

    result = await sign_and_submit(pay_tx, XRPL_CLIENT, wallet)
    return {
        "shareholder": shareholder_addr,
        "tokens_sent": tokens_to_send,
        "tx_result": result.result
    }


async def create_amm_pool(
    issuer_seed: str,
    issuer_addr: str,
    token_symbol: str,
    token_amount: float,
    rlusd_amount: float
):
    """
    Create an AMM pool on XRPL pairing 'token_symbol' with RLUSD.
    """
    wallet = Wallet.from_seed(issuer_seed)

    amount1 = {
        "currency": token_symbol,
        "issuer": issuer_addr,
        "value": str(token_amount)
    }
    amount2 = {
        "currency": RLUSD_CURRENCY,
        "issuer": RLUSD_ISSUER,
        "value": str(rlusd_amount)
    }

    amm_create_tx = AMMCreate(
        account=issuer_addr,
        amount=amount1,
        amount2=amount2,
        # Example trading fee: 500 => 0.5%
        trading_fee=500
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

    # 2) Create an issuing wallet for the company (and set trustline to RLUSD).
    issuing_addr, issuing_seed = await create_issuing_wallet()

    # 3) Calculate each shareholder's required RLUSD (rounded to 2 decimals).
    new_shareholders = []
    for sh in data.shareholders:
        # portion_of_liquidity: fraction of the liquidity that each shareholder effectively covers
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

    # 4) Insert doc into SQLite
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
    If not all are ready, returns which ones haven't paid or haven't trustlined.
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

    # 1) Check on-chain RLUSD payment + trustline for each shareholder
    updated_shareholders = []
    for sh in company["shareholders"]:
        if not sh["has_paid"]:
            payment_ok = await check_rlusd_payment(
                company_addr=issuing_addr,
                shareholder_addr=sh["wallet_address"],
                amount_needed=sh["required_rlusd"]
            )
            if payment_ok:
                sh["has_paid"] = True

        if not sh["has_trustline"]:
            line_ok = await check_trustline(
                shareholder_addr=sh["wallet_address"],
                token_symbol=symbol,
                issuer_addr=issuing_addr
            )
            if line_ok:
                sh["has_trustline"] = True

        updated_shareholders.append(sh)

    # 2) Update DB with new has_paid / has_trustline
    for sh in updated_shareholders:
        await db.execute(
            """
            UPDATE shareholders
            SET has_paid=?, has_trustline=?
            WHERE id=?
            """,
            (
                int(sh["has_paid"]),
                int(sh["has_trustline"]),
                sh["id"]
            )
        )
    await db.commit()

    # 3) Identify any shareholders still not paid or not trustlined
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

    # If anyone hasn't paid or hasn't trustlined, do not distribute
    if not_paid or not_trustlined:
        return {
            "message": "Not all shareholders have paid + trustlined. Distribution not performed.",
            "not_paid": not_paid,
            "not_trustlined": not_trustlined
        }

    # 4) If everyone paid & trustlined, distribute tokens
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

    # 5) Create the AMM for the liquidity portion
    liquidity_tokens = total_supply * (liquidity_percent / 100.0)
    liquidity_usd_value = company["total_valuation_usd"] * (liquidity_percent / 100.0)

    amm_result = await create_amm_pool(
        issuer_seed=issuing_seed,
        issuer_addr=issuing_addr,
        token_symbol=symbol,
        token_amount=liquidity_tokens,
        rlusd_amount=liquidity_usd_value
    )

    # 6) Mark the company as distributed
    for sh in updated_shareholders:
        await db.execute(
            """
            UPDATE shareholders
            SET tokens_distributed=?
            WHERE id=?
            """,
            (
                int(sh["tokens_distributed"]),
                sh["id"]
            )
        )

    await db.execute(
        """
        UPDATE companies
        SET state=?
        WHERE _id=?
        """,
        ("distributed", company["_id"])
    )
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
