"""
Serviço de categorização de gastos baseado em palavras-chave
"""
from typing import Dict, List, Optional
import re


class CategorizationService:
    """Categoriza gastos automaticamente baseado em descrição"""
    
    # Mapeamento de palavras-chave para categorias
    CATEGORIES = {
        'Alimentação': [
            'mercado', 'supermercado', 'padaria', 'açougue', 'peixaria',
            'restaurante', 'lanchonete', 'pizzaria', 'delivery', 'ifood',
            'uber eats', 'rappi', 'café', 'cafezinho', 'almoço', 'jantar',
            'comida', 'alimento', 'feira', 'hortifruti'
        ],
        'Transporte': [
            'uber', 'taxi', '99', 'cabify', 'gasolina', 'combustível',
            'posto', 'estacionamento', 'pedágio', 'ônibus', 'metrô',
            'bilhete', 'passagem', 'transporte', 'viagem', 'passagem aérea'
        ],
        'Saúde': [
            'farmacia', 'farmácia', 'medicamento', 'remédio', 'médico',
            'dentista', 'clínica', 'hospital', 'exame', 'laboratório',
            'plano de saúde', 'unimed', 'amil', 'sulamerica'
        ],
        'Educação': [
            'curso', 'faculdade', 'universidade', 'escola', 'material escolar',
            'livro', 'apostila', 'mensalidade', 'matrícula'
        ],
        'Lazer': [
            'cinema', 'show', 'festival', 'ingresso', 'jogo', 'viagem',
            'passeio', 'parque', 'praia', 'hotel', 'hospedagem'
        ],
        'Vestuário': [
            'roupa', 'camisa', 'calça', 'sapato', 'tênis', 'acessório',
            'loja', 'shopping', 'moda', 'vestuário'
        ],
        'Serviços': [
            'internet', 'net', 'vivo', 'claro', 'oi', 'tim', 'telefone',
            'celular', 'energia', 'luz', 'água', 'gás', 'condomínio',
            'aluguel', 'iptu', 'iptu', 'seguro', 'banco', 'tarifa'
        ],
        'Outros': []  # Categoria padrão
    }
    
    def __init__(self):
        """Inicializa o serviço de categorização"""
        # Criar regex patterns para cada categoria
        self.patterns = {}
        for categoria, palavras in self.CATEGORIES.items():
            if palavras:
                # Criar pattern case-insensitive
                pattern = '|'.join([re.escape(p) for p in palavras])
                self.patterns[categoria] = re.compile(pattern, re.IGNORECASE)
    
    def categorizar(self, descricao: str) -> str:
        """
        Categoriza uma descrição de gasto
        
        Args:
            descricao: Descrição do gasto
            
        Returns:
            Nome da categoria
        """
        descricao_lower = descricao.lower().strip()
        
        # Verificar cada categoria
        for categoria, pattern in self.patterns.items():
            if pattern.search(descricao_lower):
                return categoria
        
        # Se não encontrou, retornar "Outros"
        return 'Outros'
    
    def listar_categorias(self) -> List[str]:
        """Retorna lista de todas as categorias"""
        return list(self.CATEGORIES.keys())
    
    def adicionar_palavra_chave(self, categoria: str, palavra: str) -> bool:
        """
        Adiciona uma nova palavra-chave para uma categoria
        
        Args:
            categoria: Nome da categoria
            palavra: Palavra-chave a adicionar
            
        Returns:
            True se adicionado com sucesso, False se categoria não existe
        """
        if categoria not in self.CATEGORIES:
            return False
        
        if palavra.lower() not in [p.lower() for p in self.CATEGORIES[categoria]]:
            self.CATEGORIES[categoria].append(palavra.lower())
            # Recriar pattern
            pattern = '|'.join([re.escape(p) for p in self.CATEGORIES[categoria]])
            self.patterns[categoria] = re.compile(pattern, re.IGNORECASE)
        
        return True
    
    def obter_estatisticas_categoria(self, transacoes: List[Dict]) -> Dict[str, float]:
        """
        Calcula estatísticas por categoria
        
        Args:
            transacoes: Lista de transações com 'valor' e 'categoria'
            
        Returns:
            Dicionário com total por categoria
        """
        stats = {}
        for transacao in transacoes:
            categoria = transacao.get('categoria', 'Outros')
            valor = transacao.get('valor', 0)
            stats[categoria] = stats.get(categoria, 0) + valor
        return stats
