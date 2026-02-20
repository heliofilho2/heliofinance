import 'package:flutter/material.dart';
import '../utils/colors.dart';

/// Widget que mostra cor do saldo baseado no valor
class BalanceColorIndicator extends StatelessWidget {
  final double balance;
  final double size;

  const BalanceColorIndicator({
    super.key,
    required this.balance,
    this.size = 12,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: _getBalanceColor(balance),
        shape: BoxShape.circle,
      ),
    );
  }

  static Color _getBalanceColor(double balance) {
    if (balance < 0) return AppColors.budgetDanger; // Vermelho (negativo)
    if (balance < 100) return Colors.red[300]!; // Vermelho claro (perto de zero)
    if (balance < 500) return AppColors.budgetWarning; // Amarelo (pouco)
    if (balance < 2000) return Colors.green[300]!; // Verde claro
    return AppColors.budgetSafe; // Verde escuro
  }

  static Color getBalanceColor(double balance) {
    return _getBalanceColor(balance);
  }
}
