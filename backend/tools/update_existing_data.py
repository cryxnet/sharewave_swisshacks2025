import asyncio
import random
from database import Database
from models import (
    Company,
    Investor,
    RevenueStage,
    BusinessModel,
    ExitStrategy,
    FocusArea,
    FounderType,
    RiskAppetite,
    TimeHorizon,
)
from matching_algo import (
    get_embedding,
    generate_company_text_for_embedding,
    generate_investor_text_for_embedding,
)
from typing import List, Dict, Any, Optional
import json

# Industry-specific sub-industries mapping for more realistic data
INDUSTRY_SUB_INDUSTRIES = {
    "Software": ["SaaS", "Enterprise Software", "DevOps", "API", "Cloud Services"],
    "AI": [
        "Machine Learning",
        "Natural Language Processing",
        "Computer Vision",
        "Robotics",
        "Predictive Analytics",
    ],
    "Biotech": [
        "Genomics",
        "Pharmaceuticals",
        "Diagnostic Tools",
        "Gene Therapy",
        "Bioinformatics",
    ],
    "HealthTech": [
        "Telemedicine",
        "Health Monitoring",
        "Medical Devices",
        "Health Records",
        "Digital Therapeutics",
    ],
    "CleanTech": [
        "Renewable Energy",
        "Energy Storage",
        "Carbon Capture",
        "Smart Grid",
        "Water Tech",
    ],
    "Fintech": [
        "Payment Processing",
        "InsurTech",
        "Blockchain",
        "Personal Finance",
        "RegTech",
    ],
    "Mobility": [
        "Electric Vehicles",
        "Ride Sharing",
        "Logistics",
        "Urban Transport",
        "Autonomous Vehicles",
    ],
    "AgriTech": [
        "Precision Agriculture",
        "Smart Farming",
        "Crop Monitoring",
        "Supply Chain",
        "Vertical Farming",
    ],
    "Sustainability": [
        "Circular Economy",
        "Waste Management",
        "Eco Materials",
        "Conservation",
        "Carbon Footprint",
    ],
    "EdTech": [
        "E-Learning",
        "Educational Games",
        "Language Learning",
        "School Management",
        "Career Development",
    ],
    "Aerospace": [
        "Satellite Tech",
        "Space Tourism",
        "Propulsion Systems",
        "Drone Technology",
        "Space Mining",
    ],
    "MedTech": [
        "Medical Imaging",
        "Surgery Tech",
        "Patient Monitoring",
        "Diagnostics",
        "Rehabilitation",
    ],
    "Cybersecurity": [
        "Threat Detection",
        "Data Protection",
        "Identity Management",
        "Network Security",
        "Cryptography",
    ],
    "Big Data": [
        "Data Analytics",
        "Business Intelligence",
        "Data Visualization",
        "Real-time Processing",
        "Data Storage",
    ],
    "Quantum Computing": [
        "Quantum Hardware",
        "Quantum Algorithms",
        "Quantum Software",
        "Quantum Security",
        "Quantum Sensing",
    ],
    "FoodTech": [
        "Alternative Proteins",
        "Food Delivery",
        "Ghost Kitchens",
        "Food Processing",
        "Precision Fermentation",
    ],
    "LegalTech": [
        "Contract Analysis",
        "Legal Research",
        "Compliance",
        "E-Discovery",
        "IP Management",
    ],
    "XR/VR": [
        "Virtual Reality",
        "Augmented Reality",
        "Mixed Reality",
        "Immersive Training",
        "Digital Twins",
    ],
}

# Founder types by industry tendencies (for more realistic matches)
INDUSTRY_FOUNDER_TENDENCIES = {
    "Software": ["TECHNICAL", "SERIAL"],
    "AI": ["TECHNICAL", "ACADEMIC"],
    "Biotech": ["ACADEMIC", "TECHNICAL"],
    "HealthTech": ["ACADEMIC", "FIRST_TIME"],
    "CleanTech": ["TECHNICAL", "ACADEMIC"],
    "Fintech": ["SERIAL", "TECHNICAL"],
    "Mobility": ["TECHNICAL", "SERIAL"],
    "AgriTech": ["TECHNICAL", "FIRST_TIME"],
    "Sustainability": ["FIRST_TIME", "FEMALE"],
    "EdTech": ["ACADEMIC", "FEMALE"],
    "Aerospace": ["TECHNICAL", "ACADEMIC"],
    "MedTech": ["ACADEMIC", "FEMALE"],
    "Cybersecurity": ["TECHNICAL", "SERIAL"],
    "Big Data": ["TECHNICAL", "SERIAL"],
    "Quantum Computing": ["ACADEMIC", "TECHNICAL"],
    "FoodTech": ["FIRST_TIME", "UNDERREPRESENTED"],
    "LegalTech": ["FIRST_TIME", "TECHNICAL"],
    "XR/VR": ["TECHNICAL", "YOUNG"],
}

