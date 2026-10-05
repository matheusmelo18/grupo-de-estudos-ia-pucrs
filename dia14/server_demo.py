"""Dia 14 - Server MCP demo (stdio)."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-dia14")


@mcp.tool()
def somar(a: int, b: int) -> int:
    """Soma dois inteiros."""
    return a + b


@mcp.tool()
def status_servico(servico: str) -> dict:
    """Retorna status operacional de um servico interno."""
    base = {
        "fila": {"status": "degradada", "latencia_ms": 850},
        "impressora": {"status": "offline", "erro": "paper jam"},
        "api": {"status": "ok", "latencia_ms": 120},
    }
    return base.get(servico, {"status": "desconhecido"})


@mcp.resource("file:///docs/regras.md")
def regras() -> str:
    return "# Regras\n\n1. DELETE so com confirmacao.\n2. Fila degradada: avisar on-call.\n"


if __name__ == "__main__":
    mcp.run()
