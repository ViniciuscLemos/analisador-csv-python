# Analisador de Dados CSV — Python + SQLite

![Testes](https://github.com/ViniciuscLemos/analisador-csv-python/actions/workflows/testes.yml/badge.svg)

Lê arquivos CSV de vendas, valida e armazena os dados em SQLite e gera relatórios com estatísticas detalhadas — em texto e, opcionalmente, em JSON.

## Tecnologias
- **Python 3.10+** — linguagem principal
- **SQLite** — banco de dados embutido (sem instalação)
- **csv**, **sqlite3**, **argparse**, **unittest** — tudo da biblioteca padrão

> Nenhuma dependência externa! Tudo que é usado vem com o Python.

## O que você vai aprender com este projeto
- Leitura e escrita de arquivos CSV em Python
- Validação de dados linha a linha, sem interromper a importação
- Banco de dados SQLite com o módulo `sqlite3`: transações, `executemany`, `CHECK`, colunas geradas
- Queries SQL: `GROUP BY`, `ORDER BY`, subqueries, `strftime`, `COALESCE`
- Argumentos de linha de comando com `argparse`
- Separação entre cálculo (dados) e apresentação (texto/JSON)
- Testes automatizados com `unittest`

## Como rodar

```bash
# Não precisa instalar nada! Só execute:
python main.py
```

Na primeira execução o programa:
1. Gera um CSV com 200 vendas fictícias em `data/vendas.csv`
2. Cria um banco SQLite (`data/vendas.db`)
3. Valida e importa os dados do CSV para o banco
4. Gera um relatório em `output/relatorio.txt`

### Opções

| Opção | O que faz |
|-------|-----------|
| `--csv ARQUIVO` | Analisa outro arquivo CSV |
| `--saida PASTA` | Muda a pasta do relatório (padrão `output/`) |
| `--json` | Também salva as estatísticas em `relatorio.json` |
| `--gerar N` | Gera um CSV de exemplo novo com N vendas |
| `--seed S` | Semente do gerador — mesmo valor, mesmos dados |

```bash
python main.py --gerar 1000 --seed 42 --json
python main.py --csv minhas_vendas.csv
```

## O relatório
- Resumo geral: período, receita total, ticket médio, maior/menor venda
- Vendas por categoria
- Top 5 produtos mais vendidos
- Ranking de vendedores com participação (%) na receita
- Vendas por região
- Evolução mensal com gráfico de barras em texto

Valores no padrão brasileiro (`R$ 1.234,56`).

```
-------------------------------------------------------
  EVOLUÇÃO MENSAL
-------------------------------------------------------
  Jan/2024      R$ 26.849,60  ██████████
  Fev/2024      R$ 27.206,76  ██████████
  Mar/2024      R$ 34.261,01  █████████████
  Abr/2024      R$ 53.810,11  ████████████████████
```

## Usando seu próprio CSV
O arquivo precisa ter estas colunas (em qualquer ordem):
```
data, produto, categoria, quantidade, preco, vendedor, regiao
```
- `data` no formato `AAAA-MM-DD`
- `quantidade` inteiro maior que zero
- `preco` com ponto ou vírgula decimal (`10.50` ou `10,50`)

Linhas inválidas são ignoradas e listadas no terminal com o número da linha e o motivo; colunas faltando interrompem a execução com uma mensagem clara.

## Testes

```bash
python -m unittest discover -s tests -v
```

Rodam automaticamente no GitHub Actions a cada push.

## Estrutura do projeto
```
main.py                    # Ponto de entrada (argumentos e fluxo)
src/
├── banco.py               # Criação do banco, validação e importação do CSV
├── analisador.py          # Queries SQL, relatório em texto e JSON
└── gerador_csv.py         # Gerador de dados de exemplo
tests/
└── test_analisador.py     # Testes unitários e de ponta a ponta
data/                      # CSV e banco (criados automaticamente)
output/                    # Relatórios gerados
```
