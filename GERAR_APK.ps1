# Script para gerar APK do Flutter
Write-Host "📱 Gerando APK do App Flutter..." -ForegroundColor Green

# Verificar se Flutter está instalado
$flutterCheck = flutter --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Flutter não encontrado!" -ForegroundColor Red
    Write-Host "💡 Instale o Flutter: https://flutter.dev/docs/get-started/install" -ForegroundColor Yellow
    exit 1
}

# Navegar para diretório do app
Set-Location flutter_app

# Verificar configuração
Write-Host "🔍 Verificando configuração do Flutter..." -ForegroundColor Yellow
flutter doctor

# Limpar build anterior
Write-Host "🧹 Limpando build anterior..." -ForegroundColor Yellow
flutter clean

# Obter dependências
Write-Host "📦 Obtendo dependências..." -ForegroundColor Yellow
flutter pub get

# Verificar se API está configurada
Write-Host "🔍 Verificando configuração da API..." -ForegroundColor Yellow
$apiConfig = Get-Content "lib\config\api_config.dart" -Raw
if ($apiConfig -match "localhost:8000") {
    Write-Host "⚠️  ATENÇÃO: API configurada para localhost!" -ForegroundColor Yellow
    Write-Host "💡 Configure a URL da API em lib\config\api_config.dart antes de gerar o APK" -ForegroundColor Yellow
    $continuar = Read-Host "Deseja continuar mesmo assim? (s/N)"
    if ($continuar -ne "s" -and $continuar -ne "S") {
        Write-Host "❌ Geração cancelada" -ForegroundColor Red
        exit 1
    }
}

# Gerar APK
Write-Host "🔨 Gerando APK de release..." -ForegroundColor Green
flutter build apk --release

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ APK gerado com sucesso!" -ForegroundColor Green
    Write-Host "📁 Localização: flutter_app\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Cyan
    
    # Perguntar se quer instalar
    $instalar = Read-Host "Deseja instalar no dispositivo conectado? (s/N)"
    if ($instalar -eq "s" -or $instalar -eq "S") {
        Write-Host "📲 Instalando no dispositivo..." -ForegroundColor Yellow
        flutter install
    }
} else {
    Write-Host "❌ Erro ao gerar APK" -ForegroundColor Red
    exit 1
}

# Voltar para diretório raiz
Set-Location ..
