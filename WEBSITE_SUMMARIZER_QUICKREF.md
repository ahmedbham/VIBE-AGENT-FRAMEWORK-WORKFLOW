# Website Summarizer Workflow - Quick Reference

## What is it?

A multi-agent workflow that fetches website content and creates concise bulleted summaries using Microsoft Agent Framework's **WorkflowBuilder** to orchestrate two specialized executors.

## Quick Start

### 1. Install Dependencies
```bash
poetry install
```

### 2. Run the Demo
```bash
# Full demo with verbose output
poetry run python -m joker_agent.run_website_summarizer

# Or run the simple example
poetry run python examples/website_summarizer_example.py
```

## How It Works

```
Input: Website URL
    ↓
[Get Content Executor]
    • Extends Executor with @handler
    • Fetches HTML from URL
    • Extracts clean text
    • Removes scripts, styles, nav
    • Sends via ctx.send_message()
    ↓
Raw Text Content (via WorkflowContext)
    ↓
[Summarize Content Executor]
    • Extends Executor with @handler
    • Analyzes content
    • Extracts key points
    • Creates bulleted list
    • Yields via ctx.yield_output()
    ↓
Output: Concise Summary (via events.get_outputs())
```

**WorkflowBuilder Pattern:**
```
WorkflowBuilder
  .register_executor(GetContent)
  .register_executor(Summarize)
  .add_edge("GetContent", "Summarize")
  .set_start_executor("GetContent")
  .build()
```

## Code Example

```python
from joker_agent.website_summarizer_workflow import WebsiteSummarizerWorkflow
import asyncio

async def main():
    # Initialize workflow (uses WorkflowBuilder internally)
    workflow = WebsiteSummarizerWorkflow()
    summary = await workflow.run("https://example.com")
    print(summary)

asyncio.run(main())
```

## Files Created

### Core Implementation
- `src/joker_agent/website_summarizer_workflow.py` - Workflow with WorkflowBuilder, executors, and orchestration
- `src/joker_agent/run_website_summarizer.py` - Demo runner

### Legacy Files (no longer used directly)
- `src/joker_agent/get_content_agent.py` - Original agent implementation (preserved for reference)
- `src/joker_agent/summarize_content_agent.py` - Original agent implementation (preserved for reference)

### Documentation
- `WEBSITE_SUMMARIZER_PLAN.md` - Detailed implementation plan with WorkflowBuilder (300+ lines)
- `WEBSITE_SUMMARIZER_IMPLEMENTATION.md` - Implementation summary
- `examples/website_summarizer_example.py` - Simple usage example

### Updated Files
- `README.md` - Added workflow description
- `pyproject.toml` - Added dependencies
- `examples/README.md` - Added examples documentation

## Key Features

✅ **WorkflowBuilder Integration** - Uses Microsoft Agent Framework's fluent API  
✅ **Executor Pattern** - Extends Executor with @handler decorators  
✅ **WorkflowContext** - Type-safe data flow between executors

✅ **Multi-Agent Orchestration** - Two agents working together  
✅ **Tool Integration** - Web scraping as an agent tool  
✅ **Error Handling** - Robust error handling for network issues  
✅ **Security** - User-agent headers, timeouts, content limits  
✅ **Documentation** - Comprehensive guides and examples  

## Dependencies Added

- `requests ^2.31.0` - HTTP requests
- `beautifulsoup4 ^4.12.0` - HTML parsing
- `lxml ^5.1.0` - Fast HTML parser

## Customization

### Change Content Length Limit
Edit `src/joker_agent/website_summarizer_workflow.py`:
```python
MAX_CONTENT_LENGTH = 8000  # Change this value
```

### Change Summary Format
Edit the SummarizeContentExecutor in `src/joker_agent/website_summarizer_workflow.py`:
```python
instructions = """Your custom instructions here"""
```

### Process Multiple URLs
```python
workflow = WebsiteSummarizerWorkflow()
urls = ["https://example1.com", "https://example2.com"]
for url in urls:
    summary = await workflow.run(url)
    print(f"{url}: {summary}\n")
```

## Architecture Highlights

### Executor 1: Get Content
- **Type**: Executor with @handler decorator
- **Tool**: `get_website_content(url: str) -> str`
- **Libraries**: requests, BeautifulSoup, lxml
- **Features**: HTML parsing, text extraction, error handling
- **Output**: Sends to next executor via `ctx.send_message()`

### Executor 2: Summarize Content
- **Type**: Executor with @handler decorator
- **No tools** - Pure LLM reasoning
- **System Prompt**: Specialized for summarization
- **Output**: Bulleted list via `ctx.yield_output()`

### Workflow Orchestrator with WorkflowBuilder
- **Pattern**: Sequential execution with edges
- **Builder**: Fluent API (register → edge → build)
- **Data Flow**: GetContent → Summarize (via WorkflowContext)
- **Options**: Verbose mode, event-based outputs

## Best Practices Implemented

1. **Executor Pattern** - Extends Executor with @handler
2. **WorkflowBuilder** - Declarative workflow construction
3. **Type Hints** - All functions have type annotations
4. **Docstrings** - Comprehensive documentation
5. **Constants** - Magic numbers extracted as constants
6. **Error Handling** - Try-except blocks for network operations
7. **Security** - Modern user-agent, timeouts, content limits
8. **Clean Code** - Single responsibility per component

## Troubleshooting

### Network Errors
- Check internet connectivity
- Verify URL is accessible
- Some sites may block scraping

### Import Errors
- Ensure `poetry install` completed successfully
- Check that agent-framework is installed

### Authentication Errors
- Run `az login` to authenticate
- Verify Azure credentials are valid
- Check endpoint configuration in .env

## Further Reading

- **[WEBSITE_SUMMARIZER_PLAN.md](WEBSITE_SUMMARIZER_PLAN.md)** - Complete implementation guide
- **[WEBSITE_SUMMARIZER_IMPLEMENTATION.md](WEBSITE_SUMMARIZER_IMPLEMENTATION.md)** - What was built
- **[README.md](README.md)** - Main project documentation

## Extension Ideas

1. **Batch Processing** - Process multiple URLs in parallel
2. **Content Filtering** - Extract specific sections or topics
3. **Language Translation** - Add translation before summarization
4. **Storage** - Save summaries to database or files
5. **Scheduling** - Monitor websites for changes
6. **Advanced Scraping** - Handle JavaScript-rendered pages

## Support

For issues or questions:
1. Check the documentation files listed above
2. Review the example scripts in `examples/`
3. Refer to the detailed plan in `WEBSITE_SUMMARIZER_PLAN.md`

---

**Built with**: Microsoft Agent Framework + Azure OpenAI  
**Pattern**: Multi-Agent Workflow Orchestration  
**Use Case**: Website Content Summarization
