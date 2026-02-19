/// 앱 전역 상수
class AppConstants {
  AppConstants._();

  static const String appName = 'BuyWise';
  static const String appVersion = '1.0.0';

  // 무료 사용 제한
  static const int freeUsageLimit = 5;

  // 카테고리 (한국어)
  static const List<String> categoriesKo = [
    '전자제품', '의류', '식비', '취미', '미용/건강',
    '생활용품', '도서', '교육', '교통', '기타',
  ];

  // 카테고리 (일본어)
  static const List<String> categoriesJa = [
    '電子製品', '衣類', '食費', '趣味', '美容/健康',
    '生活用品', '書籍', '教育', '交通', 'その他',
  ];

  // 식비 키워드 (후회점수 특수 처리)
  static const Set<String> foodKeywords = {
    '식비', '음식', '배달', '카페', '커피', '외식', '식료품', '간식', '식사', '음료',
    '食費', '食品', 'デリバリー', 'カフェ', 'コーヒー', '外食', '食料品', '間食', '食事', '飲料',
  };

  // 후회 등급 경계
  static const List<double> regretThresholds = [20, 35, 50, 65, 100];

  // OpenAI
  static const String openaiModel = 'gpt-4o-mini';
  static const double openaiTemperature = 0.7;
  static const int openaiMaxTokens = 800;
  static const int openaiInsightsMaxTokens = 1500;
}
