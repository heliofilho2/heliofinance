import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';
import '../services/api_service.dart';
import '../models/dashboard_model.dart';
import '../models/transaction_model.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../widgets/balance_color_indicator.dart';

/// Tela de Visão Macro - Contas Fixas, Parcelas e Previsões
class MacroViewScreen extends StatefulWidget {
  const MacroViewScreen({super.key});

  @override
  State<MacroViewScreen> createState() => _MacroViewScreenState();
}

class _MacroViewScreenState extends State<MacroViewScreen> {
  final _apiService = ApiService();
  DashboardModel? _dashboard;
  List<Transaction> _fixedExpenses = [];
  List<Transaction> _incomes = [];
  bool _isLoading = true;
  bool _localeInitialized = false;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _initializeLocale();
  }

  Future<void> _initializeLocale() async {
    await initializeDateFormatting('pt_BR', null);
    setState(() {
      _localeInitialized = true;
    });
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Carregar dashboard
      final dashboard = await _apiService.getDashboard();
      
      // Carregar contas fixas
      final allTransactions = await _apiService.getTransactions();
      final fixed = allTransactions.where((t) => t.type == 'fixed').toList();
      final incomes = allTransactions.where((t) => t.type == 'income').toList();

      setState(() {
        _dashboard = dashboard;
        _fixedExpenses = fixed;
        _incomes = incomes;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao carregar: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_localeInitialized) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Visão Macro'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Saldo Atual
                    _buildCurrentBalance(),
                    const SizedBox(height: 24),
                    // Receitas Previstas
                    _buildIncomesSection(),
                    const SizedBox(height: 24),
                    // Contas Fixas
                    _buildFixedExpensesSection(),
                    const SizedBox(height: 24),
                    // Parcelas Ativas
                    _buildInstallmentsSection(),
                    const SizedBox(height: 24),
                    // Projeção Mensal
                    _buildMonthlyProjection(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildCurrentBalance() {
    if (_dashboard == null) return const SizedBox.shrink();

    final balance = _dashboard!.currentBalance;
    final color = BalanceColorIndicator.getBalanceColor(balance);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Saldo Atual',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            Formatters.currency(balance),
            style: GoogleFonts.inter(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Última atualização: ${DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now())}',
            style: GoogleFonts.inter(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIncomesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Receitas Previstas',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton.icon(
              onPressed: () => _showAddIncomeDialog(),
              icon: const Icon(Icons.add, size: 16),
              label: const Text('Adicionar'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (_incomes.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.grey[600]),
                const SizedBox(width: 8),
                Text(
                  'Nenhuma receita cadastrada',
                  style: GoogleFonts.inter(color: Colors.grey[600]),
                ),
              ],
            ),
          )
        else
          ..._incomes.map((income) => _buildIncomeCard(income)),
      ],
    );
  }

  Widget _buildIncomeCard(Transaction income) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.income.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.arrow_downward,
              color: AppColors.income,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  income.description,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'Recorrente: ${_getRecurrenceText(income)}',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          Text(
            Formatters.currency(income.amount),
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.income,
            ),
          ),
        ],
      ),
    );
  }

  String _getRecurrenceText(Transaction transaction) {
    // Por enquanto, assume mensal. Pode ser melhorado depois
    return 'Mensal';
  }

  Widget _buildFixedExpensesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Contas Fixas',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton.icon(
              onPressed: () => _showAddFixedExpenseDialog(),
              icon: const Icon(Icons.add, size: 16),
              label: const Text('Adicionar'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (_fixedExpenses.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.grey[600]),
                const SizedBox(width: 8),
                Text(
                  'Nenhuma conta fixa cadastrada',
                  style: GoogleFonts.inter(color: Colors.grey[600]),
                ),
              ],
            ),
          )
        else
          ..._fixedExpenses.map((expense) => _buildFixedExpenseCard(expense)),
        const SizedBox(height: 8),
        _buildTotalFixedExpenses(),
      ],
    );
  }

  Widget _buildFixedExpenseCard(Transaction expense) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.expense.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.arrow_upward,
              color: AppColors.expense,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  expense.description,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (expense.category != null)
                  Text(
                    expense.category!,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),
          Text(
            Formatters.currency(expense.amount.abs()),
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.expense,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit, size: 18),
            onPressed: () => _editTransaction(expense),
            color: Colors.grey[600],
          ),
        ],
      ),
    );
  }

  Widget _buildTotalFixedExpenses() {
    final total = _fixedExpenses.fold<double>(
      0.0,
      (sum, expense) => sum + expense.amount.abs(),
    );

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.expense.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.expense.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Total de Contas Fixas',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            Formatters.currency(total),
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.expense,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstallmentsSection() {
    if (_dashboard == null || _dashboard!.activeInstallments.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Parcelas Ativas',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.grey[600]),
                const SizedBox(width: 8),
                Text(
                  'Nenhuma parcela ativa',
                  style: GoogleFonts.inter(color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Parcelas Ativas',
          style: GoogleFonts.inter(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ..._dashboard!.activeInstallments.map((inst) => _buildInstallmentCard(inst)),
        const SizedBox(height: 8),
        _buildTotalInstallments(),
      ],
    );
  }

  Widget _buildInstallmentCard(ActiveInstallment installment) {
    final startDate = DateTime.parse(installment.startDate);
    final monthsPaid = installment.totalInstallments - installment.remainingInstallments;
    final monthsRemaining = installment.remainingInstallments;
    final totalPaid = monthsPaid * installment.installmentValue;
    final totalRemaining = monthsRemaining * installment.installmentValue;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: AppColors.budgetWarning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.credit_card,
                  color: AppColors.budgetWarning,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      installment.description,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '${installment.remainingInstallments} de ${installment.totalInstallments} parcelas restantes',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                Formatters.currency(installment.installmentValue),
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.budgetWarning,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Pago: ${Formatters.currency(totalPaid)}',
                style: GoogleFonts.inter(
                  fontSize: 11,
                  color: Colors.grey[600],
                ),
              ),
              Text(
                'Restante: ${Formatters.currency(totalRemaining)}',
                style: GoogleFonts.inter(
                  fontSize: 11,
                  color: AppColors.budgetWarning,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTotalInstallments() {
    if (_dashboard == null) return const SizedBox.shrink();

    final total = _dashboard!.activeInstallments.fold<double>(
      0.0,
      (sum, inst) => sum + inst.installmentValue,
    );

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.budgetWarning.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.budgetWarning.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Total de Parcelas Mensais',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            Formatters.currency(total),
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.budgetWarning,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMonthlyProjection() {
    if (_dashboard == null) return const SizedBox.shrink();

    final perf = _dashboard!.monthPerformance;
    final totalFixed = _fixedExpenses.fold<double>(
      0.0,
      (sum, e) => sum + e.amount.abs(),
    );
    final totalInstallments = _dashboard!.activeInstallments.fold<double>(
      0.0,
      (sum, inst) => sum + inst.installmentValue,
    );
    final totalIncome = _incomes.fold<double>(
      0.0,
      (sum, i) => sum + i.amount,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Projeção Mensal',
          style: GoogleFonts.inter(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[200]!),
          ),
          child: Column(
            children: [
              _buildProjectionRow('Receitas', totalIncome > 0 ? totalIncome : perf.entradas, AppColors.income),
              _buildProjectionRow('Contas Fixas', totalFixed > 0 ? totalFixed : perf.fixos, AppColors.expense),
              _buildProjectionRow('Parcelas', totalInstallments > 0 ? totalInstallments : perf.parcelas, AppColors.budgetWarning),
              _buildProjectionRow('Variáveis', perf.variaveis, Colors.grey[700]!),
              const Divider(),
              _buildProjectionRow(
                'Performance',
                perf.performance,
                perf.performance >= 0 ? AppColors.budgetSafe : AppColors.budgetDanger,
                isBold: true,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildProjectionRow(String label, double value, Color color, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: isBold ? 16 : 14,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            Formatters.currency(value),
            style: GoogleFonts.inter(
              fontSize: isBold ? 18 : 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  void _showAddIncomeDialog() {
    // Implementar diálogo para adicionar receita
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Funcionalidade em desenvolvimento')),
    );
  }

  void _showAddFixedExpenseDialog() {
    // Implementar diálogo para adicionar conta fixa
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Funcionalidade em desenvolvimento')),
    );
  }

  void _editTransaction(Transaction transaction) {
    // Implementar edição
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Funcionalidade em desenvolvimento')),
    );
  }
}
