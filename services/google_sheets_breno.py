"""
Serviço Google Sheets adaptado para estrutura da planilha do Método Breno
Estrutura: Data, Entrada, Saída, Diário, Saldo (por mês)
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
import re

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


class GoogleSheetsBreno:
    """Integração com Google Sheets - Método Breno"""
    
    def __init__(self, spreadsheet_id: str, credentials_path: str = None):
        """
        Inicializa serviço do Google Sheets
        
        Args:
            spreadsheet_id: ID da planilha (da URL)
            credentials_path: Caminho para arquivo de credenciais JSON
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        
        if not self.credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH não configurado")
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
        
        # Autenticar
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scope
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            self.worksheet = self.spreadsheet.sheet1
        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg.lower() or "jwt" in error_msg.lower():
                raise ValueError(
                    f"Erro de autenticação JWT: {error_msg}\n\n"
                    "Possíveis soluções:\n"
                    "1. Sincronize o relógio do sistema: w32tm /resync\n"
                    "2. Verifique se a service account tem acesso à planilha\n"
                    "3. Gere novas credenciais no Google Cloud Console\n"
                    "4. Execute: python test_google_auth.py para diagnóstico"
                ) from e
            raise
        
        # Mapeamento de meses
        self.month_names = {
            1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
            5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
            9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
        }
        
        # Cada mês ocupa 6 colunas (Data, Entrada, Saída, Diário, Saldo, vazio)
        self.cols_per_month = 6
    
    def _parse_currency(self, value: str) -> float:
        """Converte string de moeda para float"""
        if not value or value == '':
            return 0.0
        
        # Remove R$, espaços, e converte vírgula para ponto
        value = str(value).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return float(value)
        except:
            return 0.0
    
    def _format_currency(self, value: float) -> str:
        """Formata float para string de moeda brasileira"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def _get_month_column_offset(self, month: int) -> int:
        """Retorna offset da coluna inicial do mês (0-indexed)"""
        return (month - 1) * self.cols_per_month
    
    def _get_day_row(self, day: int) -> int:
        """Retorna linha do dia (0-indexed, linha 2 = cabeçalho, linha 3+ = dias)"""
        return day + 1  # Linha 2 é cabeçalho, linha 3 é dia 1
    
    def _get_cell_value(self, row: int, col: int) -> str:
        """Obtém valor de uma célula"""
        try:
            cell = self.worksheet.cell(row + 1, col + 1)  # gspread é 1-indexed
            return cell.value or ''
        except:
            return ''
    
    def _set_cell_value(self, row: int, col: int, value: Any):
        """
        Define valor de uma célula
        PROTEÇÃO: NUNCA atualiza a coluna Saldo (col_offset + 4)
        """
        # Verificar se está tentando atualizar coluna Saldo (col_offset + 4 para qualquer mês)
        # Cada mês tem 6 colunas, então Saldo está em: month_offset + 4
        # Bloquear qualquer atualização na posição 4 de cada bloco de 6 colunas
        if (col % self.cols_per_month) == 4:
            raise ValueError(
                f"PROTEÇÃO: Tentativa de atualizar coluna Saldo bloqueada! "
                f"O bot NUNCA atualiza a coluna Saldo - apenas Entrada, Saída e Diário."
            )
        
        try:
            self.worksheet.update_cell(row + 1, col + 1, value)  # gspread é 1-indexed
        except Exception as e:
            print(f"Erro ao atualizar célula ({row}, {col}): {e}")
    
    def _get_current_month_data(self) -> Dict[str, Any]:
        """Obtém dados do mês atual"""
        now = datetime.now()
        month = now.month
        year = now.year
        day = now.day
        
        col_offset = self._get_month_column_offset(month)
        
        # Colunas: Data=0, Entrada=1, Saída=2, Diário=3, Saldo=4
        col_data = col_offset
        col_entrada = col_offset + 1
        col_saida = col_offset + 2
        col_diario = col_offset + 3
        col_saldo = col_offset + 4
        
        # Ler dados do dia atual
        row = self._get_day_row(day)
        
        entrada = self._parse_currency(self._get_cell_value(row, col_entrada))
        saida = self._parse_currency(self._get_cell_value(row, col_saida))
        diario = self._parse_currency(self._get_cell_value(row, col_diario))
        saldo = self._parse_currency(self._get_cell_value(row, col_saldo))
        
        return {
            'month': month,
            'year': year,
            'day': day,
            'row': row,
            'col_entrada': col_entrada,
            'col_saida': col_saida,
            'col_diario': col_diario,
            'col_saldo': col_saldo,
            'entrada': entrada,
            'saida': saida,
            'diario': diario,
            'saldo': saldo
        }
    
    def _calculate_saldo(self, month_data: Dict[str, Any]) -> float:
        """
        Lê o saldo atual da planilha (calculado automaticamente pelas fórmulas)
        NÃO calcula nem atualiza - apenas lê o valor existente
        """
        # Apenas ler o saldo do dia atual (já calculado pela planilha)
        return month_data.get('saldo', 0.0)
    
    def _update_saldo(self, month_data: Dict[str, Any], novo_saldo: float):
        """
        NÃO FAZ NADA - Esta função existe apenas para compatibilidade
        O bot NUNCA atualiza a coluna Saldo - apenas lê os valores
        A planilha calcula o saldo automaticamente via fórmulas
        """
        # NÃO atualizar saldo - nunca tocar na coluna Saldo
        pass
    
    def _calculate_semaforo(self, saldo: float, performance: float, gasto_diario: float, limite_diario: float) -> Dict[str, Any]:
        """Calcula semáforo baseado no saldo e performance"""
        # Verde: saldo positivo e performance positiva
        # Amarelo: saldo positivo mas performance negativa OU gasto > 80% do limite
        # Vermelho: saldo negativo OU gasto > limite
        
        if saldo < 0:
            return {
                'semaforo': '🔴',
                'status': 'VERMELHO',
                'status_text': 'Saldo negativo! Evite novos gastos.'
            }
        
        if performance < 0:
            if gasto_diario > limite_diario * 0.8 if limite_diario > 0 else False:
                return {
                    'semaforo': '🟡',
                    'status': 'AMARELO',
                    'status_text': 'Atenção! Performance negativa e gasto próximo do limite.'
                }
            return {
                'semaforo': '🟡',
                'status': 'AMARELO',
                'status_text': 'Performance negativa. Cuidado com gastos.'
            }
        
        if limite_diario > 0 and gasto_diario > limite_diario * 0.8:
            return {
                'semaforo': '🟡',
                'status': 'AMARELO',
                'status_text': 'Atenção! Você atingiu 80% do limite diário.'
            }
        
        return {
            'semaforo': '🟢',
            'status': 'VERDE',
            'status_text': 'Você está dentro da meta diária.'
        }
    
    def registrar_gasto_diario(self, valor: float, descricao: str = "Gasto diário") -> Dict[str, Any]:
        """
        Registra gasto diário
        
        Lógica:
        - Se o valor atual é o previsto padrão (50), SUBSTITUI
        - Se o valor atual é diferente de 50, SOMA
        - Se não registrar nada, o bot zera automaticamente ao final do dia
        """
        try:
            month_data = self._get_current_month_data()
            
            # Valor atual do diário
            valor_atual = month_data['diario']
            
            # Valor previsto padrão
            VALOR_PREVISTO_PADRAO = 50.0
            
            # Se o valor atual é o previsto padrão (ou muito próximo), SUBSTITUIR
            # Senão, SOMAR ao valor existente
            if abs(valor_atual - VALOR_PREVISTO_PADRAO) < 0.01:
                # Ainda está com o valor previsto, substituir
                novo_diario = valor
                diferenca = valor - valor_atual
                acao = "substituído"
            else:
                # Já tem um valor diferente, somar
                novo_diario = valor_atual + valor
                diferenca = valor
                acao = "adicionado"
            
            # Atualizar célula (substitui o previsto)
            self._set_cell_value(month_data['row'], month_data['col_diario'], self._format_currency(novo_diario))
            
            # NÃO atualizar saldo - a planilha calcula automaticamente via fórmulas
            # Apenas atualizar o diário, a planilha recalcula o saldo automaticamente
            # Ler saldo atualizado (calculado pela planilha automaticamente)
            saldo_atual = self._parse_currency(self._get_cell_value(month_data['row'], month_data['col_saldo']))
            
            # Obter status atualizado
            status = self.obter_status_atual()
            
            return {
                'sucesso': True,
                'saldo_atual': saldo_atual,
                'gasto_diario': novo_diario,
                'previsto': valor_atual,  # Valor anterior para mostrar na mensagem
                'acao': acao,
                'diferenca': diferenca,
                'semaforo': status.get('semaforo', '🟢'),
                'status': status.get('status_text', 'OK')
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def zerar_diario_nao_registrado(self, dia: int = None, mes: int = None) -> Dict[str, Any]:
        """
        Zera o diário do dia se não foi registrado nenhum gasto
        
        Verifica se o valor ainda é o previsto padrão (50) e, se for, zera.
        Se o valor foi alterado (mesmo que seja 0), não mexe.
        """
        try:
            now = datetime.now()
            if dia is None:
                dia = now.day
            if mes is None:
                mes = now.month
            
            col_offset = self._get_month_column_offset(mes)
            col_diario = col_offset + 3
            row = self._get_day_row(dia)
            
            # Ler valor atual do diário
            valor_atual = self._parse_currency(self._get_cell_value(row, col_diario))
            
            # Valor previsto padrão (você pode ajustar isso)
            VALOR_PREVISTO_PADRAO = 50.0
            
            # Se o valor ainda é o previsto padrão (ou muito próximo), significa que não foi registrado
            # Zerar apenas se for exatamente o previsto ou se estiver vazio/zero mas tinha previsto
            if abs(valor_atual - VALOR_PREVISTO_PADRAO) < 0.01:
                # Ainda está com o valor previsto, zerar
                self._set_cell_value(row, col_diario, self._format_currency(0.0))
                
                # NÃO atualizar saldo - a planilha recalcula automaticamente via fórmulas
                # Apenas zerar o diário, a planilha fará o resto
                
                # Ler saldo atualizado (calculado pela planilha)
                col_saldo = col_offset + 4
                novo_saldo = self._parse_currency(self._get_cell_value(row, col_saldo))
                
                return {
                    'sucesso': True,
                    'dia': dia,
                    'valor_previsto': VALOR_PREVISTO_PADRAO,
                    'zerado': True,
                    'novo_saldo': novo_saldo
                }
            else:
                # Valor foi alterado, não zerar
                return {
                    'sucesso': True,
                    'dia': dia,
                    'valor_atual': valor_atual,
                    'zerado': False,
                    'mensagem': f'Valor já foi alterado para {self._format_currency(valor_atual)}'
                }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def zerar_diarios_nao_registrados_ontem(self) -> Dict[str, Any]:
        """Zera diários não registrados do dia anterior"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            return self.zerar_diario_nao_registrado(yesterday.day, yesterday.month)
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def registrar_entrada(self, valor: float, descricao: str = "Entrada") -> Dict[str, Any]:
        """Registra entrada na coluna 'Entrada'"""
        try:
            month_data = self._get_current_month_data()
            
            # Adicionar à entrada atual
            nova_entrada = month_data['entrada'] + valor
            
            # Atualizar célula
            self._set_cell_value(month_data['row'], month_data['col_entrada'], self._format_currency(nova_entrada))
            
            # NÃO atualizar saldo - a planilha calcula automaticamente via fórmulas
            # A fórmula da planilha: =(B3)-(C3+D3) já faz o cálculo
            # Apenas atualizar a entrada, a planilha recalcula o saldo automaticamente
            
            # Ler saldo atualizado (calculado pela planilha)
            saldo_atual = self._parse_currency(self._get_cell_value(month_data['row'], month_data['col_saldo']))
            
            return {
                'sucesso': True,
                'saldo_atual': saldo_atual
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def registrar_saida_fixa(self, valor: float, descricao: str = "Saída fixa") -> Dict[str, Any]:
        """Registra saída fixa na coluna 'Saída'"""
        try:
            month_data = self._get_current_month_data()
            
            # Adicionar à saída atual
            nova_saida = month_data['saida'] + valor
            
            # Atualizar célula
            self._set_cell_value(month_data['row'], month_data['col_saida'], self._format_currency(nova_saida))
            
            # NÃO atualizar saldo - a planilha calcula automaticamente via fórmulas
            # A fórmula da planilha: =(B3)-(C3+D3) já faz o cálculo
            # Apenas atualizar a saída, a planilha recalcula o saldo automaticamente
            
            # Ler saldo atualizado (calculado pela planilha)
            saldo_atual = self._parse_currency(self._get_cell_value(month_data['row'], month_data['col_saldo']))
            
            return {
                'sucesso': True,
                'saldo_atual': saldo_atual
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def obter_status_atual(self) -> Dict[str, Any]:
        """Obtém status financeiro atual"""
        try:
            month_data = self._get_current_month_data()
            
            # Saldo do dia atual
            saldo = month_data['saldo']
            
            # Gasto diário do dia atual
            gasto_diario = month_data['diario']
            
            # Ler totais acumulados do mês (linha 38 da planilha)
            now = datetime.now()
            month = now.month
            col_offset = self._get_month_column_offset(month)
            
            # Linha 38 = totais do mês (índice 37 em 0-based, mas gspread é 1-based = linha 38)
            total_row = 37  # 0-based, então linha 38 no gspread
            total_entrada = self._parse_currency(self._get_cell_value(total_row, col_offset + 1))  # Coluna Entrada
            total_saida = self._parse_currency(self._get_cell_value(total_row, col_offset + 2))     # Coluna Saída
            total_diario = self._parse_currency(self._get_cell_value(total_row, col_offset + 3))   # Coluna Diário
            
            # Se não encontrou na linha 38, tentar linha 37 (pode variar)
            if total_entrada == 0 and total_saida == 0:
                total_row = 36
                total_entrada = self._parse_currency(self._get_cell_value(total_row, col_offset + 1))
                total_saida = self._parse_currency(self._get_cell_value(total_row, col_offset + 2))
                total_diario = self._parse_currency(self._get_cell_value(total_row, col_offset + 3))
            
            # Calcular performance usando totais do mês
            # Performance = Entradas Totais - Saídas Totais - Diário Total
            performance = total_entrada - total_saida - total_diario
            
            # Calcular limite diário sugerido
            # Método Breno: usar valor previsto da planilha (ex: R$ 50/dia)
            # Se não houver previsto, calcular baseado na performance restante
            VALOR_PREVISTO_PADRAO = 50.0
            days_in_month = (datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day
            days_remaining = days_in_month - now.day + 1
            
            # Tentar ler valor previsto do dia atual (se ainda não foi alterado)
            diario_previsto = self._parse_currency(self._get_cell_value(month_data['row'], month_data['col_diario']))
            
            # Se o valor atual é o previsto padrão (ou próximo), usar esse valor
            if abs(diario_previsto - VALOR_PREVISTO_PADRAO) < 0.01:
                limite_diario = VALOR_PREVISTO_PADRAO
            elif days_remaining > 0 and performance > 0:
                # Se já foi alterado, calcular baseado na performance restante
                limite_diario = performance / days_remaining
            else:
                limite_diario = 0
            
            # Calcular semáforo
            semaforo_info = self._calculate_semaforo(saldo, performance, gasto_diario, limite_diario)
            
            return {
                'saldo': saldo,
                'gasto_diario': gasto_diario,
                'entrada': total_entrada,  # Total do mês
                'saida': total_saida,      # Total do mês
                'diario_total': total_diario,  # Total do mês
                'performance': performance,
                'limite_diario': limite_diario,
                'semaforo': semaforo_info['semaforo'],
                'status': semaforo_info['status'],
                'status_text': semaforo_info['status_text']
            }
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"ERRO em obter_status_atual: {error_msg}")
            return {
                'erro': str(e),
                'saldo': 0.0,
                'gasto_diario': 0.0,
                'entrada': 0.0,
                'saida': 0.0,
                'diario_total': 0.0,
                'performance': 0.0,
                'limite_diario': 0.0,
                'semaforo': '🟢',
                'status': 'erro',
                'status_text': f'Erro: {str(e)}'
            }
    
    def calcular_projecao_futura(self, meses_futuros: int = 6) -> Dict[str, Any]:
        """
        Calcula projeção de saldo futuro baseado em valores previstos da planilha
        Considera entradas, saídas e diários previstos para os próximos meses
        
        Args:
            meses_futuros: Quantidade de meses futuros para projetar (padrão: 6)
        
        Returns:
            Dict com projeções mês a mês e alertas
        """
        try:
            now = datetime.now()
            mes_atual = now.month
            ano_atual = now.year
            
            # Obter saldo atual do mês atual
            status_atual = self.obter_status_atual()
            saldo_inicial = status_atual.get('saldo', 0.0)
            
            projecoes = []
            alertas = []
            saldo_acumulado = saldo_inicial
            
            for i in range(1, meses_futuros + 1):
                # Calcular mês futuro
                mes_futuro = mes_atual + i
                ano_futuro = ano_atual
                
                # Ajustar ano se passar de dezembro
                while mes_futuro > 12:
                    mes_futuro -= 12
                    ano_futuro += 1
                
                col_offset = self._get_month_column_offset(mes_futuro)
                
                # Ler totais previstos do mês (linha 38 ou 37)
                total_row = 37
                entrada_prevista = self._parse_currency(self._get_cell_value(total_row, col_offset + 1))
                saida_prevista = self._parse_currency(self._get_cell_value(total_row, col_offset + 2))
                diario_previsto = self._parse_currency(self._get_cell_value(total_row, col_offset + 3))
                
                # Se não encontrou, tentar linha 36
                if entrada_prevista == 0 and saida_prevista == 0:
                    total_row = 36
                    entrada_prevista = self._parse_currency(self._get_cell_value(total_row, col_offset + 1))
                    saida_prevista = self._parse_currency(self._get_cell_value(total_row, col_offset + 2))
                    diario_previsto = self._parse_currency(self._get_cell_value(total_row, col_offset + 3))
                
                # Calcular performance prevista do mês
                performance_prevista = entrada_prevista - saida_prevista - diario_previsto
                
                # Saldo final do mês = saldo inicial + performance
                saldo_final = saldo_acumulado + performance_prevista
                
                # Nome do mês
                nome_mes = self.month_names.get(mes_futuro, f'Mês {mes_futuro}')
                
                projecao = {
                    'mes': mes_futuro,
                    'ano': ano_futuro,
                    'nome_mes': nome_mes,
                    'entrada_prevista': entrada_prevista,
                    'saida_prevista': saida_prevista,
                    'diario_previsto': diario_previsto,
                    'performance_prevista': performance_prevista,
                    'saldo_inicial': saldo_acumulado,
                    'saldo_final': saldo_final,
                    'negativo': saldo_final < 0
                }
                
                projecoes.append(projecao)
                
                # Gerar alerta se ficar negativo
                if saldo_final < 0:
                    alertas.append({
                        'mes': nome_mes,
                        'ano': ano_futuro,
                        'saldo_projetado': saldo_final,
                        'severidade': 'alta' if saldo_final < -1000 else 'media',
                        'mensagem': f'⚠️ Projeção indica saldo negativo em {nome_mes}/{ano_futuro}: {self._format_currency(saldo_final)}'
                    })
                
                # Atualizar saldo acumulado para próximo mês
                saldo_acumulado = saldo_final
            
            return {
                'sucesso': True,
                'saldo_atual': saldo_inicial,
                'mes_atual': self.month_names.get(mes_atual, f'Mês {mes_atual}'),
                'ano_atual': ano_atual,
                'projecoes': projecoes,
                'alertas': alertas,
                'total_alertas': len(alertas),
                'meses_projetados': meses_futuros
            }
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"ERRO em calcular_projecao_futura: {error_msg}")
            return {
                'sucesso': False,
                'erro': str(e),
                'projecoes': [],
                'alertas': []
            }