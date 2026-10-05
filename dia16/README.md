# DataOps Agent - Dia 16

Kickoff do projeto. Hoje: arquitetura, base SQLite e setup do Git.

## Como trabalhamos

Somos 3 no teclado, com 2 copilotos.

- **Piloto (teclado)** escreve o codigo. Os outros dois pesquisam, revisam e
  testam **ao vivo** - nao passa a vez com um PR para o outro.
- **O piloto muda todo dia.** O esquema de pilots Dia 16..20 vale para todos:
  o piloto do dia fala em voz alta o que vai fazer antes de digitar, e quem
  pega o teclado fala o que/entrega no pitch. Ficar sempre na mesma funcao
  concentrates o conhecimento e trava o grupo.
- **Commits pequenos**, prefixo `feat:` / `fix:` / `docs:`. Um commit, uma
  ideia.
- **Ninguem faz push quebrando o outro.** Antes de todo push:
  `python tests/smoke_test_db.py`.
- **No comeco do dia:** `git pull`. **No fim:** `git push` + tag
  (hoje: `v0.1-setup`).
- **Conflito resolvido junto**, na mesma tela. Ninguem mergeia sozinho.

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/database/init_db.py
python src/database/seed_data.py
```

Depois:

```bash
python tests/smoke_test_db.py          # esperado: N/N verificacoes aprovadas
pytest tests/test_schema_constraints.py  # esperado: 3 passed
python src/database/gerar_er.py        # diagrama Mermaid a partir do schema real
```

Se os tres veem numeros diferentes, o problema e de ambiente (ordem de
execucao, `.env`, versao do Python), nao de logica - porque `random.Random(42)`
torna a base identica em qualquer maquina.

## Estrutura

```
dataops-agent/
├── src/
│   ├── database/    # init_db.py, seed_data.py + exercicios bonus
│   ├── tools/       # (Dia 18)
│   ├── agent/       # (Dia 19)
│   └── mcp_server/  # (Dia 20)
├── data/            # dataops.db - gerado, fora do git
├── tests/           # smoke tests
├── docs/            # dicionario_dados.md + arquitetura
├── app.py           # Streamlit (Dia 19)
└── requirements.txt
```

`docs/dicionario_dados.md` e a fonte da verdade do dominio. Leia antes de
escrever SQL.

Bonus, fora do fluxo do dia: `python src/database/inject_anomalies.py` corrompe
a base de proposito (restaure com `seed_data.py`), e `gerar_er.py` imprime o
`erDiagram` gerado do schema real.