/// Modelos de dados para Dashboard
class DashboardModel {
  final double currentBalance;
  final MonthPerformance monthPerformance;
  final TrafficLight trafficLight;
  final Commitment commitment;
  final List<Projection> projections;
  final List<ActiveInstallment> activeInstallments;
  final List<RecentTransaction> recentTransactions;

  DashboardModel({
    required this.currentBalance,
    required this.monthPerformance,
    required this.trafficLight,
    required this.commitment,
    required this.projections,
    required this.activeInstallments,
    required this.recentTransactions,
  });

  factory DashboardModel.fromJson(Map<String, dynamic> json) {
    return DashboardModel(
      currentBalance: (json['current_balance'] as num).toDouble(),
      monthPerformance: MonthPerformance.fromJson(json['month_performance']),
      trafficLight: TrafficLight.fromJson(json['traffic_light']),
      commitment: Commitment.fromJson(json['commitment']),
      projections: (json['projections'] as List?)
          ?.map((p) => Projection.fromJson(p))
          .toList() ?? [],
      activeInstallments: (json['active_installments'] as List?)
          ?.map((i) => ActiveInstallment.fromJson(i))
          .toList() ?? [],
      recentTransactions: (json['recent_transactions'] as List?)
          ?.map((t) => RecentTransaction.fromJson(t))
          .toList() ?? [],
    );
  }
}

class MonthPerformance {
  final double performance;
  final double entradas;
  final double fixos;
  final double variaveis;
  final double parcelas;

  MonthPerformance({
    required this.performance,
    required this.entradas,
    required this.fixos,
    required this.variaveis,
    required this.parcelas,
  });

  factory MonthPerformance.fromJson(Map<String, dynamic> json) {
    return MonthPerformance(
      performance: (json['performance'] as num).toDouble(),
      entradas: (json['entradas'] as num).toDouble(),
      fixos: (json['fixos'] as num).toDouble(),
      variaveis: (json['variaveis'] as num).toDouble(),
      parcelas: (json['parcelas'] as num).toDouble(),
    );
  }
}

class TrafficLight {
  final String status; // 'green', 'yellow', 'red'
  final String label;
  final double performance;

  TrafficLight({
    required this.status,
    required this.label,
    required this.performance,
  });

  factory TrafficLight.fromJson(Map<String, dynamic> json) {
    return TrafficLight(
      status: json['status'] as String,
      label: json['label'] as String,
      performance: (json['performance'] as num).toDouble(),
    );
  }
}

class Commitment {
  final double ratio;
  final double fixosParcelas;
  final double mediaReceita;

  Commitment({
    required this.ratio,
    required this.fixosParcelas,
    required this.mediaReceita,
  });

  factory Commitment.fromJson(Map<String, dynamic> json) {
    return Commitment(
      ratio: (json['ratio'] as num).toDouble(),
      fixosParcelas: (json['fixos_parcelas'] as num).toDouble(),
      mediaReceita: (json['media_receita'] as num).toDouble(),
    );
  }
}

class Projection {
  final int year;
  final int month;
  final String monthName;
  final double performance;
  final double balance;
  final double entradas;
  final double saidas;

  Projection({
    required this.year,
    required this.month,
    required this.monthName,
    required this.performance,
    required this.balance,
    required this.entradas,
    required this.saidas,
  });

  factory Projection.fromJson(Map<String, dynamic> json) {
    return Projection(
      year: json['year'] as int,
      month: json['month'] as int,
      monthName: json['month_name'] as String,
      performance: (json['performance'] as num).toDouble(),
      balance: (json['balance'] as num).toDouble(),
      entradas: (json['entradas'] as num).toDouble(),
      saidas: (json['saidas'] as num).toDouble(),
    );
  }
}

class ActiveInstallment {
  final int id;
  final String description;
  final double installmentValue;
  final int remainingInstallments;
  final int totalInstallments;
  final String startDate;

  ActiveInstallment({
    required this.id,
    required this.description,
    required this.installmentValue,
    required this.remainingInstallments,
    required this.totalInstallments,
    required this.startDate,
  });

  factory ActiveInstallment.fromJson(Map<String, dynamic> json) {
    return ActiveInstallment(
      id: json['id'] as int,
      description: json['description'] as String,
      installmentValue: (json['installment_value'] as num).toDouble(),
      remainingInstallments: json['remaining_installments'] as int,
      totalInstallments: json['total_installments'] as int,
      startDate: json['start_date'] as String,
    );
  }
}

class RecentTransaction {
  final int id;
  final String date;
  final String description;
  final double amount;
  final String type;
  final String? category;

  RecentTransaction({
    required this.id,
    required this.date,
    required this.description,
    required this.amount,
    required this.type,
    this.category,
  });

  factory RecentTransaction.fromJson(Map<String, dynamic> json) {
    return RecentTransaction(
      id: json['id'] as int,
      date: json['date'] as String,
      description: json['description'] as String,
      amount: (json['amount'] as num).toDouble(),
      type: json['type'] as String,
      category: json['category'] as String?,
    );
  }
}
