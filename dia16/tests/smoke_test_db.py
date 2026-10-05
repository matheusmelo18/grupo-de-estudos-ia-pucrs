"""Dia 16 - Bloco 6: smoke test cruzado da base.

Roda sem pytest de proposito: antes de todo push os 3 executam
`python tests/smoke_test_db.py` e todos precisam ver o MESMO `N/N verificacoes
aprovadas`. Divergencia = problema de ambiente (ordem de execucao, `.env`,
versao do Python), nao de logica.

Criterio de sucesso: `N/N verificacoes aprovadas` e codigo de saida 0.

Investigacao: por que comparar com ANOMALIAS_ESPERADAS em vez de hardcodar 6,
4, 5...? Porque ai o teste tem uma unica fonte de verdade. Se o seed mudar, o
teste acompanha - e uma divergencia real ainda aparece.
"""

import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src" / "database"))

from init_db import CAMINHO_DB, conectar  # noqa: E402
from seed_data import ANOMALIAS_ESPERADAS  # noqa: E402

# Cada anomalia e uma query; o esperado vem de ANOMALIAS_ESPERADAS.
ANOMALIAS_SQL = {
    "clientes_sem_email": "SELECT COUNT(*) FROM clientes WHERE email IS NULL",
    "emails_duplicados": """
        SELECT COALESCE(SUM(n), 0) FROM (
            SELECT COUNT(*) AS n FROM clientes WHERE email IS NOT NULL
            GROUP BY email HAVING COUNT(*) > 1)
    """,
    "produtos_preco_zero": "SELECT COUNT(*) FROM produtos WHERE preco = 0",
    "pedidos_valor_negativo": "SELECT COUNT(*) FROM pedidos WHERE valor_total < 0",
    "pedidos_data_futura": "SELECT COUNT(*) FROM pedidos WHERE data_pedido > date('now')",
}

resultados: list[bool] = []


def checar(nome: str, condicao: bool, detalhe: str = "") -> None:
    resultados.append(bool(condicao))
    print(f"{'[OK]   ' if condicao else '[FALHA]'} {nome}{' ' + detalhe if detalhe else ''}")


def escalar(conexao: sqlite3.Connection, sql: str) -> int:
    return conexao.execute(sql).fetchone()[0]


def main() -> int:
    checar("arquivo dataops.db existe", CAMINHO_DB.exists())
    if not CAMINHO_DB.exists():
        print("Rode primeiro: python src/database/init_db.py && python src/database/seed_data.py")
        return 1

    with conectar() as conexao:
        checar("integridade do arquivo", escalar(conexao, "PRAGMA integrity_check") == "ok")
        checar("chaves estrangeiras ativas", escalar(conexao, "PRAGMA foreign_keys") == 1)

        for tabela in ("clientes", "produtos", "pedidos"):
            total = escalar(conexao, f"SELECT COUNT(*) FROM {tabela}")
            checar(f"{tabela} tem 50+ linhas", total >= 50, f"({total})")

        juncao = escalar(
            conexao,
            "SELECT COUNT(*) FROM pedidos"
            " JOIN clientes ON clientes.id = pedidos.cliente_id"
            " JOIN produtos ON produtos.id = pedidos.produto_id",
        )
        checar("JOIN pedidos+clientes+produtos retorna linhas", juncao >= 1, f"({juncao})")

        for chave, sql in ANOMALIAS_SQL.items():
            checar(f"anomalia: {chave}", escalar(conexao, sql) == ANOMALIAS_ESPERADAS[chave])

        # Integridade referencial na pratica: cliente inexistente e recusado.
        try:
            conexao.execute(
                "INSERT INTO pedidos (cliente_id, produto_id, quantidade, valor_total, data_pedido)"
                " VALUES (?, ?, ?, ?, ?)",
                (9999, 1, 1, 10.0, "2025-01-01"),
            )
            checar("cliente inexistente e recusado (FK)", False)
        except sqlite3.IntegrityError:
            checar("cliente inexistente e recusado (FK)", True)

    print(f"\n{sum(resultados)}/{len(resultados)} verificacoes aprovadas")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())