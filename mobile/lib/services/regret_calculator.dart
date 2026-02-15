import 'dart:math';
import '../models/purchase.dart';
import '../config/constants.dart';

/// 후회 점수 계산 로직 (regret_calculator.py → Dart 변환)
///
/// 7가지 요인, 100점 만점:
/// 1. 필요도-사용빈도 갭 (30)
/// 2. 금액 가중치 (20)
/// 3. 반복 구매 (15)
/// 4. 시간 경과 (15)
/// 5. 최근성 (10)
/// 6. 새벽 구매 (10)
/// 7. 충동 패턴 (10)
class RegretCalculator {
  RegretCalculator._();

  /// 카테고리가 식비 관련인지 판단
  static bool isFoodCategory(String category) {
    final cat = category.trim();
    return AppConstants.foodKeywords.any((kw) => cat.contains(kw));
  }

  /// 필요도-사용빈도 갭 점수 (0-30)
  static double necessityUsageGapScore(int necessity, int usage) {
    final gap = necessity - usage;
    if (gap <= 0) return 0;
    if (gap == 1) return 5;
    if (gap == 2) return 12;
    if (gap == 3) return 20;
    return 30;
  }

  /// 시간 경과 대비 사용빈도 점수 (0-15)
  static double timeDecayScore(int daysSince, int usage) {
    if (daysSince < 7) return 0;

    double timeWeight;
    if (daysSince < 30) {
      timeWeight = 0.3;
    } else if (daysSince < 90) {
      timeWeight = 0.6;
    } else if (daysSince < 180) {
      timeWeight = 0.9;
    } else {
      timeWeight = 1.2;
    }

    final usagePenalty = (5 - usage) / 4.0;
    final score = usagePenalty * timeWeight * 12;
    return min(score, 15);
  }

  /// 금액 가중치 점수 (0-20)
  static double priceWeightScore(
      double amount, double avgAmount, double maxAmount) {
    if (amount <= 10000) return 2;

    final priceRatio = avgAmount > 0 ? amount / avgAmount : 1.0;
    final maxRatio = maxAmount > 0 ? amount / maxAmount : 0.0;
    final logAmount = log(amount / 1000) / ln10;

    final score = priceRatio * 4 + maxRatio * 6 + logAmount * 2;
    return min(score, 20);
  }

  /// 최근성 점수 (0-10)
  static double recencyScore(int daysSince) {
    if (daysSince <= 3) return 8;
    if (daysSince <= 7) return 6;
    if (daysSince <= 14) return 4;
    if (daysSince <= 30) return 2;
    return 0;
  }

  /// 동일 카테고리 반복 구매 점수 (0-15)
  static double categoryRepetitionScore(
    String category,
    List<DateTime> categoryDates,
    DateTime currentDate,
  ) {
    if (categoryDates.length <= 1) return 0;

    final nearbyCount = categoryDates.where((d) {
      return d != currentDate &&
          (d.difference(currentDate).inDays).abs() <= 30;
    }).length;

    if (nearbyCount >= 3) return 15;
    if (nearbyCount == 2) return 10;
    if (nearbyCount == 1) return 5;
    return 0;
  }

  /// 새벽 구매 점수 (0-10)
  static double lateNightScore(DateTime purchaseDate) {
    final hour = purchaseDate.hour;
    if (hour >= 0 && hour < 5) return 10;
    if (hour >= 23) return 7;
    if (hour >= 21 && hour < 23) return 4;
    return 0;
  }

  /// 충동 구매 패턴 점수 (0-10)
  static double impulseBuyingScore(
    DateTime purchaseDate,
    List<DateTime> allDates,
  ) {
    // 같은 날 구매 건수
    final sameDayCount = allDates
        .where((d) =>
            d.year == purchaseDate.year &&
            d.month == purchaseDate.month &&
            d.day == purchaseDate.day)
        .length;

    if (sameDayCount >= 4) return 10;
    if (sameDayCount == 3) return 7;
    if (sameDayCount == 2) return 4;

    // 3일 이내 연속 구매
    final consecutiveCount = allDates.where((d) {
      final diff = purchaseDate.difference(d).inDays;
      return diff >= 0 && diff <= 3 && d != purchaseDate;
    }).length;

    if (consecutiveCount >= 5) return 8;
    if (consecutiveCount >= 3) return 5;
    if (consecutiveCount >= 2) return 3;

    return 0;
  }

