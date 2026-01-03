# Detailed Plan: Creating an Agent with Function Calling Using AzureOpenAIChatClient

## Overview
This document provides a detailed plan and implementation guide for creating an AI agent using Microsoft's Agent Framework with Azure OpenAI that can call functions as tools. The specific example implements a weather information agent that uses a `get-weather` function.

## Architecture

### Components

1. **AzureOpenAIChatClient**: The main client from the `agent-framework` package that communicates with Azure OpenAI
2. **Function Tool**: A Python function (`get_weather`) that the agent can call
3. **Agent**: An agent instance created with system instructions and registered tools
4. **Runner**: A script to execute and test the agent

## Implementation Details

### 1. Function Tool Definition

The function tool is defined as a standard Python function with:
- Type annotations for parameters (required for the framework to generate the tool schema)
- A descriptive docstring (used by the framework to help the LLM understand when to call the function)
- A clear return type

```python
def get_weather(location: str) -> str:
    """Get the weather for a given location.
    
    Args:
        location: The location to get weather information for
        
    Returns:
        A string describing the weather at the specified location
    """
    return f"The weather in {location} is cloudy with a high of 15°C."
```

**Key Points:**
- The `location: str` parameter annotation is crucial - it tells the framework what type of input to expect
- The docstring provides context to the LLM about what this function does
- The return value is a fixed string as per requirements, but in production this could call a real weather API

### 2. Agent Configuration

The agent is configured with:

```python
self.client = AzureOpenAIChatClient(
    credential=self.credential, 
    endpoint="https://hosted-agent-deployment.services.ai.azure.com"
)

self.agent = self.client.create_agent(
    instructions=SYSTEM_PROMPT,
    tools=[get_weather]  # Register the function as a tool
)
```

**Key Points:**
- The `tools` parameter accepts a list of Python functions
- The framework automatically converts the function signature into an OpenAI-compatible tool schema
- The agent will automatically determine when to call the function based on user prompts

### 3. System Instructions

System instructions guide the agent's behavior:

```python
SYSTEM_PROMPT = "You are a helpful assistant that can provide weather information."
```

This instruction helps the agent understand its role and when to use the weather tool.

### 4. Execution Flow

When a user asks about weather:

1. **User Input**: "What's the weather like in Seattle?"
2. **Agent Analysis**: The LLM analyzes the prompt and determines it needs weather information
3. **Function Call**: The agent calls `get_weather(location="Seattle")`
4. **Function Execution**: The function returns "The weather in Seattle is cloudy with a high of 15°C."
5. **Response Generation**: The agent uses this information to formulate a natural language response
6. **User Output**: The agent responds with the weather information in a conversational manner

## File Structure

```
src/joker_agent/
├── __init__.py
├── agent.py              # Original joker agent
├── run.py                # Original joker agent runner
├── weather_agent.py      # NEW: Weather agent with function calling
└── run_weather_agent.py  # NEW: Weather agent runner/demo
```

## Usage

### Prerequisites
- Python >= 3.10
- Poetry (or pip)
- Azure CLI logged in (`az login`)
- Access to Azure OpenAI or Azure AI Foundry endpoint

### Installation
```bash
poetry install
# or
pip install agent-framework azure-identity openai python-dotenv
```

### Running the Weather Agent
```bash
poetry run python -m joker_agent.run_weather_agent
# or
python -m joker_agent.run_weather_agent
```

### Expected Output
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

## Key Features Demonstrated

### 1. Function Tool Registration
- Shows how to define a Python function as a tool
- Demonstrates proper type annotations and docstrings
- Illustrates the `tools` parameter in `create_agent()`

### 2. Automatic Function Calling
- The agent automatically determines when to call the function
- No manual orchestration needed
- The framework handles parameter extraction from natural language

### 3. Flexible Integration
- Functions can be as simple or complex as needed
- Can integrate with external APIs, databases, or services
- Return values are automatically incorporated into agent responses

## Extension Possibilities

### Multiple Functions
Add more functions to provide diverse capabilities:
```python
def get_weather(location: str) -> str:
    """Get weather information."""
    return f"The weather in {location} is cloudy with a high of 15°C."

def get_time(timezone: str) -> str:
    """Get current time in a timezone."""
    from datetime import datetime
    return f"The time is {datetime.now()}"

self.agent = self.client.create_agent(
    instructions=SYSTEM_PROMPT,
    tools=[get_weather, get_time]  # Multiple tools
)
```

### Complex Parameters
Use Pydantic models for structured inputs:
```python
from pydantic import BaseModel, Field

class WeatherQuery(BaseModel):
    location: str = Field(description="City name or coordinates")
    units: str = Field(default="celsius", description="Temperature units")

def get_weather(query: WeatherQuery) -> str:
    """Get weather with specific units."""
    return f"The weather in {query.location} is 15°{query.units[0].upper()}"
```

### Async Functions
The framework supports async function tools:
```python
async def get_weather_async(location: str) -> str:
    """Get weather asynchronously."""
    # Could call external API
    return f"The weather in {location} is cloudy with a high of 15°C."
```

## Best Practices

1. **Clear Function Names**: Use descriptive names that indicate the function's purpose
2. **Type Annotations**: Always include type hints for all parameters and return values
3. **Comprehensive Docstrings**: Provide detailed descriptions to help the LLM understand when to use the function
4. **Error Handling**: In production, add proper error handling within functions
5. **Validation**: Validate inputs to ensure the function receives expected data
6. **Testing**: Test functions independently before integrating with the agent

## Security Considerations

1. **Input Validation**: Always validate and sanitize inputs to function tools
2. **Rate Limiting**: Implement rate limiting for functions that call external services
3. **Credential Management**: Use Azure managed identities or secure credential storage
4. **Logging**: Log function calls for audit and debugging purposes
5. **Error Messages**: Avoid exposing sensitive information in error messages

## Troubleshooting

### Common Issues

1. **Function Not Called**
   - Check that the function has proper type annotations
   - Ensure the docstring clearly describes the function's purpose
   - Verify the system instructions guide the agent toward using tools

2. **Parameter Mismatch**
   - Verify parameter types match between function definition and expected input
   - Check that parameter names are descriptive

3. **Authentication Errors**
   - Ensure Azure CLI is logged in: `az login`
   - Verify the endpoint URL is correct
   - Check that credentials have appropriate permissions

## Conclusion

This implementation demonstrates the core concepts of function calling with Azure OpenAI using Microsoft's Agent Framework. The pattern shown here can be extended to create sophisticated agents capable of interacting with various tools, APIs, and services, making AI agents actionable and useful in real-world scenarios.

The `get_weather` function serves as a simple but complete example that can be adapted for more complex use cases such as:
- Database queries
- API integrations
- File operations
- Calculations
- Data transformations
- Multi-step workflows

By following this plan and implementation, developers can quickly create agents with function calling capabilities that bridge the gap between conversational AI and executable actions.
