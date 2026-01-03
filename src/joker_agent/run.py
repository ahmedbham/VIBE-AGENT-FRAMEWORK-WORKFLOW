import asyncio

from joker_agent.agent import JokerAgent


async def main() -> None:
    agent = JokerAgent()
    result = await agent.run("Tell me a joke about a pirate")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
