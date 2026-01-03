# Detailed Plan: Multi-Agent Website Summarization Workflow

## Overview
This document provides a detailed plan and implementation guide for creating a multi-agent workflow using Microsoft's Agent Framework with Azure OpenAI. The workflow consists of two agents working together to fetch and summarize website content.

## Architecture

### Workflow Components

1. **Get Content Agent**: Retrieves the content from a given website URL
2. **Summarize Content Agent**: Processes the content and creates a concise bulleted list summary
3. **Workflow Orchestrator**: Coordinates the execution of both agents in sequence

### Data Flow

```
User Input (URL) 
    ↓
Get Content Agent → Raw Website Content
    ↓
Summarize Content Agent → Bulleted Summary
    ↓
Final Output
```

## Implementation Details

### 1. Get Content Agent

**Purpose**: Extract text content from a website URL.

**Implementation Approach**:
- Define a `get_website_content` function that fetches HTML content from a URL
- Use the `requests` library to retrieve the webpage
- Parse HTML with `BeautifulSoup` to extract text content
- Register this function as a tool for the agent
- Create an agent with system instructions to extract and return website content

**Function Signature**:
```python
def get_website_content(url: str) -> str:
    """Fetch and extract text content from a website URL.
    
    Args:
        url: The website URL to fetch content from
        
    Returns:
        The extracted text content from the website
    """
```

**Agent Configuration**:
```python
SYSTEM_PROMPT = "You are an agent that retrieves website content. When given a URL, use the get_website_content tool to fetch the content and return it."
```

### 2. Summarize Content Agent

**Purpose**: Generate a concise bulleted list summary of provided text content.

**Implementation Approach**:
- Create an agent with system instructions focused on summarization
- Configure the agent to output summaries in bulleted list format
- Optimize for conciseness and key point extraction

**Agent Configuration**:
```python
SYSTEM_PROMPT = """You are an expert content summarizer. Your task is to:
1. Analyze the provided text content
2. Extract the key points and main ideas
3. Create a concise summary in bulleted list format
4. Focus on the most important information
5. Keep each bullet point clear and brief
"""
```

### 3. Workflow Orchestrator

**Purpose**: Chain the two agents together to create a complete workflow.

**Implementation Approach**:
- Create a `WebsiteSummarizerWorkflow` class
- Initialize both agents (Get Content and Summarize Content)
- Implement a `run` method that:
  1. Takes a URL as input
  2. Calls the Get Content agent with the URL
  3. Passes the retrieved content to the Summarize Content agent
  4. Returns the final summary

**Workflow Class Structure**:
```python
class WebsiteSummarizerWorkflow:
    def __init__(self):
        self.get_content_agent = GetContentAgent()
        self.summarize_agent = SummarizeContentAgent()
    
    async def run(self, url: str) -> str:
        # Step 1: Get website content
        content = await self.get_content_agent.run(url)
        
        # Step 2: Summarize the content
        summary = await self.summarize_agent.run(content)
        
        return summary
```

## File Structure

```
src/joker_agent/
├── __init__.py
├── agent.py                      # Original joker agent
├── run.py                        # Original joker agent runner
├── weather_agent.py              # Weather agent with function calling
├── run_weather_agent.py          # Weather agent runner/demo
├── get_content_agent.py          # NEW: Agent to fetch website content
├── summarize_content_agent.py    # NEW: Agent to summarize content
├── website_summarizer_workflow.py # NEW: Workflow orchestrator
└── run_website_summarizer.py     # NEW: Demo script

examples/
├── README.md
├── simple_weather_example.py
└── website_summarizer_example.py  # NEW: Simple usage example
```

## Dependencies

### Required Packages
- `requests`: For HTTP requests to fetch website content
- `beautifulsoup4`: For HTML parsing and text extraction
- `lxml`: HTML parser for BeautifulSoup

### Update pyproject.toml
```toml
[tool.poetry.dependencies]
python = ">=3.10,<4"
agent-framework = {version = ">=1.0.0b0", allow-prereleases = true}
azure-identity = "^1.17.0"
openai = "^1.59.6"
python-dotenv = "^1.0.1"
requests = "^2.31.0"           # NEW
beautifulsoup4 = "^4.12.0"     # NEW
lxml = "^5.1.0"                # NEW
```

## Usage

### Prerequisites
- Python >= 3.10
- Poetry (or pip)
- Azure CLI logged in (`az login`)
- Access to Azure OpenAI or Azure AI Foundry endpoint
- Active internet connection to fetch website content

### Installation
```bash
poetry install
```

### Running the Workflow
```bash
poetry run python -m joker_agent.run_website_summarizer
# or
python -m joker_agent.run_website_summarizer
```

### Example Usage in Code
```python
import asyncio
from joker_agent.website_summarizer_workflow import WebsiteSummarizerWorkflow

async def main():
    workflow = WebsiteSummarizerWorkflow()
    
    url = "https://example.com/article"
    print(f"Analyzing: {url}")
    
    summary = await workflow.run(url)
    print(f"\nSummary:\n{summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Expected Output
```
============================================================
Website Summarizer - Multi-Agent Workflow Demo
============================================================

