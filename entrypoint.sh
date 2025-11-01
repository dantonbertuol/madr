#!/bin/sh

# Executa as migrações do banco de dados
uv run alembic upgrade head

# Inicia a aplicação
uv run uvicorn --host 0.0.0.0 --port 8000 madr.app:app