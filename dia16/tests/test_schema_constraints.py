"""Bonus Dia 16: pytest das regras do schema (o smoke test cobre os dados).

Criterio de sucesso: `pytest tests/test_schema_constraints.py` -> `3 passed`.

Investigacao: por que `pytest.raises`? O banco precisa REJEITAR o dado ruim.
Um INSERT que passa onde deveria falhar e um bug silencioso - e o agente do dia
seguinte confiaria no que o banco aceitou.
"""

import sqlite3
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src" / "database"))

from init_db import CAMINHO_DB, conectar  # noqa: E402


@pytest.fixture
def conexao():
    if not CAMINHO_DB.exists():
        pytest.skip("Rode python src/database/init_db.py && python src/database/seed_data.py")
    with conectar() as conexao:
        yield conexao


def test_foreign_keys_ativas(conexao):
    assert conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_tabelas_obrigatorias_existem(conexao):
    existentes = {
        linha["name"]
        for linha in conexao.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert {"clientes", "pedidos"} <= existentes


def test_rejeicao_chave_estrangeira_invalida(conexao):
    """O enunciado citava uma coluna `status` que o dominio de e-commerce nao
    define. Usamos as colunas reais de `pedidos`: o que se testa aqui e a
    REJEICAO pela FK, nao a lista de colunas."""
    produto_id = conexao.execute("SELECT id FROM produtos LIMIT 1").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conexao.execute(
            "INSERT INTO pedidos (cliente_id, produto_id, quantidade, valor_total, data_pedido)"
            " VALUES (?, ?, ?, ?, ?)",
            (999999, produto_id, 1, 150.0, "2025-01-15"),
        )