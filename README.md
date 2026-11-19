# Data Engineering Lab

Laboratório progressivo de Engenharia de Dados com foco em práticas próximas de ambientes corporativos.

## Stack do laboratório

- **GitHub Codespaces**: ambiente de desenvolvimento no navegador.
- **Docker Compose**: execução dos serviços.
- **Apache Airflow 2.10.5**: orquestração de pipelines.
- **PostgreSQL 16**: metadados do Airflow (não é o warehouse analítico).
- **Databricks Free Edition**: plataforma lakehouse/warehouse, integrada em uma etapa posterior.
- **GitHub Actions**: lint e testes automatizados.

## Etapa 1 — iniciar o Codespace

1. Abra **Code → Codespaces → Create codespace** e selecione a branch `feat/airflow-codespaces-foundation`.
2. O `initializeCommand` cria o arquivo local `.env` com credenciais aleatórias. Ele está no `.gitignore`.
3. Aguarde o Dev Container iniciar e instalar as dependências.
4. No terminal do Codespace, inicialize o banco e o Airflow:

```bash
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler
docker compose ps
```

5. Abra a porta **8080** na aba **Ports**.
6. Entre com usuário `admin`. Consulte a senha gerada em `.env`:

```bash
grep _AIRFLOW_WWW_USER_PASSWORD .env
```

## Validar a DAG

A DAG `hello_data_platform` está em `airflow/dags/hello_data_platform.py`.

1. No Airflow, habilite a DAG.
2. Execute-a manualmente.
3. Confira o log da tarefa `validate_environment`.

## Comandos úteis

```bash
docker compose ps
docker compose logs -f airflow-scheduler
docker compose down
python scripts/check_environment.py
pytest -q
ruff check .
```

Para apagar também o volume do PostgreSQL (operação destrutiva):

```bash
docker compose down -v
```

## Segurança e limites

- Nunca versione `.env`, senhas, tokens ou chaves.
- O PostgreSQL do Compose é apenas o metastore do Airflow.
- Não exponha o Airflow diretamente à internet em um ambiente produtivo.
- Esta configuração é didática e destinada ao Codespaces; não é uma implantação HA/produção.
- O primeiro start pode levar alguns minutos para baixar as imagens Docker.

## Próximas etapas

1. Criar pipeline de ingestão batch com dados sintéticos.
2. Implementar camadas Bronze, Silver e Gold.
3. Adicionar validações, idempotência, incrementalidade e backfill.
4. Integrar Databricks Free Edition.
5. Evoluir testes e CI.
