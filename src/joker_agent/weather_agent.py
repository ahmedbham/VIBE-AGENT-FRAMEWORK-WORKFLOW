from typing import Optional
import os

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = "You are a helpful assistant that can provide weather information."


def get_weather(location: str) -> str:
    """Get the weather for a given location.
    
    Args:
        location: The location to get weather information for
        
    Returns:
        A string describing the weather at the specified location
    """
    return f"The weather in {location} is cloudy with a high of 15°C."


class WeatherAgent:
    def __init__(self, *, credential: Optional[AzureCliCredential] = None) -> None:
        """Initialize the Weather Agent with function calling capability.
        
        Args:
            credential: Azure credential for authentication. Defaults to AzureCliCredential.
        """
        self.credential = credential or AzureCliCredential()
        # Initialize the Azure OpenAI Chat Client
        self.client = AzureOpenAIChatClient(
            credential=self.credential, 
            endpoint="https://hosted-agent-deployment.services.ai.azure.com"
        )
        # Create agent with system instructions and register the get_weather function as a tool
        self.agent = self.client.create_agent(
            instructions=SYSTEM_PROMPT,
            tools=[get_weather]  # Register the get_weather function as a tool
        )

    async def run(self, user_prompt: str) -> str:
        """Run the agent with a user prompt.
        
        Args:
            user_prompt: The user's query or request
            
        Returns:
            The agent's response as a string
        """
        response = await self.agent.run(user_prompt)
        return response.text if response.text else ""
