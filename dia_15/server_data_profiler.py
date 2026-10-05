"""Dia 15 - Bonus 2: servidor MCP de profiling de dados tabulares (CSV em memoria).

Criterio de sucesso: ao enviar uma string CSV com celulas vazias, o servidor
retorna o dicionario com a contagem exata de nulos por coluna via protocolo MCP.
"""

import csv
import io
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("data-profiler")


@mcp.tool()
def auditar_csv(
    conteudo_csv: Annotated[str, Field(description="Conteúdo textual bruto no formato CSV com cabeçalho")],
) -> dict:
    """Analisa um arquivo CSV em memória e retorna contagem de linhas, colunas e valores nulos por coluna."""
    f = io.StringIO(conteudo_csv.strip())
    leitor = csv.DictReader(f)
    if not leitor.fieldnames:
        return {"sucesso": False, "erro": "CSV vazio ou sem cabecalho"}

    colunas = leitor.fieldnames
    total_linhas = 0
    nulos_por_coluna = {col: 0 for col in colunas}

    for linha in leitor:
        total_linhas += 1
        for col in colunas:
            val = (linha.get(col) or "").strip()
            if val == "" or val.lower() in ("null", "none", "nan"):
                nulos_por_coluna[col] += 1

    return {
        "sucesso": True,
        "total_linhas": total_linhas,
        "colunas": colunas,
        "nulos_por_coluna": nulos_por_coluna,
    }


if __name__ == "__main__":
    print("Servidor data-profiler iniciado em stdio", file=sys.stderr)
    mcp.run(transport="stdio")
