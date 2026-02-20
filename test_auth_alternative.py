"""
Teste alternativo de autenticação - tenta diferentes abordagens
"""
import os
import sys
from pathlib import Path
import json

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    
    print("✅ Bibliotecas importadas")
    print()
    
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    if not creds_path:
        print("❌ GOOGLE_CREDENTIALS_PATH não configurado")
        sys.exit(1)
    
    print(f"📁 Carregando credenciais: {creds_path}")
    
    # Ler arquivo JSON
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
    
    # Verificar chave privada
    private_key = creds_data.get('private_key', '')
    if not private_key:
        print("❌ Chave privada não encontrada no JSON")
        sys.exit(1)
    
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("⚠️  Formato da chave privada pode estar incorreto")
    
    print("✅ Chave privada encontrada")
    print()
    
    # Tentar abordagem 1: Credenciais diretas
    print("🔐 Tentativa 1: Autenticação direta...")
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(
            creds_data,
            scopes=scope
        )
        
        # Forçar refresh do token
        if not creds.valid:
            creds.refresh(Request())
        
        print("✅ Token gerado com sucesso")
        
        # Tentar autorizar
        client = gspread.authorize(creds)
        print("✅ Cliente autorizado")
        
        # Tentar abrir planilha
        spreadsheet_id = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✅ Planilha aberta: {spreadsheet.title}")
        print()
        print("🎉 SUCESSO! Autenticação funcionando!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()
        print("💡 SOLUÇÃO: Gere novas credenciais")
        print()
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Vá em 'IAM & Admin' > 'Service Accounts'")
        print("3. Clique na service account: bot-financeiro")
        print("4. Vá em 'Keys' > 'Add Key' > 'Create new key'")
        print("5. Escolha 'JSON' e baixe")
        print("6. Substitua o arquivo google-credentials.json")
        print()
        print("⚠️  IMPORTANTE: Revogue a chave antiga após criar a nova!")
        
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)
