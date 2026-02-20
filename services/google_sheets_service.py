"""
Serviço de integração com Google Sheets
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy.orm import Session
from core.models_sqlalchemy import Transaction

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


class GoogleSheetsService:
    """Integra com Google Sheets para preencher planilha"""
    
    def __init__(self, spreadsheet_id: str, credentials_path: str = None):
        """
        Inicializa serviço do Google Sheets
        
        Args:
            spreadsheet_id: ID da planilha (da URL)
            credentials_path: Caminho para arquivo de credenciais JSON
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        
        if not self.credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH não configurado")
        
        # Autenticar
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scope
        )
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)
    
    def sync_transactions_to_sheet(self, db: Session, month: int = None, year: int = None):
        """
        Sincroniza transações do banco para a planilha Google Sheets
        
        Args:
            db: Sessão do banco de dados
            month: Mês a sincronizar (None = mês atual)
            year: Ano a sincronizar (None = ano atual)
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        # Nome do mês em português
        month_names = {
            1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
            5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
            9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
        }
        month_name = month_names[month]
        
        # Buscar transações do mês
        start_date = f"{year}-{month:02d}-01"
        last_day = (datetime(year, month + 1, 1) - timedelta(days=1)).day
        end_date = f"{year}-{month:02d}-{last_day}"
        
        transactions = db.query(Transaction).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date).all()
        
        # Calcular qual coluna do mês na planilha
        # A planilha tem 12 meses em colunas: JAN, FEV, MAR, etc.
        # Cada mês ocupa 6 colunas (Data, Entrada, Saída, Diário, Saldo, vazio)
        month_col_offset = (month - 1) * 6
        
        # Estrutura da planilha (baseada no CSV):
        # Linha 1: Cabeçalho dos meses
        # Linha 2: Cabeçalho (Data, Entrada, Saída, Diário, Saldo)
        # Linha 3+: Dados dos dias (1 a 31)
        
        try:
            # Tentar acessar a aba correta (geralmente a primeira)
            worksheet = self.spreadsheet.sheet1
            
            # Calcular saldo inicial do mês
            all_before = db.query(Transaction).filter(
                Transaction.date < start_date
            ).all()
            initial_balance = sum(t.amount for t in all_before)
            
            running_balance = initial_balance
            
            # Agrupar transações por dia
            transactions_by_day = {}
            for t in transactions:
                day = int(t.date.split('-')[2])
                if day not in transactions_by_day:
                    transactions_by_day[day] = {'entrada': 0, 'saida': 0, 'diario': 0}
                
                if t.amount > 0:
                    transactions_by_day[day]['entrada'] += t.amount
                else:
                    if t.type == 'variable':
                        transactions_by_day[day]['diario'] += abs(t.amount)
                    else:
                        transactions_by_day[day]['saida'] += abs(t.amount)
            
            # Preencher planilha (começando na linha 3, que é o dia 1)
            for day in range(1, last_day + 1):
                row = day + 2  # Linha 3 = dia 1, linha 4 = dia 2, etc.
                
                day_data = transactions_by_day.get(day, {'entrada': 0, 'saida': 0, 'diario': 0})
                
                # Calcular saldo acumulado
                running_balance += day_data['entrada'] - day_data['saida'] - day_data['diario']
                
                # Colunas do mês (baseado na estrutura do CSV)
                # Coluna 1: Data (já preenchida)
                # Coluna 2: Entrada
                # Coluna 3: Saída
                # Coluna 4: Diário
                # Coluna 5: Saldo
                
                col_data = month_col_offset + 1  # Primeira coluna do mês
                col_entrada = month_col_offset + 2
                col_saida = month_col_offset + 3
                col_diario = month_col_offset + 4
                col_saldo = month_col_offset + 5
                
                # Atualizar células
                if day_data['entrada'] > 0:
                    worksheet.update_cell(row, col_entrada, day_data['entrada'])
                if day_data['saida'] > 0:
                    worksheet.update_cell(row, col_saida, day_data['saida'])
                if day_data['diario'] > 0:
                    worksheet.update_cell(row, col_diario, day_data['diario'])
                
                # Sempre atualizar saldo
                worksheet.update_cell(row, col_saldo, running_balance)
            
            return {
                'success': True,
                'message': f'Planilha sincronizada para {month_name}/{year}',
                'transactions_synced': len(transactions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao sincronizar: {str(e)}'
            }
    
    def get_sheet_data(self, range_name: str = None):
        """Lê dados da planilha"""
        try:
            worksheet = self.spreadsheet.sheet1
            if range_name:
                return worksheet.get(range_name)
            return worksheet.get_all_values()
        except Exception as e:
            raise Exception(f"Erro ao ler planilha: {str(e)}")


# Função auxiliar para criar credenciais
def create_credentials_file(credentials_json: str, output_path: str = "credentials.json"):
    """
    Cria arquivo de credenciais a partir de JSON string
    
    Args:
        credentials_json: String JSON das credenciais do Google
        output_path: Caminho onde salvar o arquivo
    """
    import json
    from pathlib import Path
    
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        json.dump(json.loads(credentials_json), f, indent=2)
    
    return str(output_path)
