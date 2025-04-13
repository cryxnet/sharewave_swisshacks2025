# ShareWave Investor-Company Matching System

## Overview

The ShareWave matching system connects promising startups with suitable investors using a sophisticated algorithm that considers multiple factors beyond simple industry or stage matching. The system leverages both structured attribute matching and natural language understanding through vector embeddings to find the most compatible relationships between companies and investors.

## Table of Contents

1. [Data Models](#data-models)
2. [Matching Algorithm](#matching-algorithm)
3. [Integration Guide](#integration-guide)
4. [API Endpoints](#api-endpoints)
5. [Examples](#examples)

## Data Models

### Company Profile

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Company name |
| `industry` | string | Primary industry (e.g., FinTech, HealthTech) |
| `sub_industries` | string[] | Specific segments (e.g., RegTech, Digital Therapeutics) |
| `stage` | string | Funding stage (Pre-Seed, Seed, Series A–D, Growth) |
| `description` | string | Company description used for embeddings |
| `location` | string | Primary country or "Remote" |
| `total_valuation_usd` | number | Company valuation in USD |
| `revenue_stage` | enum | Pre-revenue, Early revenue, Break-even, Profitable |
| `business_model` | enum | SaaS, Hardware, Marketplace, Subscription |
| `focus_areas` | string[] | Sustainability, ESG, AI, Fintech, etc. |
| `founder_types` | string[] | Female, Underrepresented, Technical, Academic, etc. |
| `risk_appetite` | enum | Conservative, Moderate, Aggressive, Very aggressive |
| `time_horizon` | enum | Short-term (1-3y), Medium-term (3-5y), Long-term (5y+) |
| `exit_strategy` | enum | Acquisition, IPO, Long-term growth |
| `esg_focus` | boolean | Whether focused on sustainability/impact |
| `embedding` | number[] | Vector embedding of company profile |

### Investor Profile

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Fund/investor name |
| `investor_type` | string | VC, Angel, PE, Family Office, Impact Fund |
| `preferred_industries` | string[] | Industries of interest |
| `excluded_industries` | string[] | Industries explicitly avoided |
| `preferred_stages` | string[] | Funding stages of interest |
| `preferred_locations` | string[] | Countries of interest or "Remote" |
| `min_investment_usd` | number | Minimum check size |
| `max_investment_usd` | number | Maximum check size |
| `business_model_focus` | string[] | Preferred business models |
| `profile_summary` | string | Description used for embeddings |
| `preferred_focus_areas` | string[] | Areas of interest (Sustainability, AI, etc.) |
| `preferred_founder_types` | string[] | Founder preferences (Female, Technical, etc.) |
| `risk_appetite` | enum | Conservative, Moderate, Aggressive, Very aggressive |
| `preferred_time_horizon` | enum[] | Short-term, Medium-term, Long-term |
| `esg_mandate` | boolean | Whether impact is a requirement |
| `exit_timeline_years` | number | Expected investment horizon (years) |
| `embedding` | number[] | Vector embedding of investor profile |

## Matching Algorithm

The matching algorithm calculates a score (0-100) between companies and investors based on multiple weighted factors:

### Scoring Weights

| Factor | Weight | Description |
|--------|--------|-------------|
| Industry | 1.0 | Match on primary industry |
| Excluded Industry | -2.0 | Strong negative signal (automatic zero) |
| Sub-industry | 0.8 | Match on specialized segments |
| Stage | 1.0 | Funding stage alignment |
| Location | 0.5 | Geographic preference match |
| Valuation | 0.8 | Check size compatibility |
| Revenue Stage | 0.7 | Company revenue maturity |
| Business Model | 0.9 | Business model compatibility |
| ESG Alignment | 1.0 | Sustainability/impact alignment |
| Exit Alignment | 0.8 | Time horizon and exit expectations |
| Focus Areas | 1.2 | Thematic interest alignment |
| Founder Types | 1.0 | Founder background preferences |
| Risk Appetite | 0.8 | Risk tolerance alignment |
| Time Horizon | 0.7 | Investment timeline compatibility |
| Embedding | 3.0 | Semantic similarity from vector embeddings |

### Matching Logic

1. **Automatic Filters**:
   - Excluded industries result in a zero score
   - ESG mandate mismatch results in a negative contribution

2. **Attribute Matching**:
   - Direct attribute matches (e.g., industry, stage) receive full points
   - Partial matches (e.g., some overlap in preferred industries) receive partial points
   - Flexibility is rewarded (e.g., investors without specific preferences get partial points)

3. **Vector Embedding Similarity**:
   - Cosine similarity between company and investor embeddings
   - Captures semantic understanding beyond keyword matching
   - Generated from text descriptions and key attributes

4. **Score Normalization**:
   - Final score is normalized to 0-100 scale

## Integration Guide

### Basic Integration Steps

1. **Getting Matches for a Company**:
   - Call `find_matches_for_company(company_id, companies, investors, top_n=5)`
   - Returns top N investor matches with scores and details

2. **Getting Matches for an Investor**:
   - Call `find_matches_for_investor(investor_id, companies, investors, top_n=5)`
   - Returns top N company matches with scores and details

### Required Implementation

For frontend/backend integration:

1. Ensure both frontend and backend have access to the matching algorithm
2. Frontend should display match results with:
   - Match score (prominence based on score)
   - Key matching factors
   - Basic entity details

## API Endpoints

### Get Matches for Company

```
GET /api/companies/{company_id}/matches?limit=5
```

**Response:**
```json
{
  "matches": [
    {
      "entity_id": "investor-123",
      "name": "Tech Ventures Capital",
      "score": 87.5,
      "details": {
        "type": "VC",
        "industries": ["Software", "AI", "Fintech"],
        "excluded_industries": ["Gambling", "Tobacco"],
        "stages": ["Seed", "Series A"],
        "min_investment": "$1,000,000",
        "max_investment": "$10,000,000",
        "business_models": ["SaaS", "Marketplace"],
        "esg_mandate": "No",
        "exit_timeline": "5 years"
      }
    },
    // Additional matches...
  ]
}
```

### Get Matches for Investor

```
GET /api/investors/{investor_id}/matches?limit=5
```

**Response:**
```json
{
  "matches": [
    {
      "entity_id": "company-456",
      "name": "TechFlow Solutions",
      "score": 92.3,
      "details": {
        "industry": "Software",
        "sub_industries": ["SaaS", "Enterprise Software"],
        "stage": "Series A",
        "location": "Switzerland",
        "valuation": "$15,000,000",
        "revenue_stage": "early_revenue",
        "business_model": "saas",
        "esg_focus": "No",
        "exit_strategy": "acquisition"
      }
    },
    // Additional matches...
  ]
}
```

## Examples

### Example: Finding Matches for a SaaS Company

```python
# Get matches for TechFlow Solutions
matches = find_matches_for_company(
    "company-123",  # TechFlow's ID
    companies,      # List of all companies
    investors,      # List of all investors
    top_n=3         # Get top 3 matches
)

# Display matches
print(f"Top matches for TechFlow Solutions:")
for match in matches:
    print(f"{match.name} - Score: {match.score}")
    print(f"  Type: {match.details['type']}")
    print(f"  Industries: {', '.join(match.details['industries'])}")
    print(f"  Stages: {', '.join(match.details['stages'])}")
    print(f"  Investment Range: {match.details['min_investment']} - {match.details['max_investment']}")
```

**Output:**
```
Top matches for TechFlow Solutions:
Tech Ventures Capital - Score: 87.5
  Type: VC
  Industries: Software, AI, Fintech
  Stages: Seed, Series A
  Investment Range: $1,000,000 - $10,000,000

Digital Growth Partners - Score: 72.3
  Type: VC
  Industries: Software, Fintech
  Stages: Series A, Series B
  Investment Range: $5,000,000 - $25,000,000

SaaS Seed Fund - Score: 68.9
  Type: Angel Syndicate
  Industries: Software, SaaS
  Stages: Seed
  Investment Range: $500,000 - $2,000,000
```

### Example: Finding Matches for an Impact Investor

```python
# Get matches for Green Future Investments
matches = find_matches_for_investor(
    "investor-789",  # Green Future's ID
    companies,       # List of all companies
    investors,       # List of all investors
    top_n=3          # Get top 3 matches
)

# Display matches
print(f"Top matches for Green Future Investments:")
for match in matches:
    print(f"{match.name} - Score: {match.score}")
    print(f"  Industry: {match.details['industry']}")
    print(f"  Stage: {match.details['stage']}")
    print(f"  Valuation: {match.details['valuation']}")
    print(f"  ESG Focus: {match.details['esg_focus']}")
```

**Output:**
```
Top matches for Green Future Investments:
GreenEnergy Corp - Score: 94.1
  Industry: CleanTech
  Stage: Series B
  Valuation: $50,000,000
  ESG Focus: Yes

OceanClean Robotics - Score: 88.7
  Industry: Sustainability
  Stage: Series B
  Valuation: $45,000,000
  ESG Focus: Yes

SmartGrid AI - Score: 77.2
  Industry: CleanTech
  Stage: Series A
  Valuation: $18,000,000
  ESG Focus: Yes
```

## Technical Implementation Details

### Embedding Generation

The system uses Azure OpenAI's `text-embedding-3-small` model to generate vector embeddings from:

1. For companies: Name, industry, stage, location, focus areas, description, etc.
2. For investors: Name, type, preferred industries, stages, profile summary, etc.

These embeddings capture semantic similarities that keyword matching might miss.

### Database Interaction

The matching system interacts with a SQLite database through the `Database` class, which handles:
- Loading companies and investors
- Storing and retrieving embeddings
- Updating entity profiles

### Recalculating Matches

Matches should be recalculated when:
1. A company or investor profile is updated
2. New companies or investors are added to the system
3. Matching algorithm weights or logic is adjusted

## Conclusion

This matching system provides a sophisticated way to connect companies and investors based on multiple dimensions of compatibility, going far beyond traditional filters. By considering both structured attributes and semantic understanding, it creates matches that reflect real-world investment decision factors.