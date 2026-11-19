"""Gera CSV determinístico com vendas fictícias e anomalias controladas."""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

PRODUCTS = [
    ("P001", "Notebook"), ("P002", "Monitor"), ("P003", "Teclado"),
    ("P004", "Mouse"), ("P005", "Headset"),
]
CHANNELS = ["ecommerce", "loja_fisica", "marketplace"]
STATUSES = ["approved", "approved", "approved", "cancelled", "refunded"]
FIELDS = [
    "sale_id", "sale_date", "customer_id", "product_id", "product_name",
    "quantity", "unit_price", "discount", "channel", "status",
]


def generate_sales(output_dir: str = "data/raw", row_count: int = 1000, seed: int = 42) -> str:
    """Cria a origem CSV; registros problemáticos são intencionais para testes."""
    if row_count < 20:
        raise ValueError("row_count deve ser >= 20 para incluir casos de qualidade.")

    rng = random.Random(seed)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    file_path = target / "sales.csv"
    start = date(2026, 1, 1)
    rows: list[dict[str, object]] = []

    for i in range(row_count):
        product_id, product_name = rng.choice(PRODUCTS)
        quantity = rng.randint(1, 5)
        unit_price = round(rng.uniform(25, 2500), 2)
        rows.append({
            "sale_id": f"S{i + 1:07d}",
            "sale_date": (start + timedelta(days=rng.randrange(90))).isoformat(),
            "customer_id": f"C{rng.randint(1, 250):05d}",
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": round(unit_price * quantity * rng.uniform(0, 0.15), 2),
            "channel": rng.choice(CHANNELS),
            "status": rng.choice(STATUSES),
        })

    rows[3]["customer_id"] = ""
    rows[7]["quantity"] = -2
    rows[11]["unit_price"] = ""
    rows[15]["sale_date"] = "data-invalida"
    rows[19] = dict(rows[0])

    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return str(file_path)
