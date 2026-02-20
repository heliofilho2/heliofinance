# Script para limpar cache do Gradle e liberar espaço
Write-Host "🧹 Limpando cache do Gradle..." -ForegroundColor Cyan

$gradleCache = "$env:USERPROFILE\.gradle\caches"
$gradleDaemon = "$env:USERPROFILE\.gradle\daemon"

if (Test-Path $gradleCache) {
    $sizeBefore = (Get-ChildItem $gradleCache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "📊 Tamanho atual do cache: $([math]::Round($sizeBefore, 2)) GB" -ForegroundColor Yellow
    
    Write-Host "🗑️  Removendo cache..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $gradleCache -ErrorAction SilentlyContinue
    Write-Host "✅ Cache removido" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Cache não encontrado" -ForegroundColor Gray
}

if (Test-Path $gradleDaemon) {
    Write-Host "🛑 Parando daemons do Gradle..." -ForegroundColor Yellow
    Get-ChildItem $gradleDaemon -Directory | ForEach-Object {
        $stopFile = Join-Path $_.FullName "stop"
        if (-not (Test-Path $stopFile)) {
            New-Item -ItemType File -Path $stopFile -Force | Out-Null
        }
    }
}

Write-Host ""
Write-Host "✅ Limpeza concluída!" -ForegroundColor Green
Write-Host "💡 Agora tente gerar o APK novamente" -ForegroundColor Cyan
