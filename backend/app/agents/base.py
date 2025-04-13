#app/agents/base.py
from abc import ABC, abstractmethod
from app.models.schemas import UploadedDocument, AgentScore
from app.models.schemas import DocumentType
from app.config import settings
import os

class BaseAgent(ABC):
    def __init__(self, agent_type: DocumentType):
        self.agent_type = agent_type
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        with open(f"prompts/{self.agent_type}_prompt.txt", "r") as f:
            return f.read()
    
    @abstractmethod
    async def analyze(self, document: UploadedDocument) -> AgentScore:
        pass
