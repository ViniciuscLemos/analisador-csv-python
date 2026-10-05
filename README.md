# Analisador de CSV de vendas

![Testes](https://github.com/ViniciuscLemos/analisador-csv-python/actions/workflows/testes.yml/badge.svg)

Programa em Python que lê um CSV de vendas, joga os dados num banco SQLite e gera um relatório com as consultas em SQL.

Não precisa instalar nada além do Python (3.10+).

## Rodando

```bash
python main.py
```

Se não existir um CSV em `data/vendas.csv`, ele gera um com 200 vendas inventadas. O relatório fica em `output/relatorio.txt` e também aparece no terminal.

O relatório traz:
- o total vendido e o ticket médio
- as vendas por categoria e por região
- os produtos mais vendidos
- o ranking dos vendedores
- um gráfico simples, feito de texto, com a receita de cada mês

Opções:

```bash
python main.py --csv minhas_vendas.csv   # usar outro arquivo
python main.py --gerar 1000 --seed 42    # gerar um CSV novo
python main.py --json                    # salvar também em JSON
```

## Formato do CSV

```
data,produto,categoria,quantidade,preco,vendedor,regiao
2024-03-10,Notebook,Eletrônicos,1,2500.00,Ana Lima,Sudeste
```

A data precisa estar no formato `AAAA-MM-DD`, e o preço pode ser escrito com ponto ou com vírgula. Se alguma linha estiver errada, o programa pula essa linha e avisa qual foi e por quê.

## Testes

```bash
python -m unittest discover -s tests
```

## Arquivos

```
main.py
src/banco.py         cria o banco e importa o CSV
src/analisador.py    consultas e montagem do relatório
src/gerador_csv.py   gera os dados de exemplo
```