# Business model by industry tendencies
INDUSTRY_BUSINESS_MODEL = {
    "Software": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "AI": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "Biotech": [BusinessModel.HARDWARE, BusinessModel.SUBSCRIPTION],
    "HealthTech": [BusinessModel.HARDWARE, BusinessModel.SAAS],
    "CleanTech": [BusinessModel.HARDWARE, BusinessModel.SUBSCRIPTION],
    "Fintech": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "Mobility": [BusinessModel.HARDWARE, BusinessModel.SUBSCRIPTION],
    "AgriTech": [BusinessModel.HARDWARE, BusinessModel.SAAS],
    "Sustainability": [BusinessModel.HARDWARE, BusinessModel.MARKETPLACE],
    "EdTech": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "Aerospace": [BusinessModel.HARDWARE],
    "MedTech": [BusinessModel.HARDWARE, BusinessModel.SAAS],
    "Cybersecurity": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "Big Data": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "Quantum Computing": [BusinessModel.HARDWARE, BusinessModel.SAAS],
    "FoodTech": [BusinessModel.HARDWARE, BusinessModel.MARKETPLACE],
    "LegalTech": [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION],
    "XR/VR": [BusinessModel.HARDWARE, BusinessModel.SUBSCRIPTION],
}

# Revenue stage mapping by company stage
STAGE_REVENUE_MAPPING = {
    "Pre-Seed": [RevenueStage.PRE_REVENUE],
    "Seed": [RevenueStage.PRE_REVENUE, RevenueStage.EARLY_REVENUE],
    "Series A": [RevenueStage.EARLY_REVENUE, RevenueStage.BREAK_EVEN],
    "Series B": [RevenueStage.BREAK_EVEN, RevenueStage.PROFITABLE],
    "Series C": [RevenueStage.BREAK_EVEN, RevenueStage.PROFITABLE],
    "Growth": [RevenueStage.PROFITABLE],
}

# ESG focus likelihood by industry (0-100)
INDUSTRY_ESG_LIKELIHOOD = {
    "CleanTech": 90,
    "Sustainability": 95,
    "AgriTech": 70,
    "Mobility": 60,
    "FoodTech": 65,
    "Biotech": 40,
    "HealthTech": 40,
    "MedTech": 35,
    "EdTech": 50,
    "Software": 20,
    "AI": 25,
    "Fintech": 30,
    "Cybersecurity": 15,
    "Big Data": 20,
    "Quantum Computing": 25,
    "Aerospace": 30,
    "LegalTech": 30,
    "XR/VR": 20,
}


