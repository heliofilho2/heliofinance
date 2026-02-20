import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/colors.dart';
import '../models/dashboard_model.dart';

/// Indicador de Semáforo Financeiro
class TrafficLightIndicator extends StatelessWidget {
  final TrafficLight trafficLight;
  final double? performance;

  const TrafficLightIndicator({
    super.key,
    required this.trafficLight,
    this.performance,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppColors.getTrafficLightColor(trafficLight.status);
    final icon = _getIcon(trafficLight.status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  trafficLight.label,
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                if (performance != null)
                  Text(
                    'Performance: ${performance! >= 0 ? '+' : ''}${performance!.toStringAsFixed(2)}',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getIcon(String status) {
    switch (status) {
      case 'green':
        return Icons.check_circle;
      case 'yellow':
        return Icons.warning;
      case 'red':
        return Icons.error;
      default:
        return Icons.help;
    }
  }
}
