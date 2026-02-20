# Script PowerShell para iniciar o Agendador de Lembretes
Write-Host "⏰ Iniciando Agendador de Lembretes..." -ForegroundColor Cyan
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
Write-Host "🚀 Executando agendador..." -ForegroundColor Cyan
Write-Host ""

# Executar agendador
python bot\scheduler_breno.py