🌐 URL: https://example.com/article

📥 Step 1: Get Content Agent - Fetching website content...
✓ Content retrieved successfully (2,450 characters)

📝 Step 2: Summarize Content Agent - Creating summary...
✓ Summary generated

📋 Summary:
• Main point 1: Key information about the topic
• Main point 2: Important detail or finding
• Main point 3: Supporting evidence or context
• Main point 4: Conclusion or takeaway
• Main point 5: Additional relevant information

============================================================
```

## Key Features

### 1. Multi-Agent Orchestration
- Demonstrates how to chain multiple agents together
- Shows data passing between agents
- Illustrates workflow coordination

### 2. Tool Registration with Get Content Agent
- Implements a custom function tool for web scraping
- Shows how to integrate external libraries (requests, BeautifulSoup)
- Demonstrates error handling in tool functions

### 3. Structured Output from Summarize Agent
- Uses system instructions to control output format
- Generates consistent bulleted list summaries
- Focuses on extracting key information

### 4. Real-World Application
- Solves a practical use case (website summarization)
- Can be extended for content analysis, research, or monitoring
- Demonstrates integration with web technologies

## Extension Possibilities

### 1. Multiple URL Processing
Process multiple URLs in parallel or sequence:
```python
async def run_batch(self, urls: list[str]) -> list[str]:
    """Process multiple URLs and return summaries."""
    tasks = [self.run(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 2. Content Type Detection
Add an agent to detect content type and adjust processing:
```python
class ContentTypeAgent:
    """Detect if URL is article, video, PDF, etc."""
    pass
```

### 3. Language Translation
Add translation between content fetching and summarization:
```python
class TranslateContentAgent:
    """Translate content before summarization."""
    pass
```

### 4. Summary Customization
Allow users to specify summary length or focus:
```python
async def run(self, url: str, summary_length: str = "medium", 
              focus: str = None) -> str:
    """Run workflow with customization options."""
    pass
```

### 5. Content Storage
Save fetched content and summaries to a database:
```python
def save_to_database(url: str, content: str, summary: str):
    """Store results for future reference."""
    pass
```

## Best Practices

### 1. Error Handling
- Handle network errors when fetching URLs
- Validate URL format before processing
- Provide meaningful error messages
- Implement timeouts for HTTP requests

### 2. Content Extraction
- Remove scripts, styles, and navigation elements
- Focus on main content areas
- Handle different HTML structures gracefully
- Respect robots.txt and rate limits

### 3. Agent Communication
- Use clear data formats between agents
- Validate data passed between agents
- Log intermediate results for debugging
- Handle empty or invalid content

### 4. Performance
- Set reasonable timeouts for web requests
- Limit content length to avoid token limits
- Consider caching frequently accessed URLs
- Implement retry logic for failed requests

### 5. Security
- Validate and sanitize URLs
- Set user-agent headers appropriately
- Respect website terms of service
- Avoid scraping sensitive or private content
- Handle authentication if required

## Security Considerations

1. **URL Validation**: Validate URLs to prevent SSRF attacks
2. **Content Sanitization**: Clean HTML content before processing
3. **Rate Limiting**: Implement delays between requests
4. **User-Agent**: Set appropriate user-agent headers
5. **Error Messages**: Avoid exposing internal system details
6. **HTTPS**: Prefer HTTPS URLs when available
7. **Credential Management**: Use secure methods for any required authentication

## Troubleshooting

### Common Issues

1. **Failed to Fetch Content**
   - Check internet connectivity
   - Verify URL is accessible
   - Check for website blocking (403 Forbidden)
   - Ensure user-agent is set

2. **Content Extraction Issues**
   - Website might use JavaScript rendering
   - HTML structure might be complex
   - Content might be in iframes
   - Try different parsing strategies

3. **Summary Quality**
   - Content might be too short or too long
   - Adjust system instructions
   - Provide more context to summarization agent
   - Try different prompting strategies

4. **Authentication Errors**
   - Ensure Azure CLI is logged in
   - Verify endpoint configuration
   - Check API quotas and limits

## Testing

### Unit Tests
Test individual components:
- Test `get_website_content` function with various URLs
- Test content extraction from different HTML structures
- Test summarization with different content lengths

### Integration Tests
Test the complete workflow:
- Test with real website URLs
- Verify data flow between agents
- Check output format consistency

### Example Test URLs
- News article: https://example.com/news
- Blog post: https://example.com/blog
- Documentation: https://docs.example.com
- Product page: https://example.com/products

## Conclusion

This multi-agent workflow demonstrates advanced patterns in AI agent orchestration:
- **Agent Chaining**: Sequential execution of multiple agents
- **Tool Integration**: Custom functions for external operations
- **Data Transformation**: Processing and reformatting data between stages
- **Real-World Application**: Practical use case implementation

The website summarization workflow can serve as a template for building more complex multi-agent systems that involve:
- Data gathering → Processing → Analysis workflows
- Multi-step decision making
- Parallel agent execution
- Complex orchestration patterns

By following this plan, developers can create sophisticated AI workflows that combine multiple specialized agents to accomplish complex tasks that would be difficult for a single agent to handle effectively.
