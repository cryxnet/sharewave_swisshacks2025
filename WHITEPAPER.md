# ShareWave: Democratizing Private Equity via Blockchain

## Executive Summary

ShareWave is an innovative decentralized platform that tokenizes private company shares, enabling non-accredited investors to participate in private equity markets. Built on the XRP Ledger (XRPL), ShareWave leverages blockchain technology to issue, distribute, and trade company shares (tokens) in a trustless and transparent manner. The platform uses real on-chain RLUSD payments and automated market-maker (AMM) liquidity pools to ensure that token issuance is fully collateralized and instantly tradeable.

---

## Introduction

Traditional private equity markets are typically reserved for accredited investors, leaving smaller investors with limited access to early-stage or privately held companies. ShareWave addresses this issue by allowing companies to convert their equity into blockchain-based tokens. Through this process, companies can democratically raise capital, while investors benefit from transparency, immediate liquidity, and direct participation in corporate governance.

---

## Problem Statement

- **Access Barrier:** Private companies and startups have historically been accessible only to venture capitalists and high-net-worth individuals, thus narrowing the pool of potential investors.
- **Lack of Liquidity:** Private equity assets are often illiquid; even after an investment is made, investors might struggle to exit their positions quickly.
- **Transparency & Trust:** Existing private equity transactions frequently lack transparency regarding investor contributions, share distribution, and governance, leading to trust issues.

---

## Solution Overview

ShareWave provides a fully integrated, end-to-end solution on XRPL by:

- **Tokenized Equity:** Companies create digital tokens representing their shares. These tokens are backed by real on-chain RLUSD payments from investors, ensuring every token is properly collateralized.
- **Decentralized Investment:** The platform opens private equity to a broader audience, allowing eligible investors to participate by purchasing these tokens.
- **Immediate Liquidity:** A portion of the tokens is reserved for forming an AMM pool. This liquidity pool, created immediately upon token distribution, ensures that tokens can be traded in a secondary market.
- **Transparent Governance:** Once tokens are issued, investors can access a real-time cap table and participate in company governance decisions.

---

## Key Components

### 1. Company Creation & Token Issuance

- **Issuing (Company) Wallet as a Vault:**  
  An XRPL issuing wallet is automatically generated for the company. This wallet acts as a secure vault that:

  - **Receives all RLUSD payments** from shareholders.
  - **Issues tokens on demand** by "creating" them at the moment they are sent via blockchain Payment transactions.
  - **Distributes tokens** to the initial stakeholders.
  - **Holds liquidity** – both in the form of reserved tokens and collected RLUSD – to later fund the AMM pool.

- **Token Structure & Cap Table:**  
  Companies specify their total token supply, overall valuation, and the percentage of tokens reserved as liquidity (e.g., 10%). The remaining tokens are allocated to shareholders according to their ownership percentages; these percentages are adjusted to include each investor’s proportionate share toward funding liquidity.

### 2. Payment & Trustline Verification

- **On-Chain RLUSD Payment:**  
  Each investor must send the calculated RLUSD amount to the company’s issuing (vault) wallet. This payment is transparently verified on the XRPL by scanning the ledger.
- **Trustline Setup:**  
  Investors are required to establish a trustline from their XRPL wallet to the company’s token (identified by its symbol and issuing wallet). This ensures that the tokens can be transferred into their wallets.

### 3. Token Distribution & AMM Liquidity Provision

- **Dual Role of the Issuing Wallet (Vault):**  
  Once every investor has made their payment and set up a trustline, the issuing (company) wallet fulfills its twin responsibilities:
  - **Token Distribution:**  
    It sends the non-liquidity portion of tokens directly to each investor’s wallet via Payment transactions in proportion to their original ownership.
  - **AMM Pool Creation:**  
    Simultaneously, the wallet uses the liquidity portion (reserved tokens) along with the corresponding RLUSD funds received from investors to create an AMM pool on XRPL. This pool immediately enables secondary market trading for the tokens, ensuring continuous liquidity and transparent price discovery.

### 4. Investor & Governance Dashboards

- **Investor Dashboard:**  
  Investors can view real-time information on their holdings, transaction history, and the company’s full cap table.
