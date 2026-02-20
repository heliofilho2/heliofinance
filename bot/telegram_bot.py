"""
Bot Telegram para registro rápido de transações
"""
import asyncio
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.parser import CommandParser
import httpx


# Configuração
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Fallback: tentar ler de arquivo .env ou usar token hardcoded para desenvolvimento
if not TELEGRAM_TOKEN:
    # Tentar ler de arquivo .env se existir
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    TELEGRAM_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

# Token hardcoded para desenvolvimento (REMOVER EM PRODUÇÃO)
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y"
    print("⚠️  Usando token hardcoded (apenas para desenvolvimento)")

API_URL = os.getenv("API_URL", "http://localhost:8000")

parser = CommandParser()


def format_currency(value: float) -> str:
    """Formata valor como moeda"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


async def get_dashboard_summary() -> str:
    """Busca resumo do dashboard da API"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_URL}/api/dashboard")
            if response.status_code == 200:
                data = response.json()
                
                balance = data.get('current_balance', 0)
                perf = data.get('month_performance', {}).get('performance', 0)
                traffic = data.get('traffic_light', {})
                commitment = data.get('commitment', {}).get('ratio', 0)
                
                return (
                    f"💰 *Resumo Financeiro*\n\n"
                    f"Saldo: {format_currency(balance)}\n"
                    f"Performance: {format_currency(perf)}\n"
                    f"Status: {traffic.get('label', 'N/A')}\n"
                    f"Comprometimento: {commitment:.1f}%"
                )
            else:
                return f"Erro na API: {response.status_code}"
    except httpx.ConnectError:
        return "❌ API não está rodando. Inicie a API primeiro."
    except Exception as e:
        return f"Erro: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text(
        "💰 *Gestão Financeira - Método Breno*\n\n"
        "Comandos disponíveis:\n"
        "• /start - Iniciar bot\n"
        "• /resumo - Ver resumo financeiro\n"
        "• /relatorio - Gerar relatório semanal completo\n"
        "• /sincronizar - Sincronizar com Google Sheets\n"
        "• /setchatid - Configurar envio automático de relatórios\n"
        "• /help - Ajuda\n\n"
        "Registre transações digitando:\n"
        "• mercado 87\n"
        "• recebi cliente 2500\n"
        "• aluguel 1200\n"
        "• simular emprestimo 10000 18 0.02",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    await update.message.reply_text(
        "📖 *Ajuda*\n\n"
        "*Gastos:*\n"
        "• mercado 87\n"
        "• uber 25\n"
        "• aluguel 1200\n\n"
        "*Receitas:*\n"
        "• recebi cliente 2500\n"
        "• recebi projeto 5000\n\n"
        "*Simulações:*\n"
        "• simular emprestimo 10000 18 0.02\n"
        "• simular compra notebook 4200 10",
        parse_mode='Markdown'
    )


