"""Valida a importação de todas as DAGs usando o DagBag do Airflow."""

from __future__ import annotations

import sys

from airflow.models import DagBag


def main() -> int:
    dag_bag = DagBag(dag_folder="/opt/airflow/dags", include_examples=False)

    if dag_bag.import_errors:
        print("Foram encontrados erros ao importar DAGs:")
        for file_path, error in dag_bag.import_errors.items():
            print(f"\n{file_path}\n{error}")
        return 1

    dag_ids = sorted(dag_bag.dags)
    print(f"DAGs carregadas com sucesso: {len(dag_ids)}")
    for dag_id in dag_ids:
        print(f" - {dag_id}")

    if not dag_ids:
        print("Aviso: nenhuma DAG foi encontrada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