- **Governance Tools:**  
  The platform displays detailed token distribution, allowing shareholders to participate in corporate governance (such as voting on important decisions) in a transparent manner.

---

## How It Works – Flow Diagram

```plaintext
         [ XRPL Testnet ]
                │
   ┌────────────┴────────────┐
   │   Shareholder Wallets   │
   │ (Investors using XRPL)  │
   └────────────┬────────────┘
                │
      (Send RLUSD & Set Trustline)
                │
                ▼
       ┌────────────────────┐
       │ Issuing Wallet     │
       │ (Company's Vault)  │
       │  - Receives RLUSD  │
       │  - Issues Tokens   │
       └────────────┬───────┘
                │
 ┌──────────────┴──────────────┐
 │     1. Distribute Tokens    │
 │ (Non-Liquidity Portion to    │
 │   Shareholders via Payment) │
 └──────────────┬──────────────┘
                │
                │ (Remaining tokens, reserved for liquidity)
                ▼
       ┌────────────────────┐
       │ Create AMM Pool    │
       │ (AMMCreate TX:     │
       │  Pair Tokens & RLUSD) │
       └──────────────┬──────┘
                │
                ▼
    Public Secondary Market (Liquid Trading)
```

---

## Technical Architecture

- **Backend:**  
  The system is built using FastAPI with SQLite via SQLAlchemy. The backend manages company records, calculates investor payment requirements, verifies on-chain transactions, triggers token distribution, and creates the AMM pool.

- **Blockchain Integration:**  
  The platform uses the xrpl-py SDK to interact with the XRPL testnet. Real-time ledger queries (e.g., AccountTx, AccountLines) verify investor payments and trustline setups.

- **Liquidity & AMM:**  
  XRPL’s native AMM functionality is leveraged to create a liquidity pool pairing the company token with RLUSD. This ensures immediate secondary market trading and ongoing liquidity.

- **Investor & Governance Dashboards:**  
  Investors have access to an intuitive dashboard that displays real-time token holdings, transaction history, and comprehensive governance tools for active participation in corporate decision-making.

---

## The Issuing Wallet as a Vault

A core innovation in ShareWave is the use of the issuing wallet as a secure vault:

- Central Repository:
  The issuing wallet is not simply a tool for sending tokens. It functions as a secure vault that receives all RLUSD payments from shareholders. This ensures that every token issued is fully backed by actual funds.

- Token Issuance on Demand:
  Unlike traditional tokens that must be pre-minted, XRPL tokens are created at the moment of issuance—when the issuing wallet sends a Payment transaction. In this system, the issuing wallet’s vault-like nature underpins token creation by guaranteeing that funds are available to collateralize every issued token.

- Future Functionalities:
  The vault model opens up opportunities for advanced financial operations later on. With all investment capital securely stored in the issuing wallet, future implementations might include automated dividend distributions, collateral-backed lending, or further liquidity enhancements—all managed transparently on-chain.

---

## Proof that it works

In the demo video we are demonstrating all the functuionakity and the settlemens.
For a proof that our solution is working we are provid the wallet addresses and more.

- #1 Stakeholder: rMCaggVd5fUr9Hty3hxVkv5YHcRRsB1cwE
- #2 Stakeholder: r43HarrgJU8MUKHKS52BeMSSobSfh34bBA
- #3 Stakeholder: rD4P433T6VLKKCEg5tiQ7TZ9BSFNZPgCK9

- Company Issuing Wallet: rLpXb2V556Mg3oYKVUqPgEaSqhK1LfcRZ1
- Company token Symbol: ROAIC
- AMM: r4TEAKmxLRQ2NovPr8Dug9phAfNk7k9Wwf

---

## Conclusion

ShareWave revolutionizes private equity by enabling companies to tokenize their shares securely on the XRPL. Central to this approach is the company’s issuing wallet, which serves as a vault: it collects investor funds, issues tokens to initial stakeholders, and simultaneously creates an AMM pool with the reserved liquidity. This dual function of the issuing wallet ensures that each token is fully collateralized and that a liquid secondary market is immediately available for trading. Through transparent on-chain verification and innovative token distribution, ShareWave democratizes investment opportunities and sets a new standard for corporate governance and liquidity in private equity.
