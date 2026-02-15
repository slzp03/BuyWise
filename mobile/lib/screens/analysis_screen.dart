import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/supabase_service.dart';
import '../services/regret_calculator.dart';
import '../services/openai_service.dart';
import '../models/purchase.dart';
import '../models/analysis.dart';
import '../l10n/translations.dart';
import '../widgets/charts/regret_chart.dart';
import '../widgets/charts/category_chart.dart';

/// 분석 화면
class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  List<Purchase> _purchases = [];
  bool _isLoading = false;
  bool _isAnalyzing = false;
  bool _hasAnalyzed = false;
  String? _psychologyResult;
  String? _insightsResult;

  String get _lang {
    return context.read<AuthService>().currentUser?.language ?? 'ko';
  }

  String? get _userId {
    return context.read<AuthService>().currentUser?.id;
  }

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (_userId == null) return;

    setState(() => _isLoading = true);

    final purchases =
        await SupabaseService.instance.loadPurchases(_userId!);

    // 후회 점수 계산
    if (purchases.isNotEmpty) {
      RegretCalculator.addRegretScores(purchases);
    }

    setState(() {
      _purchases = purchases;
      _isLoading = false;
    });
  }

  Future<void> _runAiAnalysis() async {
    if (_purchases.isEmpty) return;

    final auth = context.read<AuthService>();
    if (!auth.canUse) {
      _showUsageLimitDialog();
      return;
    }

    setState(() => _isAnalyzing = true);

    // 데이터 준비
    final totalAmount = _purchases.fold<double>(0, (s, p) => s + p.amount);
    final avgScore = _purchases.fold<double>(
            0, (s, p) => s + (p.regretScore ?? 0)) /
        _purchases.length;
    final regretPurchases =
        _purchases.where((p) => (p.regretScore ?? 0) > 50).toList();
    final regretRatio = regretPurchases.length / _purchases.length * 100;

    // 카테고리별 정보
    final categoryBreakdown = <String, Map<String, dynamic>>{};
    for (final p in _purchases) {
      categoryBreakdown.putIfAbsent(
          p.category, () => {'count': 0, 'amount': 0.0});
      categoryBreakdown[p.category]!['count'] =
          (categoryBreakdown[p.category]!['count'] as int) + 1;
      categoryBreakdown[p.category]!['amount'] =
          (categoryBreakdown[p.category]!['amount'] as double) + p.amount;
    }

    // 상위 후회 아이템
    final sorted = List<Purchase>.from(_purchases)
      ..sort(
          (a, b) => (b.regretScore ?? 0).compareTo(a.regretScore ?? 0));
    final topRegret = sorted.take(5).map((p) => {
          'category': p.category,
          'product': p.productName,
          'amount': p.amount,
          'score': p.regretScore ?? 0.0,
          'necessity': p.necessityScore,
          'usage': p.usageFrequency,
        }).toList();

    // 주요 후회 원인
    final factorSums = <String, double>{};
    for (final p in _purchases) {
      if (p.regretFactors != null) {
        p.regretFactors!.forEach((key, value) {
          if (key != 'total_score') {
            factorSums[key] = (factorSums[key] ?? 0) + value;
          }
        });
      }
    }
    String mainCause = '알 수 없음';
    if (factorSums.isNotEmpty) {
      final topEntry = factorSums.entries
          .reduce((a, b) => a.value > b.value ? a : b);
      mainCause = topEntry.key;
    }

    // 카테고리별 지출
    final categorySpending = <String, double>{};
    for (final p in _purchases) {
      categorySpending[p.category] =
          (categorySpending[p.category] ?? 0) + p.amount;
    }

    // 두 API 동시 호출
    final results = await Future.wait([
      OpenAIService.instance.generatePsychologyAnalysis(
        overallScore: avgScore,
        totalPurchases: _purchases.length,
        totalAmount: totalAmount,
        regretRatio: regretRatio,
        mainCause: mainCause,
        topRegretItems: topRegret,
        categoryBreakdown: categoryBreakdown,
        language: _lang,
      ),
      OpenAIService.instance.generateSmartInsights(
        overallScore: avgScore,
        totalPurchases: _purchases.length,
        totalAmount: totalAmount,
        targetItems: topRegret,
        categorySpending: categorySpending,
        language: _lang,
      ),
    ]);

    final psychResult = results[0];
    final insightResult = results[1];

    // DB에 분석 결과 저장
    if (_userId != null) {
      final analysis = Analysis(
        purchaseCount: _purchases.length,
        totalSpent: totalAmount,
        averageRegretScore: avgScore,
        highRegretCount: regretPurchases.length,
        psychologyAnalysis:
            psychResult.success ? psychResult.content : null,
        smartInsights:
            insightResult.success ? insightResult.content : null,
      );
      final analysisId = await SupabaseService.instance
          .saveAnalysis(_userId!, analysis);

      // AI 사용량 로그
      if (psychResult.success) {
        await SupabaseService.instance.logAiUsage(
          userId: _userId!,
          analysisId: analysisId,
          callType: 'psychology',
          promptTokens: psychResult.promptTokens,
          completionTokens: psychResult.completionTokens,
          totalTokens: psychResult.totalTokens,
        );
      }
      if (insightResult.success) {
        await SupabaseService.instance.logAiUsage(
          userId: _userId!,
          analysisId: analysisId,
          callType: 'smart_insights',
          promptTokens: insightResult.promptTokens,
          completionTokens: insightResult.completionTokens,
          totalTokens: insightResult.totalTokens,
        );
      }

      // 사용 횟수 증가
      await auth.incrementUsage();
    }

    setState(() {
      _psychologyResult =
          psychResult.success ? psychResult.content : psychResult.errorMessage;
      _insightsResult = insightResult.success
          ? insightResult.content
          : insightResult.errorMessage;
      _isAnalyzing = false;
      _hasAnalyzed = true;
    });
  }

  void _showUsageLimitDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('사용 제한'),
        content: const Text(
            '무료 사용 횟수를 모두 소진하셨습니다.\n프리미엄 플랜으로 업그레이드하세요.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lang = _lang;

    return Scaffold(
      appBar: AppBar(
        title: Text(AppTranslations.t('nav_analysis', lang: lang)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _purchases.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.analytics_outlined,
                          size: 64, color: Colors.grey[300]),
                      const SizedBox(height: 16),
                      Text(
                        AppTranslations.t('no_purchases_yet', lang: lang),
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey[500]),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 요약 카드
                      _buildSummaryCards(lang),
                      const SizedBox(height: 24),

                      // 후회 등급 분포 차트
                      RegretDistributionChart(
                          purchases: _purchases, lang: lang),
                      const SizedBox(height: 24),

                      // 카테고리 분석 차트
                      CategoryChart(purchases: _purchases, lang: lang),
                      const SizedBox(height: 24),

                      // AI 분석 버튼
                      _buildAiSection(lang),
                    ],
                  ),
                ),
    );
  }

  Widget _buildSummaryCards(String lang) {
    final totalAmount = _purchases.fold<double>(0, (s, p) => s + p.amount);
    final avgScore = _purchases.fold<double>(
            0, (s, p) => s + (p.regretScore ?? 0)) /
        _purchases.length;
    final regretCount =
        _purchases.where((p) => (p.regretScore ?? 0) > 50).length;
    final categories = _purchases.map((p) => p.category).toSet().length;

    return Column(
      children: [
        Row(
          children: [
            _SummaryCard(
              title: AppTranslations.t('total_purchases', lang: lang),
              value: '${_purchases.length}',
              icon: Icons.shopping_bag,
              color: Colors.blue,
            ),
            const SizedBox(width: 12),
            _SummaryCard(
              title: AppTranslations.t('total_amount', lang: lang),
              value: '${(totalAmount / 10000).toStringAsFixed(1)}만',
              icon: Icons.payments,
              color: Colors.green,
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _SummaryCard(
              title: AppTranslations.t('overall_regret', lang: lang),
              value: avgScore.toStringAsFixed(1),
              icon: Icons.sentiment_dissatisfied,
              color: avgScore > 50 ? Colors.red : Colors.orange,
            ),
            const SizedBox(width: 12),
            _SummaryCard(
              title: AppTranslations.t('num_categories', lang: lang),
              value: '$categories',
              icon: Icons.category,
              color: Colors.purple,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAiSection(String lang) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.auto_awesome, color: Color(0xFF6366F1)),
                const SizedBox(width: 8),
                Text(
                  AppTranslations.t('ai_analysis', lang: lang),
                  style: const TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            if (!_hasAnalyzed && !_isAnalyzing)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _runAiAnalysis,
                  icon: const Icon(Icons.auto_awesome),
                  label: Text(AppTranslations.t('btn_ai', lang: lang)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),

            if (_isAnalyzing) ...[
              const Center(child: CircularProgressIndicator()),
              const SizedBox(height: 12),
              Center(
                child: Text(
                  AppTranslations.t('ai_analyzing', lang: lang),
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ),
            ],

            if (_hasAnalyzed && _psychologyResult != null) ...[
              const Divider(),
              const SizedBox(height: 8),
              SelectableText(
                _psychologyResult!,
                style: const TextStyle(fontSize: 14, height: 1.6),
              ),
            ],

            if (_hasAnalyzed && _insightsResult != null) ...[
              const SizedBox(height: 24),
              const Divider(),
              const SizedBox(height: 8),
              SelectableText(
                _insightsResult!,
                style: const TextStyle(fontSize: 14, height: 1.6),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _SummaryCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 18, color: color),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      title,
                      style: TextStyle(
                          fontSize: 11, color: Colors.grey[600]),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                value,
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
