"""
FastAPI - Backend principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
import uvicorn

# Criar app
app = FastAPI(
    title="Gestão Financeira - Método Breno",
    description="API para gestão financeira pessoal",
    version="1.0.0"
)

# CORS (para app futuro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco
try:
    init_db()
    print("✅ Banco de dados inicializado")
except Exception as e:
    print(f"⚠️  Erro ao inicializar banco: {e}")
    import traceback
    traceback.print_exc()

# Importar rotas
from api.routes_transactions import router as transactions_router
from api.routes_dashboard import router as dashboard_router
from api.routes_simulations import router as simulations_router
from api.routes_google_sheets import router as google_sheets_router

# Registrar rotas
app.include_router(transactions_router, prefix="/api", tags=["transactions"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(simulations_router, prefix="/api", tags=["simulations"])
app.include_router(google_sheets_router, prefix="/api", tags=["google-sheets"])


@app.get("/")
def root():
    """Health check"""
    return {"status": "ok", "message": "Gestão Financeira API"}


@app.get("/health")
def health():
    """Health check detalhado"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
