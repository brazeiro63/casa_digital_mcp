# sync_mercadolivre.py
import requests
import time
import json

# Configuração
BASE_URL = "http://localhost:8000/api/v1"
SYNC_ENDPOINT = "/sync/products/"  # Endpoint correto conforme o código

# Termos de busca para diferentes categorias
search_terms = {
    "Smartphones": ["smartphone", "celular", "iphone", "samsung galaxy"],
    "Notebooks": ["notebook", "laptop", "macbook", "computador portatil"],
    "TVs": ["smart tv", "tv 4k", "televisor", "tv led"],
    "Eletrodomésticos": ["geladeira", "fogão", "microondas", "lava louças", "lava roupas"],
    "Casa e Decoração": ["sofá", "mesa", "cadeira", "cama", "decoração"],
    "Informática": ["monitor", "teclado", "mouse", "impressora", "ssd", "pendrive"]
}

# Categorias específicas para cada termo (opcional)
categories = {
    "smartphone": "MLB1051",
    "celular": "MLB1051",
    "iphone": "MLB1051",
    "samsung galaxy": "MLB1051",
    "notebook": "MLB1648",
    "laptop": "MLB1648",
    "macbook": "MLB1648",
    "smart tv": "MLB1000",
    "tv 4k": "MLB1000",
    "geladeira": "MLB5726",
    "fogão": "MLB5726",
    "microondas": "MLB5726"
    # Adicione mais mapeamentos conforme necessário
}

# Função para sincronizar produtos
def sync_products(platform, search_term, limit=50, category=None):
    print(f"Sincronizando produtos para: '{search_term}' na plataforma '{platform}'")
    
    try:
        # Preparar a URL e os parâmetros para a requisição
        url = f"{BASE_URL}{SYNC_ENDPOINT}{platform}/"
        
        # Parâmetros da requisição conforme esperado pelo endpoint
        params = {
            "query": search_term,
            "limit": limit
        }
        
        # Adicionar categoria se especificada
        if category:
            params["category"] = category
        
        # Fazer a requisição para o endpoint de sincronização
        response = requests.post(url, params=params)
        
        # Verificar o resultado
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sincronização iniciada para '{search_term}' na plataforma '{platform}'")
            print(f"  Detalhes: {result}")
            return True
        else:
            print(f"✗ Erro na sincronização para '{search_term}': {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exceção ao sincronizar '{search_term}': {str(e)}")
        return False

# Função principal
def main():
    print("=== Iniciando sincronização de produtos do Mercado Livre ===")
    
    # Plataforma alvo
    platform = "mercadolivre"
    
    total_success = 0
    total_attempts = 0
    
    # Para cada categoria e seus termos de busca
    for category_name, terms in search_terms.items():
        print(f"\n>> Categoria: {category_name}")
        
        # Para cada termo de busca na categoria
        for term in terms:
            total_attempts += 1
            
            # Obter a categoria específica para o termo, se disponível
            specific_category = categories.get(term)
            
            # Sincronizar produtos
            success = sync_products(
                platform=platform,
                search_term=term,
                limit=50,
                category=specific_category
            )
            
            if success:
                total_success += 1
            
            # Pausa para não sobrecarregar a API
            time.sleep(5)
    
    # Resumo
    print("\n=== Resumo da sincronização ===")
    print(f"Total de tentativas: {total_attempts}")
    print(f"Sincronizações iniciadas com sucesso: {total_success}")
    print(f"Taxa de sucesso: {(total_success/total_attempts)*100:.2f}%")
    
    # Verificar produtos importados (após um tempo para permitir que as tarefas em segundo plano terminem)
    print("\nAguardando 30 segundos para que as tarefas em segundo plano terminem...")
    time.sleep(30)
    
    try:
        response = requests.get(f"{BASE_URL}/products/")
        if response.status_code == 200:
            products = response.json()
            print(f"\nTotal de produtos no banco de dados: {len(products)}")
        else:
            print(f"\nNão foi possível verificar o total de produtos: {response.status_code}")
    except Exception as e:
        print(f"\nErro ao verificar produtos: {str(e)}")

if __name__ == "__main__":
    main()