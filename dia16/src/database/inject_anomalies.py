"""Bonus Dia 16: corrompe a base de proposito, para o agente do Dia 17.

NAO faz parte do fluxo do dia. Existe para voce estragar a base e ver o agente
reagir. Depois: `python src/database/seed_data.py` restaura tudo.

Criterio de sucesso: imprime quantos nulos e negativos foram injetados.

Investigacao: `random.seed(42)` tambem aqui - o exercicio precisa ser
reproduzivel: duas execucoes injetam as mesmas linhas.
"""

import random
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "database"))

from init_db import conectar  # noqa: E402


def escalar(conexao: sqlite3.Connection, sql: str) -> int:
    return conexao.execute(sql).fetchone()[0]


def corromper_base(conexao: sqlite3.Connection, taxa_nulos: float = 0.08,
                   taxa_negativos: float = 0.05) -> dict:
    random.seed(42)
    nulos = int(escalar(conexao, "SELECT COUNT(*) FROM clientes WHERE email IS NOT NULL") * taxa_nulos)
    negativos = int(escalar(conexao, "SELECT COUNT(*) FROM pedidos WHERE valor_total >= 0") * taxa_negativos)

    conexao.execute(
        "UPDATE clientes SET email = NULL WHERE id IN ("
        "  SELECT id FROM clientes WHERE email IS NOT NULL ORDER BY id LIMIT ?)", (nulos,))
    conexao.execute(
        "UPDATE pedidos SET valor_total = -abs(valor_total) WHERE id IN ("
        "  SELECT id FROM pedidos WHERE valor_total >= 0 ORDER BY id LIMIT ?)", (negativos,))
    conexao.commit()
    return {"nulos_injetados": nulos, "negativos_injetados": negativos}


if __name__ == "__main__":
    with conectar() as conexao:
        print(corromper_base(conexao))
    print("Base corrompida. Rode `python src/database/seed_data.py` para restaurar.")