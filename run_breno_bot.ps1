# Script PowerShell para iniciar o Bot Breno
Write-Host "🤖 Iniciando Bot Telegram - Método Breno..." -ForegroundColor Cyan
Write-Host ""

# Mudar para diretório do script
Set-Location $PSScriptRoot

# Ativar ambiente virtual
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Ativando ambiente virtual..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment não encontrado. Usando Python global." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Executando bot..." -ForegroundColor Cyan
Write-Host ""

# Executar bot
python bot\breno_bot.py
