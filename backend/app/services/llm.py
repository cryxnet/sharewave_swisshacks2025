# app/services/llm.py
from openai import AzureOpenAI
from app.config import settings

class AzureOpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-15-preview"
        )
    
    async def analyze(self, prompt: str) -> dict:
        response = await self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a due diligence expert analyzing company documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # Parse the response to extract structured information
        # This is simplified - you'd need proper response parsing
        return {
            "safety_score": 75.0,  # Example
            "comments": response.choices[0].message.content
        }