from pathlib import Path

import pyarrow.parquet as pq

from ingestion.generate_sales import generate_sales
from processing.sales_pipeline import build_bronze, build_gold, build_silver


def test_synthetic_sales_pipeline_creates_medallion_layers(
    tmp_path: Path, monkeypatch
) -> None:
    raw = tmp_path / "raw"
    generate_sales(str(raw), row_count=100, seed=7)
    first = (raw / "sales.csv").read_bytes()
    generate_sales(str(raw), row_count=100, seed=7)
    assert (raw / "sales.csv").read_bytes() == first

    monkeypatch.setattr("processing.sales_pipeline.DATA_ROOT", tmp_path)
    build_bronze()
    build_silver()
    build_gold()

    bronze = pq.read_table(tmp_path / "bronze/sales/sales.parquet")
    silver = pq.read_table(tmp_path / "silver/sales/sales.parquet")
    gold = pq.read_table(tmp_path / "gold/sales_daily_channel/sales_daily_channel.parquet")
    assert bronze.num_rows == 100
    assert silver.num_rows < bronze.num_rows
    assert silver.num_rows == len(set(silver.column("sale_id").to_pylist()))
    assert gold.num_rows > 0
