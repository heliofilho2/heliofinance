import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';
import '../widgets/balance_card.dart';

/// Tela Principal de Dashboard (inspirada no HTML)
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _status;
  List<Map<String, dynamic>>? _alertas;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = ApiService();
      final status = await apiService.getStatus();
      final alertas = await apiService.getAlertas();
      
      setState(() {
        _status = status;
        _alertas = List<Map<String, dynamic>>.from(alertas);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? _buildErrorState()
                : _buildDashboard(),
      ),
      bottomNavigationBar: _buildBottomNav(),
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
            'Erro ao carregar dados',
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
            onPressed: _loadData,
            child: const Text('Tentar novamente'),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard() {
    if (_status == null) return const SizedBox.shrink();

    final saldo = (_status!['saldo'] as num).toDouble();
    final performance = (_status!['performance'] as num).toDouble();
    final semaforo = _status!['semaforo'] as String;
    final statusText = _status!['status_text'] as String;
    final gastoDiario = (_status!['gasto_diario'] as num).toDouble();
    final limiteDiario = (_status!['limite_diario'] as num).toDouble();
    final entrada = (_status!['entrada'] as num).toDouble();
    final saida = (_status!['saida'] as num).toDouble();
    final diarioTotal = (_status!['diario_total'] as num).toDouble();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            _buildHeader(),
            const SizedBox(height: 8),
            
            // Alertas (se houver)
            if (_alertas != null && _alertas!.isNotEmpty) ...[
              _buildAlertasSection(),
              const SizedBox(height: 16),
            ],
            
            // Card de Saldo
            BalanceCard(
              balance: saldo,
              savingsThisMonth: performance > 0 ? performance : null,
            ),
            const SizedBox(height: 16),
            
            // Semáforo
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: _buildTrafficLight(semaforo, statusText, performance),
            ),
            const SizedBox(height: 16),
            
            // Resumo do Mês
            _buildMonthSummary(entrada, saida, diarioTotal, performance),
            const SizedBox(height: 16),
            
            // Gasto Diário
            _buildDailyExpense(gastoDiario, limiteDiario),
            const SizedBox(height: 16),
            
            // Ações Rápidas
            _buildQuickActions(),
            const SizedBox(height: 80), // Espaço para bottom nav
          ],
        ),
      ),
    );
  }
  
  Widget _buildAlertasSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: Colors.orange.shade700),
              const SizedBox(width: 8),
              Text(
                'Alertas Ativos',
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange.shade900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ..._alertas!.take(3).map((alerta) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alerta['emoji'] ?? '⚠️',
                  style: const TextStyle(fontSize: 20),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    alerta['titulo'] ?? 'Alerta',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          )),
          if (_alertas!.length > 3)
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/alertas');
              },
              child: const Text('Ver todos os alertas'),
            ),
        ],
      ),
    );
  }
  
  Widget _buildTrafficLight(String semaforo, String statusText, double performance) {
    Color color;
    if (semaforo.contains('🟢')) {
      color = Colors.green;
    } else if (semaforo.contains('🟡')) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }
    
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
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: color, width: 3),
            ),
            child: Center(
              child: Text(
                semaforo,
                style: const TextStyle(fontSize: 32),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Status Financeiro',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  statusText,
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Performance: ${_formatCurrency(performance)}',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: performance >= 0 ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMonthSummary(double entrada, double saida, double diario, double performance) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
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
          Text(
            'Resumo do Mês',
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade900,
            ),
          ),
          const SizedBox(height: 16),
          _buildSummaryRow('💰 Entradas', entrada, Colors.green),
          const SizedBox(height: 12),
          _buildSummaryRow('💳 Saídas Fixas', saida, Colors.blue),
          const SizedBox(height: 12),
          _buildSummaryRow('🛒 Gastos Diários', diario, Colors.orange),
          const Divider(height: 24),
          _buildSummaryRow('📊 Performance', performance, performance >= 0 ? Colors.green : Colors.red, isBold: true),
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
  
  Widget _buildDailyExpense(double gastoDiario, double limiteDiario) {
    final percentual = limiteDiario > 0 ? (gastoDiario / limiteDiario) * 100 : 0;
    Color progressColor = Colors.green;
    if (percentual >= 100) {
      progressColor = Colors.red;
    } else if (percentual >= 80) {
      progressColor = Colors.orange;
    }
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Gasto Diário',
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade900,
                ),
              ),
              Text(
                '${percentual.toStringAsFixed(0)}%',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: progressColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LinearProgressIndicator(
            value: percentual / 100,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(progressColor),
            minHeight: 8,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Gasto hoje: ${_formatCurrency(gastoDiario)}',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
              Text(
                'Limite: ${_formatCurrency(limiteDiario)}',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  String _formatCurrency(double value) {
    return 'R\$ ${value.toStringAsFixed(2).replaceAll('.', ',')}';
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
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
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.primary.withOpacity(0.2),
                width: 2,
              ),
            ),
            child: const Icon(
              Icons.person,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Disciplina Financeira',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                    letterSpacing: 0.5,
                  ),
                ),
                Text(
                  'Olá, Helio Filho do Face',
                  style: GoogleFonts.inter(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[900],
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              Navigator.pushNamed(context, '/alertas');
            },
          ),
        ],
      ),
    );
  }


  Widget _buildQuickActions() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Ações Rápidas',
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade900,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildActionButton(
                icon: Icons.assessment,
                label: 'Relatório\nSemanal',
                onTap: () {
                  Navigator.pushNamed(context, '/relatorio-semanal');
                },
              ),
              _buildActionButton(
                icon: Icons.bar_chart,
                label: 'Relatório\nMensal',
                onTap: () {
                  Navigator.pushNamed(context, '/relatorio-mensal');
                },
              ),
              _buildActionButton(
                icon: Icons.warning_amber_rounded,
                label: 'Alertas',
                onTap: () {
                  Navigator.pushNamed(context, '/alertas');
                },
              ),
              _buildActionButton(
                icon: Icons.category,
                label: 'Categorias',
                onTap: () {
                  Navigator.pushNamed(context, '/categorias');
                },
              ),
              _buildActionButton(
                icon: Icons.trending_up,
                label: 'Projeção',
                onTap: () {
                  Navigator.pushNamed(context, '/projecao');
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey[200]!),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.02),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Icon(
              icon,
              color: AppColors.primary,
              size: 24,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Colors.grey[900],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(Icons.home, 'Início', true, () {}),
              _buildNavItem(Icons.assessment, 'Relatórios', false, () {
                Navigator.pushNamed(context, '/relatorio-semanal');
              }),
              _buildNavItem(Icons.warning_amber_rounded, 'Alertas', false, () {
                Navigator.pushNamed(context, '/alertas');
              }),
              _buildNavItem(Icons.category, 'Categorias', false, () {
                Navigator.pushNamed(context, '/categorias');
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, bool isActive, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? AppColors.primary : Colors.grey[400],
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 10,
              fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
              color: isActive ? AppColors.primary : Colors.grey[400],
            ),
          ),
        ],
      ),
    );
  }
}
