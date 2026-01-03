from typing import Optional
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from joker_agent.get_content_agent import GetContentAgent
from joker_agent.summarize_content_agent import SummarizeContentAgent

load_dotenv()


class WebsiteSummarizerWorkflow:
    """Multi-agent workflow for fetching and summarizing website content.
    
    This workflow orchestrates two agents:
    1. Get Content Agent: Retrieves content from a website URL
    2. Summarize Content Agent: Creates a concise bulleted summary
    """
    
    def __init__(self, *, credential: Optional[AzureCliCredential] = None) -> None:
        """Initialize the workflow with both agents.
        
        Args:
            credential: Azure credential for authentication. Defaults to AzureCliCredential.
        """
        self.credential = credential or AzureCliCredential()
        
        # Initialize both agents
        self.get_content_agent = GetContentAgent(credential=self.credential)
        self.summarize_agent = SummarizeContentAgent(credential=self.credential)
    
    async def run(self, url: str, verbose: bool = True) -> str:
        """Run the complete workflow to fetch and summarize website content.
        
        Args:
            url: The website URL to process
            verbose: Whether to print progress information
            
        Returns:
            A concise bulleted summary of the website content
        """
        if verbose:
            print(f"🌐 URL: {url}\n")
            print("📥 Step 1: Get Content Agent - Fetching website content...")
        
        # Step 1: Get website content
        content = await self.get_content_agent.run(url)
        
        if verbose:
            content_preview = content[:100] + "..." if len(content) > 100 else content
            print(f"✓ Content retrieved successfully ({len(content)} characters)")
            print(f"   Preview: {content_preview}\n")
            print("📝 Step 2: Summarize Content Agent - Creating summary...")
        
        # Step 2: Summarize the content
        summary = await self.summarize_agent.run(content)
        
        if verbose:
            print("✓ Summary generated\n")
        
        return summary
