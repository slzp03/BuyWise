import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../models/purchase.dart';
import '../../l10n/translations.dart';

/// 카테고리별 지출 파이 차트
class CategoryChart extends StatelessWidget {
  final List<Purchase> purchases;
  final String lang;

  const CategoryChart({
    super.key,
    required this.purchases,
    required this.lang,
  });

  @override
  Widget build(BuildContext context) {
    final categoryData = _calculateCategoryData();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppTranslations.t('category_analysis', lang: lang),
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: Row(
                children: [
                  // 파이 차트
                  Expanded(
                    flex: 3,
                    child: PieChart(
                      PieChartData(
                        sections: _buildSections(categoryData),
                        centerSpaceRadius: 40,
                        sectionsSpace: 2,
                      ),
                    ),
                  ),
                  // 범례
                  Expanded(
                    flex: 2,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: categoryData.entries
                          .take(6)
                          .toList()
                          .asMap()
                          .entries
                          .map((entry) {
                        final color = _colors[entry.key % _colors.length];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Row(
                            children: [
                              Container(
                                width: 10,
                                height: 10,
                                decoration: BoxDecoration(
                                  color: color,
                                  borderRadius: BorderRadius.circular(2),
                                ),
                              ),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  entry.value.key,
                                  style: const TextStyle(fontSize: 11),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),

            // 카테고리 상세 테이블
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            ...categoryData.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: Text(
                        entry.value.key,
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                    Expanded(
                      flex: 2,
                      child: Text(
                        _formatAmount(entry.value.value['amount'] as double),
                        style: const TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w500),
                        textAlign: TextAlign.right,
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 40,
                      child: Text(
                        '${entry.value.value['count']}건',
                        style: TextStyle(
                            fontSize: 11, color: Colors.grey[600]),
                        textAlign: TextAlign.right,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Map<int, MapEntry<String, Map<String, dynamic>>> _calculateCategoryData() {
    final map = <String, Map<String, dynamic>>{};
    for (final p in purchases) {
      map.putIfAbsent(p.category, () => {'amount': 0.0, 'count': 0});
      map[p.category]!['amount'] =
          (map[p.category]!['amount'] as double) + p.amount;
      map[p.category]!['count'] =
          (map[p.category]!['count'] as int) + 1;
    }

    // 금액 내림차순 정렬
    final sorted = map.entries.toList()
      ..sort((a, b) => (b.value['amount'] as double)
          .compareTo(a.value['amount'] as double));

    return Map.fromEntries(
      sorted.asMap().entries.map((e) => MapEntry(e.key, e.value)),
    );
  }

  List<PieChartSectionData> _buildSections(
      Map<int, MapEntry<String, Map<String, dynamic>>> data) {
    final totalAmount =
        purchases.fold<double>(0, (s, p) => s + p.amount);

    return data.entries.take(6).map((entry) {
      final amount = entry.value.value['amount'] as double;
      final percentage = totalAmount > 0 ? (amount / totalAmount * 100) : 0;
      final color = _colors[entry.key % _colors.length];

      return PieChartSectionData(
        value: amount,
        title: percentage > 5 ? '${percentage.toStringAsFixed(0)}%' : '',
        color: color,
        radius: 50,
        titleStyle: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    }).toList();
  }

  String _formatAmount(double amount) {
    if (amount >= 10000) {
      return '${(amount / 10000).toStringAsFixed(1)}만';
    }
    return '${amount.toInt()}';
  }

  static const _colors = [
    Color(0xFF6366F1),
    Color(0xFF22C55E),
    Color(0xFFF59E0B),
    Color(0xFFEF4444),
    Color(0xFF8B5CF6),
    Color(0xFF06B6D4),
    Color(0xFFF97316),
    Color(0xFFEC4899),
  ];
}
