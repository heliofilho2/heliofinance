import 'package:intl/intl.dart';

/// Formatadores de dados
class Formatters {
  /// Formata valor monetário
  static String currency(double value) {
    final formatter = NumberFormat.currency(
      locale: 'pt_BR',
      symbol: 'R\$',
      decimalDigits: 2,
    );
    return formatter.format(value);
  }

  /// Formata data
  static String date(DateTime date) {
    return DateFormat('dd/MM/yyyy').format(date);
  }

  /// Formata data e hora
  static String dateTime(DateTime date) {
    return DateFormat('dd/MM/yyyy HH:mm').format(date);
  }

  /// Formata data relativa (hoje, ontem, etc)
  static String relativeDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      final dateOnly = DateTime(date.year, date.month, date.day);
      
      final difference = today.difference(dateOnly).inDays;
      
      if (difference == 0) {
        return 'Hoje, ${DateFormat('HH:mm').format(date)}';
      } else if (difference == 1) {
        return 'Ontem, ${DateFormat('HH:mm').format(date)}';
      } else if (difference < 7) {
        return '${difference} dias atrás';
      } else {
        return DateFormat('dd MMM', 'pt_BR').format(date);
      }
    } catch (e) {
      return dateString;
    }
  }

  /// Formata porcentagem
  static String percentage(double value) {
    return '${value.toStringAsFixed(1)}%';
  }

  /// Formata número compacto
  static String compactNumber(double value) {
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}M';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    }
    return value.toStringAsFixed(0);
  }
}
