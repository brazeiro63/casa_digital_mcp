# Casa Digital MCP

Servidor MCP (Model Context Protocol) para integração de afiliados e automação de vendas.

## Funcionalidades

- Integração com plataformas de afiliados
- API para consulta de produtos
- Suporte a agentes de IA para automação de vendas via WhatsApp

## Requisitos

- Python 3.9+
- PostgreSQL
- Redis

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente virtual:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Instale as dependências: `pip install -e .`
5. Configure o arquivo `.env` com suas credenciais
6. Inicialize o banco de dados: `python -m app.db.init_db`
7. Execute a aplicação: `python run.py`

## Uso com Docker

```bash
docker-compose up -d