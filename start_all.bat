@echo off
echo ========================================
echo  Sistema de Gestao Financeira - Breno
echo ========================================
echo.
echo Iniciando API e Bot...
echo.

REM Configurar token
set TELEGRAM_BOT_TOKEN=8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y
set API_URL=http://localhost:8000

echo [1/2] Iniciando API FastAPI...
start "API - FastAPI" cmd /k "python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Bot Telegram...
start "Bot - Telegram" cmd /k "python bot/telegram_bot.py"

echo.
echo ========================================
echo  Sistema iniciado!
echo ========================================
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Abra o Telegram e teste seu bot!
echo.
pause
