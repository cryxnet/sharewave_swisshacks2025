# app/agents/financial.py
from app.agents.base import BaseAgent
from app.models.schemas import DocumentType, UploadedDocument, AgentScore
from app.services.llm import AzureOpenAIService

class FinancialAgent(BaseAgent):
    def __init__(self):
        super().__init__(DocumentType.FINANCIAL)
        self.llm = AzureOpenAIService()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        # Load the financial prompt template from a file or define it here
        return (
            """You are a financial due diligence expert analyzing company documents. Your task is to evaluate the financial health and viability of the company.

Document to analyze:
{document_content}

Please analyze the following aspects:
1. Financial statements and metrics
2. Cash flow and runway
3. Revenue growth and projections
4. Funding history and capital structure
5. Key financial risks

Provide your analysis in the following format:
- Safety Score (0-100): [score]

Be particularly alert for:
- Inconsistent financial statements
- Unrealistic projections
- Poor cash management
- High burn rate with limited runway
- Concentration risks
"""
        )
    
    async def analyze(self, document: UploadedDocument) -> AgentScore:
        prompt = self.prompt_template.format(
            document_content=document.content
        )
        
        response = await self.llm.analyze(prompt)
        
        # Parse LLM response to extract safety score and comments
        # This is a simplified version - you'd need proper response parsing
        safety_score = float(response.get("safety_score", 0))
        comments = response.get("comments", "")
        
        return AgentScore(
            agent_type=self.agent_type,
            safety_score=safety_score,
            comments=comments
        )