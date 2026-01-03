# Examples

This directory contains example scripts demonstrating various agent capabilities.

## Simple Weather Example

A minimal example showing function calling with the Weather Agent:

```bash
poetry run python examples/simple_weather_example.py
```

This example demonstrates:
- How to initialize a Weather Agent
- How the agent automatically calls the `get_weather` function tool
- Basic usage pattern for agents with function calling

## Website Summarizer Example

A simple example demonstrating the multi-agent workflow for website summarization:

```bash
poetry run python examples/website_summarizer_example.py
```

This example demonstrates:
- How to create a multi-agent workflow
- How to chain two agents together (Get Content → Summarize Content)
- Data passing between agents
- Real-world application of web scraping and summarization

## Full Weather Demo

A comprehensive demonstration with multiple weather queries:

```bash
poetry run python -m joker_agent.run_weather_agent
```

This shows the agent handling various types of weather queries and consistently using the function tool to provide responses.

## Full Website Summarizer Demo

A comprehensive demonstration of the multi-agent workflow:

```bash
poetry run python -m joker_agent.run_website_summarizer
```

This shows the complete workflow with detailed progress information and multiple URL processing.

## Key Concepts Demonstrated

### Function Tool Definition (Weather Agent)
```python
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."
```

### Tool Registration
```python
self.agent = self.client.create_agent(
    instructions=SYSTEM_PROMPT,
    tools=[get_weather]  # Register function as a tool
)
```

### Automatic Function Calling
When you ask "What's the weather in Seattle?", the agent:
1. Analyzes the query
2. Determines it needs weather information
3. Calls `get_weather(location="Seattle")`
4. Uses the result to generate a natural response

No manual orchestration is needed - the framework handles everything automatically!

### Multi-Agent Workflow (Website Summarizer)
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

### Agent Chaining
The workflow demonstrates how to chain multiple agents:
1. **Get Content Agent** uses a web scraping tool to fetch website content
2. Output from the first agent becomes input to the second agent
3. **Summarize Content Agent** processes the content into a bulleted summary
4. The orchestrator manages the flow seamlessly
