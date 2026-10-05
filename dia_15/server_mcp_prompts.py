"""Dia 15 - Bonus 3: MCP Prompts reutilizaveis com @mcp.prompt().

Criterio de sucesso: o servidor responde requisicoes dos metodos prompts/list
e prompts/get com os argumentos preenchidos.
"""

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("prompt-server")


@mcp.prompt()
def template_auditoria_dados(nome_tabela: str, criticidade: str = "alta") -> str:
    """Gera o prompt estruturado de auditoria analítica para o modelo de linguagem."""
    return f"""Você é um auditor sênior de dados. Analise a tabela '{nome_tabela}' (Criticidade: {criticidade}).
Siga rigorosamente estas 3 etapas:
1. Verifique a existência de chaves primárias duplicadas ou ausentes.
2. Identifique anomalias temporais ou valores numéricos negativos em campos monetários.
3. Elabore um relatório executivo com sugestões de correção de integridade."""


if __name__ == "__main__":
    print("Servidor de prompts MCP rodando via stdio", file=sys.stderr)
    mcp.run(transport="stdio")
