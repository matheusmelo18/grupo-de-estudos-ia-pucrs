# Dicionario de Dados - DataOps Agent

Base de estudo: **e-commerce**. O agente do Dia 17 vai investigate este banco,
entao o dicionario precisa ser legivel por humano **e** por LLM. Por isso
nomes de coluna descritivos e sem sigla: `data_pedido` e melhor que `dt_ped`
porque o modelo le o schema como texto.

O arquivo `data/dataops.db` **nao** vai para o git: e 100% reproduzivel a
partir de `init_db.py` + `seed_data.py`. Versionar binario gerado so gera
conflito de merge.

## clientes

| Coluna | Tipo | Restricoes | Descricao |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador do cliente |
| nome | TEXT | NOT NULL | Nome completo |
| email | TEXT | aceita NULL | Contato. **6 clientes nao tem email** (anomalia) e **3 compartilham o mesmo email** (anomalia) |
| cidade | TEXT | NOT NULL | Cidade de origem |
| criado_em | DATETIME | NOT NULL | Data de cadastro (ISO `YYYY-MM-DD`) |

## produtos

| Coluna | Tipo | Restricoes | Descricao |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador do produto |
| nome | TEXT | NOT NULL | Nome do produto |
| categoria | TEXT | NOT NULL | Eletronicos, Livros, Casa, Esporte ou Moda |
| preco | REAL | NOT NULL, CHECK (preco >= 0) | Preco unitario. **4 produtos tem preco 0** (anomalia) |

## pedidos

| Coluna | Tipo | Restricoes | Descricao |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador do pedido |
| cliente_id | INTEGER | NOT NULL, FK -> clientes(id) | Quem comprou |
| produto_id | INTEGER | NOT NULL, FK -> produtos(id) | O que foi comprado |
| quantidade | INTEGER | NOT NULL, CHECK (quantidade > 0) | Quantidade de itens |
| valor_total | REAL | NOT NULL | Preco x quantidade. **5 pedidos tem valor negativo** (anomalia) |
| data_pedido | DATETIME | NOT NULL | Data do pedido. **3 estao em 2030** (anomalia) |

## Relacionamentos

- `clientes` 1 --- N `pedidos` (um cliente, muitos pedidos)
- `produtos` 1 --- N `pedidos` (um produto, muitos pedidos)

As duas chaves estrangeiras so valem se `PRAGMA foreign_keys = ON` estiver
ligado na conexao. O SQLite vem **desligado** por padrao e o estado e por
conexao, nao do arquivo: e por isso que `conectar()` liga sempre.

## 5 perguntas de negocio

1. Quais clientes estao sem e-mail cadastrado?
2. Qual categoria tem o maior faturamento (soma de `valor_total`)?
3. Quais pedidos tem valor negativo?
4. Quais e-mails estao duplicados entre clientes?
5. Qual o ticket medio por cidade?

## Anomalias que planejamos injetar

Quantidades **exatas** - o smoke test confere uma a uma (`ANOMALIAS_ESPERADAS`
em `src/database/seed_data.py`):

| Anomalia | Quantidade | Como o smoke test conta |
|---|---|---|
| `clientes_sem_email` | 6 | `WHERE email IS NULL` |
| `emails_duplicados` | 3 | linhas com email repetido (nao nulo) |
| `produtos_preco_zero` | 4 | `WHERE preco = 0` |
| `pedidos_valor_negativo` | 5 | `WHERE valor_total < 0` |
| `pedidos_data_futura` | 3 | `WHERE data_pedido > date('now')` |

Elas nao sao bugs: sao o **material de estudo** do agente. Um agente que
responde "12 clientes sem e-mail" sem checar a anomalia vai errar no Dia 17.