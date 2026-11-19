"""Verificações rápidas da estrutura local do laboratório."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    ".devcontainer/devcontainer.json",
    "docker-compose.yml",
    "airflow/dags",
    "scripts/bootstrap.py",
    "requirements-dev.txt",
)


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        print("Itens ausentes:")
        for path in missing:
            print(f" - {path}")
        return 1

    print("Estrutura básica do laboratório validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
