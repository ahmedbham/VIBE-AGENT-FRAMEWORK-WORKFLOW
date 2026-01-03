import asyncio

from joker_agent.weather_agent import WeatherAgent


async def main() -> None:
    """Demonstrate the Weather Agent with function calling capability."""
    agent = WeatherAgent()
    
    # Example prompts that should trigger the get_weather function
    prompts = [
        "What's the weather like in Seattle?",
        "Can you tell me the weather in New York?",
        "How's the weather in Tokyo today?"
    ]
    
    print("=" * 60)
    print("Weather Agent with Function Calling Demo")
    print("=" * 60)
    
    for prompt in prompts:
        print(f"\n🔵 User: {prompt}")
        result = await agent.run(prompt)
        print(f"🤖 Agent: {result}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
