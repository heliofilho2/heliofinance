/// Modelo de Transação
class Transaction {
  final int? id;
  final String date;
  final String description;
  final double amount;
  final String type; // 'income', 'fixed', 'variable', 'installment'
  final String? category;
  final int? installmentGroupId;
  final String? createdAt;

  Transaction({
    this.id,
    required this.date,
    required this.description,
    required this.amount,
    required this.type,
    this.category,
    this.installmentGroupId,
    this.createdAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] as int?,
      date: json['date'] as String,
      description: json['description'] as String,
      amount: (json['amount'] as num).toDouble(),
      type: json['type'] as String,
      category: json['category'] as String?,
      installmentGroupId: json['installment_group_id'] as int?,
      createdAt: json['created_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'date': date,
      'description': description,
      'amount': amount,
      'type': type,
      if (category != null) 'category': category,
      if (installmentGroupId != null) 'installment_group_id': installmentGroupId,
      if (createdAt != null) 'created_at': createdAt,
    };
  }
}

/// Modelo de Simulação de Empréstimo
class LoanSimulation {
  final double value;
  final int installments;
  final double monthlyRate;
  final double installmentValue;
  final double totalPaid;
  final double impactOnPerformance;
  final double newCommitment;
  final List<ProjectionImpact> projectionImpact;

  LoanSimulation({
    required this.value,
    required this.installments,
    required this.monthlyRate,
    required this.installmentValue,
    required this.totalPaid,
    required this.impactOnPerformance,
    required this.newCommitment,
    required this.projectionImpact,
  });

  factory LoanSimulation.fromJson(Map<String, dynamic> json) {
    return LoanSimulation(
      value: (json['value'] as num).toDouble(),
      installments: json['installments'] as int,
      monthlyRate: (json['monthly_rate'] as num).toDouble(),
      installmentValue: (json['installment_value'] as num).toDouble(),
      totalPaid: (json['total_paid'] as num).toDouble(),
      impactOnPerformance: (json['impact_on_performance'] as num).toDouble(),
      newCommitment: (json['new_commitment'] as num).toDouble(),
      projectionImpact: (json['projection_impact'] as List)
          .map((p) => ProjectionImpact.fromJson(p))
          .toList(),
    );
  }
}

/// Modelo de Simulação de Compra Parcelada
class InstallmentPurchaseSimulation {
  final String description;
  final double totalValue;
  final int installments;
  final double installmentValue;
  final List<ProjectionImpact> projectionImpact;

  InstallmentPurchaseSimulation({
    required this.description,
    required this.totalValue,
    required this.installments,
    required this.installmentValue,
    required this.projectionImpact,
  });

  factory InstallmentPurchaseSimulation.fromJson(Map<String, dynamic> json) {
    return InstallmentPurchaseSimulation(
      description: json['description'] as String,
      totalValue: (json['total_value'] as num).toDouble(),
      installments: json['installments'] as int,
      installmentValue: (json['installment_value'] as num).toDouble(),
      projectionImpact: (json['projection_impact'] as List)
          .map((p) => ProjectionImpact.fromJson(p))
          .toList(),
    );
  }
}

/// Impacto na Projeção
class ProjectionImpact {
  final int year;
  final int month;
  final String monthName;
  final double balanceBefore;
  final double balanceAfter;
  final double performanceBefore;
  final double performanceAfter;
  final String status; // 'green', 'yellow', 'red'

  ProjectionImpact({
    required this.year,
    required this.month,
    required this.monthName,
    required this.balanceBefore,
    required this.balanceAfter,
    required this.performanceBefore,
    required this.performanceAfter,
    required this.status,
  });

  factory ProjectionImpact.fromJson(Map<String, dynamic> json) {
    return ProjectionImpact(
      year: json['year'] as int,
      month: json['month'] as int,
      monthName: json['month_name'] as String,
      balanceBefore: (json['balance_before'] as num).toDouble(),
      balanceAfter: (json['balance_after'] as num).toDouble(),
      performanceBefore: (json['performance_before'] as num).toDouble(),
      performanceAfter: (json['performance_after'] as num).toDouble(),
      status: json['status'] as String,
    );
  }
}
