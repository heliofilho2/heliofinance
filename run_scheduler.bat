@echo off
echo Iniciando Agendador de Relatorios Semanais...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python scheduler.py
pause
