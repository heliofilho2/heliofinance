"""
Serviço de alertas baseado no Método Breno
Alertas para performance negativa, gastos diários, saldo baixo, etc.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from services.google_sheets_breno import GoogleSheetsBreno


class AlertService:
    """Gerencia alertas e notificações financeiras"""
    
    def __init__(self, sheets_service: GoogleSheetsBreno):
        self.sheets_service = sheets_service
        self.alertas_enviados = set()  # Para evitar spam
    
    def verificar_alertas(self) -> List[Dict[str, Any]]:
        """
        Verifica todos os alertas possíveis e retorna lista de alertas ativos
        
        Returns:
            Lista de alertas com tipo, mensagem e prioridade
        """
        alertas = []
        
        # Obter status atual
        status = self.sheets_service.obter_status_atual()
        
        # 1. Alerta de performance negativa (sem economia)
        alerta_perf = self._verificar_performance_negativa(status)
        if alerta_perf:
            alertas.append(alerta_perf)
        
        # 2. Alerta de gasto diário próximo do limite (80%)
        alerta_gasto = self._verificar_gasto_diario(status)
        if alerta_gasto:
            alertas.append(alerta_gasto)
        
        # 3. Alerta de saldo baixo
        alerta_saldo = self._verificar_saldo_baixo(status)
        if alerta_saldo:
            alertas.append(alerta_saldo)
        
        # 4. Alerta de meta de economia
        alerta_meta = self._verificar_meta_economia(status)
        if alerta_meta:
            alertas.append(alerta_meta)
        
        return alertas
    
    def _verificar_performance_negativa(self, status: Dict) -> Optional[Dict]:
        """
        Verifica se performance está negativa
        Baseado no e-book: performance negativa é problema se não está economizando
        """
        performance = status.get('performance', 0)
        
        if performance < 0:
            # Performance negativa - alertar
            return {
                'tipo': 'performance_negativa',
                'prioridade': 'alta',
                'titulo': '⚠️ Performance Negativa',
                'mensagem': (
                    f"📊 Sua performance está negativa: {self._format_currency(performance)}\n\n"
                    f"💡 Segundo o Método Breno:\n"
                    f"• Se você está economizando, está tudo certo!\n"
                    f"• Se NÃO está economizando, revise seus gastos.\n\n"
                    f"🔍 Use `/status` para ver detalhes completos."
                ),
                'emoji': '⚠️'
            }
        return None
    
    def _verificar_gasto_diario(self, status: Dict) -> Optional[Dict]:
        """Verifica se gasto diário está próximo ou acima do limite"""
        gasto_diario = status.get('gasto_diario', 0)
        limite_diario = status.get('limite_diario', 0)
        
        if limite_diario > 0:
            percentual = (gasto_diario / limite_diario) * 100
            
            if percentual >= 100:
                return {
                    'tipo': 'gasto_limite_excedido',
                    'prioridade': 'alta',
                    'titulo': '🔴 Limite Diário Excedido!',
                    'mensagem': (
                        f"🚨 Você excedeu o limite diário sugerido!\n\n"
                        f"💰 Gasto hoje: {self._format_currency(gasto_diario)}\n"
                        f"🎯 Limite sugerido: {self._format_currency(limite_diario)}\n\n"
                        f"💡 Evite novos gastos hoje para manter a planilha no verde."
                    ),
                    'emoji': '🔴'
                }
            elif percentual >= 80:
                return {
                    'tipo': 'gasto_proximo_limite',
                    'prioridade': 'media',
                    'titulo': '🟡 Atenção: Próximo do Limite',
                    'mensagem': (
                        f"⚠️ Você está próximo do limite diário!\n\n"
                        f"💰 Gasto hoje: {self._format_currency(gasto_diario)}\n"
                        f"🎯 Limite sugerido: {self._format_currency(limite_diario)}\n"
                        f"📊 Uso: {percentual:.1f}%\n\n"
                        f"💡 Cuidado com novos gastos hoje!"
                    ),
                    'emoji': '🟡'
                }
        
        return None
    
    def _verificar_saldo_baixo(self, status: Dict) -> Optional[Dict]:
        """Verifica se saldo está baixo"""
        saldo = status.get('saldo', 0)
        
        # Considerar saldo baixo se estiver abaixo de R$ 500
        if saldo < 500 and saldo >= 0:
            return {
                'tipo': 'saldo_baixo',
                'prioridade': 'media',
                'titulo': '💸 Saldo Baixo',
                'mensagem': (
                    f"💰 Seu saldo está baixo: {self._format_currency(saldo)}\n\n"
                    f"💡 Fique atento aos próximos gastos.\n"
                    f"📊 Use `/status` para ver sua situação completa."
                ),
                'emoji': '💸'
            }
        elif saldo < 0:
            return {
                'tipo': 'saldo_negativo',
                'prioridade': 'alta',
                'titulo': '🔴 Saldo Negativo!',
                'mensagem': (
                    f"🚨 ATENÇÃO: Seu saldo está negativo!\n\n"
                    f"💰 Saldo atual: {self._format_currency(saldo)}\n\n"
                    f"⚠️ Evite novos gastos e revise suas finanças urgentemente!"
                ),
                'emoji': '🔴'
            }
        
        return None
    
    def _verificar_meta_economia(self, status: Dict) -> Optional[Dict]:
        """Verifica progresso da meta de economia mensal"""
        # Esta função pode ser expandida quando implementarmos sistema de metas
        # Por enquanto, apenas verifica se há meta configurada
        return None
    
    def _format_currency(self, value: float) -> str:
        """Formata valor como moeda brasileira"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
