# Data Engineering Lab

Laboratório progressivo de Engenharia de Dados com práticas próximas de ambientes corporativos.

## Governança do repositório

O fluxo de integração é obrigatório:

```text
branches de trabalho -> dev -> main
```

- Toda branch de trabalho deve nascer da versão atual de `dev`.
- PR de feature/fix/chore/docs/test/refactor deve ter `dev` como destino.
- Somente `dev` pode ter PR com destino a `main`.
- CI e Branch policy precisam passar antes do merge.
- Push direto em `main` e `dev` deve ser bloqueado pelas regras de proteção do GitHub.

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para comandos, convenções e critérios de PR. A política automatizada está em `.github/workflows/branch-policy.yml`.

## Stack

- **GitHub Codespaces**: ambiente de desenvolvimento no navegador.
- **Docker Compose**: execução dos serviços.
- **Apache Airflow 2.10.5 / Python 3.12**: orquestração.
- **PostgreSQL 16**: metadados do Airflow.
- **PyArrow / Parquet**: armazenamento colunar nas camadas do laboratório.
- **Databricks Free Edition**: integração prevista em etapa posterior.
- **GitHub Actions / GHCR**: CI e publicação da imagem customizada.

## Iniciar o ambiente no Codespaces

1. Crie um Codespace a partir da branch que contém esta implementação.
2. Aguarde o Dev Container preparar a workspace.
3. No terminal, execute:

```bash
bash scripts/start_codespace.sh
```

O script cria `.env` apenas se ainda não existir, valida o Compose, constrói a imagem, inicializa o metastore e inicia webserver/scheduler. Não sobrescreve credenciais existentes.

Abra a porta **8080** na aba **Ports**. Usuário: `admin`. Para consultar a senha aleatória:

```bash
grep _AIRFLOW_WWW_USER_PASSWORD .env
```

Para parar sem apagar o banco: `docker compose down`.

## Pipeline de vendas sintéticas

A DAG `synthetic_sales_pipeline` executa quatro tarefas encadeadas:

1. **generate_synthetic_sales**: gera 1.000 vendas fictícias em CSV com seed fixa.
2. **build_bronze**: converte CSV em Parquet e preserva os registros recebidos.
3. **build_silver**: tipa campos, valida dados, remove inválidos e deduplica por `sale_id`.
4. **build_gold**: agrega pedidos aprovados por data e canal, calculando pedidos, receita líquida e itens vendidos.

Os dados ficam em `data/raw`, `data/bronze`, `data/silver` e `data/gold`, persistidos no workspace do Codespace.

### Executar

1. Acesse o Airflow pela porta encaminhada 8080.
2. Ative `synthetic_sales_pipeline`.
3. Clique em **Trigger DAG** e acompanhe as tasks/logs.
4. Inspecione os arquivos Parquet na pasta `data/`.

A origem contém intencionalmente cliente nulo, quantidade negativa, preço ausente, data inválida e duplicidade. Bronze preserva os registros; Silver remove os registros inválidos e duplicados. O gerador recria o arquivo a cada execução: esta primeira versão é **full refresh didático**, ainda não é incremental. Watermark, partições e backfill serão desenvolvidos depois.

## Testes

```bash
python -m pip install -r requirements-dev.txt -r requirements-airflow.txt
ruff check .
PYTHONPATH=src pytest -q
```

## Segurança e limites

- Nunca versione `.env`, senhas, tokens ou chaves.
- PostgreSQL é o metastore do Airflow, não o warehouse analítico.
- Os dados são fictícios e locais ao Codespace.
- A configuração é didática, sem HA/hardening de produção.
- O CD publica a imagem no GHCR; não implanta um Airflow remoto.

## Próximas etapas

1. Ingestão incremental com watermark e partições por data.
2. Idempotência, backfill e reconciliação.
3. Integração Databricks Free Edition.
4. dbt para modelagem Gold.
