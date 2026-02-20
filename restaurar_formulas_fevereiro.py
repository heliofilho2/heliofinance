"""
Script para restaurar fórmulas de saldo em fevereiro
A planilha deve ter fórmulas como: =(B3)-(C3+D3) para calcular saldo
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

import gspread
from google.oauth2.service_account import Credentials

creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json')
spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

print("🔧 Restaurando fórmulas de saldo em fevereiro...")
print()

try:
    # Autenticar
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.sheet1
    
    # Fevereiro = mês 2
    # Cada mês ocupa 6 colunas: Data=0, Entrada=1, Saída=2, Diário=3, Saldo=4
    month = 2
    col_offset = (month - 1) * 6
    col_entrada = col_offset + 1  # Coluna B (1-indexed no gspread)
    col_saida = col_offset + 2    # Coluna C
    col_diario = col_offset + 3   # Coluna D
    col_saldo = col_offset + 4    # Coluna E
    
    # Linha 2 = cabeçalho, Linha 3 = dia 1
    # Para cada dia (1 a 31)
    formulas_restauradas = 0
    
    for day in range(1, 32):
        row = day + 2  # Linha 3 = dia 1 (gspread é 1-indexed)
        
        if day == 1:
            # Dia 1: Saldo anterior (último dia do mês anterior) + Entrada - Saída - Diário
            # Para fevereiro, o saldo anterior está no último dia de janeiro (linha 33 = dia 31)
            # Coluna de saldo de janeiro = col_offset - 2 (6 colunas antes, saldo é +4)
            prev_month_col_saldo = col_offset - 2  # Coluna E de janeiro
            prev_row = 33  # Último dia de janeiro
            # Fórmula: =E33+B3-C3-D3 (saldo anterior + entrada - saída - diário)
            formula = f"=E{prev_row}+B{row}-C{row}-D{row}"
        else:
            # Dias seguintes: Saldo do dia anterior + Entrada - Saída - Diário
            prev_row = row - 1
            # Fórmula: =E_prev_row+B_row-C_row-D_row
            formula = f"=E{prev_row}+B{row}-C{row}-D{row}"
        
        # Atualizar célula com fórmula
        try:
            worksheet.update_cell(row, col_saldo + 1, formula)  # +1 porque gspread é 1-indexed
            formulas_restauradas += 1
            
            if day <= 5 or day >= 28:
                print(f"✅ Dia {day:2d}: Fórmula restaurada: {formula}")
        except Exception as e:
            print(f"⚠️  Dia {day:2d}: Erro ao restaurar fórmula: {e}")
    
    print()
    print(f"🎉 {formulas_restauradas} fórmulas restauradas com sucesso!")
    print()
    print("💡 Agora a planilha calculará os saldos automaticamente.")
    print("   O bot não vai mais sobrescrever as fórmulas!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