async def update_companies_direct_db(db: Database) -> None:
    """Update existing companies directly in the database without going through models."""
    cursor = await db.db.execute("SELECT * FROM company")
    rows = await cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    print(f"Found {len(rows)} companies to update")

    for row in rows:
        company_data = dict(zip(column_names, row))
        company_id = company_data["id"]
        updated_fields = {}

        # Add sub_industries if missing
        if "sub_industries" not in company_data or not company_data["sub_industries"]:
            industry = company_data.get("industry", "")
            possible_subs = INDUSTRY_SUB_INDUSTRIES.get(industry, [])
            if possible_subs:
                # Select 1-3 random sub-industries
                count = min(random.randint(1, 3), len(possible_subs))
                updated_fields["sub_industries"] = json.dumps(
                    random.sample(possible_subs, count)
                )

        # Add revenue_stage if missing
        if "revenue_stage" not in company_data or not company_data["revenue_stage"]:
            stage = company_data.get("stage", "Seed")
            possible_stages = STAGE_REVENUE_MAPPING.get(
                stage, [RevenueStage.EARLY_REVENUE]
            )
            updated_fields["revenue_stage"] = random.choice(possible_stages).value

        # Add business_model if missing
        if "business_model" not in company_data or not company_data["business_model"]:
            industry = company_data.get("industry", "")
            possible_models = INDUSTRY_BUSINESS_MODEL.get(
                industry, [BusinessModel.SAAS]
            )
            updated_fields["business_model"] = random.choice(possible_models).value

        # Add exit_strategy if missing
        if "exit_strategy" not in company_data or not company_data["exit_strategy"]:
            # Large companies more likely to aim for IPO
            valuation = company_data.get("total_valuation_usd", 0)
            if valuation > 40_000_000:
                updated_fields["exit_strategy"] = ExitStrategy.IPO.value
            elif valuation > 10_000_000:
                updated_fields["exit_strategy"] = random.choice(
                    [ExitStrategy.ACQUISITION.value, ExitStrategy.IPO.value]
                )
            else:
                # Earlier companies typically aim for acquisition
                updated_fields["exit_strategy"] = ExitStrategy.ACQUISITION.value

        # Add focus_areas if missing
        if (
            "focus_areas" not in company_data
            or not company_data["focus_areas"]
            or company_data["focus_areas"] == "[]"
        ):
            # Randomly select 0-3 focus areas
            focus_count = random.randint(0, 3)
            if focus_count > 0:
                # Get all possible focus areas
                all_focus_areas = [area.value for area in FocusArea]

                # Sustainability companies more likely to have sustainability focus
                if "Sustainability" in company_data.get(
                    "industry", ""
                ) or "Clean" in company_data.get("industry", ""):
                    sustainability_focus = ["sustainability", "esg", "climate_tech"]
                    chosen = random.sample(
                        sustainability_focus,
                        min(focus_count, len(sustainability_focus)),
                    )
                    remaining = focus_count - len(chosen)
                    if remaining > 0:
                        other_areas = [a for a in all_focus_areas if a not in chosen]
                        chosen.extend(random.sample(other_areas, remaining))
                else:
                    chosen = random.sample(all_focus_areas, focus_count)

                updated_fields["focus_areas"] = json.dumps(chosen)
            else:
                updated_fields["focus_areas"] = json.dumps([])

        # Add founder_types if missing
        if (
            "founder_types" not in company_data
            or not company_data["founder_types"]
            or company_data["founder_types"] == "[]"
        ):
            # Get industry-specific founder tendencies
            industry = company_data.get("industry", "")
            founder_tendencies = INDUSTRY_FOUNDER_TENDENCIES.get(
                industry, ["TECHNICAL", "FIRST_TIME"]
            )

            # Add 1-2 founder types, ensuring at least one from the industry tendency if possible
            count = random.randint(1, 2)
            if count == 1:
                updated_fields["founder_types"] = json.dumps(
                    [random.choice(founder_tendencies)]
                )
            else:
                # One from tendencies, one random from all types
                all_types = [founder_type.value for founder_type in FounderType]
                first_type = [random.choice(founder_tendencies)]
                remaining = [t for t in all_types if t not in first_type]
                first_type.append(random.choice(remaining))
                updated_fields["founder_types"] = json.dumps(first_type)

        # Add risk_appetite if missing
        if "risk_appetite" not in company_data or not company_data["risk_appetite"]:
            stage = company_data.get("stage", "")
            if stage in ["Pre-Seed", "Seed"]:
                # Early stage companies tend to be more risk-taking
                risk_options = [RiskAppetite.AGGRESSIVE, RiskAppetite.VERY_AGGRESSIVE]
            elif stage in ["Series A"]:
                risk_options = [RiskAppetite.MODERATE, RiskAppetite.AGGRESSIVE]
            else:
                # Later stage companies tend to be more conservative
                risk_options = [RiskAppetite.CONSERVATIVE, RiskAppetite.MODERATE]

            updated_fields["risk_appetite"] = random.choice(risk_options).value

        # Add time_horizon if missing
        if "time_horizon" not in company_data or not company_data["time_horizon"]:
            stage = company_data.get("stage", "")
            exit_strategy = company_data.get("exit_strategy", "")

            if exit_strategy == ExitStrategy.IPO.value:
                # IPO typically has longer horizon
                updated_fields["time_horizon"] = TimeHorizon.LONG_TERM.value
            elif stage in ["Pre-Seed", "Seed"]:
                # Early stage often has medium to long horizons
                updated_fields["time_horizon"] = random.choice(
                    [TimeHorizon.MEDIUM_TERM.value, TimeHorizon.LONG_TERM.value]
                )
            else:
                # Later stage can have shorter horizons
                updated_fields["time_horizon"] = random.choice(
                    [t.value for t in TimeHorizon]
                )

        # Add esg_focus if missing
        if "esg_focus" not in company_data or company_data["esg_focus"] is None:
            industry = company_data.get("industry", "")
            likelihood = INDUSTRY_ESG_LIKELIHOOD.get(industry, 20)
            updated_fields["esg_focus"] = (
                1 if random.randint(1, 100) <= likelihood else 0
            )

        # If we have updated fields, update the database
        if updated_fields:
            # Build the SQL update statement
            set_clauses = [f"{field} = ?" for field in updated_fields.keys()]
            set_statement = ", ".join(set_clauses)
            values = list(updated_fields.values())
            values.append(company_id)  # For the WHERE clause

            sql = f"UPDATE company SET {set_statement} WHERE id = ?"

            await db.db.execute(sql, values)
            await db.db.commit()

            # Now reload the company to recalculate the embedding
            company = await get_company_by_id(db, company_id)
            if company:
                # Generate new embedding text
                text = generate_company_text_for_embedding(company.model_dump())
                embedding = get_embedding(text)

                if embedding is not None:
                    # Update only the embedding
                    embedding_json = json.dumps(embedding.tolist())
                    await db.db.execute(
                        "UPDATE company SET embedding = ? WHERE id = ?",
                        (embedding_json, company_id),
                    )
                    await db.db.commit()
                    print(f"Updated company: {company.name}")
                else:
                    print(
                        f"Failed to generate new embedding for company: {company.name}"
                    )
            else:
                print(f"Failed to reload company with ID: {company_id}")


