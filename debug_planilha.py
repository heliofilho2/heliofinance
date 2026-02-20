"""
Script para debugar leitura da planilha e comparar valores
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

# Configurar
creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json')
spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

print("🔍 Debug: Lendo dados da planilha...")
print()

try:
    service = GoogleSheetsBreno(spreadsheet_id, creds_path)
    
    # Obter dados do mês atual
    now = datetime.now()
    month = now.month
    day = now.day
    
    print(f"📅 Data atual: {day}/{month}/{now.year}")
    print()
    
    # Obter dados brutos
    month_data = service._get_current_month_data()
    
    print("📊 Dados lidos da planilha:")
    print(f"   Linha: {month_data['row']}")
    print(f"   Coluna Entrada: {month_data['col_entrada']}")
    print(f"   Coluna Saída: {month_data['col_saida']}")
    print(f"   Coluna Diário: {month_data['col_diario']}")
    print(f"   Coluna Saldo: {month_data['col_saldo']}")
    print()
    print(f"💰 Valores do dia {day}:")
    print(f"   Entrada: R$ {month_data['entrada']:,.2f}")
    print(f"   Saída: R$ {month_data['saida']:,.2f}")
    print(f"   Diário: R$ {month_data['diario']:,.2f}")
    print(f"   Saldo: R$ {month_data['saldo']:,.2f}")
    print()
    
    # Obter status
    status = service.obter_status_atual()
    
    print("📈 Status calculado:")
    print(f"   Saldo: R$ {status['saldo']:,.2f}")
    print(f"   Gasto Diário: R$ {status['gasto_diario']:,.2f}")
    print(f"   Entrada: R$ {status['entrada']:,.2f}")
    print(f"   Saída: R$ {status['saida']:,.2f}")
    print(f"   Performance: R$ {status['performance']:,.2f}")
    print(f"   Limite Diário: R$ {status['limite_diario']:,.2f}")
    print(f"   Semáforo: {status['semaforo']} {status['status']}")
    print()
    
    # Ler células diretamente para comparar
    print("🔍 Lendo células diretamente da planilha...")
    worksheet = service.worksheet
    
    # Ler linha do dia atual
    row = month_data['row'] + 1  # gspread é 1-indexed
    col_entrada = month_data['col_entrada'] + 1
    col_saida = month_data['col_saida'] + 1
    col_diario = month_data['col_diario'] + 1
    col_saldo = month_data['col_saldo'] + 1
    
    cell_entrada = worksheet.cell(row, col_entrada)
    cell_saida = worksheet.cell(row, col_saida)
    cell_diario = worksheet.cell(row, col_diario)
    cell_saldo = worksheet.cell(row, col_saldo)
    
    print(f"   Célula Entrada ({row}, {col_entrada}): '{cell_entrada.value}'")
    print(f"   Célula Saída ({row}, {col_saida}): '{cell_saida.value}'")
    print(f"   Célula Diário ({row}, {col_diario}): '{cell_diario.value}'")
    print(f"   Célula Saldo ({row}, {col_saldo}): '{cell_saldo.value}'")
    print()
    
    # Verificar se há valores acumulados no mês
    print("📊 Verificando valores acumulados do mês...")
    month_col_offset = service._get_month_column_offset(month)
    
    # Ler linha de totais (linha 37-38 do CSV que vimos antes)
    # Linha 37: ESTRUTURA (ENTRADAS, SAÍDAS, DIÁRIO)
    # Linha 38: TOTAIS DO MÊS
    
    # Tentar ler linha 38 (índice 37 em 0-based, mas gspread é 1-based, então linha 38)
    try:
        total_row = 38
        total_entrada = worksheet.cell(total_row, month_col_offset + 2).value  # Coluna Entrada
        total_saida = worksheet.cell(total_row, month_col_offset + 3).value      # Coluna Saída
        total_diario = worksheet.cell(total_row, month_col_offset + 4).value    # Coluna Diário
        
        print(f"   Totais do mês (linha {total_row}):")
        print(f"   Entrada Total: '{total_entrada}'")
        print(f"   Saída Total: '{total_saida}'")
        print(f"   Diário Total: '{total_diario}'")
    except Exception as e:
        print(f"   ⚠️  Erro ao ler totais: {e}")
    
    print()
    print("💡 Compare os valores acima com o que você vê na planilha.")
    print("   Se houver diferença, pode ser:")
    print("   1. O código está lendo a célula errada")
    print("   2. O formato da planilha mudou")
    print("   3. Os valores acumulados estão em outro lugar")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
