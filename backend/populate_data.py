import asyncio
import os
from database import Database
from models import Company, Investor, RevenueStage, BusinessModel, ExitStrategy
from matching_algo import get_embedding, generate_company_text_for_embedding, generate_investor_text_for_embedding

# Sample company data
SAMPLE_COMPANIES = [
    {
        "name": "TechFlow Solutions",
        "industry": "Software",
        "sub_industries": ["SaaS", "Enterprise Software"],
        "stage": "Series A",
        "description": "Cloud-native enterprise software solutions",
        "location": "Switzerland",
        "total_valuation_usd": 15_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "BioInnovate Labs",
        "industry": "Biotech",
        "sub_industries": ["Pharmaceuticals", "Gene Therapy"],
        "stage": "Seed",
        "description": "Revolutionary biotech research in healthcare",
        "location": "Germany",
        "total_valuation_usd": 5_000_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.SUBSCRIPTION,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "GreenEnergy Corp",
        "industry": "CleanTech",
        "sub_industries": ["Renewable Energy", "Energy Storage"],
        "stage": "Series B",
        "description": "Sustainable energy solutions for industry",
        "location": "Remote",
        "total_valuation_usd": 50_000_000.0,
        "revenue_stage": RevenueStage.BREAK_EVEN,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.IPO,
        "esg_focus": True
    },
    {
        "name": "NeuroSync AI",
        "industry": "AI",
        "sub_industries": ["Health AI", "Cognitive Computing"],
        "stage": "Seed",
        "description": "Cognitive AI tools for mental health diagnostics",
        "location": "Germany",
        "total_valuation_usd": 3_000_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "AgroNova Tech",
        "industry": "AgriTech",
        "sub_industries": ["Precision Agriculture", "IoT"],
        "stage": "Series A",
        "description": "Smart farming solutions using IoT and AI",
        "location": "Netherlands",
        "total_valuation_usd": 12_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "QuantumLeap Systems",
        "industry": "Quantum Computing",
        "sub_industries": ["Quantum Hardware", "Quantum Algorithms"],
        "stage": "Pre-Seed",
        "description": "Building scalable quantum hardware",
        "location": "Switzerland",
        "total_valuation_usd": 1_500_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "UrbanMobility Inc.",
        "industry": "Mobility",
        "sub_industries": ["Electric Vehicles", "Urban Transport"],
        "stage": "Series B",
        "description": "Electric micro-mobility solutions for cities",
        "location": "Remote",
        "total_valuation_usd": 40_000_000.0,
        "revenue_stage": RevenueStage.BREAK_EVEN,
        "business_model": BusinessModel.SUBSCRIPTION,
        "exit_strategy": ExitStrategy.IPO,
        "esg_focus": True
    },
    {
        "name": "MedScan Diagnostics",
        "industry": "HealthTech",
        "sub_industries": ["Medical Imaging", "AI Diagnostics"],
        "stage": "Series A",
        "description": "AI-powered medical imaging diagnostics",
        "location": "Germany",
        "total_valuation_usd": 10_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "EcoFabric Co.",
        "industry": "Sustainability",
        "sub_industries": ["Textiles", "Biodegradable Materials"],
        "stage": "Seed",
        "description": "Sustainable and biodegradable textile production",
        "location": "Sweden",
        "total_valuation_usd": 2_800_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "FinNova AI",
        "industry": "Fintech",
        "sub_industries": ["Personal Finance", "AI"],
        "stage": "Series A",
        "description": "AI-driven personal finance and wealth management tools",
        "location": "Switzerland",
        "total_valuation_usd": 9_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "DeepSpace Mining",
        "industry": "Aerospace",
        "sub_industries": ["Space Mining", "Materials"],
        "stage": "Series B",
        "description": "Asteroid mining tech for rare materials",
        "location": "Germany",
        "total_valuation_usd": 70_000_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.IPO,
        "esg_focus": False
    },
    {
        "name": "SmartGrid AI",
        "industry": "CleanTech",
        "sub_industries": ["Grid Optimization", "Energy AI"],
        "stage": "Series A",
        "description": "AI solutions for optimizing energy grids",
        "location": "Switzerland",
        "total_valuation_usd": 18_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "EduBotics",
        "industry": "EdTech",
        "sub_industries": ["Robotics", "Education"],
        "stage": "Seed",
        "description": "Robotic education kits for children and schools",
        "location": "Germany",
        "total_valuation_usd": 3_500_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "CyberGuard Labs",
        "industry": "Cybersecurity",
        "sub_industries": ["Threat Detection", "Machine Learning"],
        "stage": "Series A",
        "description": "Advanced threat detection using machine learning",
        "location": "Remote",
        "total_valuation_usd": 15_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "PlantAI",
        "industry": "AgriTech",
        "sub_industries": ["AI", "Plant Science"],
        "stage": "Seed",
        "description": "AI-based plant health diagnostics and monitoring",
        "location": "Netherlands",
        "total_valuation_usd": 2_200_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "OceanClean Robotics",
        "industry": "Sustainability",
        "sub_industries": ["Marine Robotics", "Ocean Cleanup"],
        "stage": "Series B",
        "description": "Robots for cleaning plastic from oceans and rivers",
        "location": "Switzerland",
        "total_valuation_usd": 45_000_000.0,
        "revenue_stage": RevenueStage.BREAK_EVEN,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.IPO,
        "esg_focus": True
    },
    {
        "name": "BioSynth Foods",
        "industry": "FoodTech",
        "sub_industries": ["Alternative Proteins", "Synthetic Biology"],
        "stage": "Series A",
        "description": "Synthetic biology for alternative protein production",
        "location": "Germany",
        "total_valuation_usd": 13_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "LegalEase AI",
        "industry": "LegalTech",
        "sub_industries": ["AI", "Contract Analysis"],
        "stage": "Seed",
        "description": "AI-based contract analysis and legal assistance",
        "location": "Remote",
        "total_valuation_usd": 4_000_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": False
    },
    {
        "name": "NanoMed Devices",
        "industry": "MedTech",
        "sub_industries": ["Nanotechnology", "Drug Delivery"],
        "stage": "Series A",
        "description": "Nanotech for targeted drug delivery",
        "location": "Germany",
        "total_valuation_usd": 11_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "SolarX Innovations",
        "industry": "CleanTech",
        "sub_industries": ["Solar Energy", "Flexible Materials"],
        "stage": "Seed",
        "description": "High-efficiency solar panels with flexible materials",
        "location": "Switzerland",
        "total_valuation_usd": 3_800_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "DataSphere Analytics",
        "industry": "Big Data",
        "sub_industries": ["Real-time Analytics", "Data Processing"],
        "stage": "Series B",
        "description": "Scalable analytics platform for real-time insights",
        "location": "Remote",
        "total_valuation_usd": 55_000_000.0,
        "revenue_stage": RevenueStage.BREAK_EVEN,
        "business_model": BusinessModel.SAAS,
        "exit_strategy": ExitStrategy.IPO,
        "esg_focus": False
    },
    {
        "name": "ReGen Materials",
        "industry": "Sustainability",
        "sub_industries": ["Recycling", "Material Science"],
        "stage": "Series A",
        "description": "Upcycling waste into high-performance materials",
        "location": "Germany",
        "total_valuation_usd": 8_000_000.0,
        "revenue_stage": RevenueStage.EARLY_REVENUE,
        "business_model": BusinessModel.HARDWARE,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    },
    {
        "name": "MindLink VR",
        "industry": "XR/VR",
        "sub_industries": ["Mental Health", "Biofeedback"],
        "stage": "Pre-Seed",
        "description": "Immersive therapy solutions using VR and biofeedback",
        "location": "Remote",
        "total_valuation_usd": 1_200_000.0,
        "revenue_stage": RevenueStage.PRE_REVENUE,
        "business_model": BusinessModel.SUBSCRIPTION,
        "exit_strategy": ExitStrategy.ACQUISITION,
        "esg_focus": True
    }
]

