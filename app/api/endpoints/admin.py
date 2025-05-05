# app/api/endpoints/admin.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.session import get_db
from app.models.product import Product

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")

@router.get("/affiliate-dashboard", response_class=HTMLResponse)
async def affiliate_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Dashboard para gerenciamento de links de afiliado.
    """
    stats = {
        "total_products": db.query(Product).count(),
        "with_affiliate": db.query(Product).filter(Product.affiliate_url != None).count(),
        "without_affiliate": db.query(Product).filter(Product.affiliate_url == None).count(),
    }
    
    stats["coverage"] = round((stats["with_affiliate"] / stats["total_products"] * 100) if stats["total_products"] > 0 else 0, 2)
    
    return templates.TemplateResponse(
        "affiliate_dashboard.html",
        {"request": request, "stats": stats}
    )