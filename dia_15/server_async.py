"""Dia 15 - Bonus 1: ferramentas assincronas para trabalho I/O-bound.

Resultado esperado: consultar_varios com 4 nomes retorna em ~1 segundo
(e nao 4), demonstrando concorrencia com asyncio.gather.
"""

import asyncio
import sys
import time

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-async")


@mcp.tool()
async def consultar_servico_lento(nome: str, atraso_segundos: float = 1.0) -> dict:
    """Simula uma consulta de rede lenta a um servico interno e retorna a latencia observada."""
    inicio = time.perf_counter()
    # NUNCA time.sleep aqui: ele bloquearia o loop inteiro do servidor
    await asyncio.sleep(atraso_segundos)
    return {"servico": nome, "latencia_s": round(time.perf_counter() - inicio, 2)}


@mcp.tool()
async def consultar_varios(nomes: list[str]) -> list[dict]:
    """Consulta varios servicos em paralelo e retorna a lista de latencias."""
    return list(await asyncio.gather(*(consultar_servico_lento(nome) for nome in nomes)))


if __name__ == "__main__":
    print("server-async iniciado", file=sys.stderr)
    mcp.run(transport="stdio")
