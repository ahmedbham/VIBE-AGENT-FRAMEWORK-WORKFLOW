# Detailed Plan: Multi-Agent Website Summarization Workflow

## Overview
This document provides a detailed plan and implementation guide for creating a multi-agent workflow using Microsoft's Agent Framework with Azure OpenAI. The workflow consists of two agents working together to fetch and summarize website content.

## Architecture

### Workflow Components

1. **Get Content Executor**: Retrieves the content from a given website URL using the Executor pattern
2. **Summarize Content Executor**: Processes the content and creates a concise bulleted list summary
3. **Workflow Orchestrator**: Uses Microsoft Agent Framework's `WorkflowBuilder` to coordinate execution

### Data Flow

```
User Input (URL) 
    ↓
Get Content Executor → Raw Website Content (via WorkflowContext)
    ↓
Summarize Content Executor → Bulleted Summary
    ↓
Final Output
```

## Implementation Details

### 1. Get Content Executor

**Purpose**: Extract text content from a website URL using the Executor pattern.

**Implementation Approach**:
- Create a `GetContentExecutor` class that extends `Executor`
- Define a `get_website_content` function that fetches HTML content from a URL
- Use the `requests` library to retrieve the webpage
- Parse HTML with `BeautifulSoup` to extract text content
- Register this function as a tool for the agent
- Use `@handler` decorator to define the processing method
- Send extracted content to the next executor via `WorkflowContext.send_message()`

**Executor Structure**:
```python
class GetContentExecutor(Executor):
    def __init__(self, executor_id: str, credential: Optional[AzureCliCredential] = None):
        super().__init__(id=executor_id)
        self.agent = self.client.create_agent(
            instructions="...",
            tools=[get_website_content]
        )
    
    @handler
    async def process(self, url: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(f"Fetch content from: {url}")
        await ctx.send_message(response.text)
```

### 2. Summarize Content Executor

**Purpose**: Generate a concise bulleted list summary of provided text content.

**Implementation Approach**:
- Create a `SummarizeContentExecutor` class that extends `Executor`
- Configure the agent with system instructions focused on summarization
- Configure the agent to output summaries in bulleted list format
- Use `@handler` decorator to define the processing method
- Yield final output via `WorkflowContext.yield_output()`

**Executor Structure**:
```python
class SummarizeContentExecutor(Executor):
    def __init__(self, executor_id: str, credential: Optional[AzureCliCredential] = None):
        super().__init__(id=executor_id)
        self.agent = self.client.create_agent(
            instructions="You are an expert content summarizer..."
        )
    
    @handler
    async def process(self, content: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(f"Summarize: {content}")
        await ctx.yield_output(response.text)
```

### 3. Workflow Orchestrator with WorkflowBuilder

**Purpose**: Chain the two executors together using Microsoft Agent Framework's `WorkflowBuilder`.

**Implementation Approach**:
- Create a `WebsiteSummarizerWorkflow` class
- Use `WorkflowBuilder` to register executors and define edges
- Configure the workflow with a name and description
- Set the start executor
- Build the workflow to create an immutable `Workflow` object
- Implement a `run` method that executes the workflow and retrieves outputs

**Workflow Class Structure**:
```python
from agent_framework import WorkflowBuilder

class WebsiteSummarizerWorkflow:
    def __init__(self, credential=None):
        self.credential = credential or AzureCliCredential()
        
        # Build the workflow using WorkflowBuilder
        self.workflow = (
            WorkflowBuilder(name="WebsiteSummarizer")
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
    
    async def run(self, url: str) -> str:
        # Run the workflow
        events = await self.workflow.run(url)
        
        # Get outputs
        outputs = events.get_outputs()
        return outputs[0] if outputs else ""
```

**Key Features of WorkflowBuilder**:
- **Fluent API**: Chain method calls to build the workflow
- **Executor Registration**: Register executors with factory functions
- **Edge Definition**: Define data flow between executors
- **Immutable Workflow**: Build creates an immutable workflow object
- **Event-based Output**: Retrieve outputs via event system
        
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
