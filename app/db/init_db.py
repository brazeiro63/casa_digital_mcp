from sqlalchemy.orm import Session

from app.db.session import Base, engine

def init_db() -> None:
    # Cria as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")