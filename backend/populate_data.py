import asyncio
import os
from database import Database
from models import Company, Investor
from matching_algo import get_embedding, generate_company_text_for_embedding, generate_investor_text_for_embedding

# Sample company data
SAMPLE_COMPANIES = [
    {
        "name": "TechFlow Solutions",
        "industry": "Software",
        "stage": "Series A",
        "description": "Cloud-native enterprise software solutions",
        "location": "Switzerland",
        "total_valuation_usd": 15_000_000.0
    },
    {
        "name": "BioInnovate Labs",
        "industry": "Biotech",
        "stage": "Seed",
        "description": "Revolutionary biotech research in healthcare",
        "location": "Germany",
        "total_valuation_usd": 5_000_000.0
    },
    {
        "name": "GreenEnergy Corp",
        "industry": "CleanTech",
        "stage": "Series B",
        "description": "Sustainable energy solutions for industry",
        "location": "Remote",
        "total_valuation_usd": 50_000_000.0
    },
    {
        "name": "NeuroSync AI",
        "industry": "AI",
        "stage": "Seed",
        "description": "Cognitive AI tools for mental health diagnostics",
        "location": "Germany",
        "total_valuation_usd": 3_000_000.0
    },
    {
        "name": "AgroNova Tech",
        "industry": "AgriTech",
        "stage": "Series A",
        "description": "Smart farming solutions using IoT and AI",
        "location": "Netherlands",
        "total_valuation_usd": 12_000_000.0
    },
    {
        "name": "QuantumLeap Systems",
        "industry": "Quantum Computing",
        "stage": "Pre-Seed",
        "description": "Building scalable quantum hardware",
        "location": "Switzerland",
        "total_valuation_usd": 1_500_000.0
    },
    {
        "name": "UrbanMobility Inc.",
        "industry": "Mobility",
        "stage": "Series B",
        "description": "Electric micro-mobility solutions for cities",
        "location": "Remote",
        "total_valuation_usd": 40_000_000.0
    },
    {
        "name": "MedScan Diagnostics",
        "industry": "HealthTech",
        "stage": "Series A",
        "description": "AI-powered medical imaging diagnostics",
        "location": "Germany",
        "total_valuation_usd": 10_000_000.0
    },
    {
        "name": "EcoFabric Co.",
        "industry": "Sustainability",
        "stage": "Seed",
        "description": "Sustainable and biodegradable textile production",
        "location": "Sweden",
        "total_valuation_usd": 2_800_000.0
    },
    {
        "name": "FinNova AI",
        "industry": "Fintech",
        "stage": "Series A",
        "description": "AI-driven personal finance and wealth management tools",
        "location": "Switzerland",
        "total_valuation_usd": 9_000_000.0
    },
    {
        "name": "DeepSpace Mining",
        "industry": "Aerospace",
        "stage": "Series B",
        "description": "Asteroid mining tech for rare materials",
        "location": "Germany",
        "total_valuation_usd": 70_000_000.0
    },
    {
        "name": "SmartGrid AI",
        "industry": "CleanTech",
        "stage": "Series A",
        "description": "AI solutions for optimizing energy grids",
        "location": "Switzerland",
        "total_valuation_usd": 18_000_000.0
    },
    {
        "name": "EduBotics",
        "industry": "EdTech",
        "stage": "Seed",
        "description": "Robotic education kits for children and schools",
        "location": "Germany",
        "total_valuation_usd": 3_500_000.0
    },
    {
        "name": "CyberGuard Labs",
        "industry": "Cybersecurity",
        "stage": "Series A",
        "description": "Advanced threat detection using machine learning",
        "location": "Remote",
        "total_valuation_usd": 15_000_000.0
    },
    {
        "name": "PlantAI",
        "industry": "AgriTech",
        "stage": "Seed",
        "description": "AI-based plant health diagnostics and monitoring",
        "location": "Netherlands",
        "total_valuation_usd": 2_200_000.0
    },
    {
        "name": "OceanClean Robotics",
        "industry": "Sustainability",
        "stage": "Series B",
        "description": "Robots for cleaning plastic from oceans and rivers",
        "location": "Switzerland",
        "total_valuation_usd": 45_000_000.0
    },
    {
        "name": "BioSynth Foods",
        "industry": "FoodTech",
        "stage": "Series A",
        "description": "Synthetic biology for alternative protein production",
        "location": "Germany",
        "total_valuation_usd": 13_000_000.0
    },
    {
        "name": "LegalEase AI",
        "industry": "LegalTech",
        "stage": "Seed",
        "description": "AI-based contract analysis and legal assistance",
        "location": "Remote",
        "total_valuation_usd": 4_000_000.0
    },
    {
        "name": "NanoMed Devices",
        "industry": "MedTech",
        "stage": "Series A",
        "description": "Nanotech for targeted drug delivery",
        "location": "Germany",
        "total_valuation_usd": 11_000_000.0
    },
    {
        "name": "SolarX Innovations",
        "industry": "CleanTech",
        "stage": "Seed",
        "description": "High-efficiency solar panels with flexible materials",
        "location": "Switzerland",
        "total_valuation_usd": 3_800_000.0
    },
    {
        "name": "DataSphere Analytics",
        "industry": "Big Data",
        "stage": "Series B",
        "description": "Scalable analytics platform for real-time insights",
        "location": "Remote",
        "total_valuation_usd": 55_000_000.0
    },
    {
        "name": "ReGen Materials",
        "industry": "Sustainability",
        "stage": "Series A",
        "description": "Upcycling waste into high-performance materials",
        "location": "Germany",
        "total_valuation_usd": 8_000_000.0
    },
    {
        "name": "MindLink VR",
        "industry": "XR/VR",
        "stage": "Pre-Seed",
        "description": "Immersive therapy solutions using VR and biofeedback",
        "location": "Remote",
        "total_valuation_usd": 1_200_000.0
    }
]

