import asyncio
import json
from database import Database
from models import Company, Investor
from matching_algo import find_matches_for_company, find_matches_for_investor

async def display_company_info(company):
    """Print company information in a readable format."""
    print(f"\n{'=' * 50}")
    print(f"COMPANY: {company.name}")
    print(f"{'=' * 50}")
    print(f"ID: {company.id}")
    print(f"Industry: {company.industry}")
    
    # Display sub-industries if present
    if hasattr(company, 'sub_industries') and company.sub_industries:
        sub_industries = company.sub_industries
        # If it's a string representation of a list, parse it
        if isinstance(sub_industries, str):
            try:
                sub_industries = json.loads(sub_industries)
            except json.JSONDecodeError:
                sub_industries = [sub_industries]
        print(f"Sub-Industries: {', '.join(sub_industries)}")
    
    print(f"Stage: {company.stage}")
    
    # Display revenue stage if present
    if hasattr(company, 'revenue_stage') and company.revenue_stage:
        print(f"Revenue Stage: {company.revenue_stage}")
    
    print(f"Location: {company.location}")
    print(f"Valuation: ${company.total_valuation_usd:,.2f}")
    
    # Display business model if present
    if hasattr(company, 'business_model') and company.business_model:
        print(f"Business Model: {company.business_model}")
    
    # Display exit strategy if present
    if hasattr(company, 'exit_strategy') and company.exit_strategy:
        print(f"Exit Strategy: {company.exit_strategy}")
    
    # Display ESG focus if present
    if hasattr(company, 'esg_focus'):
        print(f"ESG Focus: {'Yes' if company.esg_focus else 'No'}")
    
    print(f"Description: {company.description}")
    print(f"{'=' * 50}\n")

async def display_investor_info(investor):
    """Print investor information in a readable format."""
    print(f"\n{'=' * 50}")
    print(f"INVESTOR: {investor.name}")
    print(f"{'=' * 50}")
    print(f"ID: {investor.id}")
    print(f"Type: {investor.investor_type}")
    print(f"Preferred Industries: {', '.join(investor.preferred_industries)}")
    
    # Display excluded industries if present
    if hasattr(investor, 'excluded_industries') and investor.excluded_industries:
        excluded = investor.excluded_industries
        # If it's a string representation of a list, parse it
        if isinstance(excluded, str):
            try:
                excluded = json.loads(excluded)
            except json.JSONDecodeError:
                excluded = [excluded]
        print(f"Excluded Industries: {', '.join(excluded)}")
    
    print(f"Preferred Stages: {', '.join(investor.preferred_stages)}")
    print(f"Preferred Locations: {', '.join(investor.preferred_locations)}")
    
    # Display business model focus if present
    if hasattr(investor, 'business_model_focus') and investor.business_model_focus:
        models = investor.business_model_focus
        # If it's a string representation of a list, parse it
        if isinstance(models, str):
            try:
                models = json.loads(models)
            except json.JSONDecodeError:
                models = [models]
        print(f"Business Model Focus: {', '.join(models)}")
    
    # Display ESG mandate if present
    if hasattr(investor, 'esg_mandate'):
        print(f"ESG Mandate: {'Yes' if investor.esg_mandate else 'No'}")
    
    # Display exit timeline if present
    if hasattr(investor, 'exit_timeline_years') and investor.exit_timeline_years:
        print(f"Exit Timeline: {investor.exit_timeline_years} years")
    
    print(f"Investment Range: ${investor.min_investment_usd:,.2f} - " + 
          (f"${investor.max_investment_usd:,.2f}" if investor.max_investment_usd else "No upper limit"))
    print(f"Profile: {investor.profile_summary}")
    print(f"{'=' * 50}\n")

async def display_matches(matches, entity_type):
    """Display match results."""
    if not matches:
        print(f"No {entity_type} matches found.")
        return
        
    print(f"\nTop {len(matches)} {entity_type} matches:")
    print(f"{'-' * 60}")
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.name} (Score: {match.score:.2f})")
        for key, value in match.details.items():
            if value:  # Only print non-empty details
                if isinstance(value, list):
                    value = ', '.join(value)
                print(f"   {key.replace('_', ' ').title()}: {value}")
        print(f"{'-' * 60}")

async def safe_json_load(field_value):
    """Safely load JSON string to Python object."""
    if isinstance(field_value, str):
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            return field_value
    return field_value

async def preprocess_entities(entities):
    """Preprocess entities to ensure JSON fields are properly loaded."""
    for entity in entities:
        for field_name, field_value in entity.model_dump().items():
            if isinstance(field_value, str) and field_value.startswith('[') and field_value.endswith(']'):
                try:
                    parsed_value = json.loads(field_value)
                    setattr(entity, field_name, parsed_value)
                except json.JSONDecodeError:
                    pass
    return entities

async def run_demo():
    """Run a demonstration of the matching functionality."""
    db = Database()
    try:
        await db.connect()
        
        # Get all companies and investors
        companies = await db.get_all_companies()
        investors = await db.get_all_investors()
        
        if not companies or not investors:
            print("Database is empty. Please run populate_database.py first.")
            return
            
        print(f"Found {len(companies)} companies and {len(investors)} investors in the database")
        
        # Preprocess to ensure JSON fields are properly loaded
        companies = await preprocess_entities(companies)
        investors = await preprocess_entities(investors)
        
        # Demo 1: Find matches for a company
        print("\n\n--- DEMO 1: MATCHING INVESTORS FOR A COMPANY ---")
        target_company = companies[0]  # Use the first company
        await display_company_info(target_company)
        
        matches = find_matches_for_company(
            target_company.id,
            companies,
            investors,
            top_n=3
        )
        
        await display_matches(matches, "investor")
        
        # Demo 2: Find matches for an investor
        print("\n\n--- DEMO 2: MATCHING COMPANIES FOR AN INVESTOR ---")
        target_investor = investors[0]  # Use the first investor
        await display_investor_info(target_investor)
        
        matches = find_matches_for_investor(
            target_investor.id,
            companies,
            investors,
            top_n=3
        )
        
        await display_matches(matches, "company")
            
    except Exception as e:
        print(f"Error in demo: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(run_demo())