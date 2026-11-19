"""Prepara diretórios e segredos locais para o Docker Compose."""

from __future__ import annotations

import base64
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"

DIRECTORIES = (
    "airflow/dags",
    "airflow/logs",
    "airflow/plugins",
    "airflow/config",
    "src/ingestion",
    "src/processing",
    "src/validation",
    "src/common",
    "tests/unit",
    "tests/integration",
)


def generate_env() -> None:
    """Cria .env apenas quando ainda não existe, sem sobrescrever credenciais."""
    if ENV_FILE.exists():
        print(".env já existe; mantendo as configurações atuais.")
        return

    fernet_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "AIRFLOW_FERNET_KEY": fernet_key,
        "AIRFLOW_WEBSERVER_SECRET_KEY": secrets.token_urlsafe(32),
        "_AIRFLOW_WWW_USER_USERNAME": "admin",
        "_AIRFLOW_WWW_USER_PASSWORD": secrets.token_urlsafe(18),
        "AIRFLOW_UID": str(os.getuid() if hasattr(os, "getuid") else 50000),
    }
    ENV_FILE.write_text(
        "# Gerado localmente. Nunca versione este arquivo.\n"
        + "".join(f"{key}={value}\n" for key, value in values.items()),
        encoding="utf-8",
    )
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        pass
    print(f".env criado em {ENV_FILE}")
    print("Guarde a senha do Airflow exibida no arquivo .env.")


def main() -> None:
    for directory in DIRECTORIES:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    generate_env()


if __name__ == "__main__":
    main()
