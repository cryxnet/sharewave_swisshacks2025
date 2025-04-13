import os
from typing import List, Dict, Optional, Any, Union
import numpy as np
import dotenv
from openai import AzureOpenAI
from sklearn.metrics.pairwise import cosine_similarity

from models import Company, Investor, MatchResult
from database import Database

# Load environment variables
dotenv.load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# --- Embedding Generation ---


# Updates for matching_algo.py
def generate_company_text_for_embedding(company: Dict[str, Any]) -> str:
    """Generate text representation of a company for embedding."""
    parts = [company.get("name", ""), f"Industry: {company.get('industry', 'N/A')}"]

    # Add sub-industries if present
    sub_industries = company.get("sub_industries", [])
    if sub_industries:
        parts.append(f"Sub-Industries: {', '.join(sub_industries)}")

    # Add stage and location
    parts.append(f"Stage: {company.get('stage', 'N/A')}")
    parts.append(f"Location: {company.get('location', 'N/A')}")

    # Add revenue stage if present
    if company.get("revenue_stage"):
        parts.append(f"Revenue Stage: {company.get('revenue_stage')}")

    # Add business model if present
    if company.get("business_model"):
        parts.append(f"Business Model: {company.get('business_model')}")

    # Add exit strategy if present
    if company.get("exit_strategy"):
        parts.append(f"Exit Strategy: {company.get('exit_strategy')}")

    # Add focus areas if present
    focus_areas = company.get("focus_areas", [])
    if focus_areas:
        parts.append(f"Focus Areas: {', '.join(focus_areas)}")

    # Add founder types if present
    founder_types = company.get("founder_types", [])
    if founder_types:
        parts.append(f"Founder Types: {', '.join(founder_types)}")

    # Add risk appetite if present
    if company.get("risk_appetite"):
        parts.append(f"Risk Appetite: {company.get('risk_appetite')}")

    # Add time horizon if present
    if company.get("time_horizon"):
        parts.append(f"Time Horizon: {company.get('time_horizon')}")

    # Add expected exit if present
    # if company.get('expected_exit'):
    # parts.append(f"Expected Exit: {company.get('expected_exit')}")

    # Add ESG focus if present
    if company.get("esg_focus"):
        parts.append("ESG Focus: Yes")

    # Add description
    if company.get("description"):
        parts.append(company.get("description"))

    return ". ".join(filter(None, parts))


