from pydantic import BaseModel
from typing import List, Dict
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    FINANCIAL = "financial"
    BUSINESS = "business"
    LEGAL = "legal"
    MARKET = "market"
    RISK = "risk"

class UploadedDocument(BaseModel):
    filename: str
    doc_type: DocumentType
    content: str

class DueDiligenceRequest(BaseModel):
    company_name: str
    documents: List[UploadedDocument]

class AgentScore(BaseModel):
    agent_type: DocumentType
    safety_score: float
    comments: str

class DueDiligenceResponse(BaseModel):
    company_name: str
    is_safe: bool
    average_score: float
    agent_scores: List[AgentScore]
    timestamp: datetime