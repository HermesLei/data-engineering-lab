#!/usr/bin/env bash
# Inicializa Airflow + PostgreSQL no GitHub Codespaces.
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

command -v docker >/dev/null 2>&1 || {
  echo "ERRO: Docker CLI não encontrado. Reabra pelo Dev Container."
  exit 1
}
docker compose version >/dev/null 2>&1 || {
  echo "ERRO: Docker Compose plugin indisponível."
  exit 1
}

python3 scripts/bootstrap.py

echo "[1/4] Validando Docker Compose..."
docker compose config --quiet
echo "[2/4] Construindo imagem do Airflow..."
docker compose build airflow-init
echo "[3/4] Inicializando banco e usuário administrador..."
docker compose up airflow-init
echo "[4/4] Iniciando webserver e scheduler..."
docker compose up -d airflow-webserver airflow-scheduler

echo
echo "Airflow iniciado. Abra a porta 8080 na aba Ports."
echo "Usuário: admin"
echo "Consulte a senha com: grep _AIRFLOW_WWW_USER_PASSWORD .env"
docker compose ps