def generate_investor_text_for_embedding(investor: Dict[str, Any]) -> str:
    """Generate text representation of an investor for embedding."""
    parts = [investor.get("name", ""), f"Type: {investor.get('investor_type', 'N/A')}"]

    # Add preferred and excluded industries
    parts.append(
        f"Preferred Industries: {', '.join(investor.get('preferred_industries', []))}"
    )

    excluded_industries = investor.get("excluded_industries", [])
    if excluded_industries:
        parts.append(f"Excluded Industries: {', '.join(excluded_industries)}")

    # Add preferred stages and locations
    parts.append(f"Preferred Stages: {', '.join(investor.get('preferred_stages', []))}")
    parts.append(
        f"Preferred Locations: {', '.join(investor.get('preferred_locations', []))}"
    )

    # Add business model focus if present
    business_models = investor.get("business_model_focus", [])
    if business_models:
        parts.append(f"Business Model Focus: {', '.join(business_models)}")

    # Add ESG mandate if present
    if investor.get("esg_mandate"):
        parts.append("ESG Mandate: Yes")

    # Add exit timeline if present
    if investor.get("exit_timeline_years"):
        parts.append(f"Exit Timeline: {investor.get('exit_timeline_years')} years")

    # Add other preferences
    focus_areas = investor.get("preferred_focus_areas", [])
    if focus_areas:
        parts.append(f"Preferred Focus Areas: {', '.join(focus_areas)}")

    # Add preferred founder types if present
    founder_types = investor.get("preferred_founder_types", [])
    if founder_types:
        parts.append(f"Preferred Founder Types: {', '.join(founder_types)}")

    # Add risk appetite if present
    if investor.get("risk_appetite"):
        parts.append(f"Risk Appetite: {investor.get('risk_appetite')}")

    # Add preferred time horizon if present
    time_horizons = investor.get("preferred_time_horizon", [])
    if time_horizons:
        parts.append(f"Preferred Time Horizons: {', '.join(time_horizons)}")

    # Add profile summary
    if investor.get("profile_summary"):
        parts.append(investor.get("profile_summary"))

    return ". ".join(filter(None, parts))


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding vector for text using Azure OpenAI API."""
    if not text:
        print("Warning: Empty text provided for embedding")
        return None

    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small",  # Your deployment name
        )
        embedding = response.data[0].embedding
        return np.array(embedding)
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


# --- Match Score Calculation ---

# Define matching weights for different criteria
# --- Match Score Calculation ---

# Define matching weights for different criteria
# Update matching weights
MATCH_WEIGHTS = {
    "industry": 1.0,
    "excluded_industry": -2.0,  # Strong negative signal
    "sub_industry": 0.8,
    "stage": 1.0,
    "location": 0.5,
    "valuation": 0.8,
    "revenue_stage": 0.7,
    "business_model": 0.9,
    "esg_alignment": 1.0,
    "exit_alignment": 0.8,
    "focus_areas": 1.2,
    "founder_types": 1.0,
    "risk_appetite": 0.8,
    "time_horizon": 0.7,
    "embedding": 3.0,
}


def calculate_match_score(
    company: Union[Company, Dict[str, Any]], investor: Union[Investor, Dict[str, Any]]
) -> float:
    """Calculate match score between a company and an investor."""
    # Convert to dict if Pydantic models were passed
    company_data = company if isinstance(company, dict) else company.model_dump()
    investor_data = investor if isinstance(investor, dict) else investor.model_dump()

    score = 0.0
    max_possible_score = sum(
        [weight for weight in MATCH_WEIGHTS.values() if weight > 0]
    )

    # --- Industry Match ---
    company_industry = company_data.get("industry")
    investor_industries = investor_data.get("preferred_industries", [])
    investor_excluded = investor_data.get("excluded_industries", [])

    # Check for excluded industries (strong negative signal)
    if company_industry and investor_excluded and company_industry in investor_excluded:
        return 0.0  # Automatic zero score for excluded industries

    if company_industry and investor_industries:
        if company_industry in investor_industries:
            score += MATCH_WEIGHTS["industry"]
    elif company_industry and not investor_industries:
        # Partial score if investor doesn't specify industries (more flexible)
        score += MATCH_WEIGHTS["industry"] * 0.5

    # --- Sub-Industry Match ---
    company_subs = company_data.get("sub_industries", [])
    if company_subs and investor_industries:
        matches = set(company_subs).intersection(set(investor_industries))
        if matches:
            overlap_percent = len(matches) / len(company_subs)
            score += MATCH_WEIGHTS["sub_industry"] * min(overlap_percent * 1.5, 1.0)

    # --- Business Model Match ---
    company_biz_model = company_data.get("business_model")
    investor_biz_models = investor_data.get("business_model_focus", [])

    if company_biz_model and investor_biz_models:
        if company_biz_model in investor_biz_models:
            score += MATCH_WEIGHTS["business_model"]

    # --- ESG Alignment ---
    company_esg = company_data.get("esg_focus", False)
    investor_esg = investor_data.get("esg_mandate", False)

    if investor_esg and company_esg:
        score += MATCH_WEIGHTS["esg_alignment"]
    elif investor_esg and not company_esg:
        # ESG mandate but company isn't ESG focused - significant mismatch
        score -= MATCH_WEIGHTS["esg_alignment"]

    # --- Exit Strategy Alignment ---
    company_exit = company_data.get("exit_strategy")
    investor_timeline = investor_data.get("exit_timeline_years")

    if company_exit and investor_timeline:
        # Map exit strategies to typical timelines
        exit_timelines = {"acquisition": 5, "ipo": 7, "long_term_growth": 10}

        company_timeline = exit_timelines.get(company_exit, 7)

        # Score based on alignment of timelines
        timeline_diff = abs(company_timeline - investor_timeline)
        if timeline_diff <= 2:
            score += MATCH_WEIGHTS["exit_alignment"]
        elif timeline_diff <= 4:
            score += MATCH_WEIGHTS["exit_alignment"] * 0.5

    # --- Revenue Stage Match ---
    company_rev_stage = company_data.get("revenue_stage")
    if company_rev_stage:
        stage_ranks = {
            "pre_revenue": 1,
            "early_revenue": 2,
            "break_even": 3,
            "profitable": 4,
        }
        rev_rank = stage_ranks.get(company_rev_stage, 0)

        # Early investors might prefer early revenue stages
        early_investor = any(
            s in ["seed", "pre-seed"] for s in investor_data.get("preferred_stages", [])
        )
        if early_investor and rev_rank <= 2:
            score += MATCH_WEIGHTS["revenue_stage"]
        # Later investors typically prefer more mature revenue stages
        elif not early_investor and rev_rank >= 3:
            score += MATCH_WEIGHTS["revenue_stage"]
        # Add partial score for middle stage
        elif rev_rank == 2:
            score += MATCH_WEIGHTS["revenue_stage"] * 0.5

    # --- Stage Match ---
    company_stage = company_data.get("stage")
    investor_stages = investor_data.get("preferred_stages", [])

    if company_stage and investor_stages:
        if company_stage in investor_stages:
            score += MATCH_WEIGHTS["stage"]
    elif company_stage and not investor_stages:
        # Partial score if investor doesn't specify stages
        score += MATCH_WEIGHTS["stage"] * 0.5

    # --- Location Match ---
    company_location = company_data.get("location")
    investor_locations = investor_data.get("preferred_locations", [])

    if company_location and investor_locations:
        if company_location == "Remote" and "Remote" in investor_locations:
            score += MATCH_WEIGHTS["location"]
        elif company_location != "Remote" and (
            company_location in investor_locations or "Remote" in investor_locations
        ):
            score += MATCH_WEIGHTS["location"]
    elif company_location and not investor_locations:
        # Partial score if investor doesn't specify locations
        score += MATCH_WEIGHTS["location"] * 0.5

    # --- Focus Areas Match ---
    company_focus_areas = company_data.get("focus_areas", [])
    investor_focus_areas = investor_data.get("preferred_focus_areas", [])

    if company_focus_areas and investor_focus_areas:
        # Calculate overlap percentage
        matches = set(company_focus_areas).intersection(set(investor_focus_areas))
        if matches:
            overlap_percent = len(matches) / max(len(company_focus_areas), 1)
            score += MATCH_WEIGHTS["focus_areas"] * min(overlap_percent * 1.5, 1.0)
    elif company_focus_areas and not investor_focus_areas:
        # Partial score if investor doesn't specify focus areas
        score += MATCH_WEIGHTS["focus_areas"] * 0.3

    # --- Founder Types Match ---
    company_founder_types = company_data.get("founder_types", [])
    investor_founder_types = investor_data.get("preferred_founder_types", [])

    if company_founder_types and investor_founder_types:
        # Calculate overlap percentage
        matches = set(company_founder_types).intersection(set(investor_founder_types))
        if matches:
            overlap_percent = len(matches) / max(len(investor_founder_types), 1)
            score += MATCH_WEIGHTS["founder_types"] * min(overlap_percent * 1.5, 1.0)
    elif company_founder_types and not investor_founder_types:
        # Partial score if investor doesn't specify founder preferences
        score += MATCH_WEIGHTS["founder_types"] * 0.2

    # --- Risk Appetite Match ---
    company_risk = company_data.get("risk_appetite")
    investor_risk = investor_data.get("risk_appetite")

    if company_risk and investor_risk:
        risk_levels = {
            "conservative": 1,
            "moderate": 2,
            "aggressive": 3,
            "very_aggressive": 4,
        }

        company_risk_level = risk_levels.get(company_risk.lower(), 0)
        investor_risk_level = risk_levels.get(investor_risk.lower(), 0)

        # Perfect match or investor is willing to take more risk than company needs
        if company_risk_level == investor_risk_level:
            score += MATCH_WEIGHTS["risk_appetite"]
        elif abs(company_risk_level - investor_risk_level) == 1:
            # Close match
            score += MATCH_WEIGHTS["risk_appetite"] * 0.5

    # --- Time Horizon Match ---
    company_horizon = company_data.get("time_horizon")
    investor_horizons = investor_data.get("preferred_time_horizon", [])

    if company_horizon and investor_horizons:
        if company_horizon in investor_horizons:
            score += MATCH_WEIGHTS["time_horizon"]
        # If company wants long-term but investor prefers medium-term, partial match
        elif company_horizon == "long_term" and "medium_term" in investor_horizons:
            score += MATCH_WEIGHTS["time_horizon"] * 0.5
        # If company wants short-term but investor prefers medium-term, partial match
        elif company_horizon == "short_term" and "medium_term" in investor_horizons:
            score += MATCH_WEIGHTS["time_horizon"] * 0.5

    # --- Investment Range Match ---
    company_valuation = company_data.get("total_valuation_usd")
    min_investment = investor_data.get("min_investment_usd")
    max_investment = investor_data.get("max_investment_usd")

    if company_valuation is not None:
        # Typical investment range: 0.5% to 15% of company valuation
        plausible_min = company_valuation * 0.005
        plausible_max = company_valuation * 0.15

        # Investor's range or default if not specified
        investor_min = min_investment if min_investment is not None else 0
        investor_max = max_investment if max_investment is not None else float("inf")

        # Check if ranges overlap
        if max(plausible_min, investor_min) <= min(plausible_max, investor_max):
            score += MATCH_WEIGHTS["valuation"]
        elif min_investment is None and max_investment is None:
            # Full score if investor hasn't specified investment range
            score += MATCH_WEIGHTS["valuation"]

    # --- Embedding Similarity ---
    company_embedding = company_data.get("embedding")
    investor_embedding = investor_data.get("embedding")

    if company_embedding is not None and investor_embedding is not None:
        # Convert to numpy arrays if needed
        if not isinstance(company_embedding, np.ndarray):
            company_embedding = np.array(company_embedding)
        if not isinstance(investor_embedding, np.ndarray):
            investor_embedding = np.array(investor_embedding)

        # Reshape for cosine similarity calculation
        company_emb_2d = company_embedding.reshape(1, -1)
        investor_emb_2d = investor_embedding.reshape(1, -1)

        # Calculate cosine similarity
        similarity = cosine_similarity(company_emb_2d, investor_emb_2d)[0][0]
        similarity = max(0, similarity)  # Ensure non-negative

        score += MATCH_WEIGHTS["embedding"] * similarity
    # Normalize score to be between 0 and 100
    normalized_score = max(0, min(score / max_possible_score, 1.0)) * 100

    return round(normalized_score, 2)


# --- Finding Matches ---


def find_matches_for_company(
    company_id: str,
    company: List[Union[Company, Dict]],
    investors: List[Union[Investor, Dict]],
    top_n: int = 5,
) -> List[MatchResult]:
    """Find the best investor matches for a specific company."""
    # Convert to dict if Pydantic models were passed
    companies_data = [c if isinstance(c, dict) else c.model_dump() for c in company]
    investors_data = [i if isinstance(i, dict) else i.model_dump() for i in investors]

    # Find the target company
    target_company = next((c for c in companies_data if c["id"] == company_id), None)
    if not target_company:
        print(f"Error: Company with ID {company_id} not found")
        return []

    if target_company.get("embedding") is None:
        print(f"Warning: Company {target_company['name']} has no embedding")

    # Calculate match scores with all investors
    matches = []
    for investor in investors_data:
        if investor.get("embedding") is None:
            print(f"Warning: Investor {investor['name']} has no embedding")
            continue

        score = calculate_match_score(target_company, investor)

        # Only include meaningful matches
        min_threshold = MATCH_WEIGHTS["embedding"] * 0.1
        if score > min_threshold:
            matches.append(
                MatchResult(
                    entity_id=investor["id"],
                    name=investor["name"],
                    score=score,
                    details={
                        "type": investor.get("investor_type"),
                        "industries": investor.get("preferred_industries"),
                        "excluded_industries": investor.get("excluded_industries"),
                        "stages": investor.get("preferred_stages"),
                        "min_investment": f"${investor.get('min_investment_usd', 0):,.0f}",
                        "max_investment": f"${investor.get('max_investment_usd', 0):,.0f}"
                        if investor.get("max_investment_usd")
                        else "No limit",
                        "business_models": investor.get("business_model_focus"),
                        "esg_mandate": "Yes" if investor.get("esg_mandate") else "No",
                        "exit_timeline": f"{investor.get('exit_timeline_years')} years"
                        if investor.get("exit_timeline_years")
                        else "Not specified",
                    },
                )
            )

    # Sort by score (descending) and return top N
    matches.sort(key=lambda x: x.score, reverse=True)
    return matches[:top_n]


def find_matches_for_investor(
    investor_id: str,
    company: List[Union[Company, Dict]],
    investors: List[Union[Investor, Dict]],
    top_n: int = 5,
) -> List[MatchResult]:
    """Find the best company matches for a specific investor."""
    # Convert to dict if Pydantic models were passed
    companies_data = [c if isinstance(c, dict) else c.model_dump() for c in company]
    investors_data = [i if isinstance(i, dict) else i.model_dump() for i in investors]

    # Find the target investor
    target_investor = next((i for i in investors_data if i["id"] == investor_id), None)
    if not target_investor:
        print(f"Error: Investor with ID {investor_id} not found")
        return []

    if target_investor.get("embedding") is None:
        print(f"Warning: Investor {target_investor['name']} has no embedding")

    # Calculate match scores with all companys
    matches = []
    for company in companies_data:
        if company.get("embedding") is None:
            print(f"Warning: Company {company['name']} has no embedding")
            continue

        score = calculate_match_score(company, target_investor)

        # Only include meaningful matches
        min_threshold = MATCH_WEIGHTS["embedding"] * 0.1
        if score > min_threshold:
            matches.append(
                MatchResult(
                    entity_id=company["id"],
                    name=company["name"],
                    score=score,
                    details={
                        "industry": company.get("industry"),
                        "sub_industries": company.get("sub_industries"),
                        "stage": company.get("stage"),
                        "location": company.get("location"),
                        "valuation": f"${company.get('total_valuation_usd', 0):,.0f}",
                        "revenue_stage": company.get("revenue_stage"),
                        "business_model": company.get("business_model"),
                        "esg_focus": "Yes" if company.get("esg_focus") else "No",
                        "exit_strategy": company.get("exit_strategy"),
                    },
                )
            )

    # Sort by score (descending) and return top N
    matches.sort(key=lambda x: x.score, reverse=True)
    return matches[:top_n]
