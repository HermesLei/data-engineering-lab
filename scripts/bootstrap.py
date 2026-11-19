"""Prepara diretórios e segredos locais para o Docker Compose."""

from __future__ import annotations

import base64
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
DATA_DIR = ROOT / "data"
AIRFLOW_DEFAULT_UID = 50000

DIRECTORIES = (
    "airflow/dags",
    "airflow/logs",
    "airflow/plugins",
    "airflow/config",
    "data",
    "src/ingestion",
    "src/processing",
    "src/validation",
    "src/common",
    "tests/unit",
    "tests/integration",
)


def get_airflow_uid() -> int:
    """Retorna o UID para os containers, evitando executar Airflow como root."""
    current_uid = os.getuid() if hasattr(os, "getuid") else AIRFLOW_DEFAULT_UID
    return current_uid if current_uid > 0 else AIRFLOW_DEFAULT_UID


def ensure_airflow_uid() -> None:
    """Corrige AIRFLOW_UID ausente ou igual a zero sem alterar outros segredos."""
    expected_uid = get_airflow_uid()

    if not ENV_FILE.exists():
        return

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    uid_found = False

    for line in lines:
        if line.startswith("AIRFLOW_UID="):
            uid_found = True
            try:
                current_uid = int(line.partition("=")[2])
            except ValueError:
                current_uid = 0

            if current_uid <= 0:
                updated_lines.append(f"AIRFLOW_UID={expected_uid}")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    if not uid_found:
        updated_lines.append(f"AIRFLOW_UID={expected_uid}")

    if updated_lines != lines:
        ENV_FILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
        try:
            ENV_FILE.chmod(0o600)
        except OSError:
            pass
        print(f"AIRFLOW_UID ajustado para {expected_uid}.")


def ensure_data_permissions() -> None:
    """Garante escrita do grupo usado pelos containers Airflow no volume de dados."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.chmod(0o775)


def generate_env() -> None:
    """Cria .env ou repara AIRFLOW_UID, preservando credenciais existentes."""
    if ENV_FILE.exists():
        print(".env já existe; mantendo as credenciais atuais.")
        ensure_airflow_uid()
        return

    fernet_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "AIRFLOW_FERNET_KEY": fernet_key,
        "AIRFLOW_WEBSERVER_SECRET_KEY": secrets.token_urlsafe(32),
        "_AIRFLOW_WWW_USER_USERNAME": "admin",
        "_AIRFLOW_WWW_USER_PASSWORD": secrets.token_urlsafe(18),
        "AIRFLOW_UID": str(get_airflow_uid()),
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
    ensure_data_permissions()
    generate_env()


if __name__ == "__main__":
    main()
