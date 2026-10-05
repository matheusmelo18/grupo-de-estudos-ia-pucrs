"""Dia 16 - Bloco 4: popula a base com dados deterministicos + anomalias plantadas.

Criterio de sucesso: `python src/database/seed_data.py` cria 80 clientes, 60
produtos e 150 pedidos, com as 5 anomalias nas quantidades exatas de
ANOMALIAS_ESPERADAS.

Investigacao: `random.Random(42)` e o que faz os 3 integrantes verem a mesma
base. Sem seed fixa o smoke test divergiria por acaso, e nao por bug.
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Rodado da raiz do projeto, os modulos irmaos nao estao no sys.path.
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "database"))

from init_db import conectar, criar_tabelas, resetar_banco  # noqa: E402

ANOMALIAS_ESPERADAS = {
    "clientes_sem_email": 6,
    "emails_duplicados": 3,
    "produtos_preco_zero": 4,
    "pedidos_valor_negativo": 5,
    "pedidos_data_futura": 3,
}

NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fabio", "Gisele", "Hugo", "Iara", "Jonas"]
SOBRENOMES = ["Silva", "Souza", "Lima", "Costa", "Rocha", "Alves", "Pereira", "Martins"]
CIDADES = ["Porto Alegre", "Canoas", "Gramado", "Pelotas", "Caxias do Sul"]
CATEGORIAS = ["Eletronicos", "Livros", "Casa", "Esporte", "Moda"]

DATA_INICIAL = date(2025, 1, 1)
HOJE = date.today()
EMAIL_DUPLICADO = "email.duplicado@exemplo.com"


def gerar_clientes(rng: random.Random, qtd: int = 80) -> list[tuple]:
    """(id, nome, email, cidade, criado_em). Anomalias 1 e 2 sao plantadas aqui."""
    sem_email = ANOMALIAS_ESPERADAS["clientes_sem_email"]
    return [
        (
            i,
            f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}",
            None if i <= sem_email
            else EMAIL_DUPLICADO if i in (10, 11, 12)
            else f"cliente{i}@exemplo.com",
            rng.choice(CIDADES),
            (DATA_INICIAL + timedelta(days=rng.randint(0, 600))).isoformat(),
        )
        for i in range(1, qtd + 1)
    ]


def gerar_produtos(rng: random.Random, qtd: int = 60) -> list[tuple]:
    """(id, nome, categoria, preco). Anomalia 3: os 4 primeiros tem preco 0."""
    preco_zero = ANOMALIAS_ESPERADAS["produtos_preco_zero"]
    return [
        (
            i,
            f"{rng.choice(CATEGORIAS)} {i}",
            rng.choice(CATEGORIAS),
            0.0 if i <= preco_zero else round(rng.uniform(10.0, 900.0), 2),
        )
        for i in range(1, qtd + 1)
    ]


def gerar_pedidos(rng: random.Random, qtd: int, clientes: list, produtos: list) -> list[tuple]:
    """(id, cliente_id, produto_id, quantidade, valor_total, data_pedido)."""
    # Só sorteia produtos com preco > 0: senão o valor negativo cai para 0.
    validos = [p for p in produtos if p[3] > 0]
    ids = range(1, qtd + 1)
    negativos = set(rng.sample(list(ids), ANOMALIAS_ESPERADAS["pedidos_valor_negativo"]))
    futuros = set(rng.sample(list(ids), ANOMALIAS_ESPERADAS["pedidos_data_futura"]))

    pedidos = []
    for i in ids:
        produto = rng.choice(validos)
        quantidade = rng.randint(1, 5)
        valor = round(produto[3] * quantidade, 2)
        pedidos.append((
            i,
            rng.choice(clientes)[0],
            produto[0],
            quantidade,
            -abs(valor) if i in negativos else valor,
            "2030-01-15" if i in futuros else (HOJE - timedelta(days=rng.randint(0, 300))).isoformat(),
        ))
    return pedidos


def popular() -> dict[str, int]:
    rng = random.Random(42)
    clientes = gerar_clientes(rng)
    produtos = gerar_produtos(rng)
    pedidos = gerar_pedidos(rng, 150, clientes, produtos)

    resetar_banco()
    with conectar() as conexao:
        criar_tabelas(conexao)
        # Regra de ouro: SQL so com placeholders, nunca f-string com literais.
        conexao.executemany("INSERT INTO clientes VALUES (?, ?, ?, ?, ?)", clientes)
        conexao.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?)", produtos)
        conexao.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?, ?, ?)", pedidos)
        conexao.commit()

    return {"clientes": len(clientes), "produtos": len(produtos), "pedidos": len(pedidos)}


if __name__ == "__main__":
    for tabela, total in popular().items():
        print(f"{tabela}: {total} linhas")
    print("Anomalias esperadas:", ANOMALIAS_ESPERADAS)