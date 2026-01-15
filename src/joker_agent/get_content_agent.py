from typing import Optional
import requests
from bs4 import BeautifulSoup
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


# Maximum content length to avoid token limits
MAX_CONTENT_LENGTH = 8000

SYSTEM_PROMPT = """You are an agent that retrieves website content. 
When given a URL, use the get_website_content tool to fetch the content and return it.
Extract and return the main text content from the website."""


def get_website_content(url: str) -> str:
    """Fetch and extract text content from a website URL.
    
    Args:
        url: The website URL to fetch content from
        
    Returns:
        The extracted text content from the website
    """
    try:
        # Set a user-agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Fetch the webpage with timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length to avoid token limits
        if len(text) > MAX_CONTENT_LENGTH:
            text = text[:MAX_CONTENT_LENGTH] + "... (content truncated)"
        
        return text
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing content: {str(e)}"


class GetContentAgent:
    """Agent that retrieves website content from a given URL."""
    
    def __init__(self, *, credential: Optional[DefaultAzureCredential] = None) -> None:
        """Initialize the Get Content Agent with web scraping capability.
        
        Args:
            credential: Azure credential for authentication. Defaults to DefaultAzureCredential.
        """
        self.credential = credential or DefaultAzureCredential()
        # Initialize the Azure OpenAI Chat Client
        self.client = AzureOpenAIChatClient(
            credential=self.credential, 
            endpoint="https://hosted-agent-deployment.services.ai.azure.com"
        )
        # Create agent with system instructions and register the get_website_content function as a tool
        self.agent = self.client.create_agent(
            instructions=SYSTEM_PROMPT,
            tools=[get_website_content]  # Register the get_website_content function as a tool
        )

    async def run(self, url: str) -> str:
        """Run the agent with a URL to fetch its content.
        
        Args:
            url: The website URL to fetch content from
            
        Returns:
            The extracted website content as a string
        """
        prompt = f"Please fetch and return the content from this URL: {url}"
        response = await self.agent.run(prompt)
        return response.text if response.text else ""
