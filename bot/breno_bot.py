"""
Bot Telegram Simplificado - Método Breno
Trabalha diretamente com Google Sheets
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from services.google_sheets_breno import GoogleSheetsBreno
from services.categorization_service import CategorizationService
from services.report_service import ReportService
from services.alert_service import AlertService

# Configuração
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    # Fallback para desenvolvimento
    TELEGRAM_TOKEN = "8333761115:AAGGHqQ6CyytcMVu-e00Wx_FiIn02CoOw2Y"
    print("⚠️  Usando token hardcoded (apenas para desenvolvimento)")

# ID da planilha
SPREADSHEET_ID = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

# Inicializar serviços
sheets_service = None
categorization_service = None
report_service = None
alert_service = None

def get_sheets_service():
    """Inicializa serviço Google Sheets"""
    global sheets_service
    if sheets_service is None:
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not creds_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH não configurado")
        sheets_service = GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
    return sheets_service

def get_categorization_service():
    """Inicializa serviço de categorização"""
    global categorization_service
    if categorization_service is None:
        categorization_service = CategorizationService()
    return categorization_service

def get_report_service():
    """Inicializa serviço de relatórios"""
    global report_service
    if report_service is None:
        report_service = ReportService(get_sheets_service())
    return report_service

def get_alert_service():
    """Inicializa serviço de alertas"""
    global alert_service
    if alert_service is None:
        alert_service = AlertService(get_sheets_service())
    return alert_service


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def parse_gasto_command(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse do comando /gasto ou mensagem simples
    Exemplos:
    - /gasto 50 mercado
    - mercado 50
    - 50 mercado
    """
    text = text.strip()
    
    # Remover /gasto se presente
    if text.startswith('/gasto'):
        text = text[6:].strip()
    
    # Procurar número (valor)
    numbers = re.findall(r'\d+[.,]?\d*', text)
    if not numbers:
        return None
    
    # Pegar primeiro número como valor
    valor_str = numbers[0].replace(',', '.')
    try:
        valor = float(valor_str)
    except:
        return None
    
    # Descrição é o resto do texto sem o número
    descricao = re.sub(r'\d+[.,]?\d*', '', text, count=1).strip()
    if not descricao:
        descricao = "Gasto diário"
    
    return {
        'valor': valor,
        'descricao': descricao,
        'tipo': 'diario'
    }


