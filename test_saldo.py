"""
Script para testar e debugar cálculo de saldo
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from services.google_sheets_breno import GoogleSheetsBreno

creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json')
spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

print("🔍 Debug: Testando cálculo de saldo...")
print()

try:
    service = GoogleSheetsBreno(spreadsheet_id, creds_path)
    
    now = datetime.now()
    month = now.month
    day = now.day
    
    print(f"📅 Data atual: {day}/{month}/{now.year}")
    print()
    
    # Obter dados do mês atual
    month_data = service._get_current_month_data()
    
    print("📊 Dados do dia atual:")
    print(f"   Linha: {month_data['row']}")
    print(f"   Entrada: R$ {month_data['entrada']:,.2f}")
    print(f"   Saída: R$ {month_data['saida']:,.2f}")
    print(f"   Diário: R$ {month_data['diario']:,.2f}")
    print(f"   Saldo: R$ {month_data['saldo']:,.2f}")
    print()
    
    # Calcular saldo esperado
    saldo_anterior = service._calculate_saldo(month_data)
    print(f"💰 Saldo anterior (calculado): R$ {saldo_anterior:,.2f}")
    
    # Saldo esperado = saldo anterior + entrada - saída - diário
    saldo_esperado = saldo_anterior + month_data['entrada'] - month_data['saida'] - month_data['diario']
    print(f"💰 Saldo esperado: R$ {saldo_esperado:,.2f}")
    print(f"💰 Saldo atual (na planilha): R$ {month_data['saldo']:,.2f}")
    print()
    
    if abs(saldo_esperado - month_data['saldo']) > 0.01:
        print("❌ PROBLEMA IDENTIFICADO!")
        print(f"   Diferença: R$ {abs(saldo_esperado - month_data['saldo']):,.2f}")
        print()
        print("💡 O saldo na planilha não está correto.")
        print("   Vou recalcular e atualizar...")
        print()
        
        # Recalcular saldo do dia atual
        novo_saldo = saldo_esperado
        service._set_cell_value(month_data['row'], month_data['col_saldo'], service._format_currency(novo_saldo))
        print(f"✅ Saldo do dia atual atualizado para: R$ {novo_saldo:,.2f}")
        
        # Atualizar saldos dos dias seguintes
        service._update_saldo(month_data, novo_saldo)
        print("✅ Saldos dos dias seguintes atualizados")
        
    else:
        print("✅ Saldo está correto!")
    
    # Verificar saldo do dia anterior
    if day > 1:
        prev_row = service._get_day_row(day - 1)
        prev_saldo = service._parse_currency(service._get_cell_value(prev_row, month_data['col_saldo']))
        print()
        print(f"📊 Saldo do dia anterior ({day - 1}): R$ {prev_saldo:,.2f}")
        
        # Verificar se o cálculo está correto
        prev_entrada = service._parse_currency(service._get_cell_value(prev_row, month_data['col_entrada']))
        prev_saida = service._parse_currency(service._get_cell_value(prev_row, month_data['col_saida']))
        prev_diario = service._parse_currency(service._get_cell_value(prev_row, month_data['col_diario']))
        
        print(f"   Entrada dia {day - 1}: R$ {prev_entrada:,.2f}")
        print(f"   Saída dia {day - 1}: R$ {prev_saida:,.2f}")
        print(f"   Diário dia {day - 1}: R$ {prev_diario:,.2f}")
        
        if day > 2:
            prev2_row = service._get_day_row(day - 2)
            prev2_saldo = service._parse_currency(service._get_cell_value(prev2_row, month_data['col_saldo']))
            saldo_esperado_prev = prev2_saldo + prev_entrada - prev_saida - prev_diario
            
            print()
            print(f"📊 Saldo do dia {day - 2}: R$ {prev2_saldo:,.2f}")
            print(f"💰 Saldo esperado dia {day - 1}: R$ {saldo_esperado_prev:,.2f}")
            print(f"💰 Saldo atual dia {day - 1}: R$ {prev_saldo:,.2f}")
            
            if abs(saldo_esperado_prev - prev_saldo) > 0.01:
                print(f"❌ Saldo do dia {day - 1} também está incorreto!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