async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resumo"""
    summary = await get_dashboard_summary()
    await update.message.reply_text(summary, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de comando"""
    command = update.message.text
    
    parsed = parser.parse(command)
    
    if not parsed:
        await update.message.reply_text(
            "❌ Comando não reconhecido.\n"
            "Use /help para ver exemplos."
        )
        return
    
    # Se for simulação, mostrar detalhes
    if parsed.get('type') == 'loan_simulation':
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/api/simulate/loan",
                    json={
                        "value": parsed['value'],
                        "monthly_rate": parsed['monthly_rate'],
                        "term": parsed['term']
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    await update.message.reply_text(
                        f"💳 *Simulação de Empréstimo*\n\n"
                        f"Valor: {format_currency(data['value'])}\n"
                        f"Parcela: {format_currency(data['installment'])}\n"
                        f"Total: {format_currency(data['total_payable'])}\n"
                        f"Novo comprometimento: {data['impact']['new_commitment_ratio']:.1f}%\n\n"
                        f"Use /confirmar {data['group_id']} para confirmar",
                        parse_mode='Markdown'
                    )
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
        return
    
    if parsed.get('type') == 'purchase_simulation':
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/api/simulate/installment",
                    json={
                        "description": parsed['description'],
                        "value": parsed['value'],
                        "installments": parsed['installments']
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    await update.message.reply_text(
                        f"🛒 *Simulação de Compra*\n\n"
                        f"{data['description']}\n"
                        f"Valor: {format_currency(data['value'])}\n"
                        f"Parcela: {format_currency(data['installment_value'])}\n"
                        f"Parcelas: {data['installments']}x\n\n"
                        f"Use /confirmar {data['group_id']} para confirmar",
                        parse_mode='Markdown'
                    )
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
        return
    
    # Transação normal
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{API_URL}/api/transactions/quick",
                params={"command": command}
            )
            
            if response.status_code == 200:
                data = response.json()
                transaction = data.get('transaction', {})
                
                tipo = "Receita" if transaction.get('amount', 0) > 0 else "Despesa"
                
                # Buscar resumo atualizado
                summary = await get_dashboard_summary()
                
                await update.message.reply_text(
                    f"✅ *{tipo} registrada*\n\n"
                    f"{transaction.get('description', '')}: {format_currency(abs(transaction.get('amount', 0)))}\n\n"
                    f"{summary}",
                    parse_mode='Markdown'
                )
            else:
                error_text = response.text
                try:
                    error_json = response.json()
                    error_text = error_json.get('detail', error_text)
                except:
                    pass
                await update.message.reply_text(f"❌ Erro ao registrar: {error_text}")
    except httpx.ConnectError:
        await update.message.reply_text(
            "❌ Erro: Não foi possível conectar à API.\n"
            "Verifique se a API está rodando em http://localhost:8000"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /confirmar <group_id>"""
    if not context.args:
        await update.message.reply_text("Use: /confirmar <id>")
        return
    
    try:
        group_id = int(context.args[0])
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/simulate/{group_id}/confirm")
            if response.status_code == 200:
                await update.message.reply_text("✅ Simulação confirmada!")
                summary = await get_dashboard_summary()
                await update.message.reply_text(summary, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Erro: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /relatorio - Gera e envia relatório semanal"""
    await update.message.reply_text("📊 Gerando relatório semanal... Aguarde...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from services.report_service import ReportService
        from app.database import get_db
        
        db = next(get_db())
        report_service = ReportService(db)
        report = report_service.generate_weekly_report()
        
        # Dashboard
        dashboard = report['dashboard']
        traffic_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }.get(dashboard['traffic_light']['status'], '⚪')
        
        await update.message.reply_text(
            f"📊 *RELATÓRIO SEMANAL*\n\n"
            f"Período: {report['week_start']} a {report['week_end']}\n\n"
            f"💰 *DASHBOARD*\n"
            f"Saldo: {format_currency(dashboard['current_balance'])}\n"
            f"Performance: {format_currency(dashboard['month_performance'])}\n"
            f"Status: {traffic_emoji} {dashboard['traffic_light']['label']}\n"
            f"Comprometimento: {dashboard['commitment_ratio']:.1f}%",
            parse_mode='Markdown'
        )
        
        # Enviar gráficos
        from io import BytesIO
        
        # Saldo
        await update.message.reply_photo(
            photo=BytesIO(report['charts']['balance_chart']),
            caption="📊 Evolução do Saldo"
        )
        
        # Performance
        await update.message.reply_photo(
            photo=BytesIO(report['charts']['performance_chart']),
            caption="📈 Performance Diária"
        )
        
        # Categorias
        await update.message.reply_photo(
            photo=BytesIO(report['charts']['categories_chart']),
            caption="🍰 Gastos por Categoria"
        )
        
        # Planilha
        await update.message.reply_text(
            report['spreadsheet'],
            parse_mode='Markdown'
        )
        
        db.close()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao gerar relatório: {str(e)}")
        import traceback
        traceback.print_exc()


async def setchatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /setchatid - Configura o chat ID para relatórios automáticos"""
    chat_id = update.message.chat_id
    
    # Salvar em arquivo .env ou variável de ambiente
    env_file = Path(__file__).parent.parent / ".env"
    env_content = []
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.readlines()
    
    # Atualizar ou adicionar TELEGRAM_CHAT_ID
    found = False
    for i, line in enumerate(env_content):
        if line.startswith("TELEGRAM_CHAT_ID="):
            env_content[i] = f"TELEGRAM_CHAT_ID={chat_id}\n"
            found = True
            break
    
    if not found:
        env_content.append(f"TELEGRAM_CHAT_ID={chat_id}\n")
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(env_content)
    
    await update.message.reply_text(
        f"✅ Chat ID configurado: {chat_id}\n\n"
        f"Relatórios semanais serão enviados automaticamente toda segunda-feira às 8h."
    )


async def sincronizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /sincronizar - Sincroniza transações com Google Sheets"""
    await update.message.reply_text("🔄 Sincronizando com Google Sheets... Aguarde...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_URL}/api/google-sheets/sync",
                json={}
            )
            
            if response.status_code == 200:
                data = response.json()
                await update.message.reply_text(
                    f"✅ {data.get('message', 'Sincronização concluída')}\n\n"
                    f"Transações sincronizadas: {data.get('transactions_synced', 0)}"
                )
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('detail', response.text)
                await update.message.reply_text(
                    f"❌ Erro ao sincronizar: {error_msg}\n\n"
                    f"Verifique se GOOGLE_CREDENTIALS_PATH está configurado."
                )
    except httpx.ConnectError:
        await update.message.reply_text("❌ Erro: API não está rodando.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


def main():
    """Inicia o bot"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("relatorio", relatorio))
    application.add_handler(CommandHandler("sincronizar", sincronizar))
    application.add_handler(CommandHandler("setchatid", setchatid))
    application.add_handler(CommandHandler("confirmar", confirmar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot Telegram iniciado!")
    print(f"📡 Conectado à API: {API_URL}")
    
    # Rodar bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
