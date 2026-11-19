# Contribuindo

## Estratégia de branches

O fluxo oficial do repositório é:

```text
main
 └── dev
      ├── feat/nome-da-entrega
      ├── fix/nome-do-ajuste
      ├── chore/nome-da-tarefa
      ├── docs/nome-da-documentacao
      └── test/nome-dos-testes

work branch -> Pull Request -> dev -> Pull Request -> main
```

### Regras obrigatórias

1. `main` é a branch estável e não recebe commits diretos.
2. `dev` é a branch de integração e deve partir da `main`.
3. Toda branch de trabalho deve ser criada a partir da versão atual de `dev`.
4. Branches de trabalho abrem PR somente para `dev`.
5. Somente `dev` pode abrir PR para `main`.
6. Todo PR precisa passar pelos checks de CI e pela validação **Branch policy / Validate branch flow**.
7. Se `dev` avançar enquanto sua branch estiver em desenvolvimento, atualize sua branch com `dev` e rode novamente os testes.
8. Não use bypass de regras, force-push ou merge local direto em `main`.

### Criar uma branch

Sempre atualize as referências primeiro:

```bash
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c feat/minha-entrega
```

Para correções, use prefixo `fix/`; para manutenção, `chore/`; documentação, `docs/`; refatoração, `refactor/`; testes, `test/`.

### Validar localmente

```bash
python -m pip install -r requirements-dev.txt -r requirements-airflow.txt
ruff check .
PYTHONPATH=src pytest -q
docker compose config --quiet
```

### Pull requests

- Abra PR da branch de trabalho para `dev`.
- Descreva contexto, solução, testes executados e impactos.
- Aguarde todos os checks obrigatórios.
- Após a integração e validação em `dev`, abra PR de `dev` para `main`.
- A publicação de imagem GHCR é vinculada ao CI concluído com sucesso na `main`.

A validação automatizada de fluxo está em `.github/workflows/branch-policy.yml`. As proteções contra push direto e merge sem checks também precisam estar habilitadas nas configurações de Rulesets/Branches do GitHub; o workflow sozinho não impede push direto.
