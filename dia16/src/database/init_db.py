"""Dia 16 - Bloco 3: cria o schema (DDL) da base SQLite.

Criterio de sucesso: `python src/database/init_db.py` da raiz do projeto
imprime as 3 tabelas e "Chaves estrangeiras ativas: 1".

Investigacao: e se esquecermos `PRAGMA foreign_keys = ON`? O INSERT com
cliente_id inexistente passa e o banco vira lixo silenciosamente. O SQLite
vem desligado e o estado vale por conexao, nao por arquivo.
"""

import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_DB = RAIZ / "data" / "dataops.db"

# preco >= 0 (e nao > 0) porque a anomalia "preco zero" precisa caber no CHECK.
DDL = """
CREATE TABLE clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT    NOT NULL,
    email     TEXT,
    cidade    TEXT    NOT NULL,
    criado_em DATETIME NOT NULL
);

CREATE TABLE produtos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT    NOT NULL,
    categoria TEXT    NOT NULL,
    preco     REAL    NOT NULL CHECK (preco >= 0)
);

CREATE TABLE pedidos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id  INTEGER NOT NULL REFERENCES clientes (id),
    produto_id  INTEGER NOT NULL REFERENCES produtos (id),
    quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
    valor_total REAL    NOT NULL,
    data_pedido DATETIME NOT NULL
);
"""


def conectar(caminho: Path = CAMINHO_DB) -> sqlite3.Connection:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao


def criar_tabelas(conexao: sqlite3.Connection) -> None:
    conexao.executescript(DDL)
    conexao.commit()


def resetar_banco() -> None:
    CAMINHO_DB.unlink(missing_ok=True)


if __name__ == "__main__":
    resetar_banco()
    with conectar() as conexao:
        criar_tabelas(conexao)
        tabelas = conexao.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        print("Tabelas criadas:", [linha["name"] for linha in tabelas])
        print("Chaves estrangeiras ativas:", conexao.execute("PRAGMA foreign_keys").fetchone()[0])