"""
Agendador de lembretes para o Bot Breno
"""
import schedule
import time
import asyncio
from pathlib import Path
import sys
import os
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot
from services.google_sheets_breno import GoogleSheetsBreno
from services.alert_service import AlertService
from services.report_service import ReportService

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y"

SPREADSHEET_ID = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

bot = Bot(token=TELEGRAM_TOKEN)


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


async def job_lembrete_20h():
    """Job para lembrete das 20h"""
    try:
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            print("⚠️  GOOGLE_CREDENTIALS_PATH não configurado")
            return
        
        service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
        status = service.obter_status_atual()
        
        gasto_diario = status.get('gasto_diario', 0)
        saldo = status.get('saldo', 0)
        semaforo = status.get('semaforo', '🟢')
        
        msg = (
            f"🔔 *Lembrete - Fechamento do Dia*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Não esqueça de registrar os gastos de hoje!\n\n"
            f"📅 *Gasto hoje:* {format_currency(gasto_diario)}\n"
            f"💰 *Saldo atual:* {format_currency(saldo)}\n"
            f"{semaforo} *Status:* {status.get('status_text', 'OK')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Use `/gasto` para registrar gastos restantes.\n"
            f"Se não gastou nada, não precisa fazer nada - zerarei automaticamente! ✨"
        )
        
        # Enviar para todos os chats salvos
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        if chat_id_file.exists():
            with open(chat_id_file, 'r') as f:
                chat_id = f.read().strip()
                if chat_id:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                    print(f"✅ Lembrete enviado para {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar lembrete: {e}")


async def job_resumo_matinal():
    """Job para resumo matinal às 8h com alertas"""
    try:
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            print("⚠️  GOOGLE_CREDENTIALS_PATH não configurado")
            return
        
        service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
        alert_service = AlertService(service)
        
        status = service.obter_status_atual()
        alertas = alert_service.verificar_alertas()
        
        saldo = status.get('saldo', 0)
        performance = status.get('performance', 0)
        limite_diario = status.get('limite_diario', 0)
        
        msg = (
            f"🌅 *Bom Dia! Que seu dia seja próspero!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Saldo atual:*\n"
            f"{format_currency(saldo)}\n\n"
            f"📊 *Performance do mês:*\n"
            f"{format_currency(performance)}\n\n"
        )
        
        if limite_diario > 0:
            msg += (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *Limite diário sugerido:*\n"
                f"*{format_currency(limite_diario)}*\n\n"
                f"💡 Para manter a planilha no verde até o fim do mês.\n"
            )
        else:
            msg += (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Use `/status` para ver seu limite diário sugerido.\n"
            )
        
        # Adicionar alertas importantes
        if alertas:
            alertas_altos = [a for a in alertas if a.get('prioridade') == 'alta']
            if alertas_altos:
                msg += "\n━━━━━━━━━━━━━━━━━━━━\n"
                msg += "⚠️ *ALERTAS IMPORTANTES*\n"
                msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
                for alerta in alertas_altos[:2]:  # Máximo 2 alertas
                    msg += f"{alerta.get('emoji', '⚠️')} {alerta.get('titulo', 'Alerta')}\n"
                msg += "\n💡 Use `/alertas` para ver todos os alertas.\n"
        
        # Enviar para todos os chats salvos
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        if chat_id_file.exists():
            with open(chat_id_file, 'r') as f:
                chat_id = f.read().strip()
                if chat_id:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                    print(f"✅ Resumo matinal enviado para {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar resumo matinal: {e}")


async def job_relatorio_semanal():
    """Job para enviar relatório semanal (domingos às 9h)"""
    try:
        from datetime import datetime
        now = datetime.now()
        
        # Só enviar aos domingos
        if now.weekday() != 6:  # 6 = domingo
            return
        
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            print("⚠️  GOOGLE_CREDENTIALS_PATH não configurado")
            return
        
        service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
        report_service = ReportService(service)
        
        relatorio = report_service.gerar_relatorio_semanal()
        
        if not relatorio.get('sucesso'):
            print(f"❌ Erro ao gerar relatório semanal: {relatorio.get('erro')}")
            return
        
        periodo = relatorio.get('periodo', {})
        top_5 = relatorio.get('top_5_gastos', [])
        economia = relatorio.get('economia_vs_previsto', 0)
        performance = relatorio.get('performance_semana', 0)
        
        msg = (
            f"📊 *Relatório Semanal Automático*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Período:*\n"
            f"{periodo.get('inicio')} a {periodo.get('fim')}\n\n"
        )
        
        if top_5:
            msg += f"🏆 *Top 5 Gastos da Semana:*\n"
            for i, gasto in enumerate(top_5, 1):
                msg += f"{i}. {format_currency(gasto['valor'])} - {gasto['dia']}\n"
            msg += "\n"
        
        msg += (
            f"💰 *Economia vs Previsto:*\n"
            f"{format_currency(economia)}\n\n"
            f"📈 *Performance da Semana:*\n"
            f"{format_currency(performance)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Use `/relatorio` para relatório mensal completo!"
        )
        
        # Enviar para todos os chats salvos
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        if chat_id_file.exists():
            with open(chat_id_file, 'r') as f:
                chat_id = f.read().strip()
                if chat_id:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                    print(f"✅ Relatório semanal enviado para {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar relatório semanal: {e}")


