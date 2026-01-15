from typing import Optional
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = """You are an expert content summarizer. Your task is to:
1. Analyze the provided text content
2. Extract the key points and main ideas
3. Create a concise summary in bulleted list format
4. Focus on the most important information
5. Keep each bullet point clear and brief

Format your response as a bulleted list using bullet points (•).
Each bullet should be a complete, standalone point.
Aim for 5-8 key points that capture the essence of the content."""


class SummarizeContentAgent:
    """Agent that summarizes text content into a concise bulleted list."""
    
    def __init__(self, *, credential: Optional[DefaultAzureCredential] = None) -> None:
        """Initialize the Summarize Content Agent.
        
        Args:
            credential: Azure credential for authentication. Defaults to DefaultAzureCredential.
        """
        self.credential = credential or DefaultAzureCredential()
        # Initialize the Azure OpenAI Chat Client
        self.client = AzureOpenAIChatClient(
            credential=self.credential, 
            endpoint="https://hosted-agent-deployment.services.ai.azure.com"
        )
        # Create agent with system instructions for summarization
        self.agent = self.client.create_agent(
            instructions=SYSTEM_PROMPT
        )

    async def run(self, content: str) -> str:
        """Run the agent to summarize the provided content.
        
        Args:
            content: The text content to summarize
            
        Returns:
            A concise bulleted list summary of the content
        """
        prompt = f"Please summarize the following content into a concise bulleted list:\n\n{content}"
        response = await self.agent.run(prompt)
        return response.text if response.text else ""
