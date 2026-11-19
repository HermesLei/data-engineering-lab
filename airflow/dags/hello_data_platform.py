"""DAG inicial para validar o ambiente Airflow do laboratório."""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def validate_runtime() -> None:
    """Executa uma validação simples do runtime."""
    import platform

    print("Data Engineering Lab: Airflow operacional")
    print(f"Python: {platform.python_version()}")


with DAG(
    dag_id="hello_data_platform",
    description="Valida a execução básica do Airflow no Codespaces",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["lab", "bootstrap"],
) as dag:
    validate_environment = PythonOperator(
        task_id="validate_environment",
        python_callable=validate_runtime,
    )