async def job_verificar_alertas():
    """Job para verificar e enviar alertas (a cada 6 horas)"""
    try:
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            return
        
        service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
        alert_service = AlertService(service)
        
        alertas = alert_service.verificar_alertas()
        
        # Filtrar apenas alertas de alta prioridade
        alertas_altos = [a for a in alertas if a.get('prioridade') == 'alta']
        
        if not alertas_altos:
            return
        
        # Enviar apenas 1 alerta por vez para não spammar
        alerta = alertas_altos[0]
        
        msg = (
            f"{alerta.get('emoji', '⚠️')} *{alerta.get('titulo', 'Alerta')}*\n\n"
            f"{alerta.get('mensagem', '')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Use `/alertas` para ver todos os alertas ativos."
        )
        
        # Enviar para todos os chats salvos
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        if chat_id_file.exists():
            with open(chat_id_file, 'r') as f:
                chat_id = f.read().strip()
                if chat_id:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                    print(f"✅ Alerta enviado para {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao verificar alertas: {e}")


async def job_zerar_diarios_nao_registrados():
    """Job para zerar diários não registrados do dia anterior (00:05)"""
    try:
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            print("⚠️  GOOGLE_CREDENTIALS_PATH não configurado")
            return
        
        service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
        result = service.zerar_diarios_nao_registrados_ontem()
        
        if result.get('sucesso'):
            if result.get('zerado'):
                print(f"✅ Diário do dia {result.get('dia')} zerado automaticamente")
                
                # Notificar usuário (opcional)
                chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
                if chat_id_file.exists():
                    with open(chat_id_file, 'r') as f:
                        chat_id = f.read().strip()
                        if chat_id:
                            msg = (
                                f"✅ *Diário Zerado Automaticamente*\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"💡 Não houve registro de gastos ontem.\n"
                                f"Diário do dia {result.get('dia')} foi zerado automaticamente.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"💰 *Saldo ajustado:*\n"
                                f"*{format_currency(result.get('novo_saldo', 0))}*\n\n"
                                f"✨ Tudo certo! Continue assim!"
                            )
                            await bot.send_message(
                                chat_id=chat_id,
                                text=msg,
                                parse_mode='Markdown'
                            )
            else:
                print(f"ℹ️  Diário do dia {result.get('dia')} já foi alterado: {result.get('mensagem')}")
        else:
            print(f"❌ Erro ao zerar diário: {result.get('erro')}")
    except Exception as e:
        print(f"❌ Erro ao zerar diários não registrados: {e}")


def run_async(coro):
    """Executa corrotina"""
    asyncio.run(coro)


def main():
    """Inicializa agendador"""
    print("⏰ Iniciando agendador de lembretes e relatórios...")
    
    # Lembrete às 20h
    schedule.every().day.at("20:00").do(lambda: run_async(job_lembrete_20h()))
    
    # Resumo matinal às 8h (com alertas)
    schedule.every().day.at("08:00").do(lambda: run_async(job_resumo_matinal()))
    
    # Zerar diários não registrados às 00:05 (início do novo dia)
    schedule.every().day.at("00:05").do(lambda: run_async(job_zerar_diarios_nao_registrados()))
    
    # Relatório semanal aos domingos às 9h
    schedule.every().sunday.at("09:00").do(lambda: run_async(job_relatorio_semanal()))
    
    # Verificar alertas a cada 6 horas
    schedule.every(6).hours.do(lambda: run_async(job_verificar_alertas()))
    
    print("✅ Agendador iniciado!")
    print("   - Lembrete: 20:00")
    print("   - Resumo matinal: 08:00")
    print("   - Zerar diários não registrados: 00:05")
    print("   - Relatório semanal: Domingos 09:00")
    print("   - Verificação de alertas: A cada 6 horas")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto


if __name__ == "__main__":
    main()
