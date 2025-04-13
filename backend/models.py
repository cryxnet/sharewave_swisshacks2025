# Updated models.py
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from enum import Enum

def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())

class FocusArea(str, Enum):
    SUSTAINABILITY = "sustainability"
    ESG = "esg"
    ETHICAL_SOURCING = "ethical_sourcing"
    CLIMATE_TECH = "climate_tech"
    SOCIAL_IMPACT = "social_impact"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINTECH = "fintech"
    AI = "artificial_intelligence"
    BLOCKCHAIN = "blockchain"

class FounderType(str, Enum):
    FEMALE = "female_founders"
    YOUNG = "young_founders"
    UNDERREPRESENTED = "underrepresented_groups"
    SERIAL = "serial_entrepreneurs"
    FIRST_TIME = "first_time_founders"
    TECHNICAL = "technical_founders"
    ACADEMIC = "academic_founders"

class RiskAppetite(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

class RevenueStage(str, Enum):
    PRE_REVENUE = "pre_revenue"
    EARLY_REVENUE = "early_revenue"
    BREAK_EVEN = "break_even"
    PROFITABLE = "profitable"

class BusinessModel(str, Enum):
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    HARDWARE = "hardware"
    SUBSCRIPTION = "subscription"
    LICENSING = "licensing"
    CONSULTING = "consulting"

class ExitStrategy(str, Enum):
    ACQUISITION = "acquisition"
    IPO = "ipo"
    MERGER = "merger"

class TimeHorizon(str, Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"

# Update existing models
class Company(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    industry: str
    sub_industries: List[str] = Field(default_factory=list)
    stage: str
    description: str
    location: str
    total_valuation_usd: float
    revenue_stage: Optional[str] = None
    business_model: Optional[str] = None
    exit_strategy: Optional[str] = None
    focus_areas: List[str] = Field(default_factory=list)
    founder_types: List[str] = Field(default_factory=list)
    risk_appetite: Optional[str] = None
    time_horizon: Optional[str] = None
    # expected_exit: Optional[str] = None
    esg_focus: bool = False
    embedding: Optional[List[float]] = None

class Investor(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    investor_type: str
    preferred_industries: List[str]
    excluded_industries: List[str] = Field(default_factory=list)
    preferred_stages: List[str]
    preferred_locations: List[str]
    min_investment_usd: Optional[float] = None
    max_investment_usd: Optional[float] = None
    business_model_focus: List[str] = Field(default_factory=list)
    esg_mandate: bool = False
    exit_timeline_years: Optional[int] = None
    profile_summary: str
    preferred_focus_areas: List[str] = Field(default_factory=list)
    preferred_founder_types: List[str] = Field(default_factory=list)
    risk_appetite: Optional[str] = None
    preferred_time_horizon: List[str] = Field(default_factory=list)
    embedding: Optional[List[float]] = None

class MatchResult(BaseModel):
    entity_id: str
    name: str
    score: float
    details: dict = {}
    
    def __repr__(self):
        return f"Match(Name: {self.name}, Score: {self.score:.2f}, Details: {self.details})"