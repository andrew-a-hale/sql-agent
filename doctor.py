import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("sql-agent")


@fast.agent(
    name="doctor-snowflake",
    instruction="You are a helpful AI Agent",
    servers=["snowflake"],
)
async def main():
    async with fast.run() as agent:
        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
