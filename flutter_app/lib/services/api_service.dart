import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/dashboard_model.dart';
import '../models/transaction_model.dart';
import '../config/api_config.dart';

/// Serviço de comunicação com a API REST
class ApiService {
  final String baseUrl;
  final http.Client client;

  ApiService({
    String? baseUrl,
    http.Client? client,
  }) : baseUrl = baseUrl ?? ApiConfig.baseUrl,
        client = client ?? http.Client();

  /// Busca status financeiro atual
  Future<Map<String, dynamic>> getStatus() async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao buscar status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca relatório semanal
  Future<Map<String, dynamic>> getRelatorioSemanal() async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/relatorio/semanal'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao buscar relatório: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca relatório mensal
  Future<Map<String, dynamic>> getRelatorioMensal({int? mes, int? ano}) async {
    try {
      final uri = Uri.parse('$baseUrl/api/relatorio/mensal').replace(
        queryParameters: {
          if (mes != null) 'mes': mes.toString(),
          if (ano != null) 'ano': ano.toString(),
        },
      );
      
      final response = await client.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao buscar relatório: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca alertas ativos
  Future<List<dynamic>> getAlertas() async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/alertas'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao buscar alertas: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca categorias
  Future<List<String>> getCategorias() async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/categorias'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['categorias']);
      } else {
        throw Exception('Erro ao buscar categorias: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Cria transação
  Future<Map<String, dynamic>> criarTransacao({
    required String tipo,
    required double valor,
    required String descricao,
  }) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/transacao?tipo=$tipo&valor=$valor&descricao=${Uri.encodeComponent(descricao)}'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao criar transação: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca dashboard completo (compatibilidade)
  Future<DashboardModel> getDashboard() async {
    try {
      // Usar novo endpoint de status e construir dashboard
      final status = await getStatus();
      // TODO: Construir DashboardModel a partir do status
      // Por enquanto, retornar modelo vazio
      return DashboardModel(
        currentBalance: (status['saldo'] as num).toDouble(),
        monthPerformance: MonthPerformance(
          performance: (status['performance'] as num).toDouble(),
          entradas: (status['entrada'] as num).toDouble(),
          fixos: (status['saida'] as num).toDouble(),
          variaveis: (status['diario_total'] as num).toDouble(),
          parcelas: 0,
        ),
        trafficLight: TrafficLight(
          status: status['semaforo'] == '🟢' ? 'green' : status['semaforo'] == '🟡' ? 'yellow' : 'red',
          label: status['status'] as String,
          performance: (status['performance'] as num).toDouble(),
        ),
        commitment: Commitment(
          ratio: 0,
          fixosParcelas: 0,
          mediaReceita: 0,
        ),
        projections: [],
        activeInstallments: [],
        recentTransactions: [],
      );
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Cria transação rápida via comando
  Future<Transaction> createQuickTransaction(String command) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/transactions/quick?command=${Uri.encodeComponent(command)}'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Transaction.fromJson(data['transaction']);
      } else {
        throw Exception('Erro ao criar transação: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Cria transação completa
  Future<Transaction> createTransaction(Transaction transaction) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/transactions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(transaction.toJson()),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return Transaction.fromJson(json.decode(response.body));
      } else {
        throw Exception('Erro ao criar transação: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Lista transações
  Future<List<Transaction>> getTransactions({
    int? limit,
    String? type,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (limit != null) queryParams['limit'] = limit.toString();
      if (type != null) queryParams['type_filter'] = type;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final uri = Uri.parse('$baseUrl/api/transactions').replace(
        queryParameters: queryParams,
      );

      final response = await client.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // A API retorna lista direta, não objeto com 'transactions'
        if (data is List) {
          return data.map((t) => Transaction.fromJson(t)).toList();
        } else if (data is Map && data.containsKey('transactions')) {
          return (data['transactions'] as List)
              .map((t) => Transaction.fromJson(t))
              .toList();
        } else {
          return [];
        }
      } else {
        throw Exception('Erro ao buscar transações: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Simula empréstimo
  Future<LoanSimulation> simulateLoan({
    required double value,
    required int installments,
    required double monthlyRate,
  }) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/simulate/loan'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'value': value,
          'installments': installments,
          'monthly_rate': monthlyRate,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return LoanSimulation.fromJson(json.decode(response.body));
      } else {
        throw Exception('Erro ao simular empréstimo: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Simula compra parcelada
  Future<InstallmentPurchaseSimulation> simulateInstallmentPurchase({
    required String description,
    required double totalValue,
    required int installments,
  }) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/simulate/installment'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'description': description,
          'total_value': totalValue,
          'installments': installments,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return InstallmentPurchaseSimulation.fromJson(json.decode(response.body));
      } else {
        throw Exception('Erro ao simular compra: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Atualiza transação
  Future<Transaction> updateTransaction(int transactionId, Transaction transaction) async {
    try {
      final response = await client.put(
        Uri.parse('$baseUrl/api/transactions/$transactionId'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(transaction.toJson()),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return Transaction.fromJson(json.decode(response.body));
      } else {
        throw Exception('Erro ao atualizar transação: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Deleta transação
  Future<void> deleteTransaction(int transactionId) async {
    try {
      final response = await client.delete(
        Uri.parse('$baseUrl/api/transactions/$transactionId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw Exception('Erro ao deletar transação: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Cria múltiplas transações
  Future<List<Transaction>> createBulkTransactions(List<Transaction> transactions) async {
    try {
      final response = await client.post(
        Uri.parse('$baseUrl/api/transactions/bulk'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'transactions': transactions.map((t) => t.toJson()).toList(),
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['transactions'] as List)
            .map((t) => Transaction.fromJson(t))
            .toList();
      } else {
        throw Exception('Erro ao criar transações: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  /// Busca projeção futura de saldo
  Future<Map<String, dynamic>> getProjecao({int meses = 6}) async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/api/projecao?meses=$meses'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Erro ao buscar projeção: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }
}
