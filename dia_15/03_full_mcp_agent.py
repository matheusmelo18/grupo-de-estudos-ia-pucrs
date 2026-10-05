"""Dia 15 - Bloco 4: Agente Gemini ponta a ponta com o servidor FastMCP local.

Reaproveita a ponte do Dia 14 (03_mcp_gemini_bridge.py, copiada para esta pasta).
O trace de cada ferramenta chamada aparece no terminal via print na ponte.

Validacao manual do criterio de sucesso:
    wc -l *.py                 # confere o numero de linhas citado
    shasum -a 256 server_utils.py
"""

import asyncio
import importlib
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ponte = importlib.import_module("03_mcp_gemini_bridge")

PARAMS = StdioServerParameters(command=sys.executable, args=["server_utils.py"])

PERGUNTAS = [
    "Quantas linhas de codigo Python temos neste projeto e qual o hash do arquivo server_utils.py?",
    "Quanto sao 98.6 graus Fahrenheit em Celsius?",
]


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            for pergunta in PERGUNTAS:
                print("PERGUNTA:", pergunta)
                resposta = await ponte.perguntar(sessao, pergunta)
                print("RESPOSTA:", resposta)
                print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
