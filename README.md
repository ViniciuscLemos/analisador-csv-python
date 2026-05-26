# Analisador de Dados CSV — Python + SQLite

Lê arquivos CSV de vendas, armazena em banco de dados SQLite e gera relatórios com estatísticas detalhadas.

## Tecnologias
- **Python 3.10+** — linguagem principal
- **SQLite** — banco de dados embutido (sem instalação)
- **csv** — módulo nativo para leitura de arquivos CSV
- **sqlite3** — módulo nativo para banco de dados

> Nenhuma dependência externa! Tudo que é usado vem com o Python.

## O que você vai aprender com este projeto
- Leitura e escrita de arquivos CSV em Python
- Banco de dados SQLite com o módulo `sqlite3`
- Queries SQL: `GROUP BY`, `ORDER BY`, `HAVING`, `LIMIT`, colunas calculadas
- Organização de código em módulos Python
- Formatação de strings e geração de relatórios

## Como rodar

```bash
# Não precisa instalar nada! Só execute:
python main.py
```

O programa vai:
1. Gerar um CSV com 200 registros de vendas fictícias
2. Criar um banco de dados SQLite (`data/vendas.db`)
3. Importar os dados do CSV para o banco
4. Gerar um relatório em `output/relatorio.txt`

## Estrutura do relatório gerado
- Resumo geral (receita total, ticket médio, maior/menor venda)
- Vendas por categoria
- Top 5 produtos mais vendidos
- Ranking de vendedores
- Vendas por região

## Usando seu próprio CSV
Coloque seu arquivo CSV em `data/vendas.csv` com as colunas:
```
data, produto, categoria, quantidade, preco, vendedor, regiao
```

## Estrutura do projeto
```
main.py                    # Ponto de entrada
src/
├── __init__.py
├── banco.py               # Criação do banco e importação do CSV
├── analisador.py          # Queries SQL e geração do relatório
└── gerador_csv.py         # Gerador de dados de exemplo
data/
├── vendas.csv             # Criado automaticamente
└── vendas.db              # Banco SQLite criado automaticamente
output/
└── relatorio.txt          # Relatório gerado
```
