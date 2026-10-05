"""Dia 14 - 02 client MCP via SDK (ClientSession + stdio_client)."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["dia14/server_demo.py"], env=None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:")
            for t in tools.tools:
                print(f" - {t.name}: {t.description} schema={t.inputSchema}")

            r1 = await session.call_tool("somar", {"a": 40, "b": 2})
            print("somar 40+2 =", r1.content, "isError=", r1.isError)

            r2 = await session.call_tool("status_servico", {"servico": "fila"})
            print("fila =", r2.content, "isError=", r2.isError)

            r3 = await session.call_tool(
                "status_servico", {"servico": "impressora"}
            )
            print("impressora =", r3.content, "isError=", r3.isError)


if __name__ == "__main__":
    asyncio.run(main())
