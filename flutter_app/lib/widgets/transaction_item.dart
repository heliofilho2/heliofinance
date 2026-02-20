import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../models/dashboard_model.dart';

/// Item de Transação Recente (inspirado no HTML)
class TransactionItem extends StatelessWidget {
  final RecentTransaction transaction;

  const TransactionItem({
    super.key,
    required this.transaction,
  });

  @override
  Widget build(BuildContext context) {
    final isIncome = transaction.amount > 0;
    final icon = _getIcon(transaction.type, transaction.category);
    final iconColor = _getIconColor(transaction.type, transaction.category);
    final iconBgColor = _getIconBgColor(transaction.type, transaction.category);
    final amountColor = isIncome ? AppColors.income : AppColors.expense;
    final amountPrefix = isIncome ? '+' : '-';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Ícone
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: iconBgColor,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: iconColor,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          // Informações
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  transaction.description,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[900],
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    if (transaction.category != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.getCategoryBackgroundColor(transaction.category),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          transaction.category!.toUpperCase(),
                          style: GoogleFonts.inter(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: AppColors.getCategoryColor(transaction.category),
                          ),
                        ),
                      ),
                    if (transaction.category != null) const SizedBox(width: 6),
                    Text(
                      Formatters.relativeDate(transaction.date),
                      style: GoogleFonts.inter(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Valor
          Text(
            '$amountPrefix ${Formatters.currency(transaction.amount.abs())}',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: amountColor,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getIcon(String type, String? category) {
    switch (type) {
      case 'income':
        return Icons.account_balance_wallet;
      case 'fixed':
        return Icons.home;
      case 'variable':
        if (category?.toLowerCase().contains('mercado') ?? false) {
          return Icons.shopping_cart;
        }
        if (category?.toLowerCase().contains('restaurante') ?? false) {
          return Icons.restaurant;
        }
        return Icons.payments;
      default:
        return Icons.receipt;
    }
  }

  Color _getIconColor(String type, String? category) {
    if (type == 'income') return AppColors.income;
    return AppColors.getCategoryIconColor(category);
  }

  Color _getIconBgColor(String type, String? category) {
    if (type == 'income') {
      return AppColors.income.withOpacity(0.1);
    }
    return AppColors.getCategoryBackgroundColor(category);
  }
}
