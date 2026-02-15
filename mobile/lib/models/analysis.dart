/// 분석 결과 모델
class Analysis {
  final int? id;
  final String? userId;
  final int purchaseCount;
  final double totalSpent;
  final double averageRegretScore;
  final int highRegretCount;
  final String? psychologyAnalysis;
  final String? smartInsights;
  final DateTime? createdAt;

  const Analysis({
    this.id,
    this.userId,
    required this.purchaseCount,
    required this.totalSpent,
    required this.averageRegretScore,
    required this.highRegretCount,
    this.psychologyAnalysis,
    this.smartInsights,
    this.createdAt,
  });

  factory Analysis.fromJson(Map<String, dynamic> json) {
    return Analysis(
      id: json['id'] as int?,
      userId: json['user_id'] as String?,
      purchaseCount: json['purchase_count'] as int? ?? 0,
      totalSpent: (json['total_spent'] as num?)?.toDouble() ?? 0,
      averageRegretScore:
          (json['average_regret_score'] as num?)?.toDouble() ?? 0,
      highRegretCount: json['high_regret_count'] as int? ?? 0,
      psychologyAnalysis: json['psychology_analysis'] as String?,
      smartInsights: json['smart_insights'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (userId != null) 'user_id': userId,
      'purchase_count': purchaseCount,
      'total_spent': totalSpent,
      'average_regret_score': averageRegretScore,
      'high_regret_count': highRegretCount,
      'psychology_analysis': psychologyAnalysis,
      'smart_insights': smartInsights,
    };
  }
}

/// 전체 후회 분석 요약
class RegretSummary {
  final int totalPurchases;
  final double avgRegretScore;
  final Map<String, int> distribution; // grade -> count
  final int regretCount;
  final double regretRatio;
  final double regretAmount;
  final double regretAmountRatio;
  final String mainCause;
  final double mainCauseScore;

  const RegretSummary({
    required this.totalPurchases,
    required this.avgRegretScore,
    required this.distribution,
    required this.regretCount,
    required this.regretRatio,
    required this.regretAmount,
    required this.regretAmountRatio,
    required this.mainCause,
    required this.mainCauseScore,
  });
}
