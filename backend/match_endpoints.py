from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from models import MatchResult
from database import Database
from matching_algo import find_matches_for_company, find_matches_for_investor

# Create router for matching endpoints
router = APIRouter(
    prefix="/matching",
    tags=["matching"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for API responses
class MatchDetailsResponse(BaseModel):
    entity_id: str
    name: str
    score: float
    details: dict = {}

class MatchesResponse(BaseModel):
    matches: List[MatchDetailsResponse]
    count: int
    entity_type: str  # "company" or "investor"
    entity_name: str  # Name of the entity we're finding matches for

# Database dependency
async def get_db():
    db = Database()
    try:
        await db.connect()
        yield db
    finally:
        await db.close()

@router.get("/company/{company_id}", response_model=MatchesResponse)
async def get_company_matches(
    company_id: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of matches to return"),
    min_score: float = Query(0.0, ge=0, le=10, description="Minimum match score"),
    db: Database = Depends(get_db)
):
    """
    Get investor matches for a specific company.
    
    - **company_id**: UUID of the company to find matches for
    - **limit**: Maximum number of matches to return (default: 5)
    - **min_score**: Minimum match score threshold (default: 0.0)
    """
    try:
        # Get all companies and investors from the database
        companies = await db.get_all_companies()
        investors = await db.get_all_investors()
        
        # Find the target company
        target_company = next((c for c in companies if c.id == company_id), None)
        if not target_company:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
        
        # Get matches using the matching algorithm
        matches = find_matches_for_company(
            company_id,
            companies,
            investors,
            top_n=limit
        )
        
        # Filter by minimum score if specified
        matches = [m for m in matches if m.score >= min_score]
        
        # Convert to response model
        match_details = [
            MatchDetailsResponse(
                entity_id=m.entity_id,
                name=m.name,
                score=m.score,
                details=m.details
            ) for m in matches
        ]
        
        # Return the response
        return MatchesResponse(
            matches=match_details,
            count=len(match_details),
            entity_type="investor",
            entity_name=target_company.name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")

@router.get("/investor/{investor_id}", response_model=MatchesResponse)
async def get_investor_matches(
    investor_id: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of matches to return"),
    min_score: float = Query(0.0, ge=0, le=10, description="Minimum match score"),
    db: Database = Depends(get_db)
):
    """
    Get company matches for a specific investor.
    
    - **investor_id**: UUID of the investor to find matches for
    - **limit**: Maximum number of matches to return (default: 5)
    - **min_score**: Minimum match score threshold (default: 0.0)
    """
    try:
        # Get all companies and investors from the database
        companies = await db.get_all_companies()
        investors = await db.get_all_investors()
        
        # Find the target investor
        target_investor = next((i for i in investors if i.id == investor_id), None)
        if not target_investor:
            raise HTTPException(status_code=404, detail=f"Investor with ID {investor_id} not found")
        
        # Get matches using the matching algorithm
        matches = find_matches_for_investor(
            investor_id,
            companies,
            investors,
            top_n=limit
        )
        
        # Filter by minimum score if specified
        matches = [m for m in matches if m.score >= min_score]
        
        # Convert to response model
        match_details = [
            MatchDetailsResponse(
                entity_id=m.entity_id,
                name=m.name,
                score=m.score,
                details=m.details
            ) for m in matches
        ]
        
        # Return the response
        return MatchesResponse(
            matches=match_details,
            count=len(match_details),
            entity_type="company",
            entity_name=target_investor.name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")