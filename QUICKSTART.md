# Quick Start Guide

## Weather Agent with Function Calling

This guide provides a quick introduction to using the Weather Agent with function calling capabilities.

## What is Function Calling?

Function calling allows AI agents to execute Python functions in response to user queries. Instead of just generating text, the agent can:
1. Recognize when it needs external data
2. Call the appropriate function with extracted parameters
3. Use the function's return value to generate a response

## The Weather Agent Example

### The Function Tool
```python
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."
```

### How It Works
```
User Query → Agent Analyzes → Calls Function → Returns Result
    ↓            ↓                ↓               ↓
"Weather     Needs weather    get_weather     "The weather in
in Seattle?"  info for           ("Seattle")     Seattle is..."
              Seattle
```

## Running the Examples

### Option 1: Simple Example (Single Query)
```bash
poetry run python examples/simple_weather_example.py
```

**Expected Output:**
```
Initializing Weather Agent with function calling capability...

User: What's the weather like in Seattle?
Agent: The weather in Seattle is cloudy with a high of 15°C.
```

### Option 2: Full Demo (Multiple Queries)
```bash
poetry run python -m joker_agent.run_weather_agent
```

**Expected Output:**
```
============================================================
Weather Agent with Function Calling Demo
============================================================

🔵 User: What's the weather like in Seattle?
🤖 Agent: The weather in Seattle is cloudy with a high of 15°C.

🔵 User: Can you tell me the weather in New York?
🤖 Agent: The weather in New York is cloudy with a high of 15°C.

🔵 User: How's the weather in Tokyo today?
🤖 Agent: The weather in Tokyo is cloudy with a high of 15°C.

============================================================
```

## Prerequisites

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Azure CLI login**
   ```bash
   az login
   ```

4. **Environment setup** (optional)
   Create a `.env` file:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
   AZURE_OPENAI_API_VERSION=2024-10-21
   ```

## Key Code Patterns

### 1. Define a Function Tool
```python
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    # Your logic here
    return f"The weather in {location} is cloudy with a high of 15°C."
```

**Important:**
- Use type annotations (`location: str`)
- Add a docstring to describe the function
- Return the appropriate type

### 2. Register the Tool with the Agent
```python
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    credential=credential,
    endpoint="your-endpoint"
)

agent = client.create_agent(
    instructions="You are a helpful assistant.",
    tools=[get_weather]  # Pass your function(s) here
)
```

### 3. Use the Agent
```python
async def main():
    agent = WeatherAgent()
    response = await agent.run("What's the weather in Paris?")
    print(response)
```

## Customization

### Add More Functions
```python
def get_time(timezone: str) -> str:
    """Get the current time in a timezone."""
    return f"The time is 12:00 PM in {timezone}"

agent = client.create_agent(
    instructions="You are a helpful assistant.",
    tools=[get_weather, get_time]  # Multiple tools
)
```

### Connect to Real APIs
```python
import requests

def get_weather(location: str) -> str:
    """Get real weather data from an API."""
    response = requests.get(f"https://api.weather.com/location/{location}")
    data = response.json()
    return f"The weather in {location} is {data['condition']} with {data['temp']}°C"
```

### Use Async Functions
```python
async def get_weather(location: str) -> str:
    """Get weather data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{location}")
        return response.json()
```

## Common Issues

### "ModuleNotFoundError: No module named 'agent_framework'"
**Solution:** Install dependencies
```bash
poetry install
```

### "DefaultAzureCredential failed to retrieve a token"
**Solution:** Login with Azure CLI
```bash
az login
```

### "Agent not calling the function"
**Solutions:**
- Ensure type annotations are present
- Check that the docstring is clear and descriptive
- Verify the system instructions guide the agent to use tools

## Next Steps

1. **Read the detailed plan**: [WEATHER_AGENT_PLAN.md](WEATHER_AGENT_PLAN.md)
2. **Review the implementation**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
3. **Explore the code**: Check `src/joker_agent/weather_agent.py`
4. **Experiment**: Modify the function or add new tools

## Additional Resources

- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Function Tools Tutorial](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/function-tools)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Support

For issues or questions:
1. Check the [WEATHER_AGENT_PLAN.md](WEATHER_AGENT_PLAN.md) troubleshooting section
2. Review the [examples/README.md](examples/README.md)
3. Consult the Microsoft Agent Framework documentation
