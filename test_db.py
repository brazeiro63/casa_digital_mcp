from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
print(f"Usando DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("✅ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print("❌ Erro na conexão:", e)