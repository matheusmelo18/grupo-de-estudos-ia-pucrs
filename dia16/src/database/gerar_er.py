"""Bonus Dia 16: erDiagram Mermaid gerado a partir do schema REAL.

Criterio de sucesso: `python src/database/gerar_er.py` imprime o bloco
`erDiagram` com as 3 entidades e as duas relacoes 1-N.

Investigacao: por que ler `PRAGMA table_info` em vez de repetir o DDL em
Python? Duas fontes de verdade sempre divergem. O schema do arquivo e a verdade.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "database"))

from init_db import conectar  # noqa: E402

# O Mermaid aceita poucos tipos; o resto cai para string.
TIPOS = {"INTEGER": "int", "TEXT": "string", "REAL": "float", "DATETIME": "datetime"}


def listar_tabelas(conexao) -> list[str]:
    return [
        linha["name"]
        for linha in conexao.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def gerar_mermaid(conexao) -> str:
    tabelas = listar_tabelas(conexao)
    linhas = ["erDiagram"]
    for tabela in tabelas:
        linhas.append(f"    {tabela} {{")
        for coluna in conexao.execute(f"PRAGMA table_info({tabela})"):
            campo = f"{TIPOS.get(coluna['type'], 'string')} {coluna['name']}"
            linhas.append(f"        {campo} PK" if coluna["pk"] == 1 else f"        {campo}")
        linhas.append("    }")

    for tabela in tabelas:
        for fk in conexao.execute(f"PRAGMA foreign_key_list({tabela})"):
            linhas.append(f'    {fk["table"]} ||--o{{ {tabela} : "{fk["from"]}"')

    return "\n".join(linhas)


if __name__ == "__main__":
    with conectar() as conexao:
        print(gerar_mermaid(conexao))