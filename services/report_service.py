"""
Serviço de relatórios automáticos - Semanal e Mensal
Baseado no Método Breno
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.google_sheets_breno import GoogleSheetsBreno
from services.categorization_service import CategorizationService


class ReportService:
    """Gera relatórios financeiros automáticos"""
    
    def __init__(self, sheets_service: GoogleSheetsBreno):
        self.sheets_service = sheets_service
        self.categorization = CategorizationService()
    
    def gerar_relatorio_semanal(self) -> Dict[str, Any]:
        """
        Gera relatório semanal com:
        - Top 5 gastos da semana
        - Economia vs previsto
        - Gráfico de tendência (dados)
        """
        try:
            now = datetime.now()
            # Calcular início da semana (segunda-feira)
            days_since_monday = now.weekday()
            inicio_semana = now - timedelta(days=days_since_monday)
            inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Obter dados dos últimos 7 dias
            dados_dias = []
            gastos_semana = []
            total_previsto = 0
            total_real = 0
            
            for i in range(7):
                dia = inicio_semana + timedelta(days=i)
                if dia > now:
                    break
                
                # Ler dados do dia
                month_data = self._get_day_data(dia.day, dia.month)
                if month_data:
                    previsto = 50.0  # Valor previsto padrão
                    real = month_data.get('diario', 0)
                    entrada = month_data.get('entrada', 0)
                    saida = month_data.get('saida', 0)
                    saldo = month_data.get('saldo', 0)
                    
                    dados_dias.append({
                        'dia': dia.strftime('%d/%m'),
                        'dia_semana': dia.strftime('%a'),
                        'entrada': entrada,
                        'saida': saida,
                        'diario': real,
                        'saldo': saldo,
                        'previsto': previsto
                    })
                    
                    total_previsto += previsto
                    total_real += real
                    
                    if real > 0:
                        gastos_semana.append({
                            'dia': dia.strftime('%d/%m'),
                            'valor': real,
                            'descricao': f'Gasto do dia {dia.day}'
                        })
            
            # Top 5 gastos
            top_5_gastos = sorted(gastos_semana, key=lambda x: x['valor'], reverse=True)[:5]
            
            # Economia vs previsto
            economia = total_previsto - total_real
            
            # Calcular performance da semana
            total_entrada = sum([d['entrada'] for d in dados_dias])
            total_saida = sum([d['saida'] for d in dados_dias])
            performance_semana = total_entrada - total_saida - total_real
            
            return {
                'sucesso': True,
                'periodo': {
                    'inicio': inicio_semana.strftime('%d/%m/%Y'),
                    'fim': now.strftime('%d/%m/%Y')
                },
                'top_5_gastos': top_5_gastos,
                'economia_vs_previsto': economia,
                'total_previsto': total_previsto,
                'total_real': total_real,
                'performance_semana': performance_semana,
                'tendencia_dias': dados_dias,
                'total_entrada': total_entrada,
                'total_saida': total_saida
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def gerar_relatorio_mensal(self, mes: Optional[int] = None, ano: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera relatório mensal completo com:
        - Análise completa do mês
        - Comparativo com mês anterior
        - Insights automáticos
        """
        try:
            now = datetime.now()
            mes_atual = mes or now.month
            ano_atual = ano or now.year
            
            # Obter dados do mês atual
            dados_mes_atual = self._get_month_data(mes_atual, ano_atual)
            
            # Obter dados do mês anterior
            mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
            ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
            dados_mes_anterior = self._get_month_data(mes_anterior, ano_anterior)
            
            # Calcular comparações
            comparativo = self._calcular_comparativo(dados_mes_atual, dados_mes_anterior)
            
            # Gerar insights
            insights = self._gerar_insights(dados_mes_atual, dados_mes_anterior)
            
            return {
                'sucesso': True,
                'mes_atual': {
                    'mes': mes_atual,
                    'ano': ano_atual,
                    'dados': dados_mes_atual
                },
                'mes_anterior': {
                    'mes': mes_anterior,
                    'ano': ano_anterior,
                    'dados': dados_mes_anterior
                },
                'comparativo': comparativo,
                'insights': insights
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def _get_day_data(self, dia: int, mes: int) -> Optional[Dict]:
        """Obtém dados de um dia específico"""
        try:
            col_offset = self.sheets_service._get_month_column_offset(mes)
            row = self.sheets_service._get_day_row(dia)
            
            entrada = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(row, col_offset + 1)
            )
            saida = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(row, col_offset + 2)
            )
            diario = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(row, col_offset + 3)
            )
            saldo = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(row, col_offset + 4)
            )
            
            return {
                'entrada': entrada,
                'saida': saida,
                'diario': diario,
                'saldo': saldo
            }
        except:
            return None
    
    def _get_month_data(self, mes: int, ano: int) -> Dict[str, Any]:
        """Obtém dados completos de um mês"""
        try:
            col_offset = self.sheets_service._get_month_column_offset(mes)
            
            # Ler totais do mês (linha 37 ou 38)
            total_row = 37
            total_entrada = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(total_row, col_offset + 1)
            )
            total_saida = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(total_row, col_offset + 2)
            )
            total_diario = self.sheets_service._parse_currency(
                self.sheets_service._get_cell_value(total_row, col_offset + 3)
            )
            
            # Se não encontrou, tentar linha 36
            if total_entrada == 0 and total_saida == 0:
                total_row = 36
                total_entrada = self.sheets_service._parse_currency(
                    self.sheets_service._get_cell_value(total_row, col_offset + 1)
                )
                total_saida = self.sheets_service._parse_currency(
                    self.sheets_service._get_cell_value(total_row, col_offset + 2)
                )
                total_diario = self.sheets_service._parse_currency(
                    self.sheets_service._get_cell_value(total_row, col_offset + 3)
                )
            
            performance = total_entrada - total_saida - total_diario
            
            return {
                'total_entrada': total_entrada,
                'total_saida': total_saida,
                'total_diario': total_diario,
                'performance': performance
            }
        except Exception as e:
            return {
                'total_entrada': 0,
                'total_saida': 0,
                'total_diario': 0,
                'performance': 0,
                'erro': str(e)
            }
    
    def _calcular_comparativo(self, mes_atual: Dict, mes_anterior: Dict) -> Dict[str, Any]:
        """Calcula comparação entre dois meses"""
        perf_atual = mes_atual.get('performance', 0)
        perf_anterior = mes_anterior.get('performance', 0)
        
        entrada_atual = mes_atual.get('total_entrada', 0)
        entrada_anterior = mes_anterior.get('total_entrada', 0)
        
        saida_atual = mes_atual.get('total_saida', 0)
        saida_anterior = mes_anterior.get('total_saida', 0)
        
        diario_atual = mes_atual.get('total_diario', 0)
        diario_anterior = mes_anterior.get('total_diario', 0)
        
        # Calcular variações percentuais
        def calc_variacao(atual, anterior):
            if anterior == 0:
                return 0 if atual == 0 else 100
            return ((atual - anterior) / abs(anterior)) * 100
        
        return {
            'performance': {
                'atual': perf_atual,
                'anterior': perf_anterior,
                'variacao': perf_atual - perf_anterior,
                'variacao_percentual': calc_variacao(perf_atual, perf_anterior)
            },
            'entrada': {
                'atual': entrada_atual,
                'anterior': entrada_anterior,
                'variacao': entrada_atual - entrada_anterior,
                'variacao_percentual': calc_variacao(entrada_atual, entrada_anterior)
            },
            'saida': {
                'atual': saida_atual,
                'anterior': saida_anterior,
                'variacao': saida_atual - saida_anterior,
                'variacao_percentual': calc_variacao(saida_atual, saida_anterior)
            },
            'diario': {
                'atual': diario_atual,
                'anterior': diario_anterior,
                'variacao': diario_atual - diario_anterior,
                'variacao_percentual': calc_variacao(diario_atual, diario_anterior)
            }
        }
    
    def _gerar_insights(self, mes_atual: Dict, mes_anterior: Dict) -> List[str]:
        """Gera insights automáticos baseados nos dados"""
        insights = []
        
        comparativo = self._calcular_comparativo(mes_atual, mes_anterior)
        
        # Insight sobre performance
        perf_var = comparativo['performance']['variacao_percentual']
        if perf_var > 20:
            insights.append(f"🎉 Performance melhorou {abs(perf_var):.1f}% em relação ao mês anterior!")
        elif perf_var < -20:
            insights.append(f"⚠️ Performance caiu {abs(perf_var):.1f}% em relação ao mês anterior. Revise seus gastos.")
        
        # Insight sobre gastos diários
        diario_var = comparativo['diario']['variacao_percentual']
        if diario_var > 30:
            insights.append(f"📈 Você gastou {abs(diario_var):.1f}% mais em gastos diários este mês.")
        elif diario_var < -30:
            insights.append(f"💰 Você economizou {abs(diario_var):.1f}% em gastos diários este mês!")
        
        # Insight sobre entradas
        entrada_var = comparativo['entrada']['variacao_percentual']
        if entrada_var > 20:
            insights.append(f"💵 Suas entradas aumentaram {abs(entrada_var):.1f}% este mês!")
        elif entrada_var < -20:
            insights.append(f"📉 Suas entradas diminuíram {abs(entrada_var):.1f}% este mês.")
        
        # Insight sobre saídas fixas
        saida_var = comparativo['saida']['variacao_percentual']
        if abs(saida_var) > 10:
            if saida_var > 0:
                insights.append(f"💳 Suas saídas fixas aumentaram {abs(saida_var):.1f}% este mês.")
            else:
                insights.append(f"✅ Suas saídas fixas diminuíram {abs(saida_var):.1f}% este mês!")
        
        # Insight sobre performance negativa
        perf_atual = mes_atual.get('performance', 0)
        if perf_atual < 0:
            insights.append("⚠️ Performance negativa este mês. Se não guardou dinheiro, revise seus gastos!")
        
        if not insights:
            insights.append("📊 Seu mês está equilibrado. Continue assim!")
        
        return insights