async def update_investors_direct_db(db: Database) -> None:
    """Update existing investors directly in the database without going through models."""
    cursor = await db.db.execute("SELECT * FROM investors")
    rows = await cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    print(f"Found {len(rows)} investors to update")

    for row in rows:
        investor_data = dict(zip(column_names, row))
        investor_id = investor_data["id"]
        updated_fields = {}

        # Add excluded_industries if missing
        if (
            "excluded_industries" not in investor_data
            or not investor_data["excluded_industries"]
            or investor_data["excluded_industries"] == "[]"
        ):
            # Common industries that might be excluded
            common_exclusions = [
                "Gambling",
                "Tobacco",
                "Weapons",
                "Adult Entertainment",
            ]

            # Impact investors more likely to exclude fossil fuels
            if "Impact" in investor_data.get("investor_type", ""):
                exclusions = ["Fossil Fuels", "Mining"] + random.sample(
                    common_exclusions, 1
                )
            else:
                # Regular investors exclude fewer industries
                exclusion_count = random.randint(0, 2)
                if exclusion_count > 0:
                    exclusions = random.sample(common_exclusions, exclusion_count)
                else:
                    exclusions = []

            updated_fields["excluded_industries"] = json.dumps(exclusions)

        # Add business_model_focus if missing
        if (
            "business_model_focus" not in investor_data
            or not investor_data["business_model_focus"]
            or investor_data["business_model_focus"] == "[]"
        ):
            # Get preferred industries - safely parse the JSON
            try:
                preferred_industries_str = investor_data.get(
                    "preferred_industries", "[]"
                )
                if (
                    preferred_industries_str
                    and preferred_industries_str != "null"
                    and preferred_industries_str != "None"
                ):
                    preferred_industries = json.loads(preferred_industries_str)
                else:
                    preferred_industries = []
            except Exception:
                preferred_industries = []

            # Start with empty list
            business_models = []

            # Add business models based on preferred industries
            for industry in preferred_industries:
                if industry in INDUSTRY_BUSINESS_MODEL:
                    models = INDUSTRY_BUSINESS_MODEL[industry]
                    business_models.extend([model.value for model in models])

            # Remove duplicates and take up to 3
            business_models = list(set(business_models))
            if not business_models:
                # Default if no matches
                business_models = [
                    BusinessModel.SAAS.value,
                    BusinessModel.SUBSCRIPTION.value,
                ]
            elif len(business_models) > 3:
                business_models = random.sample(business_models, 3)

            updated_fields["business_model_focus"] = json.dumps(business_models)

        # Add esg_mandate if missing
        if "esg_mandate" not in investor_data or investor_data["esg_mandate"] is None:
            # Impact investors always have ESG mandate
            if "Impact" in investor_data.get("investor_type", ""):
                updated_fields["esg_mandate"] = 1
            else:
                # Other investor types have about 30% chance
                updated_fields["esg_mandate"] = 1 if random.random() < 0.3 else 0

        # Add exit_timeline_years if missing
        if (
            "exit_timeline_years" not in investor_data
            or not investor_data["exit_timeline_years"]
        ):
            # Set exit timeline based on investor type and stage preferences
            investor_type = investor_data.get("investor_type", "")

            # Safely parse preferred_stages
            try:
                preferred_stages_str = investor_data.get("preferred_stages", "[]")
                if (
                    preferred_stages_str
                    and preferred_stages_str != "null"
                    and preferred_stages_str != "None"
                ):
                    preferred_stages = json.loads(preferred_stages_str)
                else:
                    preferred_stages = []
            except Exception:
                preferred_stages = []

            if "Angel" in investor_type or "Seed" in investor_type:
                # Early stage investors have longer timelines
                timeline = random.randint(7, 10)
            elif any(
                stage in ["Series B", "Series C", "Growth"]
                for stage in preferred_stages
            ):
                # Later stage investors have shorter timelines
                timeline = random.randint(3, 6)
            else:
                # Middle range
                timeline = random.randint(5, 8)

            updated_fields["exit_timeline_years"] = timeline

        # Add preferred_focus_areas if missing
        if (
            "preferred_focus_areas" not in investor_data
            or not investor_data["preferred_focus_areas"]
            or investor_data["preferred_focus_areas"] == "[]"
        ):
            # Impact investors focus on sustainability
            if (
                "Impact" in investor_data.get("investor_type", "")
                or investor_data.get("esg_mandate", 0) == 1
            ):
                focus_areas = ["sustainability", "esg", "climate_tech", "social_impact"]
                count = random.randint(2, 4)
                updated_fields["preferred_focus_areas"] = json.dumps(
                    random.sample(focus_areas, min(count, len(focus_areas)))
                )
            else:
                # Other investors may have some focus areas
                all_focus_areas = [area.value for area in FocusArea]
                count = random.randint(0, 3)
                if count > 0:
                    updated_fields["preferred_focus_areas"] = json.dumps(
                        random.sample(all_focus_areas, count)
                    )
                else:
                    updated_fields["preferred_focus_areas"] = json.dumps([])

        # Add preferred_founder_types if missing
        if (
            "preferred_founder_types" not in investor_data
            or not investor_data["preferred_founder_types"]
            or investor_data["preferred_founder_types"] == "[]"
        ):
            # Some investors focus on specific founder types
            all_founder_types = [founder_type.value for founder_type in FounderType]

            # Impact investors more likely to focus on female and underrepresented founders
            if (
                "Impact" in investor_data.get("investor_type", "")
                or investor_data.get("esg_mandate", 0) == 1
            ):
                diversity_focus = [
                    "female_founders",
                    "underrepresented_groups",
                    "young_founders",
                ]
                count = random.randint(1, 2)
                updated_fields["preferred_founder_types"] = json.dumps(
                    random.sample(diversity_focus, min(count, len(diversity_focus)))
                )
            else:
                # Other investors may have some preferences or none
                count = random.randint(0, 2)
                if count > 0:
                    updated_fields["preferred_founder_types"] = json.dumps(
                        random.sample(all_founder_types, count)
                    )
                else:
                    updated_fields["preferred_founder_types"] = json.dumps([])

        # Add risk_appetite if missing
        if "risk_appetite" not in investor_data or not investor_data["risk_appetite"]:
            # Determine risk appetite based on investor type and stage preferences
            investor_type = investor_data.get("investor_type", "")

            # Safely parse preferred_stages
            try:
                preferred_stages_str = investor_data.get("preferred_stages", "[]")
                if (
                    preferred_stages_str
                    and preferred_stages_str != "null"
                    and preferred_stages_str != "None"
                ):
                    preferred_stages = json.loads(preferred_stages_str)
                else:
                    preferred_stages = []
            except Exception:
                preferred_stages = []

            if "Angel" in investor_type or all(
                stage in ["Pre-Seed", "Seed"] for stage in preferred_stages if stage
            ):
                # Early stage investors typically have higher risk appetite
                risk_options = [RiskAppetite.AGGRESSIVE, RiskAppetite.VERY_AGGRESSIVE]
            elif any(
                stage in ["Series C", "Growth"] for stage in preferred_stages if stage
            ):
                # Later stage investors typically more conservative
                risk_options = [RiskAppetite.CONSERVATIVE, RiskAppetite.MODERATE]
            else:
                # Balanced approach
                risk_options = [RiskAppetite.MODERATE, RiskAppetite.AGGRESSIVE]

            updated_fields["risk_appetite"] = random.choice(risk_options).value

        # Add preferred_time_horizon if missing
        if (
            "preferred_time_horizon" not in investor_data
            or not investor_data["preferred_time_horizon"]
            or investor_data["preferred_time_horizon"] == "[]"
        ):
            # Determine time horizon based on exit timeline
            exit_timeline = investor_data.get("exit_timeline_years")
            # Make sure we have a valid integer for comparison
            if exit_timeline is None or not isinstance(exit_timeline, int):
                exit_timeline = 5  # Default value

            if exit_timeline >= 8:
                # Long term investors
                horizons = [TimeHorizon.LONG_TERM.value]
            elif exit_timeline >= 5:
                # Medium term
                horizons = [TimeHorizon.MEDIUM_TERM.value, TimeHorizon.LONG_TERM.value]
            else:
                # Short term investors
                horizons = [TimeHorizon.SHORT_TERM.value, TimeHorizon.MEDIUM_TERM.value]

            updated_fields["preferred_time_horizon"] = json.dumps(horizons)

        # If we have updated fields, update the database
        if updated_fields:
            # Build the SQL update statement
            set_clauses = [f"{field} = ?" for field in updated_fields.keys()]
            set_statement = ", ".join(set_clauses)
            values = list(updated_fields.values())
            values.append(investor_id)  # For the WHERE clause

            sql = f"UPDATE investors SET {set_statement} WHERE id = ?"

            await db.db.execute(sql, values)
            await db.db.commit()

            # Now reload the investor to recalculate the embedding
            investor = await get_investor_by_id(db, investor_id)
            if investor:
                # Generate new embedding text
                text = generate_investor_text_for_embedding(investor.model_dump())
                embedding = get_embedding(text)

                if embedding is not None:
                    # Update only the embedding
                    embedding_json = json.dumps(embedding.tolist())
                    await db.db.execute(
                        "UPDATE investors SET embedding = ? WHERE id = ?",
                        (embedding_json, investor_id),
                    )
                    await db.db.commit()
                    print(f"Updated investor: {investor.name}")
                else:
                    print(
                        f"Failed to generate new embedding for investor: {investor.name}"
                    )
            else:
                print(f"Failed to reload investor with ID: {investor_id}")


