"""Dia 14 - 04 resources demo (list + read + Gemini DELETE)."""
import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def gerar(prompt):
    last = None
    for m in MODELS:
        try:
            return client.models.generate_content(model=m, contents=prompt), m
        except Exception as e:
            last = e
            continue
    raise last if last else RuntimeError("sem modelo")


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["dia14/server_demo.py"], env=None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.list_resources()
            print("RESOURCES:", [(r.uri, r.name) for r in res.resources])
            for r in res.resources:
                conteudo = await session.read_resource(str(r.uri))
                texto = "\n".join(
                    c.text for c in conteudo.contents if hasattr(c, "text")
                )
                print(f"--- {r.uri} ---\n{texto}")
                prompt = (
                    f"Regras do servidor:\n{texto}\n\n"
                    "Usuario pediu: DELETE /docs/financeiro. Pode?"
                )
                resp, usado = gerar(prompt)
                print(f"Gemini [{usado}]:", resp.text)


if __name__ == "__main__":
    asyncio.run(main())