async def comando_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /gasto [valor] [descrição]"""
    try:
        text = ' '.join(context.args) if context.args else update.message.text
        
        parsed = parse_gasto_command(text)
        if not parsed:
            await update.message.reply_text(
                "❌ *Ops! Formato inválido*\n\n"
                "💡 *Formas de usar:*\n"
                "• `/gasto 50 mercado`\n"
                "• `mercado 50`\n"
                "• `50 mercado`\n\n"
                "📝 Basta escrever o valor e a descrição!",
                parse_mode='Markdown'
            )
            return
        
        service = get_sheets_service()
        categorization = get_categorization_service()
        
        # Categorizar automaticamente
        categoria = categorization.categorizar(parsed['descricao'])
        
        result = service.registrar_gasto_diario(
            valor=parsed['valor'],
            descricao=parsed['descricao']
        )
        
        if result['sucesso']:
            saldo = result.get('saldo_atual', 0)
            semaforo = result.get('semaforo', '🟢')
            previsto = result.get('previsto', 0)
            diferenca = result.get('diferenca', 0)
            acao = result.get('acao', 'registrado')
            gasto_diario = result.get('gasto_diario', 0)
            
            # Mensagem baseada na ação realizada
            if acao == "substituído":
                # Substituiu o previsto
                if diferenca < 0:
                    diferenca_emoji = "📉"
                    diferenca_texto = "Economizou"
                else:
                    diferenca_emoji = "📈"
                    diferenca_texto = "Gastou a mais"
                
                msg = (
                    f"✅ *Gasto registrado!*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Valor registrado:* {format_currency(parsed['valor'])}\n"
                    f"📝 *Descrição:* {parsed['descricao']}\n"
                    f"🏷️ *Categoria:* {categoria}\n\n"
                    f"📊 *Ação:* Substituiu o previsto ({format_currency(previsto)})\n"
                    f"• {diferenca_emoji} {diferenca_texto}: {format_currency(abs(diferenca))}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{semaforo} *Saldo atual:* {format_currency(saldo)}\n"
                    f"_{result.get('status', 'OK')}_"
                )
            else:
                # Somou ao valor existente
                msg = (
                    f"✅ *Gasto adicionado!*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Valor adicionado:* {format_currency(parsed['valor'])}\n"
                    f"📝 *Descrição:* {parsed['descricao']}\n"
                    f"🏷️ *Categoria:* {categoria}\n\n"
                    f"📊 *Total do dia:*\n"
                    f"• Antes: {format_currency(previsto)}\n"
                    f"• Agora: {format_currency(gasto_diario)}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{semaforo} *Saldo atual:* {format_currency(saldo)}\n"
                    f"_{result.get('status', 'OK')}_"
                )
        else:
            msg = (
                f"❌ *Erro ao registrar gasto*\n\n"
                f"🔧 {result.get('erro', 'Erro desconhecido')}\n\n"
                f"💡 Verifique o formato e tente novamente."
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Erro inesperado*\n\n"
            f"🔧 {str(e)}\n\n"
            f"💡 Tente novamente ou use `/start` para ajuda.",
            parse_mode='Markdown'
        )


async def comando_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Mostra semáforo e saldo"""
    try:
        service = get_sheets_service()
        status = service.obter_status_atual()
        
        saldo = status.get('saldo', 0)
        semaforo = status.get('semaforo', '🟢')
        status_text = status.get('status_text', 'OK')
        gasto_diario = status.get('gasto_diario', 0)
        limite_diario = status.get('limite_diario', 0)
        performance = status.get('performance', 0)
        
        # Calcular percentual usado
        if limite_diario > 0:
            percentual = (gasto_diario / limite_diario) * 100
        else:
            percentual = 0
        
        # Emoji baseado no percentual
        if percentual == 0:
            percentual_emoji = "⚪"
        elif percentual < 50:
            percentual_emoji = "🟢"
        elif percentual < 80:
            percentual_emoji = "🟡"
        else:
            percentual_emoji = "🔴"
        
        msg = (
            f"{semaforo} *Status Financeiro*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Saldo Atual*\n"
            f"{format_currency(saldo)}\n\n"
            f"📊 *Performance do Mês*\n"
            f"{format_currency(performance)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Situação de Hoje*\n\n"
            f"💸 Gasto hoje: {format_currency(gasto_diario)}\n"
            f"🎯 Limite sugerido: {format_currency(limite_diario)}\n"
            f"{percentual_emoji} Uso: {percentual:.0f}%\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 _{status_text}_"
        )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Erro ao consultar status*\n\n"
            f"🔧 {str(e)}\n\n"
            f"💡 Verifique se a planilha está acessível.",
            parse_mode='Markdown'
        )


