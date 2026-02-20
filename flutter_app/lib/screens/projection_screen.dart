import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../widgets/projection_chart.dart';
import '../models/dashboard_model.dart';

/// Tela de Projeção e Previsão Financeira
class ProjectionScreen extends StatefulWidget {
  const ProjectionScreen({super.key});

  @override
  State<ProjectionScreen> createState() => _ProjectionScreenState();
}

class _ProjectionScreenState extends State<ProjectionScreen> {
  final _apiService = ApiService();
  DashboardModel? _dashboard;
  bool _isLoading = true;
  int _monthsToShow = 6;

  @override
  void initState() {
    super.initState();
    _loadProjections();
  }

  Future<void> _loadProjections() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final dashboard = await _apiService.getDashboard();
      setState(() {
        _dashboard = dashboard;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Projeção Financeira'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadProjections,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _dashboard == null
              ? const Center(child: Text('Sem dados'))
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    final projections = _dashboard!.projections.take(_monthsToShow).toList();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Seletor de meses
          _buildMonthsSelector(),
          const SizedBox(height: 24),
          // Gráfico de Saldo
          ProjectionChart(
            projections: projections,
            showBalance: true,
          ),
          const SizedBox(height: 24),
          // Gráfico de Performance
          ProjectionChart(
            projections: projections,
            showBalance: false,
          ),
          const SizedBox(height: 24),
          // Tabela de Projeções
          _buildProjectionsTable(projections),
        ],
      ),
    );
  }

  Widget _buildMonthsSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Período de Projeção',
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildMonthButton(6, '6 meses'),
              const SizedBox(width: 8),
              _buildMonthButton(12, '12 meses'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMonthButton(int months, String label) {
    final isSelected = _monthsToShow == months;
    return Expanded(
      child: ElevatedButton(
        onPressed: () {
          setState(() {
            _monthsToShow = months;
          });
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: isSelected ? AppColors.primary : Colors.grey[200],
          foregroundColor: isSelected ? Colors.white : Colors.grey[700],
          padding: const EdgeInsets.symmetric(vertical: 12),
        ),
        child: Text(label),
      ),
    );
  }

  Widget _buildProjectionsTable(List<Projection> projections) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Detalhamento Mensal',
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ...projections.map((p) => _buildProjectionRow(p)),
        ],
      ),
    );
  }

  Widget _buildProjectionRow(Projection projection) {
    final statusColor = AppColors.getTrafficLightColor(
      projection.performance >= 0 ? 'green' : (projection.performance > -500 ? 'yellow' : 'red'),
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                projection.monthName,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                Formatters.currency(projection.balance),
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: statusColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildProjectionDetail('Entradas', Formatters.currency(projection.entradas), AppColors.income),
              _buildProjectionDetail('Saídas', Formatters.currency(projection.saidas), AppColors.expense),
              _buildProjectionDetail('Performance', Formatters.currency(projection.performance), statusColor),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProjectionDetail(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 10,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
