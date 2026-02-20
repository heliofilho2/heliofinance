import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';

class RelatorioMensalScreen extends StatefulWidget {
  const RelatorioMensalScreen({super.key});

  @override
  State<RelatorioMensalScreen> createState() => _RelatorioMensalScreenState();
}

class _RelatorioMensalScreenState extends State<RelatorioMensalScreen> {
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
      final relatorio = await apiService.getRelatorioMensal();
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

  String _formatPercent(double value) {
    final sign = value >= 0 ? '+' : '';
    return '$sign${value.toStringAsFixed(1)}%';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: const Text('Relatório Mensal'),
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

    final mesAtual = _relatorio!['mes_atual'] as Map<String, dynamic>;
    final mesAnterior = _relatorio!['mes_anterior'] as Map<String, dynamic>;
    final comparativo = _relatorio!['comparativo'] as Map<String, dynamic>;
    final insights = _relatorio!['insights'] as List<dynamic>;

    final dadosAtual = mesAtual['dados'] as Map<String, dynamic>;
    final dadosAnterior = mesAnterior['dados'] as Map<String, dynamic>;

    return RefreshIndicator(
      onRefresh: _loadRelatorio,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Mês Atual
            _buildCard(
              title: '📊 Mês Atual',
              child: Column(
                children: [
                  _buildSummaryRow('Entradas', (dadosAtual['total_entrada'] as num).toDouble(), Colors.green),
                  const SizedBox(height: 12),
                  _buildSummaryRow('Saídas', (dadosAtual['total_saida'] as num).toDouble(), Colors.blue),
                  const SizedBox(height: 12),
                  _buildSummaryRow('Gastos Diários', (dadosAtual['total_diario'] as num).toDouble(), Colors.orange),
                  const Divider(height: 24),
                  _buildSummaryRow(
                    'Performance',
                    (dadosAtual['performance'] as num).toDouble(),
                    (dadosAtual['performance'] as num).toDouble() >= 0 ? Colors.green : Colors.red,
                    isBold: true,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Comparativo
            _buildCard(
              title: '📈 Comparativo com Mês Anterior',
              child: Column(
                children: [
                  _buildComparativoRow('Performance', comparativo['performance']),
                  const SizedBox(height: 12),
                  _buildComparativoRow('Entradas', comparativo['entrada']),
                  const SizedBox(height: 12),
                  _buildComparativoRow('Saídas', comparativo['saida']),
                  const SizedBox(height: 12),
                  _buildComparativoRow('Gastos Diários', comparativo['diario']),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Insights
            if (insights.isNotEmpty) ...[
              _buildCard(
                title: '💡 Insights Automáticos',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: insights.map((insight) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('• ', style: TextStyle(fontSize: 18)),
                          Expanded(
                            child: Text(
                              insight as String,
                              style: GoogleFonts.inter(
                                fontSize: 14,
                                color: Colors.grey.shade700,
                                height: 1.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCard({String? title, required Widget child}) {
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title != null) ...[
            Text(
              title,
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
          ],
          child,
        ],
      ),
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

  Widget _buildComparativoRow(String label, Map<String, dynamic> dados) {
    final variacao = (dados['variacao'] as num).toDouble();
    final variacaoPercent = (dados['variacao_percentual'] as num).toDouble();
    final isPositive = variacao >= 0;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 14,
            color: Colors.grey.shade700,
          ),
        ),
        Row(
          children: [
            Text(
              _formatCurrency(variacao),
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: isPositive ? Colors.green : Colors.red,
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: isPositive ? Colors.green.shade50 : Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                _formatPercent(variacaoPercent),
                style: GoogleFonts.inter(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: isPositive ? Colors.green.shade700 : Colors.red.shade700,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