# Sample investor data
SAMPLE_INVESTORS = [
    {
        "name": "Tech Ventures Capital",
        "investor_type": "VC",
        "preferred_industries": ["Software", "AI", "Fintech"],
        "excluded_industries": ["Gambling", "Tobacco", "Fossil Fuels"],
        "preferred_stages": ["Seed", "Series A"],
        "preferred_locations": ["Switzerland", "Germany", "Remote"],
        "min_investment_usd": 1_000_000.0,
        "max_investment_usd": 10_000_000.0,
        "business_model_focus": ["SaaS", "Marketplace", "Subscription"],
        "esg_mandate": False,
        "exit_timeline_years": 5,
        "profile_summary": "Early-stage tech investor focused on B2B SaaS"
    },
    {
        "name": "Life Sciences Fund",
        "investor_type": "VC",
        "preferred_industries": ["Biotech", "Healthcare", "MedTech"],
        "excluded_industries": ["Tobacco", "Alcohol"],
        "preferred_stages": ["Seed", "Series A", "Series B"],
        "preferred_locations": ["Germany", "Switzerland"],
        "min_investment_usd": 2_000_000.0,
        "max_investment_usd": 20_000_000.0,
        "business_model_focus": ["Hardware", "SaaS"],
        "esg_mandate": False,
        "exit_timeline_years": 7,
        "profile_summary": "Specialized in life sciences and healthcare innovations"
    },
    {
        "name": "Green Future Investments",
        "investor_type": "Impact Fund",
        "preferred_industries": ["CleanTech", "Sustainability", "GreenEnergy"],
        "excluded_industries": ["Fossil Fuels", "Mining", "Tobacco"],
        "preferred_stages": ["Series A", "Series B"],
        "preferred_locations": ["Remote", "Switzerland", "Germany"],
        "min_investment_usd": 5_000_000.0,
        "max_investment_usd": 50_000_000.0,
        "business_model_focus": ["Hardware", "SaaS", "Marketplace"],
        "esg_mandate": True,
        "exit_timeline_years": 10,
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
    """Populate the database with sample companies and investors."""
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

        # Create companies
        print("\nCreating companies...")
        companies = []
        for company_data in SAMPLE_COMPANIES:
            company = await create_company_with_embedding(db, company_data)
            if company:
                companies.append(company)
                print(f"Created company: {company.name} (ID: {company.id})")
        
        # Create investors
        print("\nCreating investors...")
        investors = []
        for investor_data in SAMPLE_INVESTORS:
            investor = await create_investor_with_embedding(db, investor_data)
            if investor:
                investors.append(investor)
                print(f"Created investor: {investor.name} (ID: {investor.id})")
        
        #call update_existing_data to ensure all data is up to date
        # try:
        import update_existing_data
        print("Updating existing data...")

        await update_existing_data.main()
        print("Updated existing data successfully")
        # except Exception as e:
        #     print(f"Error updating existing data: {str(e)}")
            
        # Summary
        print(f"\nPopulated database with {len(companies)} companies and {len(investors)} investors")
    except Exception as e:
        print(f"Error populating database: {str(e)}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(populate_database(fresh_start=True))