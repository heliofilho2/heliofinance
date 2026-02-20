"""
Envia relatórios semanais automáticos via Telegram
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot
from telegram.constants import ParseMode
from app.database import get_db
from services.report_service import ReportService

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y"

# ID do chat (será configurado na primeira mensagem)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def format_currency(value: float) -> str:
    """Formata valor como moeda"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


async def send_weekly_report():
    """Envia relatório semanal completo"""
    if not CHAT_ID:
        print("⚠️  CHAT_ID não configurado. Use /setchatid no bot para configurar.")
        return
    
    db = next(get_db())
    report_service = ReportService(db)
    
    try:
        # Gerar relatório
        print("📊 Gerando relatório semanal...")
        report = report_service.generate_weekly_report()
        
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Mensagem inicial
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                f"📊 *RELATÓRIO SEMANAL*\n\n"
                f"Período: {report['week_start']} a {report['week_end']}\n"
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Dashboard resumido
        dashboard = report['dashboard']
        traffic_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }.get(dashboard['traffic_light']['status'], '⚪')
        
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                f"💰 *DASHBOARD ATUAL*\n\n"
                f"Saldo: {format_currency(dashboard['current_balance'])}\n"
                f"Performance do Mês: {format_currency(dashboard['month_performance'])}\n"
                f"Status: {traffic_emoji} {dashboard['traffic_light']['label']}\n"
                f"Comprometimento: {dashboard['commitment_ratio']:.1f}%\n"
                f"Entradas: {format_currency(dashboard['entradas'])}\n"
                f"Saídas: {format_currency(dashboard['saidas'])}"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Enviar gráficos
        print("📈 Enviando gráficos...")
        
        # Gráfico de saldo
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=report['charts']['balance_chart'],
            caption="📊 Evolução do Saldo - Semana"
        )
        
        # Gráfico de performance
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=report['charts']['performance_chart'],
            caption="📈 Performance Diária - Semana"
        )
        
        # Gráfico de categorias
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=report['charts']['categories_chart'],
            caption="🍰 Gastos por Categoria - Semana"
        )
        
        # Planilha da semana
        await bot.send_message(
            chat_id=CHAT_ID,
            text=report['spreadsheet'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        print("✅ Relatório enviado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar relatório: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Para testar manualmente
    asyncio.run(send_weekly_report())