async def comando_posso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /posso [valor] - Verifica se pode gastar"""
    try:
        valor_consulta = None
        
        # Se passou valor como argumento
        if context.args:
            try:
                valor_consulta = float(context.args[0].replace(',', '.'))
            except:
                pass
        
        service = get_sheets_service()
        status = service.obter_status_atual()
        
        saldo = status.get('saldo', 0)
        semaforo = status.get('semaforo', '🟢')
        gasto_diario = status.get('gasto_diario', 0)
        limite_diario = status.get('limite_diario', 0)
        performance = status.get('performance', 0)
        
        if valor_consulta:
            # Verificar se pode gastar esse valor específico
            novo_gasto = gasto_diario + valor_consulta
            pode_gastar = saldo >= valor_consulta and (limite_diario == 0 or novo_gasto <= limite_diario * 1.2)
            
            if pode_gastar:
                msg = (
                    f"✅ *Pode gastar tranquilo!*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Valor consultado:* {format_currency(valor_consulta)}\n\n"
                    f"📊 *Após o gasto:*\n"
                    f"• Saldo restante: {format_currency(saldo - valor_consulta)}\n"
                    f"• Gasto diário total: {format_currency(novo_gasto)}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{semaforo} _{status.get('status_text', 'OK')}_"
                )
            else:
                msg = (
                    f"⚠️ *Atenção! Cuidado com este gasto*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Valor consultado:* {format_currency(valor_consulta)}\n\n"
                    f"📊 *Situação atual:*\n"
                    f"• Saldo disponível: {format_currency(saldo)}\n"
                    f"• Gasto hoje: {format_currency(gasto_diario)}\n"
                    f"• Limite sugerido: {format_currency(limite_diario)}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"❌ *Este gasto pode:*\n"
                    f"• Comprometer seu saldo\n"
                    f"• Exceder o limite diário recomendado\n\n"
                    f"💡 Considere aguardar ou reduzir o valor."
                )
        else:
            # Mostrar quanto pode gastar hoje
            disponivel_hoje = limite_diario - gasto_diario if limite_diario > 0 else saldo
            disponivel_hoje = max(0, min(disponivel_hoje, saldo))
            
            msg = (
                f"💵 *Quanto posso gastar hoje?*\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 *Saldo disponível:*\n"
                f"{format_currency(saldo)}\n\n"
                f"📅 *Gasto de hoje:*\n"
                f"{format_currency(gasto_diario)}\n\n"
                f"🎯 *Limite sugerido:*\n"
                f"{format_currency(limite_diario)}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ *Pode gastar até:*\n"
                f"*{format_currency(disponivel_hoje)}*\n\n"
                f"{semaforo} _{status.get('status_text', 'OK')}_"
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Erro ao verificar*\n\n"
            f"🔧 {str(e)}\n\n"
            f"💡 Tente novamente em alguns instantes.",
            parse_mode='Markdown'
        )


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /entrada [valor] [descrição] - Registra receita"""
    try:
        text = ' '.join(context.args) if context.args else ""
        
        if not text:
            await update.message.reply_text(
                "❌ *Ops! Formato inválido*\n\n"
                "💡 *Formas de usar:*\n"
                "• `/entrada 2500 cliente X`\n"
                "• `recebi 2500`\n"
                "• `entrada 2500`\n\n"
                "📝 Informe o valor e a descrição!",
                parse_mode='Markdown'
            )
            return
        
        # Parse similar ao gasto
        numbers = re.findall(r'\d+[.,]?\d*', text)
        if not numbers:
            await update.message.reply_text(
                "❌ *Valor não encontrado!*\n\n"
                "💡 Informe o valor numérico.\n"
                "Ex: `/entrada 2500 cliente X`",
                parse_mode='Markdown'
            )
            return
        
        valor = float(numbers[0].replace(',', '.'))
        descricao = re.sub(r'\d+[.,]?\d*', '', text, count=1).strip() or "Entrada"
        
        service = get_sheets_service()
        result = service.registrar_entrada(
            valor=valor,
            descricao=descricao
        )
        
        if result['sucesso']:
            msg = (
                f"✅ *Receita registrada com sucesso!*\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 *Valor:* {format_currency(valor)}\n"
                f"📝 *Descrição:* {descricao}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💵 *Saldo atual:*\n"
                f"*{format_currency(result.get('saldo_atual', 0))}*"
            )
        else:
            msg = (
                f"❌ *Erro ao registrar entrada*\n\n"
                f"🔧 {result.get('erro', 'Erro desconhecido')}\n\n"
                f"💡 Verifique o formato e tente novamente."
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Erro inesperado*\n\n"
            f"🔧 {str(e)}\n\n"
            f"💡 Tente novamente ou use `/start` para ajuda.",
            parse_mode='Markdown'
        )


