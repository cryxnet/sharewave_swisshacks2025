import asyncio
from database import Database
from models import Company, Investor
from matching_algo import find_matches_for_company, find_matches_for_investor
import json

async def display_company_info(company):
    """Print company information in a readable format."""
    print(f"\n{'=' * 50}")
    print(f"COMPANY: {company.name}")
    print(f"{'=' * 50}")
    print(f"ID: {company.id}")
    print(f"Industry: {company.industry}")
    print(f"Stage: {company.stage}")
    print(f"Location: {company.location}")
    print(f"Valuation: ${company.total_valuation_usd:,.2f}")
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
    print(f"Preferred Stages: {', '.join(investor.preferred_stages)}")
    print(f"Preferred Locations: {', '.join(investor.preferred_locations)}")
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

async def run_demo():
    """Run a demonstration of the matching functionality."""
    db = Database()
    try:
        await db.connect()
        
        # Get all company and investors
        company = await db.get_all_companies()
        investors = await db.get_all_investors()
        
        if not company or not investors:
            print("Database is empty. Please run populate_database.py first.")
            return
            
        print(f"Found {len(company)} companys and {len(investors)} investors in the database")
        
        # Demo 1: Find matches for a company
        print("\n\n--- DEMO 1: MATCHING INVESTORS FOR A COMPANY ---")
        target_company = company[0]  # Use the first company
        await display_company_info(target_company)
        
        matches = find_matches_for_company(
            target_company.id,
            company,
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
            company,
            investors,
            top_n=3
        )
        
        await display_matches(matches, "company")
            
    except Exception as e:
        print(f"Error in demo: {str(e)}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(run_demo())