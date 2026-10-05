"""Dia 15 - Bloco 2: Servidor FastMCP multi-tool (somente leitura).

Instale (se ainda nao fez): pip install "mcp<2"
Depuracao visual (opcional, requer Node.js):
    npx @modelcontextprotocol/inspector python server_utils.py
"""

import hashlib
import sys
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("server-utils")


@mcp.tool()
def calcular_hash_arquivo(
    caminho: Annotated[str, Field(description="Caminho do arquivo local, relativo ou absoluto")],
) -> str:
    """Calcula o hash SHA-256 (em hexadecimal) do conteudo de um arquivo local."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ValueError(f"Arquivo nao encontrado: {caminho}")
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


@mcp.tool()
def contar_linhas_codigo(
    diretorio: Annotated[str, Field(description="Pasta a ser analisada (use '.' para a pasta atual)")],
    extensao: Annotated[str, Field(description="Extensao dos arquivos, com ponto")] = ".py",
) -> dict:
    """Conta arquivos e linhas de codigo de uma pasta (recursivo) para uma extensao."""
    pasta = Path(diretorio)
    if not pasta.is_dir():
        raise ValueError(f"Diretorio nao encontrado: {diretorio}")
    total_arquivos = 0
    total_linhas = 0
    for arquivo in pasta.rglob(f"*{extensao}"):
        if arquivo.is_file():
            total_arquivos += 1
            total_linhas += len(arquivo.read_text(errors="ignore").splitlines())
    return {"extensao": extensao, "arquivos": total_arquivos, "linhas": total_linhas}


@mcp.tool()
def converter_temperatura(valor: float, de: str, para: str) -> float:
    """Converte temperatura entre C (Celsius), F (Fahrenheit) e K (Kelvin)."""
    unidades = {"C", "F", "K"}
    de, para = de.upper(), para.upper()
    if de not in unidades or para not in unidades:
        raise ValueError("Unidades validas: C, F, K")

    # 1) normaliza para Celsius
    if de == "C":
        celsius = valor
    elif de == "F":
        celsius = (valor - 32) * 5 / 9
    else:  # K
        celsius = valor - 273.15

    # 2) converte de Celsius para o destino
    if para == "C":
        resultado = celsius
    elif para == "F":
        resultado = celsius * 9 / 5 + 32
    else:  # K
        resultado = celsius + 273.15

    return round(resultado, 2)


if __name__ == "__main__":
    print("server-utils iniciado (stdio)", file=sys.stderr)  # logs SEMPRE em stderr
    mcp.run(transport="stdio")
