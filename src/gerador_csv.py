"""
Gerador de CSV de exemplo
==========================
Cria um arquivo CSV com dados fictícios de vendas para testar o analisador.
"""

import csv
import random
from datetime import date, timedelta


def gerar_csv_exemplo(caminho: str, quantidade: int = 200, seed: int | None = None) -> None:
    """
    Gera um arquivo CSV com dados aleatórios de vendas.

    Parâmetros:
        caminho    — onde salvar o arquivo
        quantidade — número de registros a gerar
        seed       — semente do gerador aleatório; com o mesmo valor,
                     o CSV gerado é sempre igual (útil para testes)
    """
    # Usamos uma instância própria de Random para não afetar o random global
    rng = random.Random(seed)

    produtos = {
        "Eletrônicos": [("Notebook", 2500.0), ("Smartphone", 1800.0), ("Fone de Ouvido", 350.0), ("Tablet", 1200.0)],
        "Vestuário":   [("Camiseta", 89.90), ("Calça Jeans", 199.90), ("Tênis", 399.90), ("Jaqueta", 299.90)],
        "Alimentos":   [("Café Premium", 49.90), ("Chocolate", 29.90), ("Azeite", 79.90), ("Mel", 59.90)],
        "Livros":      [("Python para Iniciantes", 79.90), ("Clean Code", 89.90), ("O Programador Pragmático", 99.90)],
        "Casa":        [("Luminária", 149.90), ("Tapete", 299.90), ("Almofada", 79.90)],
    }

    vendedores = ["Ana Lima", "Bruno Silva", "Carla Souza", "Diego Costa", "Elisa Ramos"]
    regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

    data_inicio = date(2024, 1, 1)
    data_fim = date(2024, 12, 31)
    delta = (data_fim - data_inicio).days

    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        campos = ['data', 'produto', 'categoria', 'quantidade', 'preco', 'vendedor', 'regiao']
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()

        for _ in range(quantidade):
            categoria = rng.choice(list(produtos.keys()))
            produto, preco_base = rng.choice(produtos[categoria])

            # Variação de preço de ±15%
            preco = round(preco_base * rng.uniform(0.85, 1.15), 2)
            data_venda = data_inicio + timedelta(days=rng.randint(0, delta))

            escritor.writerow({
                'data':       data_venda.strftime('%Y-%m-%d'),
                'produto':    produto,
                'categoria':  categoria,
                'quantidade': rng.randint(1, 10),
                'preco':      preco,
                'vendedor':   rng.choice(vendedores),
                'regiao':     rng.choice(regioes),
            })
