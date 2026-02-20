"""
Rotas de simulações
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from core.models_sqlalchemy import InstallmentGroup
from core.finance_engine_api import FinanceEngineAPI

router = APIRouter()


class LoanSimulation(BaseModel):
    value: float
    monthly_rate: float
    term: int
    start_date: Optional[str] = None


class PurchaseSimulation(BaseModel):
    description: str
    value: float
    installments: int
    start_date: Optional[str] = None


@router.post("/simulate/loan")
def simulate_loan(simulation: LoanSimulation, db: Session = Depends(get_db)):
    """Simula empréstimo"""
    if simulation.start_date is None:
        simulation.start_date = datetime.now().strftime('%Y-%m-%d')
    
    # Calcular parcela
    if simulation.monthly_rate == 0:
        installment = simulation.value / simulation.term
    else:
        i = simulation.monthly_rate / 100  # Converter % para decimal
        installment = simulation.value * (i * (1 + i)**simulation.term) / ((1 + i)**simulation.term - 1)
    
    # Criar grupo de parcelas (simulação)
    group = InstallmentGroup(
        description=f"Empréstimo R$ {simulation.value:,.2f}",
        total_value=simulation.value,
        installment_value=installment,
        total_installments=simulation.term,
        remaining_installments=simulation.term,
        start_date=simulation.start_date,
        is_simulation=True
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Calcular impacto
    engine = FinanceEngineAPI(db)
    commitment_ratio, commitment_details = engine.get_commitment_ratio()
    
    new_fixos_parcelas = commitment_details['fixos_parcelas'] + installment
    new_ratio = (new_fixos_parcelas / commitment_details['media_receita'] * 100) if commitment_details['media_receita'] > 0 else 0
    
    # Projeção
    projections = engine.project_future_balance(simulation.term)
    
    return {
        "group_id": group.id,
        "value": simulation.value,
        "monthly_rate": simulation.monthly_rate,
        "term": simulation.term,
        "installment": installment,
        "total_payable": installment * simulation.term,
        "impact": {
            "monthly_impact": installment,
            "new_commitment_ratio": new_ratio,
            "current_commitment_ratio": commitment_ratio,
            "projections": projections
        }
    }


@router.post("/simulate/installment")
def simulate_purchase(simulation: PurchaseSimulation, db: Session = Depends(get_db)):
    """Simula compra parcelada"""
    if simulation.start_date is None:
        simulation.start_date = datetime.now().strftime('%Y-%m-%d')
    
    installment_value = simulation.value / simulation.installments
    
    # Criar grupo de parcelas (simulação)
    group = InstallmentGroup(
        description=simulation.description,
        total_value=simulation.value,
        installment_value=installment_value,
        total_installments=simulation.installments,
        remaining_installments=simulation.installments,
        start_date=simulation.start_date,
        is_simulation=True
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Calcular impacto
    engine = FinanceEngineAPI(db)
    projections = engine.project_future_balance(simulation.installments)
    
    return {
        "group_id": group.id,
        "description": simulation.description,
        "value": simulation.value,
        "installments": simulation.installments,
        "installment_value": installment_value,
        "impact": {
            "monthly_impact": installment_value,
            "projections": projections
        }
    }


@router.post("/simulate/{group_id}/confirm")
def confirm_simulation(group_id: int, db: Session = Depends(get_db)):
    """Confirma uma simulação (torna real)"""
    group = db.query(InstallmentGroup).filter(InstallmentGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    
    group.is_simulation = False
    db.commit()
    
    return {"message": "Simulação confirmada", "group_id": group_id}


@router.delete("/simulate/{group_id}")
def cancel_simulation(group_id: int, db: Session = Depends(get_db)):
    """Cancela uma simulação"""
    group = db.query(InstallmentGroup).filter(InstallmentGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    
    if not group.is_simulation:
        raise HTTPException(status_code=400, detail="Não é possível cancelar simulação confirmada")
    
    db.delete(group)
    db.commit()
    
    return {"message": "Simulação cancelada"}
