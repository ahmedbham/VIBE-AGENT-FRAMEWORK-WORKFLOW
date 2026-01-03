from typing import Optional
import requests
from bs4 import BeautifulSoup
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from agent_framework.azure import AzureOpenAIChatClient

load_dotenv()


# Maximum content length to avoid token limits
MAX_CONTENT_LENGTH = 8000


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


class GetContentExecutor(Executor):
    """Executor that retrieves website content from a given URL."""
    
    def __init__(self, executor_id: str, credential: Optional[AzureCliCredential] = None):
        """Initialize the Get Content Executor.
        
        Args:
            executor_id: Unique identifier for this executor
            credential: Azure credential for authentication. Defaults to AzureCliCredential.
        """
        super().__init__(id=executor_id)
        self.credential = credential or AzureCliCredential()
        self.client = AzureOpenAIChatClient(
            credential=self.credential,
            endpoint="https://hosted-agent-deployment.services.ai.azure.com"
        )
        self.agent = self.client.create_agent(
            instructions="""You are an agent that retrieves website content. 
When given a URL, use the get_website_content tool to fetch the content and return it.
Extract and return the main text content from the website.""",
            tools=[get_website_content]
        )
    
    @handler
    async def process(self, url: str, ctx: WorkflowContext[str]) -> None:
        """Process the URL and fetch its content.
        
        Args:
            url: The website URL to fetch content from
            ctx: Workflow context for sending messages to next executor
        """
        prompt = f"Please fetch and return the content from this URL: {url}"
        response = await self.agent.run(prompt)
        content = response.text if response.text else ""
        
        # Send content to the next executor in the workflow
        await ctx.send_message(content)


class SummarizeContentExecutor(Executor):
    """Executor that summarizes text content into a concise bulleted list."""
    
    def __init__(self, executor_id: str, credential: Optional[AzureCliCredential] = None):
        """Initialize the Summarize Content Executor.
        
        Args:
            executor_id: Unique identifier for this executor
            credential: Azure credential for authentication. Defaults to AzureCliCredential.
        """
        super().__init__(id=executor_id)
        self.credential = credential or AzureCliCredential()
        self.client = AzureOpenAIChatClient(
            credential=self.credential,
            endpoint="https://hosted-agent-deployment.services.ai.azure.com"
        )
        self.agent = self.client.create_agent(
            instructions="""You are an expert content summarizer. Your task is to:
1. Analyze the provided text content
2. Extract the key points and main ideas
3. Create a concise summary in bulleted list format
4. Focus on the most important information
5. Keep each bullet point clear and brief

Format your response as a bulleted list using bullet points (•).
Each bullet should be a complete, standalone point.
Aim for 5-8 key points that capture the essence of the content."""
        )
    
    @handler
    async def process(self, content: str, ctx: WorkflowContext[str]) -> None:
        """Process the content and generate a summary.
        
        Args:
            content: The text content to summarize
            ctx: Workflow context for yielding the final output
        """
        prompt = f"Please summarize the following content into a concise bulleted list:\n\n{content}"
        response = await self.agent.run(prompt)
        summary = response.text if response.text else ""
        
        # Yield the final output of the workflow
        await ctx.yield_output(summary)


class WebsiteSummarizerWorkflow:
    """Multi-agent workflow for fetching and summarizing website content using WorkflowBuilder.
    
    This workflow orchestrates two executors using Microsoft Agent Framework's WorkflowBuilder:
    1. Get Content Executor: Retrieves content from a website URL
    2. Summarize Content Executor: Creates a concise bulleted summary
    """
    
    def __init__(self, *, credential: Optional[AzureCliCredential] = None) -> None:
        """Initialize the workflow with WorkflowBuilder.
        
        Args:
            credential: Azure credential for authentication. Defaults to AzureCliCredential.
        """
        self.credential = credential or AzureCliCredential()
        
        # Build the workflow using WorkflowBuilder
        self.workflow = (
            WorkflowBuilder(name="WebsiteSummarizer", description="Fetch and summarize website content")
            .register_executor(
                lambda: GetContentExecutor("get_content", credential=self.credential),
                name="GetContent"
            )
            .register_executor(
                lambda: SummarizeContentExecutor("summarize", credential=self.credential),
                name="Summarize"
            )
            .add_edge("GetContent", "Summarize")
            .set_start_executor("GetContent")
            .build()
        )
    
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
            print("📥 Running workflow: GetContent → Summarize\n")
        
        # Run the workflow with the URL as input
        events = await self.workflow.run(url)
        
        # Get the output from the workflow
        outputs = events.get_outputs()
        summary = outputs[0] if outputs else ""
        
        if verbose:
            print("✓ Workflow completed successfully\n")
        
        return summary
