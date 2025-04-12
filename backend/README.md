# AI MATCHING SYSTEM DOCUMENTATION

## Overview
The matching system uses a sophisticated scoring algorithm to match companies with investors based on multiple criteria and AI-powered semantic matching.

## API Endpoints

### 1. Get Matches for a Company
```http
GET /matching/company/{company_id}
```
**Parameters:**
- `company_id`: UUID of the company
- `limit`: Maximum matches to return (5-20, default: 5)
- `min_score`: Minimum match score (0-10, default: 0)

### 2. Get Matches for an Investor
```http
GET /matching/investor/{investor_id}
```
**Parameters:**
- `investor_id`: UUID of the investor
- `limit`: Maximum matches to return (5-20, default: 5)
- `min_score`: Minimum match score (0-10, default: 0)

## Response Format
```json
{
    "matches": [
        {
            "entity_id": "string",
            "name": "string",
            "score": "number",
            "details": {
                // For company matches
                "industry": "string",
                "stage": "string",
                "location": "string",
                "valuation": "string",

                // For investor matches
                "type": "string",
                "industries": ["string"],
                "stages": ["string"],
                "min_investment": "string",
                "max_investment": "string"
            }
        }
    ],
    "count": "number",
    "entity_type": "investor" | "company",
    "entity_name": "string"
}
```

## Matching Criteria & Weights
| Criterion | Weight |
|-----------|--------|
| Industry Match | 1.0 |
| Stage Match | 1.0 |
| Location Match | 0.5 |
| Valuation/Investment Range | 0.8 |
| Focus Areas | 1.2 |
| Founder Types | 1.0 |
| Risk Appetite | 0.8 |
| Time Horizon | 0.7 |
| AI Semantic Match | 3.0 |

## Example Usage
```http
// Get matches for a company
GET /matching/company/[company_id]?limit=10&min_score=0.5

// Get matches for an investor
GET /matching/investor/[investor_id]?limit=10&min_score=0.5
```

## Notes
- Scores range from 0-10, with higher scores indicating better matches
- All matches include detailed information about why they matched
- The AI component uses Azure OpenAI embeddings for semantic matching
- The system considers both explicit criteria (like industry) and implicit factors (via AI matching)