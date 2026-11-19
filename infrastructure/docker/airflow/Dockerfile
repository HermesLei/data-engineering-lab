# Imagem customizada do Airflow para empacotar DAGs e código do projeto.
# Mantenha a versão alinhada com docker-compose.yml e com a matriz de CI.
FROM apache/airflow:2.10.5-python3.12

USER root
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root src /opt/airflow/src
COPY --chown=airflow:root scripts/validate_dags.py /opt/airflow/scripts/validate_dags.py

ENV PYTHONPATH="/opt/airflow:/opt/airflow/src"

USER airflow
