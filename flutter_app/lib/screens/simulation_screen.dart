import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../models/transaction_model.dart';
import 'projection_impact_screen.dart';

/// Tela de Simulação de Compras e Empréstimos
class SimulationScreen extends StatefulWidget {
  const SimulationScreen({super.key});

  @override
  State<SimulationScreen> createState() => _SimulationScreenState();
}

class _SimulationScreenState extends State<SimulationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _apiService = ApiService();
  
  // Empréstimo
  final _loanValueController = TextEditingController();
  final _loanInstallmentsController = TextEditingController();
  final _loanRateController = TextEditingController();
  
  // Compra Parcelada
  final _purchaseDescriptionController = TextEditingController();
  final _purchaseValueController = TextEditingController();
  final _purchaseInstallmentsController = TextEditingController();
  
  bool _isSimulating = false;
  LoanSimulation? _loanResult;
  InstallmentPurchaseSimulation? _purchaseResult;

  @override
  void dispose() {
    _loanValueController.dispose();
    _loanInstallmentsController.dispose();
    _loanRateController.dispose();
    _purchaseDescriptionController.dispose();
    _purchaseValueController.dispose();
    _purchaseInstallmentsController.dispose();
    super.dispose();
  }

  Future<void> _simulateLoan() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSimulating = true;
      _loanResult = null;
    });

    try {
      final value = double.parse(_loanValueController.text);
      final installments = int.parse(_loanInstallmentsController.text);
      final rate = double.parse(_loanRateController.text) / 100;

      final result = await _apiService.simulateLoan(
        value: value,
        installments: installments,
        monthlyRate: rate,
      );

      setState(() {
        _loanResult = result;
        _isSimulating = false;
      });
    } catch (e) {
      setState(() {
        _isSimulating = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e')),
        );
      }
    }
  }

  Future<void> _simulatePurchase() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSimulating = true;
      _purchaseResult = null;
    });

    try {
      final value = double.parse(_purchaseValueController.text);
      final installments = int.parse(_purchaseInstallmentsController.text);

      final result = await _apiService.simulateInstallmentPurchase(
        description: _purchaseDescriptionController.text,
        totalValue: value,
        installments: installments,
      );

      setState(() {
        _purchaseResult = result;
        _isSimulating = false;
      });
    } catch (e) {
      setState(() {
        _isSimulating = false;
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
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Simulações'),
          bottom: TabBar(
            tabs: [
              Tab(icon: const Icon(Icons.account_balance), text: 'Empréstimo'),
              Tab(icon: const Icon(Icons.shopping_cart), text: 'Compra'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildLoanSimulation(),
            _buildPurchaseSimulation(),
          ],
        ),
      ),
    );
  }

  Widget _buildLoanSimulation() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Simular Empréstimo',
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _loanValueController,
              decoration: const InputDecoration(
                labelText: 'Valor do Empréstimo',
                prefixText: 'R\$ ',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _loanInstallmentsController,
              decoration: const InputDecoration(
                labelText: 'Número de Parcelas',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _loanRateController,
              decoration: const InputDecoration(
                labelText: 'Taxa Mensal (%)',
                suffixText: '%',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSimulating ? null : _simulateLoan,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isSimulating
                  ? const CircularProgressIndicator()
                  : const Text('Simular'),
            ),
            if (_loanResult != null) ...[
              const SizedBox(height: 32),
              _buildLoanResult(_loanResult!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLoanResult(LoanSimulation result) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resultado da Simulação',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildResultRow('Parcela Mensal', Formatters.currency(result.installmentValue)),
          _buildResultRow('Total Pago', Formatters.currency(result.totalPaid)),
          _buildResultRow('Impacto na Performance', Formatters.currency(result.impactOnPerformance), isNegative: true),
          _buildResultRow('Novo Comprometimento', '${result.newCommitment.toStringAsFixed(1)}%'),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ProjectionImpactScreen(
                    projections: result.projectionImpact,
                    title: 'Impacto do Empréstimo',
                  ),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              minimumSize: const Size(double.infinity, 48),
            ),
            child: const Text('Ver Impacto Futuro'),
          ),
        ],
      ),
    );
  }

  Widget _buildPurchaseSimulation() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Simular Compra Parcelada',
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _purchaseDescriptionController,
              decoration: const InputDecoration(
                labelText: 'Descrição da Compra',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _purchaseValueController,
              decoration: const InputDecoration(
                labelText: 'Valor Total',
                prefixText: 'R\$ ',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _purchaseInstallmentsController,
              decoration: const InputDecoration(
                labelText: 'Número de Parcelas',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Campo obrigatório' : null,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSimulating ? null : _simulatePurchase,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isSimulating
                  ? const CircularProgressIndicator()
                  : const Text('Simular'),
            ),
            if (_purchaseResult != null) ...[
              const SizedBox(height: 32),
              _buildPurchaseResult(_purchaseResult!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPurchaseResult(InstallmentPurchaseSimulation result) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resultado da Simulação',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildResultRow('Descrição', result.description),
          _buildResultRow('Valor Total', Formatters.currency(result.totalValue)),
          _buildResultRow('Parcela Mensal', Formatters.currency(result.installmentValue)),
          _buildResultRow('Número de Parcelas', '${result.installments}x'),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ProjectionImpactScreen(
                    projections: result.projectionImpact,
                    title: 'Impacto da Compra',
                  ),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              minimumSize: const Size(double.infinity, 48),
            ),
            child: const Text('Ver Impacto Futuro'),
          ),
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value, {bool isNegative = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Colors.grey[700],
            ),
          ),
          Text(
            value,
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isNegative ? AppColors.expense : AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}
