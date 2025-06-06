#!/bin/sh

# Aguarda o banco estar disponível (opcional mas recomendado)
echo "Aguardando o banco ficar pronto..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Banco de dados conectável."

# Aplica migrações do Alembic
echo "Aplicando migrações do Alembic..."
alembic upgrade head

# Inicia a aplicação
echo "Iniciando a API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload