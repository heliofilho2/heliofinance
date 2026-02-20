# Script para iniciar API Google Sheets
Write-Host "🚀 Iniciando API Google Sheets para Flutter..." -ForegroundColor Green

# Ativar venv se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    
    # Verificar se as dependências estão instaladas
    Write-Host "🔍 Verificando dependências..." -ForegroundColor Yellow
    $gspread = python -c "import gspread; print('OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Instalando dependências faltantes..." -ForegroundColor Yellow
        pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 fastapi uvicorn[standard] pandas matplotlib schedule
    }
} else {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "💡 Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 fastapi uvicorn[standard] pandas matplotlib schedule
}

# Verificar se arquivo .env existe, se não, criar
if (-not (Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Yellow
    "GOOGLE_CREDENTIALS_PATH=google-credentials.json" | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
}

# Verificar se GOOGLE_CREDENTIALS_PATH está configurado
if (-not $env:GOOGLE_CREDENTIALS_PATH) {
    Write-Host "ℹ️  GOOGLE_CREDENTIALS_PATH não configurado na variável de ambiente" -ForegroundColor Yellow
    Write-Host "💡 Usando arquivo .env ou padrão (google-credentials.json)" -ForegroundColor Yellow
}

# Iniciar API
Write-Host "🌐 Iniciando servidor na porta 8000..." -ForegroundColor Green
python api/api_google_sheets.py
