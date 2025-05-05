# app/api/endpoints/affiliate_links.py
import csv
import io
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.product import Product
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/pending/", response_model=Dict[str, Any])
async def get_products_without_affiliate_links(
    platform: str = Query("mercadolivre", description="Plataforma de afiliados"),
    limit: int = Query(100, description="Número máximo de produtos a retornar"),
    db: Session = Depends(get_db)
):
    """
    Retorna produtos que não possuem links de afiliado.
    """
    products = db.query(Product).filter(
        Product.platform == platform,
        Product.affiliate_url == None
    ).limit(limit).all()
    
    total_pending = db.query(func.count(Product.id)).filter(
        Product.platform == platform,
        Product.affiliate_url == None
    ).scalar()
    
    return {
        "total_pending": total_pending,
        "returned_count": len(products),
        "products": products
    }

@router.get("/export/", response_model=Dict[str, Any])
async def export_products_for_affiliate_links(
    platform: str = Query("mercadolivre", description="Plataforma de afiliados"),
    limit: int = Query(100, description="Número máximo de produtos a exportar"),
    format: str = Query("csv", description="Formato de exportação (csv ou json)"),
    db: Session = Depends(get_db)
):
    """
    Exporta uma lista de produtos sem links de afiliado para processamento manual.
    """
    products = db.query(Product).filter(
        Product.platform == platform,
        Product.affiliate_url == None
    ).limit(limit).all()
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["product_id", "external_id", "product_url"])
        
        for product in products:
            writer.writerow([product.id, product.external_id, product.product_url])
        
        content = output.getvalue()
        filename = f"{platform}_products_for_affiliate_{len(products)}.csv"
        content_type = "text/csv"
    
    elif format.lower() == "json":
        content = [{"product_id": p.id, "external_id": p.external_id, "product_url": p.product_url} for p in products]
        filename = f"{platform}_products_for_affiliate_{len(products)}.json"
        content_type = "application/json"
    
    else:
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {format}")
    
    return {
        "filename": filename,
        "content_type": content_type,
        "content": content,
        "count": len(products)
    }

@router.post("/import/", response_model=Dict[str, Any])
async def import_affiliate_links(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa links de afiliado gerados manualmente e atualiza os produtos.
    Espera um arquivo CSV com as colunas: product_id, affiliate_url
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são suportados")
    
    try:
        contents = await file.read()
        decoded_contents = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_contents))
        
        # Validar cabeçalhos
        required_headers = ["product_id", "affiliate_url"]
        headers = reader.fieldnames
        
        if not all(header in headers for header in required_headers):
            raise HTTPException(
                status_code=400, 
                detail=f"Cabeçalhos obrigatórios não encontrados. Esperado: {required_headers}"
            )
        
        # Processar em segundo plano para arquivos grandes
        background_tasks.add_task(
            process_affiliate_links,
            decoded_contents=decoded_contents,
            db=db
        )
        
        return {
            "message": "Processamento iniciado em segundo plano",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

async def process_affiliate_links(decoded_contents: str, db: Session):
    """
    Processa os links de afiliado em segundo plano.
    """
    reader = csv.DictReader(io.StringIO(decoded_contents))
    updated_count = 0
    errors = []
    
    try:
        for row in reader:
            try:
                product_id = int(row["product_id"])
                affiliate_url = row["affiliate_url"]
                
                # Validar URL de afiliado
                if not is_valid_affiliate_url(affiliate_url):
                    errors.append(f"URL de afiliado inválida para o produto {product_id}: {affiliate_url}")
                    continue
                
                # Atualizar produto
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    product.affiliate_url = affiliate_url
                    db.add(product)
                    updated_count += 1
                else:
                    errors.append(f"Produto não encontrado: {product_id}")
            
            except Exception as e:
                errors.append(f"Erro ao processar linha: {row} - Erro: {str(e)}")
        
        # Commit das alterações
        db.commit()
        
        # Registrar resultados
        logger.info(f"Processamento concluído: {updated_count} produtos atualizados, {len(errors)} erros")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro durante o processamento em lote: {e}")

def is_valid_affiliate_url(url: str) -> bool:
    """
    Valida se a URL parece ser um link de afiliado válido do Mercado Livre.
    """
    # Verificação básica para links de afiliado do Mercado Livre
    # Ajuste conforme necessário com base nos padrões reais
    valid_patterns = [
        "mercadolivre.com.br/social/",
        "mercadolivre.com.br/link/redirect",
        "mercadolibre.com/social/",
        "mercadolibre.com/link/redirect"
    ]
    
    return any(pattern in url for pattern in valid_patterns)

@router.get("/stats/", response_model=Dict[str, Any])
async def get_affiliate_stats(
    platform: str = Query("mercadolivre", description="Plataforma de afiliados"),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas sobre os links de afiliado.
    """
    total_products = db.query(func.count(Product.id)).filter(
        Product.platform == platform
    ).scalar()
    
    with_affiliate = db.query(func.count(Product.id)).filter(
        Product.platform == platform,
        Product.affiliate_url != None
    ).scalar()
    
    without_affiliate = db.query(func.count(Product.id)).filter(
        Product.platform == platform,
        Product.affiliate_url == None
    ).scalar()
    
    return {
        "platform": platform,
        "total_products": total_products,
        "with_affiliate_url": with_affiliate,
        "without_affiliate_url": without_affiliate,
        "coverage_percentage": round((with_affiliate / total_products * 100) if total_products > 0 else 0, 2)
    }

@router.post("/validate/", response_model=Dict[str, Any])
async def validate_affiliate_links(
    background_tasks: BackgroundTasks,
    platform: str = Query("mercadolivre", description="Plataforma de afiliados"),
    db: Session = Depends(get_db)
):
    """
    Valida os links de afiliado existentes e marca os inválidos para atualização.
    """
    background_tasks.add_task(
        validate_affiliate_links_task,
        platform=platform,
        db=db
    )
    
    return {
        "message": "Validação de links iniciada em segundo plano",
        "status": "processing"
    }

async def validate_affiliate_links_task(platform: str, db: Session):
    """
    Tarefa em segundo plano para validar links de afiliado.
    """
    products = db.query(Product).filter(
        Product.platform == platform,
        Product.affiliate_url != None
    ).all()
    
    invalid_count = 0
    
    for product in products:
        if not is_valid_affiliate_url(product.affiliate_url):
            product.affiliate_url = None
            db.add(product)
            invalid_count += 1
    
    db.commit()
    logger.info(f"Validação concluída: {invalid_count} links inválidos encontrados e marcados para atualização")