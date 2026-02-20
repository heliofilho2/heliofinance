@echo off
echo Iniciando API FastAPI...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
