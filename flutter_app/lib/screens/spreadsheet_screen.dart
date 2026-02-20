import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:intl/date_symbol_data_local.dart';
import '../services/api_service.dart';
import '../models/transaction_model.dart';
import '../utils/colors.dart';
import '../utils/formatters.dart';
import '../widgets/balance_color_indicator.dart';

/// Tela de Planilha Interativa (espelho da planilha Excel)
class SpreadsheetScreen extends StatefulWidget {
  const SpreadsheetScreen({super.key});

  @override
  State<SpreadsheetScreen> createState() => _SpreadsheetScreenState();
}

class _SpreadsheetScreenState extends State<SpreadsheetScreen> {
  final _apiService = ApiService();
  List<Transaction> _transactions = [];
  bool _isLoading = true;
  DateTime _selectedDate = DateTime.now();
  Map<String, double> _dailyBalances = {};
  double _currentBalance = 0.0;

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
    _loadCurrentBalance();
    _loadTransactions();
  }

  Future<void> _loadCurrentBalance() async {
    try {
      final dashboard = await _apiService.getDashboard();
      setState(() {
        _currentBalance = dashboard.currentBalance;
      });
    } catch (e) {
      // Se falhar, começa com saldo zero
      _currentBalance = 0.0;
    }
  }

  Future<void> _loadTransactions() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Carregar saldo atual primeiro
      await _loadCurrentBalance();

      final year = _selectedDate.year;
      final month = _selectedDate.month;
      final startDate = '$year-${month.toString().padLeft(2, '0')}-01';
      final lastDay = DateTime(year, month + 1, 0).day;
      final endDate = '$year-${month.toString().padLeft(2, '0')}-$lastDay';

      // Calcular saldo inicial do mês (saldo atual menos transações deste mês em diante)
      final allTransactions = await _apiService.getTransactions();
      double initialBalance = 0.0;
      for (final t in allTransactions) {
        final tDate = DateTime.parse(t.date);
        if (tDate.year < year || (tDate.year == year && tDate.month < month)) {
          initialBalance += t.amount;
        }
      }

      final transactions = await _apiService.getTransactions(
        startDate: startDate,
        endDate: endDate,
      );

      // Calcular saldos diários
      _calculateDailyBalances(transactions, initialBalance);

      setState(() {
        _transactions = transactions;
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

  void _calculateDailyBalances(List<Transaction> transactions, double initialBalance) {
    _dailyBalances.clear();
    
    // Criar mapa de todos os dias do mês
    final year = _selectedDate.year;
    final month = _selectedDate.month;
    final lastDay = DateTime(year, month + 1, 0).day;
    
    double runningBalance = initialBalance;
    
    // Inicializar todos os dias com saldo inicial
    for (int day = 1; day <= lastDay; day++) {
      final date = DateTime(year, month, day);
      final dateKey = DateFormat('yyyy-MM-dd').format(date);
      _dailyBalances[dateKey] = runningBalance;
    }

    // Ordenar transações por data
    final sorted = List<Transaction>.from(transactions)
      ..sort((a, b) => a.date.compareTo(b.date));

    // Atualizar saldos a partir das transações
    for (final transaction in sorted) {
      runningBalance += transaction.amount;
      final dateKey = transaction.date;
      _dailyBalances[dateKey] = runningBalance;
      
      // Atualizar todos os dias seguintes
      final transDate = DateTime.parse(dateKey);
      for (int day = transDate.day + 1; day <= lastDay; day++) {
        final futureDate = DateTime(year, month, day);
        final futureDateKey = DateFormat('yyyy-MM-dd').format(futureDate);
        _dailyBalances[futureDateKey] = runningBalance;
      }
    }
  }

  Color _getBalanceColor(double balance) {
    if (balance < 0) return AppColors.budgetDanger; // Vermelho (negativo)
    if (balance < 100) return Colors.red[300]!; // Vermelho claro (perto de zero)
    if (balance < 500) return AppColors.budgetWarning; // Amarelo (pouco)
    if (balance < 2000) return Colors.green[300]!; // Verde claro
    return AppColors.budgetSafe; // Verde escuro
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
        title: const Text('Planilha Financeira'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddTransactionDialog(),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTransactions,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Seletor de mês
                _buildMonthSelector(),
                // Tabela de transações
                Expanded(
                  child: _buildSpreadsheetTable(),
                ),
              ],
            ),
    );
  }

  Widget _buildMonthSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: () {
              setState(() {
                _selectedDate = DateTime(
                  _selectedDate.year,
                  _selectedDate.month - 1,
                  1,
                );
              });
              _loadTransactions();
            },
          ),
          Text(
            DateFormat('MMMM yyyy', 'pt_BR').format(_selectedDate),
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: () {
              setState(() {
                _selectedDate = DateTime(
                  _selectedDate.year,
                  _selectedDate.month + 1,
                  1,
                );
              });
              _loadTransactions();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSpreadsheetTable() {
    // Criar lista de todos os dias do mês
    final year = _selectedDate.year;
    final month = _selectedDate.month;
    final lastDay = DateTime(year, month + 1, 0).day;
    
    // Agrupar transações por dia
    final Map<String, List<Transaction>> transactionsByDay = {};
    for (final transaction in _transactions) {
      final day = transaction.date;
      if (!transactionsByDay.containsKey(day)) {
        transactionsByDay[day] = [];
      }
      transactionsByDay[day]!.add(transaction);
    }

    // Calcular saldo inicial do mês (antes deste mês)
    double initialBalance = 0.0;
    
    // Se já temos saldos calculados, pegar o primeiro dia e subtrair transações do primeiro dia
    if (_dailyBalances.isNotEmpty) {
      final firstDay = DateTime(year, month, 1);
      final firstDayStr = DateFormat('yyyy-MM-dd').format(firstDay);
      initialBalance = _dailyBalances[firstDayStr] ?? 0.0;
      
      // Subtrair transações do primeiro dia para ter o saldo inicial (antes do primeiro dia)
      if (transactionsByDay.containsKey(firstDayStr)) {
        for (final t in transactionsByDay[firstDayStr]!) {
          initialBalance -= t.amount;
        }
      }
    }

    // Calcular saldos acumulados para cada dia
    final Map<int, double> dailyBalances = {};
    double runningBalance = initialBalance;
    
    for (int day = 1; day <= lastDay; day++) {
      final date = DateTime(year, month, day);
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      
      // Adicionar transações deste dia
      if (transactionsByDay.containsKey(dateStr)) {
        for (final t in transactionsByDay[dateStr]!) {
          runningBalance += t.amount;
        }
      }
      
      dailyBalances[day] = runningBalance;
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: lastDay,
      itemBuilder: (context, index) {
        final day = index + 1;
        final date = DateTime(year, month, day);
        final dateStr = DateFormat('yyyy-MM-dd').format(date);
        
        final dayBalance = dailyBalances[day] ?? initialBalance;
        final balanceColor = _getBalanceColor(dayBalance);
        final dayTransactions = transactionsByDay[dateStr] ?? [];

        return _buildDayCard(dateStr, dayTransactions, dayBalance, balanceColor);
      },
    );
  }

  Widget _buildDayCard(
    String date,
    List<Transaction> transactions,
    double balance,
    Color balanceColor,
  ) {
    final dateObj = DateTime.parse(date);
    final dayName = DateFormat('EEEE', 'pt_BR').format(dateObj);
    final dayNumber = dateObj.day;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
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
          // Cabeçalho do dia
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: balanceColor.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$dayNumber - $dayName',
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      Formatters.date(dateObj),
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: balanceColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    Formatters.currency(balance),
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Transações do dia
          if (transactions.isEmpty)
            Container(
              padding: const EdgeInsets.all(12),
              child: Text(
                'Sem transações',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.grey[500],
                  fontStyle: FontStyle.italic,
                ),
              ),
            )
          else
            ...transactions.map((transaction) => _buildTransactionRow(transaction)),
          // Totais do dia
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Saldo do dia:',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  Formatters.currency(balance),
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: balanceColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionRow(Transaction transaction) {
    final isIncome = transaction.amount > 0;
    final amountColor = isIncome ? AppColors.income : AppColors.expense;

    return InkWell(
      onTap: () => _showEditTransactionDialog(transaction),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Colors.grey[200]!),
          ),
        ),
        child: Row(
          children: [
            // Ícone
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: amountColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                isIncome ? Icons.arrow_downward : Icons.arrow_upward,
                size: 18,
                color: amountColor,
              ),
            ),
            const SizedBox(width: 12),
            // Descrição
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    transaction.description,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (transaction.category != null)
                    Text(
                      transaction.category!,
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        color: Colors.grey[600],
                      ),
                    ),
                ],
              ),
            ),
            // Valor
            Text(
              '${isIncome ? '+' : '-'} ${Formatters.currency(transaction.amount.abs())}',
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: amountColor,
              ),
            ),
            const SizedBox(width: 8),
            // Botão editar
            IconButton(
              icon: const Icon(Icons.edit, size: 18),
              onPressed: () => _showEditTransactionDialog(transaction),
              color: Colors.grey[600],
            ),
          ],
        ),
      ),
    );
  }

  void _showAddTransactionDialog() {
    _showTransactionDialog();
  }

  void _showEditTransactionDialog(Transaction transaction) {
    _showTransactionDialog(transaction: transaction);
  }

  void _showTransactionDialog({Transaction? transaction}) {
    final isEdit = transaction != null;
    final dateController = TextEditingController(
      text: transaction?.date ?? DateFormat('yyyy-MM-dd').format(DateTime.now()),
    );
    final descriptionController = TextEditingController(
      text: transaction?.description ?? '',
    );
    final amountController = TextEditingController(
      text: transaction?.amount.abs().toString() ?? '',
    );
    final categoryController = TextEditingController(
      text: transaction?.category ?? '',
    );
    String selectedType = transaction?.type ?? 'variable';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text(isEdit ? 'Editar Transação' : 'Nova Transação'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Data
                TextField(
                  controller: dateController,
                  decoration: const InputDecoration(
                    labelText: 'Data',
                    border: OutlineInputBorder(),
                  ),
                  readOnly: true,
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: DateTime.parse(dateController.text),
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2030),
                    );
                    if (date != null) {
                      dateController.text = DateFormat('yyyy-MM-dd').format(date);
                    }
                  },
                ),
                const SizedBox(height: 16),
                // Descrição
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Descrição',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                // Tipo
                DropdownButtonFormField<String>(
                  value: selectedType,
                  decoration: const InputDecoration(
                    labelText: 'Tipo',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'income', child: Text('Receita')),
                    DropdownMenuItem(value: 'fixed', child: Text('Fixo')),
                    DropdownMenuItem(value: 'variable', child: Text('Variável')),
                    DropdownMenuItem(value: 'installment', child: Text('Parcela')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      selectedType = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),
                // Valor
                TextField(
                  controller: amountController,
                  decoration: const InputDecoration(
                    labelText: 'Valor',
                    prefixText: 'R\$ ',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                // Categoria
                TextField(
                  controller: categoryController,
                  decoration: const InputDecoration(
                    labelText: 'Categoria (opcional)',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
            if (isEdit)
              TextButton(
                onPressed: () async {
                  await _deleteTransaction(transaction!.id!);
                  Navigator.pop(context);
                },
                child: const Text('Excluir', style: TextStyle(color: Colors.red)),
              ),
            ElevatedButton(
              onPressed: () async {
                try {
                  final amount = double.parse(amountController.text);
                  final finalAmount = selectedType == 'income' ? amount : -amount;
                  final category = categoryController.text.isEmpty ? null : categoryController.text;

                  if (isEdit) {
                    await _updateTransaction(
                      transaction!,
                      dateController.text,
                      descriptionController.text,
                      finalAmount,
                      selectedType,
                      category,
                    );
                  } else {
                    await _createTransaction(
                      dateController.text,
                      descriptionController.text,
                      finalAmount,
                      selectedType,
                      category,
                    );
                  }

                  if (mounted) {
                    Navigator.pop(context);
                    _loadTransactions();
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Erro: $e')),
                    );
                  }
                }
              },
              child: Text(isEdit ? 'Salvar' : 'Criar'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _createTransaction(
    String date,
    String description,
    double amount,
    String type,
    String? category,
  ) async {
    final transaction = Transaction(
      date: date,
      description: description,
      amount: amount,
      type: type,
      category: category,
    );
    await _apiService.createTransaction(transaction);
  }

  Future<void> _updateTransaction(
    Transaction transaction,
    String date,
    String description,
    double amount,
    String type,
    String? category,
  ) async {
    final updated = Transaction(
      id: transaction.id,
      date: date,
      description: description,
      amount: amount,
      type: type,
      category: category,
      installmentGroupId: transaction.installmentGroupId,
    );
    await _apiService.updateTransaction(transaction.id!, updated);
  }

  Future<void> _deleteTransaction(int id) async {
    await _apiService.deleteTransaction(id);
    _loadTransactions();
  }
}
