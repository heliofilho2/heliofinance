"""
Motor financeiro adaptado para SQLAlchemy/FastAPI
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from core.models_sqlalchemy import Transaction, InstallmentGroup, UserSettings
import calendar


class FinanceEngineAPI:
    """Motor de cálculos financeiros para API"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_month_performance(self, year: int, month: int) -> Dict[str, Any]:
        """Calcula performance de um mês específico"""
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Buscar transações do mês
        transactions = self.db.query(Transaction).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # Separar por tipo
        entradas = sum(t.amount for t in transactions if t.type == 'income' and t.amount > 0)
        fixos = abs(sum(t.amount for t in transactions if t.type == 'fixed' and t.amount < 0))
        variaveis = abs(sum(t.amount for t in transactions if t.type == 'variable' and t.amount < 0))
        
        # Calcular parcelas do mês
        parcelas = self._calculate_installments_for_month(year, month)
        
        # Performance
        performance = entradas - (fixos + variaveis + parcelas)
        
        return {
            'year': year,
            'month': month,
            'entradas': entradas,
            'fixos': fixos,
            'variaveis': variaveis,
            'parcelas': parcelas,
            'performance': performance,
            'total_saidas': fixos + variaveis + parcelas
        }
    
    def _calculate_installments_for_month(self, year: int, month: int) -> float:
        """Calcula total de parcelas para um mês específico"""
        groups = self.db.query(InstallmentGroup).filter(
            InstallmentGroup.is_simulation == False
        ).all()
        
        total = 0.0
        
        for group in groups:
            start = datetime.strptime(group.start_date, '%Y-%m-%d')
            month_date = datetime(year, month, 1)
            
            months_passed = (month_date.year - start.year) * 12 + (month_date.month - start.month)
            
            if months_passed >= 0 and months_passed < group.total_installments:
                if group.remaining_installments > (group.total_installments - months_passed - 1):
                    total += group.installment_value
        
        return total
    
    def get_current_balance(self) -> float:
        """Calcula saldo atual"""
        transactions = self.db.query(Transaction).all()
        return sum(t.amount for t in transactions)
    
    def get_commitment_ratio(self) -> Tuple[float, Dict[str, Any]]:
        """Calcula comprometimento"""
        today = datetime.now()
        receitas_3_meses = []
        
        for i in range(3):
            month_date = today - timedelta(days=30 * (i + 1))
            month_perf = self.get_month_performance(month_date.year, month_date.month)
            receitas_3_meses.append(month_perf['entradas'])
        
        media_receita = sum(receitas_3_meses) / 3 if receitas_3_meses else 0
        
        current_perf = self.get_month_performance(today.year, today.month)
        fixos_parcelas = current_perf['fixos'] + current_perf['parcelas']
        
        ratio = (fixos_parcelas / media_receita * 100) if media_receita > 0 else 0
        
        return ratio, {
            'fixos_parcelas': fixos_parcelas,
            'media_receita': media_receita,
            'ratio': ratio
        }
    
    def get_traffic_light_status(self) -> Tuple[str, str, float]:
        """Retorna status do semáforo financeiro"""
        today = datetime.now()
        perf = self.get_month_performance(today.year, today.month)
        
        settings = self.db.query(UserSettings).filter(UserSettings.id == 1).first()
        if not settings:
            settings = UserSettings()
        
        performance = perf['performance']
        
        _, commitment = self.get_commitment_ratio()
        media_receita = commitment['media_receita']
        
        if media_receita > 0:
            limite_critico = -(media_receita * settings.critical_threshold / 100)
        else:
            limite_critico = -1000
        
        if performance >= 0:
            return 'green', '🟢 Saudável', performance
        elif performance > limite_critico:
            return 'yellow', '🟡 Atenção', performance
        else:
            return 'red', '🔴 Crítico', performance
    
    def project_future_balance(self, months: int = 6) -> List[Dict[str, Any]]:
        """Projeta saldo futuro"""
        today = datetime.now()
        current_balance = self.get_current_balance()
        
        settings = self.db.query(UserSettings).filter(UserSettings.id == 1).first()
        if not settings:
            settings = UserSettings()
        
        # Calcular médias históricas
        receitas_3_meses = []
        variaveis_3_meses = []
        
        for i in range(3):
            month_date = today - timedelta(days=30 * (i + 1))
            month_perf = self.get_month_performance(month_date.year, month_date.month)
            receitas_3_meses.append(month_perf['entradas'])
            variaveis_3_meses.append(month_perf['variaveis'])
        
        media_receita = sum(receitas_3_meses) / 3 if receitas_3_meses else settings.average_income
        media_variavel = sum(variaveis_3_meses) / 3 if variaveis_3_meses else (settings.daily_average_expense * 30)
        
        # Projeção
        projections = []
        balance = current_balance
        
        for i in range(months):
            month_date = today + timedelta(days=30 * i)
            year = month_date.year
            month = month_date.month
            
            if i == 0:
                perf = self.get_month_performance(year, month)
            else:
                # Projeção
                month_perf_real = self.get_month_performance(year, month)
                fixos = month_perf_real['fixos'] if month_perf_real['fixos'] > 0 else self._get_fixed_expenses_for_month(year, month)
                parcelas = self._calculate_installments_for_month(year, month)
                
                perf = {
                    'entradas': media_receita,
                    'fixos': fixos,
                    'variaveis': media_variavel,
                    'parcelas': parcelas,
                    'performance': media_receita - (fixos + media_variavel + parcelas)
                }
            
            balance += perf['performance']
            
            projections.append({
                'year': year,
                'month': month,
                'month_name': calendar.month_name[month],
                'performance': perf['performance'],
                'balance': balance,
                'entradas': perf['entradas'],
                'saidas': perf.get('fixos', 0) + perf.get('variaveis', 0) + perf.get('parcelas', 0)
            })
        
        return projections
    
    def _get_fixed_expenses_for_month(self, year: int, month: int) -> float:
        """Calcula fixos recorrentes de um mês"""
        today = datetime.now()
        fixos_3_meses = []
        
        for i in range(3):
            month_date = today - timedelta(days=30 * (i + 1))
            month_perf = self.get_month_performance(month_date.year, month_date.month)
            fixos_3_meses.append(month_perf['fixos'])
        
        return sum(fixos_3_meses) / 3 if fixos_3_meses else 0
    
    def calculate_max_installment(self, keep_status: str = 'yellow') -> float:
        """Calcula parcela máxima que aguenta"""
        today = datetime.now()
        perf = self.get_month_performance(today.year, today.month)
        
        settings = self.db.query(UserSettings).filter(UserSettings.id == 1).first()
        if not settings:
            settings = UserSettings()
        
        _, commitment = self.get_commitment_ratio()
        media_receita = commitment['media_receita']
        
        if media_receita == 0:
            return 0
        
        margem_atual = perf['performance']
        
        if keep_status == 'green':
            limite = 0
        elif keep_status == 'yellow':
            limite = -(media_receita * settings.warning_threshold / 100)
        else:
            limite = -(media_receita * settings.critical_threshold / 100)
        
        max_parcela = margem_atual - limite
        
        return max(0, max_parcela)
