import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';

class RelatorioSemanalScreen extends StatefulWidget {
  const RelatorioSemanalScreen({super.key});

  @override
  State<RelatorioSemanalScreen> createState() => _RelatorioSemanalScreenState();
}

class _RelatorioSemanalScreenState extends State<RelatorioSemanalScreen> {
  Map<String, dynamic>? _relatorio;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadRelatorio();
  }

  Future<void> _loadRelatorio() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = ApiService();
      final relatorio = await apiService.getRelatorioSemanal();
      setState(() {
        _relatorio = relatorio;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  String _formatCurrency(double value) {
    return 'R\$ ${value.toStringAsFixed(2).replaceAll('.', ',')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: const Text('Relatório Semanal'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorState()
              : _buildRelatorio(),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            'Erro ao carregar relatório',
            style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            _error!,
            style: GoogleFonts.inter(fontSize: 14, color: Colors.grey),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadRelatorio,
            child: const Text('Tentar novamente'),
          ),
        ],
      ),
    );
  }

  Widget _buildRelatorio() {
    if (_relatorio == null) return const SizedBox.shrink();

    final periodo = _relatorio!['periodo'] as Map<String, dynamic>;
    final top5 = _relatorio!['top_5_gastos'] as List<dynamic>;
    final economia = (_relatorio!['economia_vs_previsto'] as num).toDouble();
    final performance = (_relatorio!['performance_semana'] as num).toDouble();
    final totalEntrada = (_relatorio!['total_entrada'] as num).toDouble();
    final totalSaida = (_relatorio!['total_saida'] as num).toDouble();

    return RefreshIndicator(
      onRefresh: _loadRelatorio,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Período
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '📅 Período',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${periodo['inicio']} a ${periodo['fim']}',
                    style: GoogleFonts.inter(fontSize: 14, color: Colors.grey.shade700),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Resumo Financeiro
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '💰 Resumo Financeiro',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildSummaryRow('Entradas', totalEntrada, Colors.green),
                  const SizedBox(height: 12),
                  _buildSummaryRow('Saídas', totalSaida, Colors.blue),
                  const Divider(height: 24),
                  _buildSummaryRow('Performance', performance, performance >= 0 ? Colors.green : Colors.red, isBold: true),
                  const SizedBox(height: 12),
                  _buildSummaryRow('Economia vs Previsto', economia, economia >= 0 ? Colors.green : Colors.orange),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Top 5 Gastos
            if (top5.isNotEmpty) ...[
              _buildCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🏆 Top 5 Gastos da Semana',
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    ...top5.asMap().entries.map((entry) {
                      final index = entry.key;
                      final gasto = entry.value as Map<String, dynamic>;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Row(
                          children: [
                            Container(
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.1),
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Text(
                                  '${index + 1}',
                                  style: GoogleFonts.inter(
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.primary,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    gasto['dia'] ?? '',
                                    style: GoogleFonts.inter(
                                      fontSize: 12,
                                      color: Colors.grey.shade600,
                                    ),
                                  ),
                                  Text(
                                    gasto['descricao'] ?? 'Gasto',
                                    style: GoogleFonts.inter(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              _formatCurrency((gasto['valor'] as num).toDouble()),
                              style: GoogleFonts.inter(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCard({required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );
  }

  Widget _buildSummaryRow(String label, double value, Color color, {bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: isBold ? 16 : 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            color: Colors.grey.shade700,
          ),
        ),
        Text(
          _formatCurrency(value),
          style: GoogleFonts.inter(
            fontSize: isBold ? 16 : 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }
}
