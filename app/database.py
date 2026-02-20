"""
Configuração do banco de dados SQLite com SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Caminho do banco
DATABASE_URL = "sqlite:///./data/finance.db"

# Criar diretório se não existir
os.makedirs("data", exist_ok=True)

# Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados criando as tabelas"""
    # Importar modelos para garantir que estão registrados
    from core.models_sqlalchemy import Transaction, InstallmentGroup, UserSettings
    Base.metadata.create_all(bind=engine)
    
    # Criar configurações padrão se não existir
    from sqlalchemy.orm import Session
    db = SessionLocal()
    try:
        from core.models_sqlalchemy import UserSettings
        existing = db.query(UserSettings).filter(UserSettings.id == 1).first()
        if not existing:
            default_settings = UserSettings(
                id=1,
                average_income=0.0,
                emergency_reserve=0.0,
                warning_threshold=70.0,
                critical_threshold=90.0,
                daily_average_expense=0.0
            )
            db.add(default_settings)
            db.commit()
    except Exception as e:
        print(f"Aviso ao inicializar settings: {e}")
        db.rollback()
    finally:
        db.close()
