import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../config/constants.dart';

/// OpenAI API 서비스 (openai_service.py → Dart 변환)
class OpenAIService {
  OpenAIService._();
  static final OpenAIService instance = OpenAIService._();

  String get _apiKey => dotenv.env['OPENAI_API_KEY'] ?? '';
  bool get isAvailable => _apiKey.isNotEmpty && _apiKey.startsWith('sk-');

  /// 소비 심리 분석 생성
  Future<AiResult> generatePsychologyAnalysis({
    required double overallScore,
    required int totalPurchases,
    required double totalAmount,
    required double regretRatio,
    required String mainCause,
    required List<Map<String, dynamic>> topRegretItems,
    required Map<String, Map<String, dynamic>> categoryBreakdown,
    String language = 'ko',
  }) async {
    if (!isAvailable) {
      return AiResult.error('API 키가 설정되지 않았습니다.');
    }

    // 카테고리 포맷
    final categoryInfo = categoryBreakdown.entries
        .take(5)
        .map((e) =>
            '  - ${e.key}: ${e.value['count']}건, 총 ${_formatCurrency(e.value['amount'])}')
        .join('\n');

    // 상위 후회 항목 포맷
    final regretInfo = topRegretItems
        .take(5)
        .asMap()
        .entries
        .map((e) =>
            '  ${e.key + 1}. ${e.value['category']} - ${e.value['product']} '
            '(${_formatCurrency(e.value['amount'])}, 후회점수: ${(e.value['score'] as double).toStringAsFixed(1)})')
        .join('\n');

    final prompt = '''당신은 20년 경력의 소비 심리 전문가이자 재무 상담가입니다.

# 분석 데이터

## 전체 개요
- **후회 점수**: ${overallScore.toStringAsFixed(1)}/100
- **총 구매 건수**: ${totalPurchases}건
- **총 지출 금액**: ${_formatCurrency(totalAmount)}
- **후회 구매 비율**: ${regretRatio.toStringAsFixed(1)}%
- **주요 후회 원인**: $mainCause

## 카테고리별 분석
${categoryInfo.isNotEmpty ? categoryInfo : "데이터 없음"}

## 후회 점수 높은 구매 TOP 5
${regretInfo.isNotEmpty ? regretInfo : "데이터 없음"}

# 응답 형식

## 📊 당신의 소비 패턴 한눈에 보기
(2-3문장으로 요약)

## 🔍 후회 구매의 주요 원인 3가지
1. **[원인 1]**: [설명]
2. **[원인 2]**: [설명]
3. **[원인 3]**: [설명]

## 💡 지금 바로 실천 가능한 개선 방안
1. **[방안 1]**: [팁]
2. **[방안 2]**: [팁]
3. **[방안 3]**: [팁]

## 🎯 이번 달 도전 과제
**목표**: [구체적 목표]
**실천 방법**: [액션 아이템]

길이: 500자 이내. 톤: 친근한 상담사.
${language == 'ja' ? '\n重要: 日本語で回答してください。' : ''}''';

    final systemMsg = language == 'ja'
        ? 'あなたは消費心理の専門家です。日本語で回答してください。'
        : '당신은 소비 심리 전문가이자 재무 상담가입니다.';

    return _callApi(
      systemMessage: systemMsg,
      userMessage: prompt,
      maxTokens: AppConstants.openaiMaxTokens,
    );
  }