async def get_company_by_id(db: Database, company_id: str) -> Optional[Company]:
    """Get a company from the database by ID."""
    cursor = await db.db.execute("SELECT * FROM company WHERE id = ?", (company_id,))
    row = await cursor.fetchone()

    if not row:
        return None

    # Convert row to dict
    company_data = dict(zip([col[0] for col in cursor.description], row))

    # Parse JSON fields
    for field in ["focus_areas", "founder_types", "sub_industries"]:
        if company_data.get(field):
            try:
                company_data[field] = json.loads(company_data[field])
            except:
                company_data[field] = []
        else:
            company_data[field] = []

    # Convert SQLite integer to boolean for esg_focus
    if "esg_focus" in company_data:
        company_data["esg_focus"] = bool(company_data["esg_focus"])
    else:
        company_data["esg_focus"] = False

    # Parse embedding if it exists
    if company_data.get("embedding"):
        try:
            company_data["embedding"] = json.loads(company_data["embedding"])
        except:
            company_data["embedding"] = None

    # Create company object
    return Company(**company_data)


async def get_investor_by_id(db: Database, investor_id: str) -> Optional[Investor]:
    """Get an investor from the database by ID."""
    cursor = await db.db.execute("SELECT * FROM investors WHERE id = ?", (investor_id,))
    row = await cursor.fetchone()

    if not row:
        return None

    # Convert row to dict
    investor_data = dict(zip([col[0] for col in cursor.description], row))

    # Parse JSON fields
    for field in [
        "preferred_industries",
        "preferred_stages",
        "preferred_locations",
        "preferred_focus_areas",
        "preferred_founder_types",
        "preferred_time_horizon",
        "excluded_industries",
        "business_model_focus",
    ]:
        if investor_data.get(field):
            try:
                investor_data[field] = json.loads(investor_data[field])
            except:
                investor_data[field] = []
        else:
            investor_data[field] = []

    # Convert SQLite integer to boolean for esg_mandate
    if "esg_mandate" in investor_data:
        investor_data["esg_mandate"] = bool(investor_data["esg_mandate"])
    else:
        investor_data["esg_mandate"] = False

    # Parse embedding if it exists
    if investor_data.get("embedding"):
        try:
            investor_data["embedding"] = json.loads(investor_data["embedding"])
        except:
            investor_data["embedding"] = None

    # Create investor object
    return Investor(**investor_data)


