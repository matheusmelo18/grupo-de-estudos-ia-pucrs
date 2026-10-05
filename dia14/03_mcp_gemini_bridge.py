"""Dia 14 - 03 bridge MCP <-> Gemini (FunctionDeclaration)."""
import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def gerar(pergunta, contents, config=None):
    last = None
    for m in MODELS:
        try:
            if config is not None:
                return client.models.generate_content(
                    model=m, contents=contents, config=config
                ), m
            return client.models.generate_content(
                model=m, contents=contents
            ), m
        except Exception as e:  # 503/404 -> tenta proximo
            last = e
            continue
    raise last if last else RuntimeError("sem modelo")


def converter_mcp_para_gemini_tools(mcp_tools):
    gemini_tools = []
    for t in mcp_tools.tools:
        gemini_tools.append(
            types.FunctionDeclaration(
                name=t.name,
                description=t.description or "",
                parameters_json_schema=t.inputSchema,
            )
        )
    return types.Tool(function_declarations=gemini_tools)


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["dia14/server_demo.py"], env=None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
            tool_config = types.GenerateContentConfig(
                tools=[converter_mcp_para_gemini_tools(mcp_tools)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )
            for pergunta in ["Quanto e 1234+4321?", "Como esta a fila?"]:
                print("PERGUNTA:", pergunta)
                resp, usado = gerar(pergunta, pergunta, tool_config)
                print(f" (modelo: {usado})")
                if not resp.function_calls:
                    print(" texto:", resp.text)
                    continue
                for fc in resp.function_calls:
                    print(f" Gemini pediu: {fc.name} {dict(fc.args)}")
                    result = await session.call_tool(fc.name, dict(fc.args))
                    part = types.Part.from_function_response(
                        name=fc.name,
                        response={"result": str(result.content)},
                    )
                    model_content = resp.candidates[0].content  # preserva thought_signature
                    resp2, _ = gerar(
                        pergunta,
                        [
                            pergunta,
                            model_content,
                            types.Content(role="user", parts=[part]),
                        ],
                    )
                    print(" resposta final:", resp2.text)


if __name__ == "__main__":
    asyncio.run(main())
