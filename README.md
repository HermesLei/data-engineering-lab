# Data Engineering Lab

Laboratório progressivo de Engenharia de Dados com práticas próximas de ambientes corporativos.

## Stack

- **GitHub Codespaces**: ambiente de desenvolvimento no navegador.
- **Docker Compose**: execução dos serviços.
- **Apache Airflow 2.10.5 / Python 3.12**: orquestração de pipelines.
- **PostgreSQL 16**: metadados do Airflow (não é o warehouse analítico).
- **Databricks Free Edition**: lakehouse/warehouse, integração prevista em etapa posterior.
- **GitHub Actions**: CI e publicação contínua da imagem.
- **GitHub Container Registry (GHCR)**: registro da imagem customizada do Airflow.

## Etapa 1 — iniciar o Codespace

1. Abra **Code → Codespaces → Create codespace** na branch `main`.
2. O `initializeCommand` cria o arquivo local `.env` com credenciais aleatórias. Ele está no `.gitignore`.
3. Aguarde o Dev Container iniciar e instalar as dependências.
4. No terminal do Codespace, inicialize o banco e o Airflow:

```bash
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler
docker compose ps
```

O Compose constrói a imagem customizada definida em `infrastructure/docker/airflow/Dockerfile`.

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

A validação de CI também importa todas as DAGs por meio de `scripts/validate_dags.py`.

## CI — integração contínua

Workflow: `.github/workflows/ci.yml`

Executado em push para `main` e branches `feat/**`, pull requests para `main`, tags `v*` e execução manual.

Jobs:
1. **Python quality**: Ruff e Pytest.
2. **Airflow image**: build da imagem Docker e validação de importação das DAGs.
3. **Compose config**: gera ambiente local e valida a configuração do Docker Compose.

O CI não precisa de secrets para executar.

## CD — publicação contínua

Workflow: `.github/workflows/cd.yml`

Após uma execução bem-sucedida do workflow **Python CI** na branch `main`, o CD:
1. Faz checkout do mesmo commit validado.
2. Constrói a imagem customizada do Airflow.
3. Publica no GitHub Container Registry.
4. Gera tags `latest` e `sha-<commit>`.
5. Inclui metadados de provenance e SBOM.

Imagem publicada:

```text
ghcr.io/hermeslei/data-engineering-lab-airflow:latest
```

A publicação usa o `GITHUB_TOKEN` com permissão `packages: write`; não é necessário criar PAT. A visibilidade inicial do pacote segue a configuração do GHCR/conta. Não publique a imagem como pública se ela vier a conter código ou dados que devam permanecer privados.

O CD publica a imagem; ele **não implanta** nem reinicia um ambiente Airflow remoto. A implantação em infraestrutura será definida quando escolhermos o destino (por exemplo, ECS, EKS ou MWAA).

## Comandos úteis

```bash
# Estado dos containers
docker compose ps

# Logs do scheduler
docker compose logs -f airflow-scheduler

# Build local da imagem
docker compose build

# Parar serviços, preservando o banco
docker compose down

# Testes e qualidade locais
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
- O `.dockerignore` impede que segredos e artefatos locais entrem no contexto de build.
- O PostgreSQL do Compose é apenas o metastore do Airflow.
- Não exponha o Airflow diretamente à internet em um ambiente produtivo.
- Esta configuração é didática e destinada ao Codespaces; não é uma implantação HA/produção.
- O primeiro start pode levar alguns minutos para baixar as imagens Docker.

## Próximas etapas

1. Criar pipeline de ingestão batch com dados sintéticos.
2. Implementar camadas Bronze, Silver e Gold.
3. Adicionar validações, idempotência, incrementalidade e backfill.
4. Integrar Databricks Free Edition.
5. Evoluir para deploy em ambiente definido e testes de integração.
