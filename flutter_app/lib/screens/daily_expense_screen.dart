import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';
import '../services/api_service.dart';
import '../models/transaction_model.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';

/// Tela de Controle de Gastos Diários
class DailyExpenseScreen extends StatefulWidget {
  const DailyExpenseScreen({super.key});

  @override
  State<DailyExpenseScreen> createState() => _DailyExpenseScreenState();
}

class _DailyExpenseScreenState extends State<DailyExpenseScreen> {
  final _apiService = ApiService();
  final _dailyBudgetController = TextEditingController(text: '50.00');
  double _dailyBudget = 50.0;
  DateTime _selectedDate = DateTime.now();
  Map<String, double> _dailyExpenses = {};
  bool _isLoading = true;

  bool _localeInitialized = false;

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
    _loadDailyExpenses();
  }

  @override
  void dispose() {
    _dailyBudgetController.dispose();
    super.dispose();
  }

  Future<void> _loadDailyExpenses() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final year = _selectedDate.year;
      final month = _selectedDate.month;
      final startDate = '$year-${month.toString().padLeft(2, '0')}-01';
      final lastDay = DateTime(year, month + 1, 0).day;
      final endDate = '$year-${month.toString().padLeft(2, '0')}-$lastDay';

      final transactions = await _apiService.getTransactions(
        startDate: startDate,
        endDate: endDate,
        type: 'variable',
      );

      // Agrupar por dia
      _dailyExpenses.clear();
      for (final transaction in transactions) {
        final day = transaction.date;
        _dailyExpenses[day] = (_dailyExpenses[day] ?? 0.0) + transaction.amount.abs();
      }

      setState(() {
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

  Future<void> _saveDailyExpense(String date, double amount) async {
    try {
      // Se amount for 0, remover gastos do dia
      if (amount == 0) {
      // Buscar transações do dia e remover
      final transactions = await _apiService.getTransactions(
        startDate: date,
        endDate: date,
        type: 'variable',
      );
        for (final t in transactions) {
          await _apiService.deleteTransaction(t.id!);
        }
        setState(() {
          _dailyExpenses.remove(date);
        });
        return;
      }

      // Criar ou atualizar transação do dia
      final existing = await _apiService.getTransactions(
        startDate: date,
        endDate: date,
        type: 'variable',
      );

      if (existing.isNotEmpty) {
        // Atualizar primeira transação
        final transaction = existing.first;
        final updated = Transaction(
          id: transaction.id,
          date: date,
          description: 'Gastos Diários',
          amount: -amount,
          type: 'variable',
          category: 'Diário',
        );
        await _apiService.updateTransaction(transaction.id!, updated);
      } else {
        // Criar nova
        final transaction = Transaction(
          date: date,
          description: 'Gastos Diários',
          amount: -amount,
          type: 'variable',
          category: 'Diário',
        );
        await _apiService.createTransaction(transaction);
      }

      setState(() {
        _dailyExpenses[date] = amount;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao salvar: $e')),
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
        title: const Text('Gastos Diários'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showBudgetDialog(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Resumo do mês
                _buildMonthSummary(),
                // Lista de dias
                Expanded(
                  child: _buildDaysList(),
                ),
              ],
            ),
    );
  }

  Widget _buildMonthSummary() {
    final totalDays = DateTime(_selectedDate.year, _selectedDate.month + 1, 0).day;
    final totalBudget = _dailyBudget * totalDays;
    final totalSpent = _dailyExpenses.values.fold(0.0, (a, b) => a + b);
    final remaining = totalBudget - totalSpent;
    final percentage = totalBudget > 0 ? (totalSpent / totalBudget * 100) : 0.0;

    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                DateFormat('MMMM yyyy', 'pt_BR').format(_selectedDate),
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'Orçamento: ${Formatters.currency(_dailyBudget)}/dia',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem('Total', Formatters.currency(totalSpent), AppColors.expense),
              _buildSummaryItem('Restante', Formatters.currency(remaining), remaining >= 0 ? AppColors.budgetSafe : AppColors.budgetDanger),
              _buildSummaryItem('Usado', '${percentage.toStringAsFixed(0)}%', percentage > 100 ? AppColors.budgetDanger : AppColors.budgetWarning),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (percentage / 100).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                percentage > 100 ? AppColors.budgetDanger : AppColors.budgetWarning,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildDaysList() {
    final totalDays = DateTime(_selectedDate.year, _selectedDate.month + 1, 0).day;
    final days = List.generate(totalDays, (i) => i + 1);

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: days.length,
      itemBuilder: (context, index) {
        final day = days[index];
        final date = DateTime(_selectedDate.year, _selectedDate.month, day);
        final dateStr = DateFormat('yyyy-MM-dd').format(date);
        final spent = _dailyExpenses[dateStr] ?? 0.0;
        final remaining = _dailyBudget - spent;
        final isToday = date.year == DateTime.now().year &&
            date.month == DateTime.now().month &&
            date.day == DateTime.now().day;

        return _buildDayCard(day, date, dateStr, spent, remaining, isToday);
      },
    );
  }

  Widget _buildDayCard(
    int day,
    DateTime date,
    String dateStr,
    double spent,
    double remaining,
    bool isToday,
  ) {
    final dayName = DateFormat('EEEE', 'pt_BR').format(date);
    final color = spent == 0
        ? Colors.grey[300]!
        : remaining < 0
            ? AppColors.budgetDanger
            : remaining < _dailyBudget * 0.3
                ? AppColors.budgetWarning
                : AppColors.budgetSafe;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isToday ? AppColors.primary.withOpacity(0.05) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isToday ? AppColors.primary : Colors.grey[200]!,
          width: isToday ? 2 : 1,
        ),
      ),
      child: InkWell(
        onTap: () => _showDayExpenseDialog(dateStr, day, dayName, spent),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // Dia
              Container(
                width: 48,
                alignment: Alignment.center,
                child: Column(
                  children: [
                    Text(
                      '$day',
                      style: GoogleFonts.inter(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: isToday ? AppColors.primary : Colors.grey[900],
                      ),
                    ),
                    Text(
                      dayName.substring(0, 3).toUpperCase(),
                      style: GoogleFonts.inter(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              // Gastos
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Gasto: ${Formatters.currency(spent)}',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Restante: ${Formatters.currency(remaining)}',
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: color,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(2),
                      child: LinearProgressIndicator(
                        value: (spent / _dailyBudget).clamp(0.0, 1.0),
                        minHeight: 4,
                        backgroundColor: Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showDayExpenseDialog(String dateStr, int day, String dayName, double currentSpent) {
    final controller = TextEditingController(
      text: currentSpent > 0 ? currentSpent.toStringAsFixed(2) : '',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('$day - $dayName'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Gasto do dia',
                prefixText: 'R\$ ',
                border: OutlineInputBorder(),
                hintText: 'Deixe vazio para zerar',
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 8),
            Text(
              'Orçamento: ${Formatters.currency(_dailyBudget)}',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () async {
              final value = controller.text.isEmpty
                  ? 0.0
                  : double.tryParse(controller.text) ?? 0.0;
              await _saveDailyExpense(dateStr, value);
              if (mounted) {
                Navigator.pop(context);
                _loadDailyExpenses();
              }
            },
            child: const Text('Salvar'),
          ),
        ],
      ),
    );
  }

  void _showBudgetDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Orçamento Diário'),
        content: TextField(
          controller: _dailyBudgetController,
          decoration: const InputDecoration(
            labelText: 'Valor por dia',
            prefixText: 'R\$ ',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.number,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              final value = double.tryParse(_dailyBudgetController.text) ?? 50.0;
              setState(() {
                _dailyBudget = value;
              });
              Navigator.pop(context);
            },
            child: const Text('Salvar'),
          ),
        ],
      ),
    );
  }
}
