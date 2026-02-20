# Configurar Android SDK
$sdkPath = "$env:LOCALAPPDATA\Android\Sdk"

# Configurar ANDROID_HOME
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $sdkPath, 'User')
$env:ANDROID_HOME = $sdkPath
Write-Host "ANDROID_HOME configurado: $sdkPath"

# Configurar PATH
$platformTools = "$sdkPath\platform-tools"
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike "*$platformTools*") {
    [System.Environment]::SetEnvironmentVariable('Path', "$currentPath;$platformTools", 'User')
    Write-Host "PATH atualizado"
}

Write-Host "Feche e reabra o terminal, depois execute: flutter doctor"
