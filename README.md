# ShareWave - Tokenization Platform with AI-powered Due Diligence

ShareWave is a comprehensive tokenization platform built on the XRP Ledger, featuring AI-powered due diligence and investor matching capabilities. The platform enables companies to tokenize their assets, create automated market maker (AMM) pools, and connect with suitable investors through AI recommendations.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Blockchain Layer](#blockchain-layer)
- [AI Recommendation Layer](#ai-recommendation-layer)
- [Due Diligence AI Agents](#due-diligence-ai-agents)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development Guidelines](#development-guidelines)

## Architecture Overview

ShareWave consists of three main components:

1. Backend: A FastAPI application that handles XRPL interactions, AI services, and database operations
2. Frontend: A Next.js application providing the user interface for company registration, token management, and AMM interactions
3. Database: SQLite storage for company and shareholder information

### Tech Stack
- Backend: Python 3.12+, FastAPI, xrpl-py
- Frontend: Next.js, TypeScript, Tailwind CSS
- Blockchain: XRP Ledger (Testnet)
- AI Services: Azure OpenAI for due diligence and matching
- Database: SQLite

## Blockchain Layer

The blockchain layer leverages the XRP Ledger for:

### Token Issuance
- Creation of custom tokens representing company shares
- Distribution of tokens to shareholders based on ownership percentages
- Support for trustline establishment between shareholders and token issuer

### Automated Market Maker (AMM)
- Creation of liquidity pools with company tokens and RLUSD
- Dynamic pricing based on product formula
- Configurable trading fees and governance through vote slots

### Shareholder Management
- Tracking of shareholder payment status
- Verification of trustline establishment
- Token distribution based on ownership percentages

### Key Blockchain Files
- `main.py` - XRPL interaction, token issuance, and AMM creation
- `database.py` - Database operations for blockchain state

## AI Recommendation Layer

The recommendation layer uses natural language processing and vector embeddings to match investors with companies:

### Features
- Generation of text embeddings for companies and investors
- Calculation of similarity scores based on multiple criteria:
    - Industry focus
    - Investment stage preferences
    - Geographic focus
    - Investment size compatibility
    - Business model alignment

### Implementation Details
- Uses Azure OpenAI for text embedding generation
- Cosine similarity for matching score calculation
- Weighted consideration of multiple compatibility factors

### Key Recommendation Files
- `matching_algo.py` - Core matching algorithm
- `match_endpoints.py` - API endpoints for matching

## Due Diligence AI Agents

The platform incorporates multiple specialized AI agents for comprehensive due diligence:

### Agent Types
1. Financial Agent: Analyzes financial statements, cash flow, revenue growth, funding history
2. Business Model Agent: Evaluates business model viability, unit economics, competitive advantages
3. Market Agent: Assesses market size, competitive landscape, trends, and go-to-market strategy

### Agent Pipeline
1. Document uploaded during company registration
2. Router agent determines document type and routes to specialized agent
3. Agent analyzes document and produces risk assessment with safety score
4. Results aggregated to produce overall due diligence report

### Key Agent Files
- `app/agents/financial.py` - Financial analysis agent
- `app/agents/business_model.py` - Business model analysis agent  
- `app/agents/market.py` - Market analysis agent
- `app/endpoints.py` - Due diligence API endpoints

## Setup & Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/cryxnet/sharewave_swisshacks2025.git
cd sharewave_swisshacks2025/backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

# XRPL
XRPL_URL=https://s.altnet.rippletest.net:51234
```

5. Run the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
# or
pnpm install
```

3. Run the development server:
```bash
npm run dev
# or
pnpm dev
```

4. Access the application at http://localhost:3000

## Configuration

### Backend Configuration
- `app/config.py` - Azure OpenAI settings
- `main.py` - XRPL settings, database connection

### Database Schema
- `companies` table: Stores company information, token parameters, and issuing wallet details
- `shareholders` table: Stores shareholder information, payment status, and trustline status

## API Documentation

Once the backend is running, access the API documentation at http://localhost:8000/docs

### Key Endpoints
- `/companies` - Create a new company and issue tokens
- `/companies/{company_id}/check_stakeholders` - Check payment and trustline status
- `/companies/{company_id}/check_and_distribute` - Distribute tokens and create AMM
- `/companies/{company_id}/full_info` - Get complete company information
- `/api/due-diligence` - Perform due diligence on company documents
- `/investors/{investor_id}/match_companies` - Get AI-recommended companies for an investor

## Development Guidelines

### Backend Development
1. Follow FastAPI's pattern for endpoint implementation
2. Use async/await for all database and external API operations
3. Add new agents in the `app/agents` directory

### Frontend Development
1. Use TypeScript for all new components
2. Follow the established component structure
3. Add new pages in the app directory

### Testing
1. Run backend tests: `pytest`
2. Run frontend tests: `npm test`

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- XRP Ledger Foundation
- Azure OpenAI team
- Swiss Hacks 2025 organizers