"""
Agendador de tarefas para envio automático de relatórios
"""
import schedule
import time
import asyncio
import os
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from bot.weekly_report_sender import send_weekly_report


def job():
    """Job agendado para enviar relatório"""
    print(f"⏰ Executando job agendado em {time.strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(send_weekly_report())


def main():
    """Inicia o agendador"""
    print("📅 Agendador de Relatórios Iniciado")
    print("📊 Relatórios serão enviados toda segunda-feira às 8h")
    
    # Agendar relatório semanal (toda segunda-feira às 8h)
    schedule.every().monday.at("08:00").do(job)
    
    # Para teste: também agendar para daqui a 1 minuto
    # schedule.every(1).minutes.do(job)
    
    print("✅ Agendamento configurado!")
    print("🔄 Aguardando horário agendado...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto


if __name__ == "__main__":
    main()