async def update_database_schema(db: Database) -> None:
    """Add missing columns to the database tables."""
    # First, ensure the tables exist
    try:
        await db.db.execute("CREATE TABLE IF NOT EXISTS company (id TEXT PRIMARY KEY)")
        await db.db.execute(
            "CREATE TABLE IF NOT EXISTS investors (id TEXT PRIMARY KEY)"
        )
    except Exception as e:
        print(f"Warning: Error ensuring tables exist: {e}")

    # Check if company table has new columns
    try:
        # Add sub_industries column if missing
        await db.db.execute(
            "ALTER TABLE company ADD COLUMN sub_industries TEXT DEFAULT '[]'"
        )
        print("Added sub_industries column to company table")
    except Exception as e:
        # Column already exists or other error
        print(f"Note: Could not add sub_industries column: {e}")
        pass

    try:
        # Add revenue_stage column if missing
        await db.db.execute("ALTER TABLE company ADD COLUMN revenue_stage TEXT")
        print("Added revenue_stage column to company table")
    except:
        pass

    try:
        # Add business_model column if missing
        await db.db.execute("ALTER TABLE company ADD COLUMN business_model TEXT")
        print("Added business_model column to company table")
    except:
        pass

    try:
        # Add exit_strategy column if missing
        await db.db.execute("ALTER TABLE company ADD COLUMN exit_strategy TEXT")
        print("Added exit_strategy column to company table")
    except:
        pass

    try:
        # Add esg_focus column if missing
        await db.db.execute(
            "ALTER TABLE company ADD COLUMN esg_focus INTEGER DEFAULT 0"
        )
        print("Added esg_focus column to company table")
    except:
        pass

    # Check if investors table has new columns
    try:
        # Add excluded_industries column if missing
        await db.db.execute(
            "ALTER TABLE investors ADD COLUMN excluded_industries TEXT DEFAULT '[]'"
        )
        print("Added excluded_industries column to investors table")
    except:
        pass

    try:
        # Add business_model_focus column if missing
        await db.db.execute(
            "ALTER TABLE investors ADD COLUMN business_model_focus TEXT DEFAULT '[]'"
        )
        print("Added business_model_focus column to investors table")
    except:
        pass

    try:
        # Add esg_mandate column if missing
        await db.db.execute(
            "ALTER TABLE investors ADD COLUMN esg_mandate INTEGER DEFAULT 0"
        )
        print("Added esg_mandate column to investors table")
    except:
        pass

    try:
        # Add exit_timeline_years column if missing
        await db.db.execute(
            "ALTER TABLE investors ADD COLUMN exit_timeline_years INTEGER"
        )
        print("Added exit_timeline_years column to investors table")
    except:
        pass

    await db.db.commit()
    print("Database schema updated successfully")


async def main():
    """Main function to update the database."""
    db = Database()
    try:
        await db.connect()
        print("Connected to database")

        # First, update the database schema
        await update_database_schema(db)

        # Now update the data for companies and investors
        await update_companies_direct_db(db)
        await update_investors_direct_db(db)

        print("Database update completed")
    except Exception as e:
        print(f"Error updating database: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