async def comando_saida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /saida [valor] [descrição] - Registra saída fixa"""
    try:
        text = ' '.join(context.args) if context.args else ""
        
        if not text:
            await update.message.reply_text(
                "❌ *Ops! Formato inválido*\n\n"
                "💡 *Forma de usar:*\n"
                "• `/saida 1200 aluguel`\n"
                "• `aluguel 1200`\n\n"
                "📝 Informe o valor e a descrição!",
                parse_mode='Markdown'
            )
            return
        
        numbers = re.findall(r'\d+[.,]?\d*', text)
        if not numbers:
            await update.message.reply_text(
                "❌ *Valor não encontrado!*\n\n"
                "💡 Informe o valor numérico.\n"
                "Ex: `/saida 1200 aluguel`",
                parse_mode='Markdown'
            )
            return
        
        valor = float(numbers[0].replace(',', '.'))
        descricao = re.sub(r'\d+[.,]?\d*', '', text, count=1).strip() or "Saída fixa"
        
        service = get_sheets_service()
        result = service.registrar_saida_fixa(
            valor=valor,
            descricao=descricao
        )
        
        if result['sucesso']:
            msg = (
                f"✅ *Saída fixa registrada!*\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 *Valor:* {format_currency(valor)}\n"
                f"📝 *Descrição:* {descricao}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💵 *Saldo atual:*\n"
                f"*{format_currency(result.get('saldo_atual', 0))}*"
            )
        else:
            msg = (
                f"❌ *Erro ao registrar saída*\n\n"
                f"🔧 {result.get('erro', 'Erro desconhecido')}\n\n"
                f"💡 Verifique o formato e tente novamente."
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Erro inesperado*\n\n"
            f"🔧 {str(e)}\n\n"
            f"💡 Tente novamente ou use `/start` para ajuda.",
            parse_mode='Markdown'
        )


async def comando_setchatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /setchatid - Salva chat_id para lembretes"""
    try:
        chat_id = str(update.message.chat_id)
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        
        with open(chat_id_file, 'w') as f:
            f.write(chat_id)
        
        await update.message.reply_text(
            f"✅ *Configuração salva!*\n\n"
            f"🔔 *Lembretes automáticos ativados:*\n\n"
            f"🌙 *20:00* - Lembrete de fechamento do dia\n"
            f"🌅 *08:00* - Resumo matinal com limite diário\n\n"
            f"💡 Você receberá notificações importantes automaticamente!",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /categorias - Lista todas as categorias disponíveis"""
    try:
        categorization = get_categorization_service()
        categorias = categorization.listar_categorias()
        
        msg = "🏷️ *Categorias Disponíveis*\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for cat in categorias:
            if cat != 'Outros':
                msg += f"• *{cat}*\n"
        
        msg += "\n━━━━━━━━━━━━━━━━━━━━\n"
        msg += "💡 *Como funciona:*\n"
        msg += "Os gastos são categorizados automaticamente baseado na descrição.\n"
        msg += "Ex: 'mercado' → Alimentação\n"
        msg += "    'uber' → Transporte"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resumo - Relatório semanal"""
    try:
        report_service = get_report_service()
        relatorio = report_service.gerar_relatorio_semanal()
        
        if not relatorio.get('sucesso'):
            await update.message.reply_text(
                f"❌ *Erro ao gerar relatório*\n\n{relatorio.get('erro', 'Erro desconhecido')}",
                parse_mode='Markdown'
            )
            return
        
        periodo = relatorio.get('periodo', {})
        top_5 = relatorio.get('top_5_gastos', [])
        economia = relatorio.get('economia_vs_previsto', 0)
        performance = relatorio.get('performance_semana', 0)
        
        msg = (
            f"📊 *Relatório Semanal*\n\n"
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
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /relatorio - Relatório mensal completo"""
    try:
        report_service = get_report_service()
        relatorio = report_service.gerar_relatorio_mensal()
        
        if not relatorio.get('sucesso'):
            await update.message.reply_text(
                f"❌ *Erro ao gerar relatório*\n\n{relatorio.get('erro', 'Erro desconhecido')}",
                parse_mode='Markdown'
            )
            return
        
        mes_atual = relatorio.get('mes_atual', {})
        comparativo = relatorio.get('comparativo', {})
        insights = relatorio.get('insights', [])
        
        dados_atual = mes_atual.get('dados', {})
        perf_atual = dados_atual.get('performance', 0)
        
        msg = (
            f"📊 *Relatório Mensal Completo*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Mês Atual:*\n"
            f"• Entradas: {format_currency(dados_atual.get('total_entrada', 0))}\n"
            f"• Saídas: {format_currency(dados_atual.get('total_saida', 0))}\n"
            f"• Diário: {format_currency(dados_atual.get('total_diario', 0))}\n"
            f"• Performance: {format_currency(perf_atual)}\n\n"
        )
        
        # Comparativo
        perf_comp = comparativo.get('performance', {})
        if perf_comp.get('variacao') != 0:
            variacao = perf_comp.get('variacao', 0)
            emoji = "📈" if variacao > 0 else "📉"
            msg += (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 *Comparativo com Mês Anterior:*\n"
                f"{emoji} Performance: {format_currency(variacao)}\n"
                f"({perf_comp.get('variacao_percentual', 0):.1f}%)\n\n"
            )
        
        # Insights
        if insights:
            msg += f"💡 *Insights Automáticos:*\n"
            for insight in insights[:5]:  # Limitar a 5 insights
                msg += f"{insight}\n"
            msg += "\n"
        
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "💡 Continue acompanhando sua evolução financeira!"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /alertas - Ver alertas ativos"""
    try:
        alert_service = get_alert_service()
        alertas = alert_service.verificar_alertas()
        
        if not alertas:
            await update.message.reply_text(
                "✅ *Nenhum Alerta Ativo*\n\n"
                "🎉 Tudo certo! Sua situação financeira está em ordem.\n\n"
                "💡 Continue monitorando com `/status`",
                parse_mode='Markdown'
            )
            return
        
        msg = "🔔 *Alertas Ativos*\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for alerta in alertas:
            msg += (
                f"{alerta.get('emoji', '⚠️')} *{alerta.get('titulo', 'Alerta')}*\n"
                f"{alerta.get('mensagem', '')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_projecao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /projecao - Projeção de saldo futuro baseado em valores previstos"""
    try:
        meses = 6  # Padrão: 6 meses
        if context.args:
            try:
                meses = int(context.args[0])
                if meses < 1 or meses > 12:
                    meses = 6
            except:
                pass
        
        service = get_sheets_service()
        projecao = service.calcular_projecao_futura(meses_futuros=meses)
        
        if not projecao.get('sucesso'):
            await update.message.reply_text(
                f"❌ *Erro ao calcular projeção*\n\n{projecao.get('erro', 'Erro desconhecido')}",
                parse_mode='Markdown'
            )
            return
        
        saldo_atual = projecao.get('saldo_atual', 0)
        mes_atual = projecao.get('mes_atual', 'Atual')
        projecoes = projecao.get('projecoes', [])
        alertas = projecao.get('alertas', [])
        
        msg = (
            f"🔮 *Projeção Financeira Futura*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Saldo Atual ({mes_atual}):*\n"
            f"{format_currency(saldo_atual)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Projeções dos Próximos {len(projecoes)} Meses:*\n\n"
        )
        
        for proj in projecoes:
            emoji = "🔴" if proj['negativo'] else "🟢"
            msg += (
                f"{emoji} *{proj['nome_mes']}/{proj['ano']}*\n"
                f"• Entrada prevista: {format_currency(proj['entrada_prevista'])}\n"
                f"• Saída prevista: {format_currency(proj['saida_prevista'])}\n"
                f"• Diário previsto: {format_currency(proj['diario_previsto'])}\n"
                f"• Performance: {format_currency(proj['performance_prevista'])}\n"
                f"• Saldo final: {format_currency(proj['saldo_final'])}\n\n"
            )
        
        if alertas:
            msg += "━━━━━━━━━━━━━━━━━━━━\n"
            msg += "⚠️ *ALERTAS DE RISCO:*\n\n"
            for alerta in alertas[:3]:  # Limitar a 3 alertas
                msg += f"{alerta['mensagem']}\n\n"
        
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💡 Use `/projecao 12` para ver 12 meses\n"
        msg += f"💡 Valores baseados nos previstos da planilha"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /meta - Gerenciar meta de economia mensal"""
    try:
        if not context.args:
            # Mostrar meta atual
            await update.message.reply_text(
                "🎯 *Meta de Economia*\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💡 *Como usar:*\n"
                "• `/meta 1000` - Define meta de R$ 1.000\n"
                "• `/meta` - Ver meta atual\n\n"
                "📊 A meta ajuda você a ter um objetivo claro de economia mensal!",
                parse_mode='Markdown'
            )
            return
        
        # Definir meta
        try:
            valor = float(context.args[0].replace(',', '.'))
            # TODO: Salvar meta em arquivo ou banco de dados
            await update.message.reply_text(
                f"✅ *Meta definida!*\n\n"
                f"🎯 *Meta de economia:* {format_currency(valor)}\n\n"
                f"💡 Você receberá alertas sobre seu progresso!",
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ *Valor inválido*\n\n"
                "💡 Use: `/meta 1000` para definir uma meta de R$ 1.000",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    # Salvar chat_id automaticamente
    try:
        chat_id = str(update.message.chat_id)
        chat_id_file = Path(__file__).parent.parent / "telegram_chat_id.txt"
        with open(chat_id_file, 'w') as f:
            f.write(chat_id)
    except:
        pass
    
    await update.message.reply_text(
        "👋 *Olá! Bem-vindo ao seu Assistente Financeiro* 💰\n\n"
        "Eu sou seu bot pessoal baseado no *Método Breno* e estou aqui para te ajudar a manter suas finanças organizadas! 🎯\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📱 *COMANDOS PRINCIPAIS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💸 *Registrar Gastos*\n"
        "`/gasto 50 mercado`\n"
        "ou simplesmente: `mercado 50`\n\n"
        "💵 *Registrar Receitas*\n"
        "`/entrada 2500 cliente X`\n"
        "ou: `recebi 2500`\n\n"
        "📤 *Registrar Saídas Fixas*\n"
        "`/saida 1200 aluguel`\n"
        "ou: `aluguel 1200`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *CONSULTAS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚦 `/status` - Ver seu semáforo financeiro e situação atual\n\n"
        "❓ `/posso 100` - Verificar se pode fazer um gasto específico\n"
        "ou apenas `/posso` para ver quanto pode gastar hoje\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *RELATÓRIOS E ANÁLISES*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📈 `/resumo` - Relatório semanal completo\n\n"
        "📊 `/relatorio` - Relatório mensal com insights\n\n"
        "🔮 `/projecao [meses]` - Projeção futura de saldo (padrão: 6 meses)\n\n"
        "🏷️ `/categorias` - Ver categorias de gastos\n\n"
        "🔔 `/alertas` - Ver alertas financeiros ativos\n\n"
        "🎯 `/meta [valor]` - Definir meta de economia mensal\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *DICAS RÁPIDAS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ Você pode enviar mensagens simples sem usar comandos:\n"
        "• `mercado 50` → Registra gasto\n"
        "• `recebi 2500` → Registra receita\n"
        "• `aluguel 1200` → Registra saída fixa\n\n"
        "🔄 *Funcionamento Automático:*\n"
        "• Se não registrar gastos, o diário é zerado automaticamente\n"
        "• Receba lembretes às 20h e resumo matinal às 8h\n"
        "• Tudo sincronizado com sua planilha Google Sheets\n\n"
        "💬 Precisa de ajuda? Use `/start` novamente para ver este menu!",
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto simples"""
    text = update.message.text.strip().lower()
    
    # Se começa com /, não processar aqui
    if text.startswith('/'):
        return
    
    # Tentar parse como gasto
    parsed = parse_gasto_command(text)
    if parsed:
        # Simular comando /gasto
        context.args = [str(parsed['valor']), parsed['descricao']]
        await comando_gasto(update, context)
        return
    
    # Verificar se é "recebi X" ou "entrada X"
    if text.startswith('recebi ') or text.startswith('entrada '):
        context.args = text.split()[1:]
        await comando_entrada(update, context)
        return
    
    # Se não reconheceu, mostrar ajuda
    await update.message.reply_text(
        "🤔 *Não entendi essa mensagem*\n\n"
        "💡 Use `/start` para ver todos os comandos disponíveis!\n\n"
        "📝 *Dicas rápidas:*\n"
        "• `mercado 50` → Registra gasto\n"
        "• `recebi 2500` → Registra receita\n"
        "• `/status` → Ver situação financeira",
        parse_mode='Markdown'
    )


def main():
    """Inicializa o bot"""
    print("🤖 Iniciando Bot Telegram - Método Breno...")
    
    # Criar aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CommandHandler("setchatid", comando_setchatid))
    application.add_handler(CommandHandler("gasto", comando_gasto))
    application.add_handler(CommandHandler("entrada", comando_entrada))
    application.add_handler(CommandHandler("saida", comando_saida))
    application.add_handler(CommandHandler("status", comando_status))
    application.add_handler(CommandHandler("posso", comando_posso))
    application.add_handler(CommandHandler("categorias", comando_categorias))
    application.add_handler(CommandHandler("resumo", comando_resumo))
    application.add_handler(CommandHandler("relatorio", comando_relatorio))
    application.add_handler(CommandHandler("alertas", comando_alertas))
    application.add_handler(CommandHandler("projecao", comando_projecao))
    application.add_handler(CommandHandler("meta", comando_meta))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Agendar lembretes (será implementado com scheduler separado)
    
    print("✅ Bot iniciado! Pressione Ctrl+C para parar.")
    
    # Iniciar polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
