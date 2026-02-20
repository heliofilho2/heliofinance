import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../models/transaction_model.dart';

/// Tela de Impacto Futuro de Simulações
class ProjectionImpactScreen extends StatelessWidget {
  final List<ProjectionImpact> projections;
  final String title;

  const ProjectionImpactScreen({
    super.key,
    required this.projections,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Impacto nos Próximos Meses',
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            ...projections.map((p) => _buildImpactCard(p)),
          ],
        ),
      ),
    );
  }

  Widget _buildImpactCard(ProjectionImpact projection) {
    final statusColor = AppColors.getTrafficLightColor(projection.status);
    final balanceDiff = projection.balanceAfter - projection.balanceBefore;
    final perfDiff = projection.performanceAfter - projection.performanceBefore;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: statusColor.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: statusColor.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                projection.monthName,
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  projection.status.toUpperCase(),
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildComparisonRow(
            'Saldo',
            Formatters.currency(projection.balanceBefore),
            Formatters.currency(projection.balanceAfter),
            balanceDiff,
          ),
          const SizedBox(height: 12),
          _buildComparisonRow(
            'Performance',
            Formatters.currency(projection.performanceBefore),
            Formatters.currency(projection.performanceAfter),
            perfDiff,
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonRow(
    String label,
    String before,
    String after,
    double diff,
  ) {
    final diffColor = diff >= 0 ? AppColors.income : AppColors.expense;
    final diffPrefix = diff >= 0 ? '+' : '';

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Text(
                    'Antes: ',
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: Colors.grey[500],
                    ),
                  ),
                  Text(
                    before,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Row(
                children: [
                  Text(
                    'Depois: ',
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: Colors.grey[500],
                    ),
                  ),
                  Text(
                    after,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: diffColor,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: diffColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '$diffPrefix${Formatters.currency(diff.abs())}',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: diffColor,
            ),
          ),
        ),
      ],
    );
  }
}
