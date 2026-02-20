"""
Parser de comandos para bot Telegram
"""
from typing import Optional, Dict, Any
from datetime import datetime


class CommandParser:
    """Parser simples para comandos rápidos"""
    
    def parse(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Parse de comandos tipo:
        - "mercado 87" -> gasto variável
        - "recebi cliente 2500" -> receita
        - "aluguel 1200" -> gasto fixo
        - "simular emprestimo 10000 18 0.02" -> simulação de empréstimo
        - "simular compra 4200 10" -> simulação de compra parcelada
        """
        command = command.strip().lower()
        
        # Simulação de empréstimo
        if command.startswith('simular emprestimo') or command.startswith('simular empréstimo'):
            parts = command.split()
            if len(parts) >= 3:
                try:
                    valor = float(parts[2])
                    prazo = int(parts[3]) if len(parts) > 3 else 24
                    taxa = float(parts[4]) if len(parts) > 4 else 0.035
                    return {
                        'type': 'loan_simulation',
                        'value': valor,
                        'term': prazo,
                        'monthly_rate': taxa
                    }
                except:
                    return None
        
        # Simulação de compra parcelada
        if command.startswith('simular compra'):
            parts = command.split()
            if len(parts) >= 4:
                try:
                    desc = parts[2]
                    valor = float(parts[3])
                    parcelas = int(parts[4]) if len(parts) > 4 else 1
                    return {
                        'type': 'purchase_simulation',
                        'description': desc,
                        'value': valor,
                        'installments': parcelas
                    }
                except:
                    return None
        
        # Receita
        if command.startswith('recebi') or command.startswith('recebido'):
            parts = command.split()
            if len(parts) >= 3:
                try:
                    desc = ' '.join(parts[1:-1])
                    valor = float(parts[-1])
                    return {
                        'type': 'income',
                        'description': desc,
                        'amount': abs(valor),
                        'category': self._infer_category(desc)
                    }
                except:
                    return None
        
        # Gasto fixo (palavras-chave)
        fixos_keywords = ['aluguel', 'luz', 'agua', 'água', 'internet', 'condominio', 'condomínio']
        is_fixo = any(command.startswith(kw) for kw in fixos_keywords)
        
        if is_fixo:
            parts = command.split()
            if len(parts) >= 2:
                try:
                    desc = parts[0]
                    valor = float(parts[1])
                    return {
                        'type': 'fixed',
                        'description': desc,
                        'amount': -abs(valor),
                        'category': self._infer_category(desc)
                    }
                except:
                    return None
        
        # Gasto variável (padrão)
        parts = command.split()
        if len(parts) >= 2:
            try:
                desc = ' '.join(parts[:-1])
                valor = float(parts[-1])
                return {
                    'type': 'variable',
                    'description': desc,
                    'amount': -abs(valor),
                    'category': self._infer_category(desc)
                }
            except:
                return None
        
        return None
    
    def _infer_category(self, description: str) -> str:
        """Infere categoria baseado na descrição"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['aluguel', 'condominio', 'condomínio']):
            return 'Moradia'
        elif any(word in desc_lower for word in ['luz', 'agua', 'água', 'internet', 'gás', 'gas']):
            return 'Utilidades'
        elif any(word in desc_lower for word in ['mercado', 'supermercado', 'padaria']):
            return 'Alimentação'
        elif any(word in desc_lower for word in ['uber', 'taxi', 'combustivel', 'combustível']):
            return 'Transporte'
        elif any(word in desc_lower for word in ['farmacia', 'farmácia', 'medico', 'médico']):
            return 'Saúde'
        elif 'recebi' in desc_lower or 'cliente' in desc_lower:
            return 'Renda PJ'
        else:
            return 'Outros'
