"""
Simple example demonstrating the Weather Agent with function calling.

This example shows how to:
1. Define a function tool (get_weather)
2. Register it with an AzureOpenAIChatClient agent
3. Have the agent automatically call the function when needed
"""

import asyncio
from joker_agent.weather_agent import WeatherAgent


async def main() -> None:
    """Run a simple weather query to demonstrate function calling."""
    print("Initializing Weather Agent with function calling capability...")
    agent = WeatherAgent()
    
    # Ask about weather - the agent will automatically call get_weather function
    user_query = "What's the weather like in Seattle?"
    print(f"\nUser: {user_query}")
    
    result = await agent.run(user_query)
    print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
