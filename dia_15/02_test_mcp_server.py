"""Dia 15 - Bloco 3: mini-test runner do server_utils.py via protocolo MCP (stdio).

Criterio de sucesso: Resumo: 7 aprovados, 0 falhas
Investigacao: qual a diferenca entre o erro de tipo ("abc" no lugar de numero)
e o erro de dominio (unidade X)? Quem barrou cada um: o FastMCP ou a sua funcao?
"""

import asyncio
import hashlib
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMS = StdioServerParameters(command=sys.executable, args=["server_utils.py"])
aprovados = 0
falhas = 0


def checar(nome: str, condicao: bool, detalhe: str = "") -> None:
    global aprovados, falhas
    if condicao:
        aprovados += 1
        print(f"  [OK]   {nome}")
    else:
        falhas += 1
        print(f"  [FALHA] {nome} {detalhe}")


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            nomes = {t.name for t in (await sessao.list_tools()).tools}
            checar("expoe as 3 ferramentas", nomes == {"calcular_hash_arquivo", "contar_linhas_codigo", "converter_temperatura"})

            r = await sessao.call_tool("converter_temperatura", {"valor": 100, "de": "C", "para": "F"})
            checar("100 C = 212 F", r.content[0].text.startswith("212"), r.content[0].text)

            # calcular_hash_arquivo com um arquivo real (este proprio script)
            esperado = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            r = await sessao.call_tool("calcular_hash_arquivo", {"caminho": __file__})
            checar("hash SHA-256 deste script confere", not r.isError and r.content[0].text == esperado, r.content[0].text)

            # erro: diretorio inexistente em contar_linhas_codigo
            r = await sessao.call_tool("contar_linhas_codigo", {"diretorio": "pasta_que_nao_existe"})
            checar("erro: diretorio inexistente gera isError", r.isError is True, r.content[0].text)

            # erro de tipo: "valor": "abc" (barrado pela validacao do FastMCP/Pydantic)
            r = await sessao.call_tool("converter_temperatura", {"valor": "abc", "de": "C", "para": "F"})
            checar("erro de tipo: 'abc' gera isError", r.isError is True, r.content[0].text)

            # erro de dominio: unidade "X" (barrado pela nossa funcao)
            r = await sessao.call_tool("converter_temperatura", {"valor": 10, "de": "X", "para": "C"})
            checar(
                "erro de dominio: unidade X c/ mensagem 'Unidades validas'",
                r.isError is True and "Unidades validas" in r.content[0].text,
                r.content[0].text,
            )

            # Prova de vida: o servidor continua respondendo depois de tantos erros
            r = await sessao.call_tool("converter_temperatura", {"valor": 0, "de": "K", "para": "C"})
            checar("servidor vivo apos os erros", not r.isError, r.content[0].text)

    print(f"\nResumo: {aprovados} aprovados, {falhas} falhas")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    asyncio.run(main())
