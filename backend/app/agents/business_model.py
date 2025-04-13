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
        return """You are a business model analysis expert conducting due diligence. Your task is to evaluate the company's business model viability and execution capability.

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


Provide your analysis in the following yaml format:
- Safety Score (0-100): [score]

"""

    async def analyze(self, document: UploadedDocument) -> AgentScore:
        prompt = self.prompt_template.format(document_content=document.content)

        response = await self.llm.analyze(prompt)

        # Parse LLM response to extract safety score and comments
        # This is a simplified version - you'd need proper response parsing
        safety_score = float(response.get("safety_score", 0))
        comments = response.get("comments", "")

        return AgentScore(
            agent_type=self.agent_type, safety_score=safety_score, comments=comments
        )
