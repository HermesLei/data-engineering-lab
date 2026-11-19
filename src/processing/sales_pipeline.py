"""Transformações locais Parquet do pipeline de vendas."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

DATA_ROOT = Path("/opt/airflow/data")


def build_bronze() -> str:
    """Preserva os registros recebidos e converte CSV para Parquet."""
    source = DATA_ROOT / "raw" / "sales.csv"
    target = DATA_ROOT / "bronze" / "sales"
    target.mkdir(parents=True, exist_ok=True)
    table = pacsv.read_csv(
        source,
        convert_options=pacsv.ConvertOptions(
            column_types={
                "quantity": pa.string(),
                "unit_price": pa.string(),
                "discount": pa.string(),
            }
        ),
    )
    output = target / "sales.parquet"
    pq.write_table(table, output, compression="snappy")
    return str(output)


def build_silver() -> str:
    """Tipa colunas, remove inválidos e deduplica por sale_id."""
    source = DATA_ROOT / "bronze" / "sales" / "sales.parquet"
    target = DATA_ROOT / "silver" / "sales"
    target.mkdir(parents=True, exist_ok=True)
    rows = pq.read_table(source).to_pylist()
    seen: set[str] = set()
    clean: list[dict[str, object]] = []

    for row in rows:
        try:
            sale_id = str(row["sale_id"]).strip()
            customer_id = str(row["customer_id"]).strip()
            sale_date = str(row["sale_date"]).strip()
            quantity = int(row["quantity"])
            unit_price = float(row["unit_price"])
            discount = float(row["discount"])
            date.fromisoformat(sale_date)
            if (
                not sale_id or not customer_id or quantity <= 0
                or unit_price <= 0 or discount < 0
                or discount > quantity * unit_price
            ):
                continue
            if sale_id in seen:
                continue
            seen.add(sale_id)
            gross = round(quantity * unit_price, 2)
            clean.append({
                **row,
                "sale_date": sale_date,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "gross_amount": gross,
                "net_amount": round(gross - discount, 2),
            })
        except (TypeError, ValueError):
            continue

    schema = pa.schema([
        ("sale_id", pa.string()), ("sale_date", pa.string()),
        ("customer_id", pa.string()), ("product_id", pa.string()),
        ("product_name", pa.string()), ("quantity", pa.int64()),
        ("unit_price", pa.float64()), ("discount", pa.float64()),
        ("channel", pa.string()), ("status", pa.string()),
        ("gross_amount", pa.float64()), ("net_amount", pa.float64()),
    ])
    result = pa.Table.from_pylist(clean, schema=schema)
    output = target / "sales.parquet"
    pq.write_table(result, output, compression="snappy")
    print(f"Silver: {len(rows)} recebidos; {len(clean)} válidos; {len(rows) - len(clean)} descartados.")
    return str(output)


def build_gold() -> str:
    """Agrega vendas aprovadas por data e canal."""
    source = DATA_ROOT / "silver" / "sales" / "sales.parquet"
    target = DATA_ROOT / "gold" / "sales_daily_channel"
    target.mkdir(parents=True, exist_ok=True)
    table = pq.read_table(source)
    approved = table.filter(pc.equal(table["status"], "approved"))
    grouped = approved.group_by(["sale_date", "channel"]).aggregate([
        ("sale_id", "count"),
        ("net_amount", "sum"),
        ("quantity", "sum"),
    ])
    grouped = grouped.rename_columns([
        "sale_date", "channel", "orders", "net_revenue", "items_sold",
    ])
    output = target / "sales_daily_channel.parquet"
    pq.write_table(grouped, output, compression="snappy")
    print(f"Gold: {grouped.num_rows} combinações de data/canal.")
    return str(output)
