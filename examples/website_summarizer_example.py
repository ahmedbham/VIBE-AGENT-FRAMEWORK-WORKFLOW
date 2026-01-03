"""
Simple example demonstrating the Website Summarizer Multi-Agent Workflow.

This example shows how to:
1. Create a workflow with two agents (Get Content and Summarize Content)
2. Pass a website URL to the workflow
3. Automatically fetch website content with the first agent
4. Summarize the content into a bulleted list with the second agent
"""

import asyncio
from joker_agent.website_summarizer_workflow import WebsiteSummarizerWorkflow


async def main() -> None:
    """Run a simple website summarization to demonstrate the multi-agent workflow."""
    print("Initializing Website Summarizer Workflow...")
    workflow = WebsiteSummarizerWorkflow()
    
    # Example URL - replace with any website you want to summarize
    url = "https://example.com"
    
    print(f"\n{'='*60}")
    print(f"Processing: {url}")
    print(f"{'='*60}\n")
    
    # Run the workflow (verbose=False for cleaner output)
    summary = await workflow.run(url, verbose=False)
    
    print("Summary:")
    print(summary)
    print()


if __name__ == "__main__":
    asyncio.run(main())
