FROM python:3.10-slim-bullseye

# Atualiza os pacotes do sistema para corrigir vulnerabilidades
RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

# Copia apenas o requirements.txt primeiro
COPY requirements.txt ./

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]