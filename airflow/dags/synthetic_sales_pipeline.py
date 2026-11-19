"""DAG didática de vendas sintéticas."""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.generate_sales import generate_sales
from processing.sales_pipeline import build_bronze, build_gold, build_silver

with DAG(
    dag_id="synthetic_sales_pipeline",
    description="Gera vendas fictícias e processa Bronze/Silver/Gold em Parquet",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["lab", "sales", "parquet", "medallion"],
) as dag:
    generate = PythonOperator(
        task_id="generate_synthetic_sales",
        python_callable=generate_sales,
        op_kwargs={"output_dir": "/opt/airflow/data/raw", "row_count": 1000, "seed": 42},
    )
    bronze = PythonOperator(task_id="build_bronze", python_callable=build_bronze)
    silver = PythonOperator(task_id="build_silver", python_callable=build_silver)
    gold = PythonOperator(task_id="build_gold", python_callable=build_gold)
    generate >> bronze >> silver >> gold