  /// 종합 후회 점수 계산
  static Map<String, double> calculateRegretScore({
    required int necessity,
    required int usage,
    required double amount,
    required DateTime purchaseDate,
    required String category,
    required List<Purchase> allPurchases,
    DateTime? now,
  }) {
    now ??= DateTime.now();
    final daysSince = now.difference(purchaseDate).inDays;

    // 통계값 계산
    final amounts = allPurchases.map((p) => p.amount).toList();
    final avgAmount = amounts.isNotEmpty
        ? amounts.reduce((a, b) => a + b) / amounts.length
        : 0.0;
    final maxAmount =
        amounts.isNotEmpty ? amounts.reduce((a, b) => a > b ? a : b) : 0.0;

    // 카테고리별 날짜
    final categoryDates = allPurchases
        .where((p) => p.category == category)
        .map((p) => p.purchaseDate)
        .toList();
    final allDates = allPurchases.map((p) => p.purchaseDate).toList();

    // 식비 여부
    final isFood = isFoodCategory(category);

    final scores = <String, double>{
      'necessity_gap':
          isFood ? 0 : necessityUsageGapScore(necessity, usage),
      'time_decay':
          isFood ? 0 : timeDecayScore(daysSince, usage),
      'price_weight': priceWeightScore(amount, avgAmount, maxAmount),
      'recency': recencyScore(daysSince),
      'category_repetition':
          categoryRepetitionScore(category, categoryDates, purchaseDate),
      'late_night': lateNightScore(purchaseDate),
      'impulse_pattern': impulseBuyingScore(purchaseDate, allDates),
    };

    final total = scores.values.reduce((a, b) => a + b);
    scores['total_score'] = min(total, 100);

    return scores;
  }

  /// 모든 구매에 후회 점수 추가
  static void addRegretScores(List<Purchase> purchases) {
    for (final purchase in purchases) {
      final scores = calculateRegretScore(
        necessity: purchase.necessityScore,
        usage: purchase.usageFrequency,
        amount: purchase.amount,
        purchaseDate: purchase.purchaseDate,
        category: purchase.category,
        allPurchases: purchases,
      );

      purchase.regretScore = scores['total_score'];
      purchase.regretFactors = scores;
    }
  }

  /// 후회 점수 해석
  static RegretInterpretation interpret(double score) {
    if (score <= 20) {
      return const RegretInterpretation(
        grade: '매우 만족',
        gradeJa: '非常に満足',
        emoji: '🟢',
        color: 0xFF4CAF50,
      );
    } else if (score <= 35) {
      return const RegretInterpretation(
        grade: '만족',
        gradeJa: '満足',
        emoji: '🟡',
        color: 0xFF8BC34A,
      );
    } else if (score <= 50) {
      return const RegretInterpretation(
        grade: '보통',
        gradeJa: '普通',
        emoji: '🟡',
        color: 0xFFFFEB3B,
      );
    } else if (score <= 65) {
      return const RegretInterpretation(
        grade: '아쉬움',
        gradeJa: '残念',
        emoji: '🟠',
        color: 0xFFFF9800,
      );
    } else {
      return const RegretInterpretation(
        grade: '후회',
        gradeJa: '後悔',
        emoji: '🔴',
        color: 0xFFF44336,
      );
    }
  }
}

/// 후회 점수 해석 데이터
class RegretInterpretation {
  final String grade;
  final String gradeJa;
  final String emoji;
  final int color;

  const RegretInterpretation({
    required this.grade,
    required this.gradeJa,
    required this.emoji,
    required this.color,
  });
}
