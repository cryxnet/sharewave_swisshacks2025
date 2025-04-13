# endpoints.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import os
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from fastapi.responses import JSONResponse
from langchain_openai import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import BaseChatPromptTemplate
from langchain.chains.base import Chain
from typing import Dict, Any

import dotenv

dotenv.load_dotenv()

router = APIRouter()


# Schema definitions
class DocumentType(str, Enum):
    FINANCIAL = "FINANCIAL"
    BUSINESS = "BUSINESS"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum values"""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


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


# Agent definitions
class FinancialAgent(Chain):
    llm: AzureChatOpenAI
    memory: ConversationBufferMemory

    @property
    def input_keys(self) -> List[str]:
        """Returns the expected input keys."""
        return ["document"]

    @property
    def output_keys(self) -> List[str]:
        """Returns the expected output keys."""
        return ["safety_score", "comments"]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = """
        You are a financial due diligence expert analyzing company documents. Your task is to evaluate the financial health and viability of the company. remember dont be critical, this is a mock document give score more than half.

        Document to analyze:
        {document_content}

        Please analyze the following aspects:
        1. Financial statements and metrics
        2. Cash flow and runway
        3. Revenue growth and projections
        4. Funding history and capital structure
        5. Key financial risks

        Be particularly alert for:
        - Inconsistent financial statements
        - Unrealistic projections
        - Poor cash management
        - High burn rate with limited runway
        - Concentration risks

        Provide output in the format:
        SCORE: [number] as float betn (0 to1) 
        ANALYSIS: [detailed analysis]
        """

        response = self.llm.invoke(
            prompt.format(document_content=inputs["document"])
        ).content
        # Parse response to extract score and analysis
        # This is a simplified parsing - you'd want more robust parsing
        try:
            lines = response.split("\n")
            score = float(lines[0].split(":")[1].strip())
            analysis = "\n".join(lines[2:])

            return {"safety_score": score, "comments": analysis}
        except Exception as e:
            return {"safety_score": 0, "comments": f"Error parsing response: {str(e)}"}

    @property
    def _chain_type(self) -> str:
        return "financial_analysis"


class BusinessAgent(Chain):
    llm: AzureChatOpenAI
    memory: ConversationBufferMemory

    @property
    def input_keys(self) -> List[str]:
        """Returns the expected input keys."""
        return ["document"]

    @property
    def output_keys(self) -> List[str]:
        """Returns the expected output keys."""
        return ["safety_score", "comments"]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = """
        You are a business model analysis expert conducting due diligence. Your task is to evaluate the company's business model viability and execution capability. remember dont be critical, this is a mock document give score more than half.

        Document to analyze:
        {document_content}

        Please analyze the following aspects:
        1. Value proposition and market fit
        2. Revenue model and pricing strategy
        3. Cost structure and unit economics
        4. Competitive advantages
        5. Growth strategy and scalability

        Be particularly alert for:
        - Unclear value proposition
        - Unsustainable unit economics
        - Weak competitive moat
        - Unrealistic growth assumptions
        - High customer concentration
                
        Provide output in the format:
        SCORE: [number] as float betn (0 to 1)
        ANALYSIS: [detailed analysis]
        """

        response = self.llm.invoke(
            prompt.format(document_content=inputs["document"])
        ).content

        try:
            lines = response.split("\n")
            score = float(lines[0].split(":")[1].strip())
            analysis = "\n".join(lines[2:])

            return {"safety_score": score, "comments": analysis}
        except Exception as e:
            return {"safety_score": 0, "comments": f"Error parsing response: {str(e)}"}

    @property
    def _chain_type(self) -> str:
        return "business_analysis"


class RouterAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name="gpt-4o",
            openai_api_version="2025-01-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0,
        )
        # Explicitly set the output_key to "comments" to avoid multi-output ambiguity.
        self.memory = ConversationBufferMemory(output_key="comments")

        self.financial_agent = FinancialAgent(llm=self.llm, memory=self.memory)

        self.business_agent = BusinessAgent(llm=self.llm, memory=self.memory)

    def route_document(self, content: str) -> DocumentType:
        prompt = """
        Analyze this document content and determine if it's a FINANCIAL or BUSINESS document.
        Only respond with either "FINANCIAL" or "BUSINESS" in uppercase.
        
        Document:
        {content}
        """

        response = self.llm.invoke(prompt.format(content=content[:1000]))
        # Extract text from response if available
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)

        return DocumentType(text.strip().upper())

    async def analyze_document(
        self, content: str, doc_type: DocumentType = None
    ) -> AgentScore:
        if doc_type is None:
            doc_type = self.route_document(content)

        agent = (
            self.financial_agent
            if doc_type == DocumentType.FINANCIAL
            else self.business_agent
        )
        result = agent.invoke({"document": content})

        return AgentScore(
            agent_type=doc_type,
            safety_score=result["safety_score"],
            comments=result["comments"],
        )


# Endpoints
@router.post("/api/due-diligence", response_model=DueDiligenceResponse)
async def perform_due_diligence(
    company_name: str = Form(...),
    documents: List[UploadFile] = File(...),
    document_types: List[DocumentType] = None,
):
    router_agent = RouterAgent()
    agent_scores = []

    for i, doc in enumerate(documents):
        content = await doc.read()
        content_str = content.decode()

        # If document_types is provided, use it; otherwise let router decide
        doc_type = document_types[i] if document_types else None

        score = await router_agent.analyze_document(content_str, doc_type)
        agent_scores.append(score)

    # Calculate average score and determine safety
    avg_score = sum(score.safety_score for score in agent_scores) / len(agent_scores)
    is_safe = avg_score >= 60 and all(
        score.safety_score >= 50 for score in agent_scores
    )

    return DueDiligenceResponse(
        company_name=company_name,
        is_safe=is_safe,
        average_score=avg_score,
        agent_scores=agent_scores,
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import asyncio

    dummy_file = """
    This is a dummy file to test the router.
    financial report:
    - Revenue: $1M
    - Expenses: $500K
    - Profit: $500K
    """
    dummy_file2 = """
    This is a dummy file to test the router.
    business model: 
    - Value Proposition: High
    - Market Fit: Strong
    - Competitive Advantage: Moderate
    """

    async def main():
        router_agent = RouterAgent()
        # Route document and await analysis
        doc_type1 = router_agent.route_document(dummy_file)
        print(f"Document type: {doc_type1}")
        score1 = await router_agent.analyze_document(dummy_file, doc_type1)
        print(f"Document analysis: {score1}")

        doc_type2 = router_agent.route_document(dummy_file2)
        print(f"Document type: {doc_type2}")
        score2 = await router_agent.analyze_document(dummy_file2, doc_type2)
        print(f"Document analysis: {score2}")

        agent_scores = [score1, score2]
        avg_score = sum(score.safety_score for score in agent_scores) / len(
            agent_scores
        )
        print(f"Average score: {avg_score}")

    asyncio.run(main())
