# Script para configurar Android SDK no Windows
Write-Host "Configurando Android SDK..." -ForegroundColor Cyan

# Caminhos possiveis do SDK
$possiblePaths = @(
    "$env:LOCALAPPDATA\Android\Sdk",
    "$env:USERPROFILE\AppData\Local\Android\Sdk",
    "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk",
    "D:\AppData\Local\Android\Sdk"
)

$sdkPath = $null

# Procurar SDK
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $sdkPath = $path
        Write-Host "[OK] SDK encontrado em: $sdkPath" -ForegroundColor Green
        break
    }
}

if (-not $sdkPath) {
    Write-Host "[ERRO] Android SDK nao encontrado!" -ForegroundColor Red
    Write-Host "[INFO] Instale o Android Studio ou configure o SDK manualmente" -ForegroundColor Yellow
    exit 1
}

# Configurar variavel de ambiente permanente
try {
    [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $sdkPath, 'User')
    Write-Host "[OK] ANDROID_HOME configurado permanentemente" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Nao foi possivel configurar permanentemente. Configure manualmente:" -ForegroundColor Yellow
    Write-Host "   ANDROID_HOME = $sdkPath" -ForegroundColor Cyan
}

# Configurar para sessao atual
$env:ANDROID_HOME = $sdkPath
$env:PATH = "$sdkPath\platform-tools;$sdkPath\tools;$sdkPath\tools\bin;$env:PATH"

Write-Host ""
Write-Host "[OK] Configuracao concluida!" -ForegroundColor Green
Write-Host "ANDROID_HOME: $env:ANDROID_HOME" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] IMPORTANTE: Feche e reabra o terminal para aplicar as mudancas permanentes" -ForegroundColor Yellow
Write-Host "[INFO] Ou execute este script antes de gerar o APK" -ForegroundColor Yellow
