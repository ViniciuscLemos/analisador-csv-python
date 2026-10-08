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

## Como fica o relatório

Um pedaço do relatório com 50 vendas geradas (`python main.py --gerar 50 --seed 1`):

```
-------------------------------------------------------
  RESUMO GERAL
-------------------------------------------------------
  Período:            2024-01-08 a 2024-12-22
  Total de vendas:    50
  Receita total:      R$ 142.855,02
  Ticket médio:       R$ 2.857,10
  Maior venda:        R$ 23.651,90
  Menor venda:        R$ 28,16

-------------------------------------------------------
  RANKING DE VENDEDORES
-------------------------------------------------------
  Vendedor         Vendas          Receita   Part.
  ------------------------------------------------
  Elisa Ramos          11     R$ 38.172,04   26,7%
  Diego Costa          14     R$ 37.728,42   26,4%
  Ana Lima             11     R$ 24.965,37   17,5%
  Bruno Silva           6     R$ 22.797,23   16,0%
  Carla Souza           8     R$ 19.191,96   13,4%

-------------------------------------------------------
  EVOLUÇÃO MENSAL
-------------------------------------------------------
  Jan/2024      R$ 20.512,20  ██████████████
  Fev/2024      R$ 25.897,73  █████████████████
  Mar/2024       R$ 2.235,17  ██
  Abr/2024      R$ 19.930,72  █████████████
  Mai/2024      R$ 29.631,84  ████████████████████
  Jun/2024         R$ 617,17  █
  Jul/2024      R$ 19.101,35  █████████████
  Ago/2024       R$ 1.793,67  █
  Set/2024       R$ 2.231,26  ██
  Out/2024      R$ 16.277,86  ███████████
  Nov/2024       R$ 2.675,37  ██
  Dez/2024       R$ 1.950,68  █
```

O relatório completo também traz as vendas por categoria, por região e os 5 produtos mais vendidos.

## Formato do CSV

```
data,produto,categoria,quantidade,preco,vendedor,regiao
2024-03-10,Notebook,Eletrônicos,1,2500.00,Ana Lima,Sudeste
```

A data precisa estar no formato `AAAA-MM-DD`, e o preço pode ser escrito com ponto ou com vírgula. O separador pode ser vírgula ou ponto e vírgula, que é como o Excel em português salva o arquivo. Se alguma linha estiver errada, o programa pula essa linha e avisa qual foi e por quê.

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
