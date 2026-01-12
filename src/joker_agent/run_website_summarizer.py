import asyncio

from joker_agent.website_summarizer_workflow import WebsiteSummarizerWorkflow


async def main() -> None:
    """Demonstrate the Website Summarizer Multi-Agent Workflow."""
    
    print("=" * 60)
    print("Website Summarizer - Multi-Agent Workflow Demo")
    print("=" * 60)
    print()
    
    # Initialize the workflow
    workflow = WebsiteSummarizerWorkflow()
    
    # Example URLs to demonstrate the workflow
    test_urls = [
        "https://google.com",  # Simple example site
        # Add more URLs as needed for testing
    ]
    
    for url in test_urls:
        try:
            # Run the workflow
            summary = await workflow.run(url, verbose=True)
            
            # Display the results
            print("📋 Summary:")
            print(summary)
            print()
            print("=" * 60)
            print()
            
        except Exception as e:
            print(f"❌ Error processing {url}: {str(e)}")
            print("=" * 60)
            print()


if __name__ == "__main__":
    asyncio.run(main())
