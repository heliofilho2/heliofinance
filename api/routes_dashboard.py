"""
Rotas do dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from core.finance_engine_api import FinanceEngineAPI

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Retorna dados completos do dashboard"""
    engine = FinanceEngineAPI(db)
    
    # Saldo atual
    current_balance = engine.get_current_balance()
    
    # Performance do mês
    from datetime import datetime
    today = datetime.now()
    month_perf = engine.get_month_performance(today.year, today.month)
    
    # Semáforo
    status, status_label, performance = engine.get_traffic_light_status()
    
    # Comprometimento
    commitment_ratio, commitment_details = engine.get_commitment_ratio()
    
    # Projeção 3 meses
    projections = engine.project_future_balance(3)
    
    # Parcelas ativas
    from core.models_sqlalchemy import InstallmentGroup
    active_installments = db.query(InstallmentGroup).filter(
        InstallmentGroup.is_simulation == False
    ).all()
    
    # Transações recentes
    from core.models_sqlalchemy import Transaction
    recent_transactions = db.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).limit(10).all()
    
    # Configurações
    from core.models_sqlalchemy import UserSettings
    settings = db.query(UserSettings).filter(UserSettings.id == 1).first()
    if not settings:
        settings = UserSettings()
    
    return {
        "current_balance": current_balance,
        "month_performance": {
            "entradas": month_perf['entradas'],
            "fixos": month_perf['fixos'],
            "variaveis": month_perf['variaveis'],
            "parcelas": month_perf['parcelas'],
            "performance": month_perf['performance'],
            "total_saidas": month_perf['total_saidas']
        },
        "traffic_light": {
            "status": status,
            "label": status_label,
            "performance": performance
        },
        "commitment": {
            "ratio": commitment_ratio,
            "fixos_parcelas": commitment_details['fixos_parcelas'],
            "media_receita": commitment_details['media_receita']
        },
        "projections": projections,
        "active_installments": [
            {
                "id": inst.id,
                "description": inst.description,
                "installment_value": inst.installment_value,
                "remaining_installments": inst.remaining_installments,
                "total_installments": inst.total_installments,
                "start_date": inst.start_date
            }
            for inst in active_installments
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "date": t.date,
                "description": t.description,
                "amount": t.amount,
                "type": t.type,
                "category": t.category
            }
            for t in recent_transactions
        ],
        "settings": {
            "average_income": settings.average_income,
            "emergency_reserve": settings.emergency_reserve,
            "warning_threshold": settings.warning_threshold,
            "critical_threshold": settings.critical_threshold
        }
    }
