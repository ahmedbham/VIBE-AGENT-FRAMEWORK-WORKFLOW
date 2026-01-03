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

## Full Weather Demo

A comprehensive demonstration with multiple weather queries:

```bash
poetry run python -m joker_agent.run_weather_agent
```

This shows the agent handling various types of weather queries and consistently using the function tool to provide responses.

## Key Concepts Demonstrated

### Function Tool Definition
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
