import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../models/purchase.dart';
import '../../l10n/translations.dart';

/// 후회 등급 분포 차트
class RegretDistributionChart extends StatelessWidget {
  final List<Purchase> purchases;
  final String lang;

  const RegretDistributionChart({
    super.key,
    required this.purchases,
    required this.lang,
  });

  @override
  Widget build(BuildContext context) {
    final distribution = _calculateDistribution();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppTranslations.t('grade_dist', lang: lang),
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: distribution.values
                          .fold<double>(0, (a, b) => a > b ? a : b) +
                      1,
                  barGroups: _buildBarGroups(distribution),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final labels = [
                            AppTranslations.t(
                                'grade_very_satisfied', lang: lang),
                            AppTranslations.t(
                                'grade_satisfied', lang: lang),
                            AppTranslations.t(
                                'grade_neutral', lang: lang),
                            AppTranslations.t(
                                'grade_regretful', lang: lang),
                            AppTranslations.t(
                                'grade_very_regretful', lang: lang),
                          ];
                          final idx = value.toInt();
                          if (idx >= 0 && idx < labels.length) {
                            return Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                labels[idx],
                                style: const TextStyle(fontSize: 10),
                              ),
                            );
                          }
                          return const SizedBox.shrink();
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 28,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toInt().toString(),
                            style: TextStyle(
                                fontSize: 10, color: Colors.grey[600]),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 1,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: Colors.grey[200]!,
                      strokeWidth: 1,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Map<String, double> _calculateDistribution() {
    int verySatisfied = 0, satisfied = 0, neutral = 0;
    int regretful = 0, veryRegretful = 0;

    for (final p in purchases) {
      final score = p.regretScore ?? 0;
      if (score <= 20) {
        verySatisfied++;
      } else if (score <= 35) {
        satisfied++;
      } else if (score <= 50) {
        neutral++;
      } else if (score <= 65) {
        regretful++;
      } else {
        veryRegretful++;
      }
    }

    return {
      'very_satisfied': verySatisfied.toDouble(),
      'satisfied': satisfied.toDouble(),
      'neutral': neutral.toDouble(),
      'regretful': regretful.toDouble(),
      'very_regretful': veryRegretful.toDouble(),
    };
  }

  List<BarChartGroupData> _buildBarGroups(Map<String, double> dist) {
    final colors = [
      const Color(0xFF4CAF50),
      const Color(0xFF8BC34A),
      const Color(0xFFFFEB3B),
      const Color(0xFFFF9800),
      const Color(0xFFF44336),
    ];

    final values = dist.values.toList();

    return List.generate(values.length, (i) {
      return BarChartGroupData(
        x: i,
        barRods: [
          BarChartRodData(
            toY: values[i],
            color: colors[i],
            width: 28,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(6),
              topRight: Radius.circular(6),
            ),
          ),
        ],
      );
    });
  }
}