  /// 스마트 인사이트 생성
  Future<AiResult> generateSmartInsights({
    required double overallScore,
    required int totalPurchases,
    required double totalAmount,
    required List<Map<String, dynamic>> targetItems,
    required Map<String, double> categorySpending,
    String language = 'ko',
  }) async {
    if (!isAvailable) {
      return AiResult.error('API 키가 설정되지 않았습니다.');
    }

    final itemsText = targetItems.asMap().entries.map((e) {
      final item = e.value;
      return '${e.key + 1}. [${item['category']}] ${item['product']} '
          '- ${_formatCurrency(item['amount'])} '
          '(후회점수: ${(item['score'] as double).toStringAsFixed(0)}, '
          '필요도: ${item['necessity']}, 사용빈도: ${item['usage']})';
    }).join('\n');

    final categoryText = categorySpending.entries
        .map((e) => '- ${e.key}: ${_formatCurrency(e.value)}')
        .join('\n');

    final shopUrl = language == 'ja'
        ? 'https://www.amazon.co.jp/s?k='
        : 'https://www.coupang.com/np/search?q=';

    final prompt = '''소비 데이터 분석 전문가로서 스마트 인사이트를 생성하세요.

# 데이터
- 후회 점수: ${overallScore.toStringAsFixed(1)}/100
- 총 ${totalPurchases}건, ${_formatCurrency(totalAmount)}

## 구매 항목
$itemsText

## 카테고리별 지출
$categoryText

# 요청: 아래 4가지 인사이트 작성

## 🏷️ 소비패턴 분류
- **[상품명]** (금액): [패턴 유형] - [설명]

## 🔄 유사 사용자 재구매율
- **[상품명]**: 재구매율 약 XX% → [해석]

## 💰 장기 저축 효과
- **[카테고리]**: 30% 절감 시 연간 약 ₩XXX 저축

## 🛒 추천 구매목록 TOP 5
1. **[브랜드+상품명]** (예상 금액): [추천 이유]
   → [쇼핑몰에서 보기](${shopUrl}검색어)

## 💡 절약 추천 TOP 5
1. **[방법]**: [실천 방안] → 예상 월 절약 ₩XX,XXX

톤: 친근하고 유용. 구체적 숫자 포함.
${language == 'ja' ? '日本語で回答してください。' : '한국어로 작성'}''';

    final systemMsg = language == 'ja'
        ? '消費データ分析の専門家です。日本語で回答してください。'
        : '소비 데이터 분석 전문가입니다.';

    return _callApi(
      systemMessage: systemMsg,
      userMessage: prompt,
      maxTokens: AppConstants.openaiInsightsMaxTokens,
    );
  }

  /// OpenAI API 호출
  Future<AiResult> _callApi({
    required String systemMessage,
    required String userMessage,
    int maxTokens = 800,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('https://api.openai.com/v1/chat/completions'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_apiKey',
        },
        body: jsonEncode({
          'model': AppConstants.openaiModel,
          'messages': [
            {'role': 'system', 'content': systemMessage},
            {'role': 'user', 'content': userMessage},
          ],
          'temperature': AppConstants.openaiTemperature,
          'max_tokens': maxTokens,
          'frequency_penalty': 0.3,
          'presence_penalty': 0.3,
        }),
      );

      if (response.statusCode != 200) {
        return AiResult.error(
            'API 오류 (${response.statusCode}): ${response.body}');
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final content =
          data['choices'][0]['message']['content'] as String;
      final usage = data['usage'] as Map<String, dynamic>;

      return AiResult(
        success: true,
        content: content.trim(),
        promptTokens: usage['prompt_tokens'] as int,
        completionTokens: usage['completion_tokens'] as int,
        totalTokens: usage['total_tokens'] as int,
      );
    } catch (e) {
      return AiResult.error('AI 분석 중 오류: $e');
    }
  }

  String _formatCurrency(dynamic amount) {
    final num value = amount is num ? amount : 0;
    // 간단한 천 단위 구분
    final str = value.toInt().toString();
    final buffer = StringBuffer();
    for (int i = 0; i < str.length; i++) {
      if (i > 0 && (str.length - i) % 3 == 0) buffer.write(',');
      buffer.write(str[i]);
    }
    return '₩$buffer';
  }
}

/// AI 결과 모델
class AiResult {
  final bool success;
  final String content;
  final String? errorMessage;
  final int promptTokens;
  final int completionTokens;
  final int totalTokens;

  const AiResult({
    required this.success,
    this.content = '',
    this.errorMessage,
    this.promptTokens = 0,
    this.completionTokens = 0,
    this.totalTokens = 0,
  });

  factory AiResult.error(String message) {
    return AiResult(
      success: false,
      errorMessage: message,
    );
  }
}
