import 'package:flutter/material.dart';

/// Cores do sistema baseadas no método Breno
class AppColors {
  // Cores primárias
  static const Color primary = Color(0xFF1a227f);
  static const Color primaryLight = Color(0xFF2d3a9f);
  static const Color primaryDark = Color(0xFF0f155f);
  
  // Backgrounds
  static const Color backgroundLight = Color(0xFFf6f6f8);
  static const Color backgroundDark = Color(0xFF121320);
  
  // Semáforo financeiro
  static const Color budgetSafe = Color(0xFF10b981);      // Verde
  static const Color budgetWarning = Color(0xFFf59e0b);   // Amarelo
  static const Color budgetDanger = Color(0xFFef4444);    // Vermelho
  
  // Cores de transação
  static const Color income = Color(0xFF10b981);          // Verde (receita)
  static const Color expense = Color(0xFFef4444);          // Vermelho (despesa)
  
  // Cores de categoria
  static const Color categoryAlimentacao = Color(0xFFf59e0b);
  static const Color categoryMoradia = Color(0xFFef4444);
  static const Color categoryLazer = Color(0xFF10b981);
  static const Color categoryTransporte = Color(0xFF3b82f6);
  static const Color categorySaude = Color(0xFF8b5cf6);
  
  // Cores neutras
  static const Color textPrimary = Color(0xFF121217);
  static const Color textSecondary = Color(0xFF666985);
  static const Color border = Color(0xFFe5e7eb);
  
  /// Retorna cor do semáforo baseado no status
  static Color getTrafficLightColor(String status) {
    switch (status) {
      case 'green':
        return budgetSafe;
      case 'yellow':
        return budgetWarning;
      case 'red':
        return budgetDanger;
      default:
        return textSecondary;
    }
  }
  
  /// Retorna cor de categoria
  static Color getCategoryColor(String? category) {
    if (category == null) return textSecondary;
    
    switch (category.toLowerCase()) {
      case 'alimentação':
      case 'alimentacao':
        return categoryAlimentacao;
      case 'moradia':
        return categoryMoradia;
      case 'lazer':
        return categoryLazer;
      case 'transporte':
        return categoryTransporte;
      case 'saúde':
      case 'saude':
        return categorySaude;
      default:
        return textSecondary;
    }
  }
  
  /// Retorna cor de ícone de categoria
  static Color getCategoryIconColor(String? category) {
    final color = getCategoryColor(category);
    return color.withOpacity(0.8);
  }
  
  /// Retorna cor de fundo de categoria
  static Color getCategoryBackgroundColor(String? category) {
    final color = getCategoryColor(category);
    return color.withOpacity(0.1);
  }
}