# Sample investor data
SAMPLE_INVESTORS = [
    {
        "name": "Tech Ventures Capital",
        "investor_type": "VC",
        "preferred_industries": ["Software", "AI", "Fintech"],
        "preferred_stages": ["Seed", "Series A"],
        "preferred_locations": ["Switzerland", "Germany", "Remote"],
        "min_investment_usd": 1_000_000.0,
        "max_investment_usd": 10_000_000.0,
        "profile_summary": "Early-stage tech investor focused on B2B SaaS"
    },
    {
        "name": "Life Sciences Fund",
        "investor_type": "VC",
        "preferred_industries": ["Biotech", "Healthcare", "MedTech"],
        "preferred_stages": ["Seed", "Series A", "Series B"],
        "preferred_locations": ["Germany", "Switzerland"],
        "min_investment_usd": 2_000_000.0,
        "max_investment_usd": 20_000_000.0,
        "profile_summary": "Specialized in life sciences and healthcare innovations"
    },
    {
        "name": "Green Future Investments",
        "investor_type": "Impact Fund",
        "preferred_industries": ["CleanTech", "Sustainability", "GreenEnergy"],
        "preferred_stages": ["Series A", "Series B"],
        "preferred_locations": ["Remote", "Switzerland", "Germany"],
        "min_investment_usd": 5_000_000.0,
        "max_investment_usd": 50_000_000.0,
        "profile_summary": "Impact-focused fund investing in sustainable technologies"
    }
]

async def create_company_with_embedding(db: Database, company_data: dict) -> Company:
    """Create a company with embeddings."""
    try:
        # Check if company already exists by name
        if await db.company_name_exists(company_data['name']):
            print(f"Company {company_data['name']} already exists, skipping...")
            return None

        # Create a new company instance
        company = Company(**company_data)
        
        # Generate text for embedding
        text = generate_company_text_for_embedding(company.model_dump())
        
        # Get embedding
        embedding = get_embedding(text)
        if embedding is not None:
            company.embedding = embedding.tolist()
            
            # Save to database
            await db.save_company(company)
            print(f"Successfully saved company: {company.name}")
            return company
        else:
            print(f"Failed to generate embedding for company: {company.name}")
            return None
    except Exception as e:
        print(f"Error creating company: {str(e)}")
        return None

async def create_investor_with_embedding(db: Database, investor_data: dict) -> Investor:
    """Create an investor with embeddings."""
    try:
        # Check if investor already exists by name
        if await db.investor_name_exists(investor_data['name']):
            print(f"Investor {investor_data['name']} already exists, skipping...")
            return None

        # Create a new investor instance
        investor = Investor(**investor_data)
        
        # Generate text for embedding
        text = generate_investor_text_for_embedding(investor.model_dump())
        
        # Get embedding
        embedding = get_embedding(text)
        if embedding is not None:
            investor.embedding = embedding.tolist()
            
            # Save to database
            await db.save_investor(investor)
            print(f"Successfully saved investor: {investor.name}")
            return investor
        else:
            print(f"Failed to generate embedding for investor: {investor.name}")
            return None
    except Exception as e:
        print(f"Error creating investor: {str(e)}")
        return None

async def populate_database(fresh_start: bool = False):
    """Populate the database with sample companys and investors."""
    # Optionally clear the database before populating
    if fresh_start:
        if os.path.exists("sharewave_db_new.sqlite"):
            try:
                os.remove("sharewave_db_new.sqlite")
                print("Removed existing database file")
            except Exception as e:
                print(f"Error removing database file: {str(e)}")
    
    # Connect to database
    db = Database()
    try:
        await db.connect()
        print("Connected to database")

        # Create companys
        print("\nCreating companys...")
        companys = []
        for company_data in SAMPLE_COMPANIES:
            company = await create_company_with_embedding(db, company_data)
            if company:
                companys.append(company)
                print(f"Created company: {company.name} (ID: {company.id})")
        
        # Create investors
        print("\nCreating investors...")
        investors = []
        for investor_data in SAMPLE_INVESTORS:
            investor = await create_investor_with_embedding(db, investor_data)
            if investor:
                investors.append(investor)
                print(f"Created investor: {investor.name} (ID: {investor.id})")
        
        # Summary
        print(f"\nPopulated database with {len(companys)} companys and {len(investors)} investors")
                
    except Exception as e:
        print(f"Error populating database: {str(e)}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(populate_database(fresh_start=True))