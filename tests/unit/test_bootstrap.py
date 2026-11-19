from pathlib import Path

from scripts import bootstrap


def test_generate_env_creates_secrets_and_does_not_overwrite(
    tmp_path: Path, monkeypatch
) -> None:
    env_file = tmp_path / ".env"
    monkeypatch.setattr(bootstrap, "ENV_FILE", env_file)

    bootstrap.generate_env()

    first_content = env_file.read_text(encoding="utf-8")
    assert "POSTGRES_PASSWORD=" in first_content
    assert "AIRFLOW_FERNET_KEY=" in first_content
    assert "_AIRFLOW_WWW_USER_PASSWORD=" in first_content

    bootstrap.generate_env()
    assert env_file.read_text(encoding="utf-8") == first_content
