from typing import Optional
import os

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = "You are good at telling jokes."


class JokerAgent:
    def __init__(self, *, credential: Optional[DefaultAzureCredential] = None) -> None:
        # AzureOpenAIChatClient reads AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, and optional API key.
        self.credential = credential or DefaultAzureCredential()
        # Read endpoint from .env via AZURE_OPENAI_ENDPOINT for consistency with Azure OpenAI clients.
        # AZURE_AI_PROJECT_ENDPOINT="https://hosted-agent-deployment.services.ai.azure.com"
        self.client = AzureOpenAIChatClient(credential=self.credential, endpoint="https://hosted-agent-deployment.services.ai.azure.com")
        self.agent = self.client.create_agent(instructions=SYSTEM_PROMPT)

    async def run(self, user_prompt: str) -> str:
        response = await self.agent.run(user_prompt)

        return response.text if response.text else ""
