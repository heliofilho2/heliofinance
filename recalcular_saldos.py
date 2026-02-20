"""
Script para recalcular todos os saldos do mês atual
Útil para corrigir saldos que estão incorretos
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from services.google_sheets_breno import GoogleSheetsBreno

creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json')
spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

print("🔄 Recalculando saldos do mês atual...")
print()

try:
    service = GoogleSheetsBreno(spreadsheet_id, creds_path)
    
    now = datetime.now()
    month = now.month
    year = now.year
    
    col_offset = service._get_month_column_offset(month)
    col_entrada = col_offset + 1
    col_saida = col_offset + 2
    col_diario = col_offset + 3
    col_saldo = col_offset + 4
    
    # Calcular saldo inicial do mês
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    prev_col_offset = service._get_month_column_offset(prev_month)
    prev_col_saldo = prev_col_offset + 4
    
    # Último dia do mês anterior
    last_day_prev_month = (datetime(prev_year, prev_month + 1, 1) - timedelta(days=1)).day
    last_row_prev = service._get_day_row(last_day_prev_month)
    saldo_inicial = service._parse_currency(service._get_cell_value(last_row_prev, prev_col_saldo))
    
    print(f"💰 Saldo inicial do mês: {service._format_currency(saldo_inicial)}")
    print()
    
    # Recalcular saldos de todos os dias do mês
    current_saldo = saldo_inicial
    days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day
    
    for day in range(1, days_in_month + 1):
        row = service._get_day_row(day)
        
        # Ler valores do dia
        entrada = service._parse_currency(service._get_cell_value(row, col_entrada))
        saida = service._parse_currency(service._get_cell_value(row, col_saida))
        diario = service._parse_currency(service._get_cell_value(row, col_diario))
        
        # Calcular saldo do dia
        current_saldo = current_saldo + entrada - saida - diario
        
        # Atualizar saldo na planilha
        service._set_cell_value(row, col_saldo, service._format_currency(current_saldo))
        
        if day <= 5 or day == now.day or day >= days_in_month - 2:
            print(f"✅ Dia {day:2d}: Saldo = {service._format_currency(current_saldo)} "
                  f"(E:{entrada:,.0f} S:{saida:,.0f} D:{diario:,.0f})")
    
    print()
    print(f"🎉 Saldos recalculados com sucesso!")
    print(f"💰 Saldo final do mês: {service._format_currency(current_saldo)}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
