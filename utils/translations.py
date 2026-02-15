"""
다국어 번역 모듈

한국어(ko)와 일본어(ja) 지원
"""

# 일본어 CSV 컬럼 → 한국어 내부 컬럼 매핑
JA_COLUMN_MAP = {
    '日付': '날짜',
    '카테고리': 'カテゴリ',  # 역방향은 아래서 처리
    'カテゴリ': '카테고리',
    '商品名': '상품명',
    '金額': '금액',
    '検討期間': '고민기간',
    '再購入意向': '재구매의향',
    '使用頻度': '사용빈도',
    '必要度': '필요도',
}

# 일본어 → 한국어 컬럼 변환용 (CSV 처리에서 사용)
JA_TO_KO_COLUMNS = {
    '日付': '날짜',
    'カテゴリ': '카테고리',
    '商品名': '상품명',
    '金額': '금액',
    '検討期間': '고민기간',
    '再購入意向': '재구매의향',
    '使用頻度': '사용빈도',
    '必要度': '필요도',
}

TRANSLATIONS = {
    'ko': {
        # 페이지
        'page_title': 'BuyWise! 구매를 현명하게!',
        'page_subtitle': '데이터 기반 구매 패턴 분석으로 현명한 소비 습관을 만들어보세요',

        # 헤더
        'data_input': '데이터 입력',
        'data_preview': '데이터 미리보기',
        'category_analysis': '카테고리 분석',
        'deep_analysis': '심층 분석',
        'regret_score': '후회 점수',
        'ai_analysis': 'AI 종합 분석',
        'summary': '종합 요약',

        # 탭
        'tab_manual': '직접 입력',
        'tab_csv': 'CSV 업로드',

        # 수동 입력
        'manual_title': '구매 항목 정보 입력',
        'manual_desc': '한 번에 한 항목씩 입력하고 \'저장\' 버튼을 누르세요. 여러 항목을 누적 입력할 수 있습니다.',
        'product_name': '상품명',
        'product_placeholder': '예: 무선이어폰',
        'product_help': '구매한 상품의 이름을 입력하세요',
        'amount': '금액 (원)',
        'amount_help': '구매 금액을 입력하세요 (숫자만)',
        'thinking_days': '고민 기간 (일)',
        'thinking_help': '구매 전 얼마나 고민했나요? (0 = 충동 구매)',
        'category': '카테고리',
        'category_help': '구매 카테고리를 선택하세요',
        'category_custom': '직접 입력',
        'category_custom_label': '카테고리 직접 입력',
        'category_custom_placeholder': '예: 반려동물용품',
        'purchase_date': '구매 날짜',
        'purchase_date_help': '구매한 날짜를 선택하세요',
        'repurchase': '재구매 의향',
        'repurchase_yes': '예',
        'repurchase_no': '아니오',
        'repurchase_help': '같은 제품을 다시 구매하고 싶으신가요?',
        'usage_freq': '사용빈도',
        'usage_help': '실제로 얼마나 자주 사용하고 있나요? (1: 전혀 안씀, 5: 매일 사용)',
        'necessity_auto': '자동 계산된 필요도',
        'necessity_labels': ['충동 구매', '약간 신중', '보통', '신중함', '매우 신중'],
        'btn_save': '💾 저장',
        'btn_reset': '초기화',
        'btn_analyze': '🚀 분석 시작',
        'btn_clear': '🗑️ 전체 삭제',
        'saved_items': '저장된 항목',

        # CSV 업로드
        'csv_upload': '구매 내역 CSV 파일을 선택하세요',
        'csv_help': '최대 5MB까지 업로드 가능합니다',
        'csv_upload_success': '파일 업로드 완료!',
        'csv_valid': 'CSV 검증 완료!',
        'csv_invalid': 'CSV 검증 실패',

        # 분석 결과
        'total_purchases': '총 구매 건수',
        'total_amount': '총 지출 금액',
        'avg_amount': '평균 구매 금액',
        'num_categories': '카테고리 수',
        'chart_type': '차트 타입 선택',
        'pie_chart': '파이 차트',
        'bar_chart': '바 차트',
        'category_detail': '카테고리별 상세 통계',
        'amount_dist': '구매 금액 분포',
        'monthly_trend': '월별 지출 추이',
        'necessity_usage': '필요도 vs 사용빈도 분석',
        'scatter_guide': """**해석 가이드**:
    - 대각선 위 (사용빈도 > 필요도): 예상보다 많이 사용한 좋은 구매
    - 대각선 아래 (필요도 > 사용빈도): 생각보다 덜 사용한 후회 구매
    - 버블 크기: 구매 금액""",

        # 후회 점수
        'overall_regret': '전체 후회 점수',
        'regret_ratio': '후회 구매 비율',
        'regret_amount': '후회 구매 금액',
        'main_cause': '주요 후회 원인',
        'satisfied_count': '만족 구매',
        'grade_dist': '후회 등급 분포',
        'top_regret': '후회 점수 높은 구매 TOP 10',
        'top_satisfied': '만족도 높은 구매 TOP 10',
        'factor_analysis': '후회 점수 요인별 기여도',
        'factor_explain': '후회 점수 요인 설명',

        # AI 분석
        'ai_caption': '소비 심리 분석과 맞춤형 인사이트를 한 번에 생성합니다',
        'btn_ai': 'AI 분석 시작',
        'ai_analyzing': '소비 패턴을 분석하고 있습니다...',
        'ai_complete': '분석 완료!',
        'ai_prev_result': '이전에 생성된 분석 결과입니다. 새로 생성하려면 위 버튼을 클릭하세요.',
        'ai_guide': '위 버튼을 클릭하면 AI가 소비 패턴을 분석하고 맞춤형 인사이트를 제공합니다.',
        'ai_preview': '분석 항목 미리보기',
        'basic_tips': '기본 개선 팁',
        'savings_sim': '저축 시뮬레이터',
        'reduction_rate': '절감 비율 (%)',
        'annual_saving': '총 연간 예상 저축액',
        'api_usage': 'API 사용량 정보',

        # 종합 요약
        'regret_purchase_ratio': '후회 구매 비율',
        'regret_purchase_amount': '후회 구매 금액',
        'good_purchase_ratio': '합리적 구매 비율',
        'top_regret_5': '후회 가능성이 높은 구매 TOP 5',
        'top_good_5': '만족도가 높은 구매 TOP 5',

        # 완료
        'analysis_complete': '**분석 완료!**\n- 모든 분석 결과를 확인하셨나요?\n- 정기적으로 구매 데이터를 업데이트하면 소비 패턴 변화를 추적할 수 있습니다!',
        'no_data': '위에서 데이터를 입력하면 분석이 시작됩니다.',

        # 사이드바
        'csv_format': 'CSV 파일 형식',
        'sample_download': '샘플 CSV 다운로드',
        'analysis_tips': '분석 팁',
        'analysis_tips_text': '- 최소 5건 이상의 데이터를 입력하면 더 정확한 분석이 가능합니다\n- 필요도와 사용빈도의 차이가 클수록 후회 점수가 높아집니다',
        'analysis_history': '분석 이력',

        # 로그인
        'login_required': '이 서비스를 이용하려면 Google 계정으로 로그인이 필요합니다.',
        'login': '로그인',
        'logout': '로그아웃',
        'my_account': '내 계정',
        'premium': '프리미엄 회원',
        'free_plan': '무료 플랜',
        'remaining': '회 남음',
        'google_login': 'Google로 로그인',

        # 카테고리 옵션
        'categories': ['전자제품', '의류', '식비', '취미', '미용/건강', '생활용품', '도서', '교육', '교통', '기타'],

        # 후회 등급
        'grade_labels': ['매우 만족\n(0-20)', '만족\n(21-35)', '보통\n(36-50)', '아쉬움\n(51-65)', '후회\n(66-100)'],

        # 후회 원인
        'cause_names': {
            '필요도갭': '필요도-사용빈도 갭',
            '시간경과': '시간 경과',
            '금액': '고가 제품',
            '최근성': '최근 구매',
            '반복구매': '반복 구매',
            '새벽구매': '새벽 시간 구매',
            '충동패턴': '충동 구매 패턴'
        },

        # 언어
        'language': '언어',

        # Buy Me a Coffee
        'support_title': '이 서비스가 도움이 되셨나요?',
        'support_desc': '커피 한 잔으로 후원해주세요!',
        'support_guide': '후원 링크 활성화: <a href="https://www.buymeacoffee.com" target="_blank">계정 생성</a> 후 app.py에서 \'yourname\' 변경',

        # 분석 이력
        'no_analysis_history': '아직 분석 이력이 없습니다.',
        'saved_purchases': '저장된 구매',
        'count_unit': '건',
        'regret_label': '후회',
        'score_unit': '점',

        # 로그인 화면
        'free_plan_desc': '**무료 플랜**:\n- 분석 5회 무료 제공\n- 모든 기능 이용 가능',
        'premium_plan_desc': '**프리미엄 플랜** (월 5,000원):\n- 무제한 분석\n- AI 심리 분석 우선 지원\n- 광고 제거',
        'terms_agree': '로그인 시 [이용약관] 및 [개인정보 처리방침]에 동의하는 것으로 간주됩니다.',

        # 사용 제한 화면
        'usage_warning': '무료 사용 횟수가 {}회 남았습니다.',
        'usage_exhausted': '무료 사용 횟수를 모두 소진하셨습니다.',
        'upgrade_title': '프리미엄 플랜으로 업그레이드',
        'free_plan_features': '**무료 플랜**\n- 분석 5회 제공\n- 기본 기능 이용\n- 광고 표시',
        'premium_plan_features': '**프리미엄 플랜** (월 5,000원)\n- 무제한 분석\n- AI 심리 분석 우선 지원\n- 광고 제거\n- 데이터 무제한 저장',
        'btn_subscribe': '프리미엄 구독하기',
        'payment_coming': '결제 시스템은 곧 오픈 예정입니다!',
        'payment_demo': '현재는 데모 버전으로, 실제 결제는 베타 출시 후 가능합니다.',

        # 후회 점수 계산
        'calculating_regret': '후회 점수 계산 중...',
        'regret_calc_complete': '후회 점수 계산 완료!',
        'file_error': '파일 처리 중 오류 발생',

        # 수동 입력 에러
        'input_error_product': '상품명을 입력해주세요.',
        'input_error_category': '카테고리를 선택하거나 입력해주세요.',
        'input_error_amount': '금액은 0보다 커야 합니다.',
        'save_complete': '저장 완료!',
        'processing_data': '데이터 처리 및 후회 점수 계산 중...',
        'validation_failed': '데이터 검증 실패',
        'analysis_done': '분석 완료!',
        'all_deleted': '모든 항목이 삭제되었습니다.',

        # 카테고리 테이블
        'col_category': '카테고리',
        'col_total_amount': '총 금액',
        'col_avg_amount': '평균 금액',
        'col_count': '구매 건수',
        'col_avg_necessity': '평균 필요도',
        'col_avg_usage': '평균 사용빈도',

        # 후회 점수 분석
        'regret_not_calculated': '후회 점수가 계산되지 않았습니다.',
        'col_grade': '등급',
        'col_count_short': '건수',
        'hover_count': '건수',
        'axis_purchase_count': '구매 건수',

        # 요인 분석
        'factor_necessity_gap': '필요도-사용빈도 갭',
        'factor_time_decay': '시간 경과',
        'factor_amount': '금액 가중치',
        'factor_recency': '최근성',
        'factor_repeat': '반복 구매',
        'factor_night': '새벽 구매',
        'factor_impulse': '충동 패턴',
        'col_factor': '요인',
        'col_avg_score': '평균 점수',
        'hover_avg': '평균',

        # 요인 설명
        'factor_explain_text': """### 각 요인이 후회 점수에 미치는 영향

1. **필요도-사용빈도 갭** (최대 30점)
   - 구매 당시 필요하다고 생각한 정도와 실제 사용 빈도의 차이
   - 갭이 클수록 후회 점수 증가

2. **시간 경과** (최대 15점)
   - 오래전에 구매했는데 사용빈도가 낮으면 점수 증가
   - 시간이 지날수록 가중치 증가

3. **금액 가중치** (최대 20점)
   - 고가 제품일수록 후회 시 심리적 부담이 크므로 가중치 증가
   - 평균 구매 금액 대비 비율로 계산

4. **최근성** (최대 10점)
   - 최근 구매는 충동 구매 가능성이 높음
   - 3일 이내 구매 시 높은 점수

5. **반복 구매** (최대 15점)
   - 같은 카테고리를 짧은 시간 내 반복 구매 시 충동 구매 의심
   - 30일 내 동일 카테고리 구매 건수로 계산

6. **새벽 구매** (최대 10점)
   - 새벽(00:00-05:00) 시간대 구매는 충동 구매 가능성 높음
   - CSV에 시간 정보가 없으면 0점

7. **충동 패턴** (최대 10점)
   - 하루에 여러 건 구매 또는 연속된 날짜에 구매 시 충동 패턴 감지
   - 같은 날 3건 이상 또는 3일 내 5건 이상 시 높은 점수""",

        # AI 분석 에러/안내
        'openai_not_installed': 'OpenAI 라이브러리가 설치되지 않았습니다.',
        'openai_setup_guide': """**OpenAI API 키 설정 방법**:
1. `.env` 파일을 프로젝트 루트에 생성
2. 다음 내용 추가: `OPENAI_API_KEY=sk-your-api-key-here`
3. OpenAI 플랫폼(https://platform.openai.com/api-keys)에서 API 키 발급
4. 앱 재시작

API 키가 없어도 기본 분석은 계속 이용 가능합니다!""",
        'openai_init_error': 'OpenAI 서비스를 초기화할 수 없습니다.',
        'default_tips': [
            '구매 전 24시간 고민 시간을 가져보세요.',
            '구매 목록을 미리 작성하는 습관을 들여보세요.',
            '장바구니에 담고 3일 후 다시 확인하세요.'
        ],
        'api_retry': 'API 키를 확인하거나 잠시 후 다시 시도해주세요.',

        # 토큰 정보
        'token_input': '입력 토큰',
        'token_output': '출력 토큰',
        'token_total': '총 토큰',
        'cost_estimate': '예상 비용',

        # AI 미리보기
        'preview_psychology': '**소비 심리 분석**\n- 소비 패턴 요약 및 주요 후회 원인 분석\n- 실천 가능한 개선 방안과 월간 도전 과제',
        'preview_insights': '**스마트 인사이트**\n- 각 구매의 소비패턴 분류 (스트레스성, 충동적, 계획적 등)\n- 유사 사용자 재구매율 추정\n- 카테고리별 장기 저축 효과 시뮬레이션\n- 추천 구매목록 TOP 5 (쿠팡 링크 포함)',

        # 저축 시뮬레이터
        'col_monthly_avg': '월 평균 지출',
        'col_annual_saving': '% 절감 시 연간 저축',

        # 광고
        'ad_sponsored': 'Sponsored',
        'ad_area': '광고 영역',
        'ad_placeholder': 'AdSense 승인 후 광고가 표시됩니다',

        # 가계부
        'expense_tracker': '가계부',
        'quick_add': '지출 기록',
        'my_purchases': '내 구매 이력',
        'delete_selected': '선택 삭제',
        'period_filter': '기간',
        'period_1m': '최근 1개월',
        'period_3m': '최근 3개월',
        'period_6m': '최근 6개월',
        'period_all': '전체',
        'no_purchases_yet': '아직 기록된 구매가 없습니다. 위에서 지출을 기록해보세요!',
        'analyze_accumulated': '누적 데이터 분석',
        'purchase_saved': '기록되었습니다!',
        'purchases_deleted': '건이 삭제되었습니다.',
        'total_records': '총 기록',
        'select_to_delete': '삭제할 항목을 선택하세요',
    },

    'ja': {
        # ページ
        'page_title': 'BuyWise! 賢く買い物!',
        'page_subtitle': 'データに基づく購買パターン分析で賢い消費習慣を身につけましょう',

        # ヘッダー
        'data_input': 'データ入力',
        'data_preview': 'データプレビュー',
        'category_analysis': 'カテゴリ分析',
        'deep_analysis': '詳細分析',
        'regret_score': '後悔スコア',
        'ai_analysis': 'AI総合分析',
        'summary': '総合まとめ',

        # タブ
        'tab_manual': '手動入力',
        'tab_csv': 'CSVアップロード',

        # 手動入力
        'manual_title': '購入アイテム情報入力',
        'manual_desc': '一つずつ入力して「保存」ボタンを押してください。複数のアイテムを追加できます。',
        'product_name': '商品名',
        'product_placeholder': '例: ワイヤレスイヤホン',
        'product_help': '購入した商品の名前を入力してください',
        'amount': '金額 (円)',
        'amount_help': '購入金額を入力してください（数字のみ）',
        'thinking_days': '検討期間 (日)',
        'thinking_help': '購入前にどれくらい悩みましたか？（0 = 衝動買い）',
        'category': 'カテゴリ',
        'category_help': '購入カテゴリを選択してください',
        'category_custom': '直接入力',
        'category_custom_label': 'カテゴリ直接入力',
        'category_custom_placeholder': '例: ペット用品',
        'purchase_date': '購入日',
        'purchase_date_help': '購入した日付を選択してください',
        'repurchase': '再購入意向',
        'repurchase_yes': 'はい',
        'repurchase_no': 'いいえ',
        'repurchase_help': '同じ商品をもう一度購入したいですか？',
        'usage_freq': '使用頻度',
        'usage_help': '実際にどれくらい使っていますか？（1: 全く使わない、5: 毎日使用）',
        'necessity_auto': '自動計算された必要度',
        'necessity_labels': ['衝動買い', 'やや慎重', '普通', '慎重', '非常に慎重'],
        'btn_save': '💾 保存',
        'btn_reset': 'リセット',
        'btn_analyze': '🚀 分析開始',
        'btn_clear': '🗑️ 全削除',
        'saved_items': '保存済みアイテム',

        # CSVアップロード
        'csv_upload': '購入履歴CSVファイルを選択してください',
        'csv_help': '最大5MBまでアップロード可能です',
        'csv_upload_success': 'ファイルアップロード完了！',
        'csv_valid': 'CSV検証完了！',
        'csv_invalid': 'CSV検証失敗',

        # 分析結果
        'total_purchases': '総購入件数',
        'total_amount': '総支出金額',
        'avg_amount': '平均購入金額',
        'num_categories': 'カテゴリ数',
        'chart_type': 'チャートタイプ選択',
        'pie_chart': '円グラフ',
        'bar_chart': '棒グラフ',
        'category_detail': 'カテゴリ別詳細統計',
        'amount_dist': '購入金額分布',
        'monthly_trend': '月別支出推移',
        'necessity_usage': '必要度 vs 使用頻度分析',
        'scatter_guide': """**解釈ガイド**:
    - 対角線の上（使用頻度 > 必要度）: 予想以上に使った良い購入
    - 対角線の下（必要度 > 使用頻度）: 思ったより使わなかった後悔する購入
    - バブルサイズ: 購入金額""",

        # 後悔スコア
        'overall_regret': '全体後悔スコア',
        'regret_ratio': '後悔購入割合',
        'regret_amount': '後悔購入金額',
        'main_cause': '主な後悔原因',
        'satisfied_count': '満足購入',
        'grade_dist': '後悔等級分布',
        'top_regret': '後悔スコアが高い購入 TOP 10',
        'top_satisfied': '満足度が高い購入 TOP 10',
        'factor_analysis': '後悔スコア要因別寄与度',
        'factor_explain': '後悔スコア要因説明',

        # AI分析
        'ai_caption': '消費心理分析とカスタムインサイトを一度に生成します',
        'btn_ai': 'AI分析開始',
        'ai_analyzing': '消費パターンを分析しています...',
        'ai_complete': '分析完了！',
        'ai_prev_result': '以前に生成された分析結果です。新しく生成するには上のボタンをクリックしてください。',
        'ai_guide': '上のボタンをクリックするとAIが消費パターンを分析し、カスタムインサイトを提供します。',
        'ai_preview': '分析項目プレビュー',
        'basic_tips': '基本改善ヒント',
        'savings_sim': '貯蓄シミュレーター',
        'reduction_rate': '削減率 (%)',
        'annual_saving': '年間予想貯蓄額',
        'api_usage': 'API使用量情報',

        # 総合まとめ
        'regret_purchase_ratio': '後悔購入割合',
        'regret_purchase_amount': '後悔購入金額',
        'good_purchase_ratio': '合理的購入割合',
        'top_regret_5': '後悔の可能性が高い購入 TOP 5',
        'top_good_5': '満足度が高い購入 TOP 5',

        # 完了
        'analysis_complete': '**分析完了！**\n- すべての分析結果を確認しましたか？\n- 定期的に購入データを更新すると、消費パターンの変化を追跡できます！',
        'no_data': '上からデータを入力すると分析が始まります。',

        # サイドバー
        'csv_format': 'CSVファイル形式',
        'sample_download': 'サンプルCSVダウンロード',
        'analysis_tips': '分析ヒント',
        'analysis_tips_text': '- 最低5件以上のデータを入力すると、より正確な分析が可能です\n- 必要度と使用頻度の差が大きいほど後悔スコアが高くなります',
        'analysis_history': '分析履歴',

        # ログイン
        'login_required': 'このサービスを利用するにはGoogleアカウントでのログインが必要です。',
        'login': 'ログイン',
        'logout': 'ログアウト',
        'my_account': 'マイアカウント',
        'premium': 'プレミアム会員',
        'free_plan': '無料プラン',
        'remaining': '回残り',
        'google_login': 'Googleでログイン',

        # カテゴリオプション
        'categories': ['電子製品', '衣類', '食費', '趣味', '美容/健康', '生活用品', '書籍', '教育', '交通', 'その他'],

        # 後悔等級
        'grade_labels': ['非常に満足\n(0-20)', '満足\n(21-35)', '普通\n(36-50)', '残念\n(51-65)', '後悔\n(66-100)'],

        # 後悔原因
        'cause_names': {
            '필요도갭': '必要度-使用頻度ギャップ',
            '시간경과': '時間経過',
            '금액': '高額商品',
            '최근성': '最近の購入',
            '반복구매': '繰り返し購入',
            '새벽구매': '深夜購入',
            '충동패턴': '衝動買いパターン'
        },

        # 言語
        'language': '言語',

        # Buy Me a Coffee
        'support_title': 'このサービスはお役に立ちましたか？',
        'support_desc': 'コーヒー1杯で応援してください！',
        'support_guide': '支援リンク有効化: <a href="https://www.buymeacoffee.com" target="_blank">アカウント作成</a> 後 app.pyで\'yourname\'を変更',

        # 分析履歴
        'no_analysis_history': '分析履歴がありません。',
        'saved_purchases': '保存された購入',
        'count_unit': '件',
        'regret_label': '後悔',
        'score_unit': '点',

        # ログイン画面
        'free_plan_desc': '**無料プラン**:\n- 分析5回無料提供\n- すべての機能利用可能',
        'premium_plan_desc': '**プレミアムプラン** (月額500円):\n- 無制限分析\n- AI心理分析優先サポート\n- 広告非表示',
        'terms_agree': 'ログイン時に[利用規約]および[プライバシーポリシー]に同意したものとみなされます。',

        # 使用制限画面
        'usage_warning': '無料使用回数が残り{}回です。',
        'usage_exhausted': '無料使用回数をすべて消費しました。',
        'upgrade_title': 'プレミアムプランにアップグレード',
        'free_plan_features': '**無料プラン**\n- 分析5回提供\n- 基本機能利用\n- 広告表示',
        'premium_plan_features': '**プレミアムプラン** (月額500円)\n- 無制限分析\n- AI心理分析優先サポート\n- 広告非表示\n- データ無制限保存',
        'btn_subscribe': 'プレミアム登録する',
        'payment_coming': '決済システムは近日オープン予定です！',
        'payment_demo': '現在はデモ版です。実際の決済はベータ版リリース後に利用可能です。',

        # 後悔スコア計算
        'calculating_regret': '後悔スコアを計算中...',
        'regret_calc_complete': '後悔スコア計算完了！',
        'file_error': 'ファイル処理中にエラーが発生しました',

        # 手動入力エラー
        'input_error_product': '商品名を入力してください。',
        'input_error_category': 'カテゴリを選択または入力してください。',
        'input_error_amount': '金額は0より大きくなければなりません。',
        'save_complete': '保存完了！',
        'processing_data': 'データ処理および後悔スコア計算中...',
        'validation_failed': 'データ検証失敗',
        'analysis_done': '分析完了！',
        'all_deleted': 'すべてのアイテムが削除されました。',

        # カテゴリテーブル
        'col_category': 'カテゴリ',
        'col_total_amount': '総金額',
        'col_avg_amount': '平均金額',
        'col_count': '購入件数',
        'col_avg_necessity': '平均必要度',
        'col_avg_usage': '平均使用頻度',

        # 後悔スコア分析
        'regret_not_calculated': '後悔スコアが計算されていません。',
        'col_grade': '等級',
        'col_count_short': '件数',
        'hover_count': '件数',
        'axis_purchase_count': '購入件数',

        # 要因分析
        'factor_necessity_gap': '必要度-使用頻度ギャップ',
        'factor_time_decay': '時間経過',
        'factor_amount': '金額加重',
        'factor_recency': '最近性',
        'factor_repeat': '繰り返し購入',
        'factor_night': '深夜購入',
        'factor_impulse': '衝動パターン',
        'col_factor': '要因',
        'col_avg_score': '平均スコア',
        'hover_avg': '平均',

        # 要因説明
        'factor_explain_text': """### 各要因が後悔スコアに与える影響

1. **必要度-使用頻度ギャップ** (最大30点)
   - 購入時に必要だと思った度合いと実際の使用頻度の差
   - ギャップが大きいほど後悔スコアが増加

2. **時間経過** (最大15点)
   - 以前に購入したのに使用頻度が低いとスコア増加
   - 時間が経つほど加重値が増加

3. **金額加重** (最大20点)
   - 高額商品ほど後悔時の心理的負担が大きいため加重値増加
   - 平均購入金額に対する比率で計算

4. **最近性** (最大10点)
   - 最近の購入は衝動買いの可能性が高い
   - 3日以内の購入で高スコア

5. **繰り返し購入** (最大15点)
   - 同じカテゴリを短期間で繰り返し購入すると衝動買いの疑い
   - 30日以内の同一カテゴリ購入件数で計算

6. **深夜購入** (最大10点)
   - 深夜(00:00-05:00)の購入は衝動買いの可能性が高い
   - CSVに時間情報がない場合は0点

7. **衝動パターン** (最大10点)
   - 1日に複数件の購入または連続した日付での購入で衝動パターン検出
   - 同日3件以上または3日以内5件以上で高スコア""",

        # AI分析エラー/案内
        'openai_not_installed': 'OpenAIライブラリがインストールされていません。',
        'openai_setup_guide': """**OpenAI APIキー設定方法**:
1. `.env`ファイルをプロジェクトルートに作成
2. 次の内容を追加: `OPENAI_API_KEY=sk-your-api-key-here`
3. OpenAIプラットフォーム(https://platform.openai.com/api-keys)でAPIキーを発行
4. アプリを再起動

APIキーがなくても基本分析は引き続きご利用いただけます！""",
        'openai_init_error': 'OpenAIサービスを初期化できません。',
        'default_tips': [
            '購入前に24時間の検討時間を設けましょう。',
            '購入リストを事前に作成する習慣をつけましょう。',
            'カートに入れて3日後にもう一度確認しましょう。'
        ],
        'api_retry': 'APIキーを確認するか、しばらくしてから再度お試しください。',

        # トークン情報
        'token_input': '入力トークン',
        'token_output': '出力トークン',
        'token_total': '総トークン',
        'cost_estimate': '推定コスト',

        # AIプレビュー
        'preview_psychology': '**消費心理分析**\n- 消費パターンの要約と主な後悔原因の分析\n- 実践可能な改善方法と月間チャレンジ',
        'preview_insights': '**スマートインサイト**\n- 各購入の消費パターン分類（ストレス性、衝動的、計画的など）\n- 類似ユーザーの再購入率推定\n- カテゴリ別長期貯蓄効果シミュレーション\n- おすすめ購入リスト TOP 5（購入リンク付き）',

        # 貯蓄シミュレーター
        'col_monthly_avg': '月平均支出',
        'col_annual_saving': '% 削減時の年間貯蓄',

        # 広告
        'ad_sponsored': 'Sponsored',
        'ad_area': '広告エリア',
        'ad_placeholder': 'AdSense承認後に広告が表示されます',

        # 家計簿
        'expense_tracker': '家計簿',
        'quick_add': '支出記録',
        'my_purchases': '購入履歴',
        'delete_selected': '選択削除',
        'period_filter': '期間',
        'period_1m': '最近1ヶ月',
        'period_3m': '最近3ヶ月',
        'period_6m': '最近6ヶ月',
        'period_all': 'すべて',
        'no_purchases_yet': 'まだ記録された購入がありません。上から支出を記録してみましょう！',
        'analyze_accumulated': '蓄積データ分析',
        'purchase_saved': '記録されました！',
        'purchases_deleted': '件が削除されました。',
        'total_records': '総記録',
        'select_to_delete': '削除するアイテムを選択してください',
    }
}


def t(key: str, lang: str = 'ko') -> str:
    """
    번역 텍스트 반환

    Args:
        key: 번역 키
        lang: 언어 코드 ('ko' 또는 'ja')

    Returns:
        번역된 텍스트. 키가 없으면 한국어 기본값 반환.
    """
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['ko'])
    result = translations.get(key)
    if result is None:
        # 한국어 폴백
        result = TRANSLATIONS['ko'].get(key, key)
    return result
