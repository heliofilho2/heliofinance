@echo off
echo ⏰ Iniciando Agendador de Lembretes...
echo.

cd /d "%~dp0"

if exist "venv\Scripts\Activate.ps1" (
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment não encontrado. Usando Python global.
)

python bot\scheduler_breno.py

pause
