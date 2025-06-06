from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session

from app.api.api import api_router
from app.core.config import settings
from app.models.product import Product
from app.db.session import get_db


app = FastAPI(
    title="Casa Digital MCP",
    description="Servidor MCP para integração de afiliados e automação de vendas",
    version="0.1.0",
)

db = Session()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Casa Digital MCP", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Configuração dos templates
templates = Jinja2Templates(directory="app/templates")

# Configuração de arquivos estáticos (opcional)
#app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/affiliate/dashboard", response_class=HTMLResponse)
async def affiliate_dashboard(request: Request):
    stats = {
        "total_products": 100,
        "with_affiliate": 100,
        "without_affiliate": 10,
    }
    return templates.TemplateResponse("affiliate_dashboard.html", {"request": request, "stats": stats})
