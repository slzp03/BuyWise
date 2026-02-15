import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/supabase_service.dart';
import '../models/analysis.dart';
import '../l10n/translations.dart';

/// 분석 이력 화면
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<Analysis> _analyses = [];
  bool _isLoading = false;

  String get _lang {
    return context.read<AuthService>().currentUser?.language ?? 'ko';
  }

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final userId = context.read<AuthService>().currentUser?.id;
    if (userId == null) return;

    setState(() => _isLoading = true);

    final analyses =
        await SupabaseService.instance.loadAnalyses(userId);

    setState(() {
      _analyses = analyses;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final lang = _lang;

    return Scaffold(
      appBar: AppBar(
        title: Text(AppTranslations.t('nav_history', lang: lang)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _analyses.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.history,
                          size: 64, color: Colors.grey[300]),
                      const SizedBox(height: 16),
                      Text(
                        lang == 'ja'
                            ? '分析履歴がありません。'
                            : '아직 분석 이력이 없습니다.',
                        style: TextStyle(color: Colors.grey[500]),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadHistory,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _analyses.length,
                    itemBuilder: (context, index) {
                      return _buildAnalysisCard(_analyses[index], lang);
                    },
                  ),
                ),
    );
  }

  Widget _buildAnalysisCard(Analysis analysis, String lang) {
    final dateStr = analysis.createdAt != null
        ? DateFormat('yyyy-MM-dd HH:mm').format(analysis.createdAt!)
        : '-';

    final score = analysis.averageRegretScore;
    final scoreColor = score > 65
        ? Colors.red
        : score > 50
            ? Colors.orange
            : score > 35
                ? Colors.amber
                : Colors.green;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 날짜 + 점수
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  dateStr,
                  style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: scoreColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${score.toStringAsFixed(1)}점',
                    style: TextStyle(
                      color: scoreColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 요약 정보
            Row(
              children: [
                _InfoChip(
                  icon: Icons.shopping_bag,
                  label: '${analysis.purchaseCount}건',
                ),
                const SizedBox(width: 12),
                _InfoChip(
                  icon: Icons.payments,
                  label:
                      '${(analysis.totalSpent / 10000).toStringAsFixed(1)}만',
                ),
                const SizedBox(width: 12),
                _InfoChip(
                  icon: Icons.warning_amber,
                  label: '후회 ${analysis.highRegretCount}건',
                ),
              ],
            ),

            // AI 분석 결과 미리보기
            if (analysis.psychologyAnalysis != null &&
                analysis.psychologyAnalysis!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                analysis.psychologyAnalysis!.length > 100
                    ? '${analysis.psychologyAnalysis!.substring(0, 100)}...'
                    : analysis.psychologyAnalysis!,
                style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey[600]),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }
}
