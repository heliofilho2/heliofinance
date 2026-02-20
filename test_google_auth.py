"""
Script de teste para verificar autenticação Google Sheets
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

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    
    print("✅ Bibliotecas importadas com sucesso")
    print()
    
    # Verificar variável de ambiente
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    if not creds_path:
        print("❌ GOOGLE_CREDENTIALS_PATH não configurado!")
        print("Configure com: $env:GOOGLE_CREDENTIALS_PATH='caminho/para/credentials.json'")
        sys.exit(1)
    
    print(f"📁 Caminho das credenciais: {creds_path}")
    
    # Verificar se arquivo existe
    if not os.path.exists(creds_path):
        print(f"❌ Arquivo não encontrado: {creds_path}")
        sys.exit(1)
    
    print("✅ Arquivo de credenciais encontrado")
    print()
    
    # Verificar formato do arquivo
    try:
        import json
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Campos obrigatórios faltando: {', '.join(missing_fields)}")
            sys.exit(1)
        
        print("✅ Formato do arquivo JSON válido")
        print(f"   Tipo: {creds_data.get('type')}")
        print(f"   Project ID: {creds_data.get('project_id')}")
        print(f"   Client Email: {creds_data.get('client_email')}")
        print()
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        sys.exit(1)
    
    # Verificar relógio do sistema
    print("🕐 Verificando relógio do sistema...")
    now = datetime.now()
    print(f"   Data/Hora atual: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tentar autenticar
    print()
    print("🔐 Tentando autenticar...")
    
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=scope
        )
        
        print("✅ Credenciais carregadas")
        
        # Tentar autorizar gspread
        client = gspread.authorize(creds)
        print("✅ Cliente gspread autorizado")
        
        # Tentar abrir planilha
        spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"
        print(f"📊 Tentando abrir planilha: {spreadsheet_id}")
        
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            print(f"✅ Planilha aberta: {spreadsheet.title}")
        except gspread.exceptions.APIError as e:
            if "PERMISSION_DENIED" in str(e) or "permission" in str(e).lower():
                print(f"❌ Erro de permissão: {e}")
                print()
                print("🔧 SOLUÇÃO:")
                print(f"1. Abra sua planilha no Google Sheets")
                print(f"2. Clique em 'Compartilhar' (canto superior direito)")
                print(f"3. Adicione este email: {creds_data.get('client_email')}")
                print(f"4. Dê permissão de 'Editor'")
                print(f"5. Clique em 'Enviar'")
                sys.exit(1)
            else:
                raise
        
        # Verificar permissões
        print()
        print("🔍 Verificando permissões...")
        worksheet = spreadsheet.sheet1
        print(f"✅ Acesso à primeira aba: {worksheet.title}")
        
        # Tentar ler uma célula
        try:
            cell_value = worksheet.cell(1, 1).value
            print(f"✅ Leitura de célula bem-sucedida: '{cell_value}'")
        except Exception as e:
            print(f"⚠️  Erro ao ler célula: {e}")
        
        print()
        print("🎉 Tudo funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro durante autenticação: {e}")
        print()
        print("💡 Possíveis soluções:")
        print("1. Verifique se o relógio do sistema está correto")
        print("2. Verifique se a service account tem acesso à planilha")
        print("3. Gere novas credenciais no Google Cloud Console")
        print("4. Compartilhe a planilha com o email da service account")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Erro ao importar bibliotecas: {e}")
    print("Instale com: pip install gspread google-auth")
    sys.exit(1)
