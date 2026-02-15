/// 구매 이력 모델
class Purchase {
  final int? id;
  final String? userId;
  final DateTime purchaseDate;
  final String category;
  final String productName;
  final double amount;
  final int necessityScore;
  final int usageFrequency;
  final int? thinkingDays;
  final bool? repurchaseIntent;
  final String source;

  // 분석 후 추가되는 필드
  double? regretScore;
  Map<String, double>? regretFactors;

  Purchase({
    this.id,
    this.userId,
    required this.purchaseDate,
    required this.category,
    required this.productName,
    required this.amount,
    required this.necessityScore,
    required this.usageFrequency,
    this.thinkingDays,
    this.repurchaseIntent,
    this.source = 'manual',
    this.regretScore,
    this.regretFactors,
  });

  factory Purchase.fromJson(Map<String, dynamic> json) {
    return Purchase(
      id: json['id'] as int?,
      userId: json['user_id'] as String?,
      purchaseDate: DateTime.parse(json['purchase_date'] as String),
      category: json['category'] as String? ?? '',
      productName: json['product_name'] as String? ?? '',
      amount: (json['amount'] as num?)?.toDouble() ?? 0,
      necessityScore: json['necessity_score'] as int? ?? 3,
      usageFrequency: json['usage_frequency'] as int? ?? 3,
      thinkingDays: json['thinking_days'] as int?,
      repurchaseIntent: json['repurchase_intent'] as bool?,
      source: json['source'] as String? ?? 'manual',
    );
  }

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'purchase_date': purchaseDate.toIso8601String().substring(0, 10),
      'category': category,
      'product_name': productName,
      'amount': amount.toInt(),
      'necessity_score': necessityScore,
      'usage_frequency': usageFrequency,
      'source': source,
    };

    if (userId != null) map['user_id'] = userId;
    if (thinkingDays != null) map['thinking_days'] = thinkingDays;
    if (repurchaseIntent != null) map['repurchase_intent'] = repurchaseIntent;

    return map;
  }

  /// 고민기간 + 재구매의향으로 필요도 자동 계산
  static int calculateNecessity({
    required int thinkingDays,
    required bool repurchaseIntent,
  }) {
    int score;
    if (thinkingDays == 0) {
      score = 1; // 충동 구매
    } else if (thinkingDays <= 1) {
      score = 2;
    } else if (thinkingDays <= 3) {
      score = 3;
    } else if (thinkingDays <= 7) {
      score = 4;
    } else {
      score = 5; // 매우 신중
    }

    // 재구매 의향이 없으면 필요도 -1
    if (!repurchaseIntent && score > 1) {
      score -= 1;
    }

    return score;
  }

  /// 후회 등급 텍스트
  String get regretGrade {
    final score = regretScore ?? 0;
    if (score <= 20) return '매우 만족';
    if (score <= 35) return '만족';
    if (score <= 50) return '보통';
    if (score <= 65) return '아쉬움';
    return '후회';
  }
}
