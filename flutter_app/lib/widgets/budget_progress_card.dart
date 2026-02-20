import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';

/// Card de Progresso de Orçamento (inspirado no HTML)
class BudgetProgressCard extends StatelessWidget {
  final String category;
  final double spent;
  final double limit;
  final Color? color;

  const BudgetProgressCard({
    super.key,
    required this.category,
    required this.spent,
    required this.limit,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (spent / limit * 100).clamp(0.0, 100.0);
    final progressColor = color ?? _getColorByPercentage(percentage);
    final statusText = _getStatusText(percentage);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  category,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${Formatters.currency(spent)} / ${Formatters.currency(limit)}',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            Text(
              statusText,
              style: GoogleFonts.inter(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: progressColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: percentage / 100,
            minHeight: 10,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(progressColor),
          ),
        ),
      ],
    );
  }

  Color _getColorByPercentage(double percentage) {
    if (percentage >= 90) return AppColors.budgetDanger;
    if (percentage >= 70) return AppColors.budgetWarning;
    return AppColors.budgetSafe;
  }

  String _getStatusText(double percentage) {
    return '${percentage.toStringAsFixed(0)}% usado';
  }
}
