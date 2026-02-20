"""
Rotas de transações
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.database import get_db
from core.models_sqlalchemy import Transaction
# TransactionService não necessário aqui, usando parser direto

router = APIRouter()


class TransactionCreate(BaseModel):
    date: str  # YYYY-MM-DD
    description: str
    amount: float
    type: str  # 'income', 'fixed', 'variable', 'installment'
    category: Optional[str] = "Outros"
    installment_group_id: Optional[int] = None


class TransactionResponse(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    type: str
    category: Optional[str]
    installment_group_id: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Converte datetime para string"""
        data = {
            'id': obj.id,
            'date': obj.date,
            'description': obj.description,
            'amount': obj.amount,
            'type': obj.type,
            'category': obj.category,
            'installment_group_id': obj.installment_group_id,
            'created_at': obj.created_at.isoformat() if obj.created_at else datetime.now().isoformat()
        }
        return cls(**data)


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Cria uma nova transação"""
    db_transaction = Transaction(
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        installment_group_id=transaction.installment_group_id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return TransactionResponse.from_orm(db_transaction)


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista transações com filtros opcionais"""
    query = db.query(Transaction)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    
    query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    transactions = query.all()
    return [TransactionResponse.from_orm(t) for t in transactions]


@router.post("/transactions/bulk")
def create_bulk_transactions(
    transactions: List[TransactionCreate],
    db: Session = Depends(get_db)
):
    """Cria múltiplas transações de uma vez"""
    created = []
    for transaction in transactions:
        db_transaction = Transaction(
            date=transaction.date,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            installment_group_id=transaction.installment_group_id
        )
        db.add(db_transaction)
        created.append(db_transaction)
    
    db.commit()
    
    for t in created:
        db.refresh(t)
    
    return {
        "message": f"{len(created)} transações criadas",
        "transactions": [TransactionResponse.from_orm(t) for t in created]
    }


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Atualiza uma transação existente"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Atualizar campos
    db_transaction.date = transaction.date
    db_transaction.description = transaction.description
    db_transaction.amount = transaction.amount
    db_transaction.type = transaction.type
    db_transaction.category = transaction.category
    db_transaction.installment_group_id = transaction.installment_group_id
    
    db.commit()
    db.refresh(db_transaction)
    
    return TransactionResponse.from_orm(db_transaction)


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Remove uma transação"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transação removida"}


@router.post("/transactions/quick")
def create_quick_transaction(command: str, db: Session = Depends(get_db)):
    """
    Cria transação a partir de comando rápido
    Ex: "mercado 87", "recebi cliente 2500"
    """
    try:
        from bot.parser import CommandParser
        
        parser = CommandParser()
        parsed = parser.parse(command)
        
        if not parsed:
            raise HTTPException(status_code=400, detail="Comando não reconhecido")
        
        # Se for simulação, retornar info sem salvar
        if parsed.get('type') in ['loan_simulation', 'purchase_simulation']:
            return {
                "type": "simulation",
                "data": parsed
            }
        
        # Validar campos obrigatórios
        if 'description' not in parsed or 'amount' not in parsed or 'type' not in parsed:
            raise HTTPException(status_code=400, detail="Dados incompletos no comando")
        
        # Criar transação
        today = datetime.now().strftime('%Y-%m-%d')
        
        db_transaction = Transaction(
            date=parsed.get('date', today),
            description=str(parsed['description']),
            amount=float(parsed['amount']),
            type=str(parsed['type']),
            category=str(parsed.get('category', 'Outros')),
            installment_group_id=None
        )
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return {
            "message": "Transação criada",
            "transaction": TransactionResponse(
                id=db_transaction.id,
                date=db_transaction.date,
                description=db_transaction.description,
                amount=db_transaction.amount,
                type=db_transaction.type,
                category=db_transaction.category or 'Outros',
                installment_group_id=db_transaction.installment_group_id,
                created_at=db_transaction.created_at.isoformat() if db_transaction.created_at else datetime.now().isoformat()
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Erro ao criar transação: {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao criar transação: {error_detail}")
