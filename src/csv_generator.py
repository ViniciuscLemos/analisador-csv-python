"""Generates a CSV of made-up sales to test the analyzer."""

import csv
import random
from datetime import date, timedelta

PRODUCTS = {
    "Electronics": [("Laptop", 2500.0), ("Smartphone", 1800.0), ("Headphones", 350.0), ("Tablet", 1200.0)],
    "Clothing":    [("T-shirt", 89.90), ("Jeans", 199.90), ("Sneakers", 399.90), ("Jacket", 299.90)],
    "Food":        [("Premium Coffee", 49.90), ("Chocolate", 29.90), ("Olive Oil", 79.90), ("Honey", 59.90)],
    "Books":       [("Python for Beginners", 79.90), ("Clean Code", 89.90), ("The Pragmatic Programmer", 99.90)],
    "Home":        [("Lamp", 149.90), ("Rug", 299.90), ("Cushion", 79.90)],
}
SELLERS = ["Ana Lima", "Bruno Silva", "Carla Souza", "Diego Costa", "Elisa Ramos"]
REGIONS = ["North", "Northeast", "Midwest", "Southeast", "South"]


def generate_sample_csv(path: str, quantity: int = 200, seed: int | None = None) -> None:
    # its own Random so it doesn't touch the global one; the same seed gives the same file
    rng = random.Random(seed)

    start = date(2024, 1, 1)
    days = (date(2024, 12, 31) - start).days

    with open(path, 'w', newline='', encoding='utf-8') as f:
        fields = ['date', 'product', 'category', 'quantity', 'price', 'seller', 'region']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for _ in range(quantity):
            category = rng.choice(list(PRODUCTS.keys()))
            product, base_price = rng.choice(PRODUCTS[category])

            writer.writerow({
                'date':     (start + timedelta(days=rng.randint(0, days))).strftime('%Y-%m-%d'),
                'product':  product,
                'category': category,
                'quantity': rng.randint(1, 10),
                'price':    round(base_price * rng.uniform(0.85, 1.15), 2),  # varies about 15%
                'seller':   rng.choice(SELLERS),
                'region':   rng.choice(REGIONS),
            })
