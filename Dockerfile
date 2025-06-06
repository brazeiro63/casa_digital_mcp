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

# Copia o script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8000

# Roda o script de inicialização
CMD ["/start.sh"]