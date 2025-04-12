import aiosqlite
import json
from typing import List, Optional, Dict, Any
from models import Company, Investor

class Database:
    def __init__(self, db_path: str = "sharewave_db_new.sqlite"):
        self.db_path = db_path
        self.db = None

    async def connect(self):
        """Connect to the database and create tables if they don't exist."""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            # Enable foreign keys
            await self.db.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
            print("Database connection established successfully")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    async def close(self):
        """Close the database connection."""
        if self.db:
            await self.db.close()

    async def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        try:
            await self.db.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                industry TEXT NOT NULL,
                stage TEXT NOT NULL,
                description TEXT,
                location TEXT,
                total_valuation_usd REAL,
                focus_areas TEXT,
                founder_types TEXT,
                risk_appetite TEXT,
                time_horizon TEXT,
                expected_exit TEXT,
                embedding TEXT  -- Store as JSON string
            )
            """)
            await self.db.execute("""
            CREATE TABLE IF NOT EXISTS investors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                investor_type TEXT,
                preferred_industries TEXT,
                preferred_stages TEXT,
                min_investment_usd REAL,
                max_investment_usd REAL,
                preferred_locations TEXT,
                profile_summary TEXT,
                preferred_focus_areas TEXT,
                preferred_founder_types TEXT,
                risk_appetite TEXT,
                preferred_time_horizon TEXT,
                embedding TEXT  -- Store as JSON string
            )
            """)
            await self.db.commit()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise

    async def company_name_exists(self, name: str) -> bool:
        """Check if a company with the given name already exists."""
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM company WHERE LOWER(name) = LOWER(?)",
            (name,)
        )
        count = await cursor.fetchone()
        return count[0] > 0

    async def investor_name_exists(self, name: str) -> bool:
        """Check if an investor with the given name already exists."""
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM investors WHERE LOWER(name) = LOWER(?)",
            (name,)
        )
        count = await cursor.fetchone()
        return count[0] > 0

    async def save_company(self, company: Company):
        """Save a company to the database."""
        try:
            embedding_json = json.dumps(company.embedding) if company.embedding else None
            
            await self.db.execute("""
            INSERT INTO company (
                id, name, industry, stage, description, location,
                total_valuation_usd, focus_areas, founder_types, 
                risk_appetite, time_horizon, expected_exit, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                industry = excluded.industry,
                stage = excluded.stage,
                description = excluded.description,
                location = excluded.location,
                total_valuation_usd = excluded.total_valuation_usd,
                focus_areas = excluded.focus_areas,
                founder_types = excluded.founder_types,
                risk_appetite = excluded.risk_appetite,
                time_horizon = excluded.time_horizon,
                expected_exit = excluded.expected_exit,
                embedding = excluded.embedding
            """, (
                company.id,
                company.name,
                company.industry,
                company.stage,
                company.description,
                company.location,
                company.total_valuation_usd,
                json.dumps(company.focus_areas),
                json.dumps(company.founder_types),
                company.risk_appetite,
                company.time_horizon,
                company.expected_exit,
                embedding_json
            ))
            await self.db.commit()
            print(f"Company saved: {company.name} (ID: {company.id})")
        except Exception as e:
            print(f"Error saving company: {str(e)}")
            raise

    async def save_investor(self, investor: Investor):
        """Save an investor to the database."""
        try:
            await self.db.execute("""
            INSERT INTO investors (
                id, name, investor_type, preferred_industries,
                preferred_stages, min_investment_usd, max_investment_usd,
                preferred_locations, profile_summary, preferred_focus_areas,
                preferred_founder_types, risk_appetite, preferred_time_horizon, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                investor_type = excluded.investor_type,
                preferred_industries = excluded.preferred_industries,
                preferred_stages = excluded.preferred_stages,
                min_investment_usd = excluded.min_investment_usd,
                max_investment_usd = excluded.max_investment_usd,
                preferred_locations = excluded.preferred_locations,
                profile_summary = excluded.profile_summary,
                preferred_focus_areas = excluded.preferred_focus_areas,
                preferred_founder_types = excluded.preferred_founder_types,
                risk_appetite = excluded.risk_appetite,
                preferred_time_horizon = excluded.preferred_time_horizon,
                embedding = excluded.embedding
            """, (
                investor.id,
                investor.name,
                investor.investor_type,
                json.dumps(investor.preferred_industries),
                json.dumps(investor.preferred_stages),
                investor.min_investment_usd,
                investor.max_investment_usd,
                json.dumps(investor.preferred_locations),
                investor.profile_summary,
                json.dumps(investor.preferred_focus_areas),
                json.dumps(investor.preferred_founder_types),
                investor.risk_appetite,
                json.dumps(investor.preferred_time_horizon),
                json.dumps(investor.embedding) if investor.embedding else None
            ))
            await self.db.commit()
            print(f"Investor saved: {investor.name} (ID: {investor.id})")
        except Exception as e:
            print(f"Error saving investor: {str(e)}")
            raise

    async def get_all_companies(self) -> List[Company]:
        """Retrieve all company from the database."""
        cursor = await self.db.execute("SELECT * FROM company")
        rows = await cursor.fetchall()
        company = []
        
        for row in rows:
            company_data = dict(zip([col[0] for col in cursor.description], row))
            
            # Parse JSON fields
            for field in ['focus_areas', 'founder_types']:
                if company_data.get(field):
                    company_data[field] = json.loads(company_data[field])
                else:
                    company_data[field] = []
                    
            # Parse embedding if it exists
            if company_data['embedding']:
                company_data['embedding'] = json.loads(company_data['embedding'])
                
            company.append(Company(**company_data))
        
        return company

    async def get_all_investors(self) -> List[Investor]:
        """Retrieve all investors from the database."""
        cursor = await self.db.execute("SELECT * FROM investors")
        rows = await cursor.fetchall()
        investors = []
        
        for row in rows:
            investor_data = dict(zip([col[0] for col in cursor.description], row))
            
            # Parse JSON fields
            for field in ['preferred_industries', 'preferred_stages', 'preferred_locations', 
                         'preferred_focus_areas', 'preferred_founder_types', 'preferred_time_horizon']:
                if investor_data.get(field):
                    investor_data[field] = json.loads(investor_data[field])
                else:
                    investor_data[field] = []
                    
            # Parse embedding if it exists
            if investor_data['embedding']:
                investor_data['embedding'] = json.loads(investor_data['embedding'])
                
            investors.append(Investor(**investor_data))
            
        return investors