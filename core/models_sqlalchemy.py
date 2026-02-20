"""
Modelos SQLAlchemy para FastAPI
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    """Modelo de transação financeira"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'income', 'fixed', 'variable', 'installment'
    category = Column(String)
    installment_group_id = Column(Integer, ForeignKey("installment_groups.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    installment_group = relationship("InstallmentGroup", back_populates="transactions")


class InstallmentGroup(Base):
    """Grupo de parcelas (empréstimo ou compra parcelada)"""
    __tablename__ = "installment_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    total_value = Column(Float, nullable=False)
    installment_value = Column(Float, nullable=False)
    total_installments = Column(Integer, nullable=False)
    remaining_installments = Column(Integer, nullable=False)
    start_date = Column(String, nullable=False)  # YYYY-MM-DD
    is_simulation = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    transactions = relationship("Transaction", back_populates="installment_group")


class UserSettings(Base):
    """Configurações do usuário"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, default=1)
    average_income = Column(Float, default=0.0)
    emergency_reserve = Column(Float, default=0.0)
    warning_threshold = Column(Float, default=70.0)
    critical_threshold = Column(Float, default=90.0)
    daily_average_expense = Column(Float, default=0.0)
