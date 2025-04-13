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
            """You are a market analysis expert conducting due diligence. Your task is to evaluate the company's market opportunity and competitive position.

Document to analyze:
{document_content}

Please analyze the following aspects:
1. Market size and growth
2. Competitive landscape
3. Market trends and dynamics
4. Customer segments and needs
5. Go-to-market strategy


Be particularly alert for:
- Market size overestimation
- Competitive threats
- Changing market dynamics
- Customer concentration
- GTM strategy feasibility

Provide your analysis in the following format:
- Safety Score (0-100): [score]

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