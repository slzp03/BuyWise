/// 다국어 번역 모듈 (ko/ja)
class AppTranslations {
  AppTranslations._();

  static const Map<String, Map<String, String>> _translations = {
    'ko': {
      // 앱
      'app_title': 'BuyWise',
      'app_subtitle': '데이터 기반 구매 패턴 분석으로 현명한 소비 습관을 만들어보세요',

      // 네비게이션
      'nav_expense': '가계부',
      'nav_analysis': '분석',
      'nav_history': '이력',
      'nav_settings': '설정',

      // 가계부
      'expense_tracker': '가계부',
      'quick_add': '지출 기록',
      'my_purchases': '내 구매 이력',
      'delete_selected': '선택 삭제',
      'period_filter': '기간',
      'period_1m': '최근 1개월',
      'period_3m': '최근 3개월',
      'period_6m': '최근 6개월',
      'period_all': '전체',
      'no_purchases_yet': '아직 기록된 구매가 없습니다.\n위에서 지출을 기록해보세요!',
      'analyze_accumulated': '누적 데이터 분석',
      'purchase_saved': '기록되었습니다!',
      'purchases_deleted': '건이 삭제되었습니다.',
      'total_records': '총 기록',
      'select_to_delete': '삭제할 항목을 선택하세요',

      // 입력 폼
      'product_name': '상품명',
      'product_placeholder': '예: 무선이어폰',
      'amount': '금액 (원)',
      'thinking_days': '고민 기간 (일)',
      'thinking_help': '구매 전 얼마나 고민했나요? (0 = 충동 구매)',
      'category': '카테고리',
      'category_custom': '직접 입력',
      'purchase_date': '구매 날짜',
      'repurchase': '재구매 의향',
      'repurchase_yes': '예',
      'repurchase_no': '아니오',
      'usage_freq': '사용빈도',
      'usage_help': '실제로 얼마나 자주 사용하고 있나요?\n(1: 전혀 안씀, 5: 매일 사용)',
      'necessity_auto': '자동 계산된 필요도',
      'btn_save': '저장',
      'btn_analyze': '분석 시작',

      // 분석
      'total_purchases': '총 구매 건수',
      'total_amount': '총 지출 금액',
      'avg_amount': '평균 구매 금액',
      'num_categories': '카테고리 수',
      'overall_regret': '전체 후회 점수',
      'regret_ratio': '후회 구매 비율',
      'regret_amount': '후회 구매 금액',
      'main_cause': '주요 후회 원인',
      'grade_dist': '후회 등급 분포',
      'top_regret': '후회 점수 높은 구매 TOP 10',
      'top_satisfied': '만족도 높은 구매 TOP 10',
      'factor_analysis': '후회 점수 요인별 기여도',
      'category_analysis': '카테고리 분석',
      'monthly_trend': '월별 지출 추이',

      // AI 분석
      'ai_analysis': 'AI 종합 분석',
      'btn_ai': 'AI 분석 시작',
      'ai_analyzing': '소비 패턴을 분석하고 있습니다...',
      'ai_complete': '분석 완료!',

      // 후회 등급
      'grade_very_satisfied': '매우 만족',
      'grade_satisfied': '만족',
      'grade_neutral': '보통',
      'grade_regretful': '아쉬움',
      'grade_very_regretful': '후회',

      // 후회 요인
      'factor_necessity_gap': '필요도-사용빈도 갭',
      'factor_time_decay': '시간 경과',
      'factor_amount': '금액 가중치',
      'factor_recency': '최근성',
      'factor_repeat': '반복 구매',
      'factor_night': '새벽 구매',
      'factor_impulse': '충동 패턴',

      // 로그인
      'login_required': '이 서비스를 이용하려면 Google 계정으로 로그인이 필요합니다.',
      'google_login': 'Google로 로그인',
      'logout': '로그아웃',
      'my_account': '내 계정',
      'premium': '프리미엄 회원',
      'free_plan': '무료 플랜',
      'remaining': '회 남음',

      // 설정
      'settings': '설정',
      'language': '언어',
      'dark_mode': '다크 모드',
      'notifications': '알림',
      'about': '앱 정보',
      'version': '버전',

      // 에러
      'input_error_product': '상품명을 입력해주세요.',
      'input_error_amount': '금액은 0보다 커야 합니다.',
      'input_error_category': '카테고리를 선택해주세요.',
      'network_error': '네트워크 오류가 발생했습니다.',
      'unknown_error': '알 수 없는 오류가 발생했습니다.',

      // 필요도 라벨
      'necessity_1': '충동 구매',
      'necessity_2': '약간 신중',
      'necessity_3': '보통',
      'necessity_4': '신중함',
      'necessity_5': '매우 신중',

      // 통화
      'currency_symbol': '₩',
      'currency_format': '#,###원',
    },

    'ja': {
      // アプリ
      'app_title': 'BuyWise',
      'app_subtitle': 'データに基づく購買パターン分析で賢い消費習慣を身につけましょう',

      // ナビゲーション
      'nav_expense': '家計簿',
      'nav_analysis': '分析',
      'nav_history': '履歴',
      'nav_settings': '設定',

      // 家計簿
      'expense_tracker': '家計簿',
      'quick_add': '支出記録',
      'my_purchases': '購入履歴',
      'delete_selected': '選択削除',
      'period_filter': '期間',
      'period_1m': '最近1ヶ月',
      'period_3m': '最近3ヶ月',
      'period_6m': '最近6ヶ月',
      'period_all': 'すべて',
      'no_purchases_yet': 'まだ記録された購入がありません。\n上から支出を記録してみましょう！',
      'analyze_accumulated': '蓄積データ分析',
      'purchase_saved': '記録されました！',
      'purchases_deleted': '件が削除されました。',
      'total_records': '総記録',
      'select_to_delete': '削除するアイテムを選択してください',

      // 入力フォーム
      'product_name': '商品名',
      'product_placeholder': '例: ワイヤレスイヤホン',
      'amount': '金額 (円)',
      'thinking_days': '検討期間 (日)',
      'thinking_help': '購入前にどれくらい悩みましたか？（0 = 衝動買い）',
      'category': 'カテゴリ',
      'category_custom': '直接入力',
      'purchase_date': '購入日',
      'repurchase': '再購入意向',
      'repurchase_yes': 'はい',
      'repurchase_no': 'いいえ',
      'usage_freq': '使用頻度',
      'usage_help': '実際にどれくらい使っていますか？\n（1: 全く使わない、5: 毎日使用）',
      'necessity_auto': '自動計算された必要度',
      'btn_save': '保存',
      'btn_analyze': '分析開始',

      // 分析
      'total_purchases': '総購入件数',
      'total_amount': '総支出金額',
      'avg_amount': '平均購入金額',
      'num_categories': 'カテゴリ数',
      'overall_regret': '全体後悔スコア',
      'regret_ratio': '後悔購入割合',
      'regret_amount': '後悔購入金額',
      'main_cause': '主な後悔原因',
      'grade_dist': '後悔等級分布',
      'top_regret': '後悔スコアが高い購入 TOP 10',
      'top_satisfied': '満足度が高い購入 TOP 10',
      'factor_analysis': '後悔スコア要因別寄与度',
      'category_analysis': 'カテゴリ分析',
      'monthly_trend': '月別支出推移',

      // AI分析
      'ai_analysis': 'AI総合分析',
      'btn_ai': 'AI分析開始',
      'ai_analyzing': '消費パターンを分析しています...',
      'ai_complete': '分析完了！',

      // 後悔等級
      'grade_very_satisfied': '非常に満足',
      'grade_satisfied': '満足',
      'grade_neutral': '普通',
      'grade_regretful': '残念',
      'grade_very_regretful': '後悔',

      // 後悔要因
      'factor_necessity_gap': '必要度-使用頻度ギャップ',
      'factor_time_decay': '時間経過',
      'factor_amount': '金額加重',
      'factor_recency': '最近性',
      'factor_repeat': '繰り返し購入',
      'factor_night': '深夜購入',
      'factor_impulse': '衝動パターン',

      // ログイン
      'login_required': 'このサービスを利用するにはGoogleアカウントでのログインが必要です。',
      'google_login': 'Googleでログイン',
      'logout': 'ログアウト',
      'my_account': 'マイアカウント',
      'premium': 'プレミアム会員',
      'free_plan': '無料プラン',
      'remaining': '回残り',

      // 設定
      'settings': '設定',
      'language': '言語',
      'dark_mode': 'ダークモード',
      'notifications': '通知',
      'about': 'アプリ情報',
      'version': 'バージョン',

      // エラー
      'input_error_product': '商品名を入力してください。',
      'input_error_amount': '金額は0より大きくなければなりません。',
      'input_error_category': 'カテゴリを選択してください。',
      'network_error': 'ネットワークエラーが発生しました。',
      'unknown_error': '不明なエラーが発生しました。',

      // 必要度ラベル
      'necessity_1': '衝動買い',
      'necessity_2': 'やや慎重',
      'necessity_3': '普通',
      'necessity_4': '慎重',
      'necessity_5': '非常に慎重',

      // 通貨
      'currency_symbol': '¥',
      'currency_format': '#,###円',
    },
  };

  /// 번역 텍스트 반환 (키가 없으면 한국어 fallback)
  static String t(String key, {String lang = 'ko'}) {
    final translations = _translations[lang] ?? _translations['ko']!;
    return translations[key] ?? _translations['ko']?[key] ?? key;
  }

  /// 카테고리 목록 반환
  static List<String> categories(String lang) {
    if (lang == 'ja') {
      return const [
        '電子製品', '衣類', '食費', '趣味', '美容/健康',
        '生活用品', '書籍', '教育', '交通', 'その他',
      ];
    }
    return const [
      '전자제품', '의류', '식비', '취미', '미용/건강',
      '생활용품', '도서', '교육', '교통', '기타',
    ];
  }
}
