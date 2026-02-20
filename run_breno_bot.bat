@echo off
echo 🤖 Iniciando Bot Telegram - Método Breno...
echo.

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Ambiente virtual ativado
) else (
    echo ⚠️  Virtual environment não encontrado. Usando Python global.
)

echo.
echo Executando bot...
python bot\breno_bot.py

pause
