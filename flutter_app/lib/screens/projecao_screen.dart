import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';

class ProjecaoScreen extends StatefulWidget {
  const ProjecaoScreen({super.key});

  @override
  State<ProjecaoScreen> createState() => _ProjecaoScreenState();
}

class _ProjecaoScreenState extends State<ProjecaoScreen> {
  Map<String, dynamic>? _projecao;
  bool _isLoading = true;
  String? _error;
  int _mesesSelecionados = 6;

  @override
  void initState() {
    super.initState();
    _loadProjecao();
  }

  Future<void> _loadProjecao() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = ApiService();
      final projecao = await apiService.getProjecao(meses: _mesesSelecionados);
      setState(() {
        _projecao = projecao;
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
    final sign = value < 0 ? '-' : '';
    final absValue = value.abs();
    return '$sign R\$ ${absValue.toStringAsFixed(2).replaceAll('.', ',')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: const Text('Projeção Futura'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          PopupMenuButton<int>(
            icon: const Icon(Icons.tune),
            onSelected: (value) {
              setState(() {
                _mesesSelecionados = value;
              });
              _loadProjecao();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 3, child: Text('3 meses')),
              const PopupMenuItem(value: 6, child: Text('6 meses')),
              const PopupMenuItem(value: 12, child: Text('12 meses')),
            ],
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorState()
              : _buildProjecao(),
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
            'Erro ao carregar projeção',
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
            onPressed: _loadProjecao,
            child: const Text('Tentar novamente'),
          ),
        ],
      ),
    );
  }

  Widget _buildProjecao() {
    if (_projecao == null || !(_projecao!['sucesso'] as bool)) {
      return Center(
        child: Text(
          _projecao?['erro'] ?? 'Erro ao calcular projeção',
          style: GoogleFonts.inter(fontSize: 14, color: Colors.grey),
        ),
      );
    }

    final saldoAtual = (_projecao!['saldo_atual'] as num).toDouble();
    final mesAtual = _projecao!['mes_atual'] as String;
    final projecoes = _projecao!['projecoes'] as List<dynamic>;
    final alertas = _projecao!['alertas'] as List<dynamic>;

    return RefreshIndicator(
      onRefresh: _loadProjecao,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Saldo Atual
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '💰 Saldo Atual',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$mesAtual: ${_formatCurrency(saldoAtual)}',
                    style: GoogleFonts.inter(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: saldoAtual >= 0 ? Colors.green : Colors.red,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Alertas
            if (alertas.isNotEmpty) ...[
              _buildCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.warning_amber_rounded, color: Colors.orange.shade700),
                        const SizedBox(width: 8),
                        Text(
                          '⚠️ Alertas de Risco',
                          style: GoogleFonts.inter(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.orange.shade900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    ...alertas.map((alerta) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        alerta['mensagem'] ?? '',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    )),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Projeções
            Text(
              '📊 Projeções dos Próximos ${projecoes.length} Meses',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade900,
              ),
            ),
            const SizedBox(height: 12),
            ...projecoes.map((proj) => _buildProjecaoCard(proj)),
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

  Widget _buildProjecaoCard(Map<String, dynamic> proj) {
    final negativo = proj['negativo'] as bool;
    final saldoFinal = (proj['saldo_final'] as num).toDouble();
    final nomeMes = proj['nome_mes'] as String;
    final ano = proj['ano'] as int;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: negativo ? Colors.red.shade50 : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: negativo ? Colors.red.shade300 : Colors.grey.shade200,
          width: negativo ? 2 : 1,
        ),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$nomeMes/$ano',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade900,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: negativo ? Colors.red.shade100 : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  negativo ? '🔴 Negativo' : '🟢 Positivo',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: negativo ? Colors.red.shade900 : Colors.green.shade900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildProjecaoRow('Entrada prevista', (proj['entrada_prevista'] as num).toDouble(), Colors.green),
          const SizedBox(height: 8),
          _buildProjecaoRow('Saída prevista', (proj['saida_prevista'] as num).toDouble(), Colors.blue),
          const SizedBox(height: 8),
          _buildProjecaoRow('Diário previsto', (proj['diario_previsto'] as num).toDouble(), Colors.orange),
          const Divider(height: 16),
          _buildProjecaoRow('Performance prevista', (proj['performance_prevista'] as num).toDouble(), 
              (proj['performance_prevista'] as num).toDouble() >= 0 ? Colors.green : Colors.red, isBold: true),
          const SizedBox(height: 8),
          _buildProjecaoRow('Saldo final', saldoFinal, negativo ? Colors.red : Colors.green, isBold: true, isLarge: true),
        ],
      ),
    );
  }

  Widget _buildProjecaoRow(String label, double value, Color color, {bool isBold = false, bool isLarge = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: isLarge ? 16 : 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            color: Colors.grey.shade700,
          ),
        ),
        Text(
          _formatCurrency(value),
          style: GoogleFonts.inter(
            fontSize: isLarge ? 18 : 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }
}
