@echo off
echo Configurando token do bot...
set TELEGRAM_BOT_TOKEN=8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y
set API_URL=http://localhost:8000
echo.
echo Iniciando Bot Telegram...
python bot/telegram_bot.py
pause
