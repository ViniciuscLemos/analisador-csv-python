"""Gera um CSV de vendas inventadas pra testar o analisador."""

import csv
import random
from datetime import date, timedelta

PRODUTOS = {
    "Eletrônicos": [("Notebook", 2500.0), ("Smartphone", 1800.0), ("Fone de Ouvido", 350.0), ("Tablet", 1200.0)],
    "Vestuário":   [("Camiseta", 89.90), ("Calça Jeans", 199.90), ("Tênis", 399.90), ("Jaqueta", 299.90)],
    "Alimentos":   [("Café Premium", 49.90), ("Chocolate", 29.90), ("Azeite", 79.90), ("Mel", 59.90)],
    "Livros":      [("Python para Iniciantes", 79.90), ("Clean Code", 89.90), ("O Programador Pragmático", 99.90)],
    "Casa":        [("Luminária", 149.90), ("Tapete", 299.90), ("Almofada", 79.90)],
}
VENDEDORES = ["Ana Lima", "Bruno Silva", "Carla Souza", "Diego Costa", "Elisa Ramos"]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def gerar_csv_exemplo(caminho: str, quantidade: int = 200, seed: int | None = None) -> None:
    # Random próprio pra não mexer no random global; com a mesma seed sai o mesmo arquivo
    rng = random.Random(seed)

    inicio = date(2024, 1, 1)
    dias = (date(2024, 12, 31) - inicio).days

    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        campos = ['data', 'produto', 'categoria', 'quantidade', 'preco', 'vendedor', 'regiao']
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()

        for _ in range(quantidade):
            categoria = rng.choice(list(PRODUTOS.keys()))
            produto, preco_base = rng.choice(PRODUTOS[categoria])

            escritor.writerow({
                'data':       (inicio + timedelta(days=rng.randint(0, dias))).strftime('%Y-%m-%d'),
                'produto':    produto,
                'categoria':  categoria,
                'quantidade': rng.randint(1, 10),
                'preco':      round(preco_base * rng.uniform(0.85, 1.15), 2),  # varia uns 15%
                'vendedor':   rng.choice(VENDEDORES),
                'regiao':     rng.choice(REGIOES),
            })
