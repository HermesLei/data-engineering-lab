FROM apache/airflow:2.10.5-python3.12

USER root
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root src /opt/airflow/src
COPY --chown=airflow:root scripts/validate_dags.py /opt/airflow/scripts/validate_dags.py
COPY --chown=airflow:root requirements-airflow.txt /opt/airflow/requirements-airflow.txt

USER airflow
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt" \
    -r /opt/airflow/requirements-airflow.txt

ENV PYTHONPATH="/opt/airflow:/opt/airflow/src"
