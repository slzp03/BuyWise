"""
AI 구매 후회 방지 분석기 - Streamlit 웹앱
해커톤 제출용 MVP

1단계: CSV 업로드 및 기본 분석
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sys
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.csv_processor import (
    validate_csv,
    process_csv_data,
    get_category_summary,
    get_basic_stats,
    calculate_necessity_from_input,
    create_dataframe_from_manual_input
)
from utils.translations import t, TRANSLATIONS
from utils.visualizer import (
    create_category_chart,
    create_amount_chart,
    create_timeline_chart,
    create_necessity_usage_scatter
)
from utils.regret_calculator import (
    add_regret_scores_to_dataframe,
    get_regret_score_interpretation,
    get_overall_regret_analysis
)

# Google OAuth
from utils.auth import (
    get_login_url,
    handle_oauth_callback,
    check_usage_limit,
    increment_usage_count,
    logout,
    save_session,
    load_session
)

# Supabase DB (선택적)
try:
    from utils.database import (
        is_db_available, get_or_create_user, get_user_by_email,
        is_admin,
        save_purchases, save_single_purchase, load_purchases,
        delete_purchases, get_purchase_count,
        save_analysis, load_analyses, load_latest_analysis,
        log_ai_usage
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# OpenAI는 선택적 기능으로 처리
try:
    from utils.openai_service import (
        get_openai_service,
        check_api_key_available
    )
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# 페이지 설정
st.set_page_config(
    page_title="BuyWise! 구매를 현명하게!",
    page_icon="buywise_icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """커스텀 CSS 로드"""
    css_file = Path(__file__).parent / "styles" / "custom.css"
    if css_file.exists():
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_lang():
    """현재 언어 코드 반환"""
    return st.session_state.get('language', 'ko')


def init_session_state():
    """세션 상태 초기화"""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = None
    if 'language' not in st.session_state:
        st.session_state.language = 'ko'


def display_header():
    """헤더 표시"""
    lang = get_lang()
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('page_title', lang)}</h1>
        <p class="subtitle">{t('page_subtitle', lang)}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")


def display_sidebar():
    """사이드바 표시"""
    lang = get_lang()
    with st.sidebar:
        st.header(t('csv_format', lang))
        if lang == 'ja':
            st.markdown("""
        **必須カラム**:
        - `日付`: YYYY-MM-DD
        - `カテゴリ`: 購入カテゴリ
        - `金額`: 購入金額（数字）
        - `検討期間`: 購入前に悩んだ日数（0 = 衝動買い）
        - `再購入意向`: はい/いいえ
        - `使用頻度`: 1-5（実際の使用頻度）

        **任意カラム**:
        - `商品名`: 商品名

        > 必要度は検討期間+再購入意向から自動計算されます。
            """)
        else:
            st.markdown("""
        **필수 컬럼**:
        - `날짜`: YYYY-MM-DD
        - `카테고리`: 구매 카테고리
        - `금액`: 구매 금액 (숫자)
        - `고민기간`: 구매 전 고민한 일수 (0 = 충동구매)
        - `재구매의향`: 예/아니오
        - `사용빈도`: 1-5 (실제 사용 빈도)

        **선택 컬럼**:
        - `상품명`: 상품 이름

        > 필요도는 고민기간+재구매의향으로 자동 계산됩니다.
            """)

        st.divider()

        st.header(t('sample_download', lang))

        # 샘플 CSV 파일 읽기
        sample_file = Path(__file__).parent / "sample_purchases.csv"
        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_data = f.read()
        else:
            sample_data = "날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도\n"

        # 일본어 모드: 전체 일본어로 변환
        if lang == 'ja':
            from utils.translations import JA_TO_KO_COLUMNS
            ko_to_ja = {v: k for k, v in JA_TO_KO_COLUMNS.items()}
            # 카테고리 매핑
            cat_ko_to_ja = dict(zip(
                TRANSLATIONS['ko']['categories'],
                TRANSLATIONS['ja']['categories']
            ))
            # 상품명 매핑
            product_ko_to_ja = {
                '무선이어폰': 'ワイヤレスイヤホン', '겨울코트': '冬コート',
                '배달음식': 'デリバリー', '보드게임': 'ボードゲーム',
                '스마트워치': 'スマートウォッチ', '운동화': 'スニーカー',
                '커피': 'コーヒー', '책': '本', '키보드': 'キーボード',
                '티셔츠': 'Tシャツ', '외식': '外食', '마우스': 'マウス',
                '청바지': 'ジーンズ', '영화관람': '映画鑑賞',
                '태블릿PC': 'タブレットPC', '명품가방': 'ブランドバッグ',
                '공연티켓': 'コンサートチケット', '카페': 'カフェ',
                '케이블': 'ケーブル', '양말': '靴下',
                '홈트레이닝기구': 'ホームトレーニング器具', '충전기': '充電器',
                '반팔티': '半袖Tシャツ', '게임': 'ゲーム',
                'VR헤드셋': 'VRヘッドセット', '세일코트': 'セールコート',
                '미술용품': '美術用品', '안마기': 'マッサージ器',
                '블루투스스피커': 'Bluetoothスピーカー',
                '브랜드운동복': 'ブランドスポーツウェア', '드론': 'ドローン',
                '액션캠': 'アクションカメラ', '한정판스니커즈': '限定版スニーカー',
                '스마트홈기기': 'スマートホーム機器',
                '디자이너자켓': 'デザイナージャケット',
            }
            lines = sample_data.strip().split('\n')
            # 헤더 변환
            header = lines[0]
            for ko, ja in ko_to_ja.items():
                header = header.replace(ko, ja)
            # 데이터 행 변환
            data_lines = []
            for line in lines[1:]:
                line = line.replace(',예,', ',はい,').replace(',아니오,', ',いいえ,')
                for ko_cat, ja_cat in cat_ko_to_ja.items():
                    line = line.replace(f',{ko_cat},', f',{ja_cat},')
                for ko_prod, ja_prod in product_ko_to_ja.items():
                    line = line.replace(f',{ko_prod},', f',{ja_prod},')
                data_lines.append(line)
            sample_data = header + '\n' + '\n'.join(data_lines) + '\n'

        st.download_button(
            label=t('sample_download', lang),
            data=sample_data,
            file_name="sample_purchases.csv",
            mime="text/csv"
        )

        st.divider()

        st.markdown(f"""
        ### {t('analysis_tips', lang)}
        {t('analysis_tips_text', lang)}
        """)

        st.divider()

        # Buy Me a Coffee 후원 버튼
        st.markdown(f"""
        <div class="support-section">
            <h3>{t('support_title', lang)}</h3>
            <p>{t('support_desc', lang)}</p>
            <a href="https://buymeacoffee.com/m.kim" target="_blank">
                <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee">
            </a>
        </div>
        """, unsafe_allow_html=True)


def display_analysis_history():
    """사이드바에 분석 이력 표시 (DB 연동 시)"""
    lang = get_lang()
    user_id = st.session_state.get('db_user_id')
    if not user_id or not DB_AVAILABLE or not is_db_available():
        return

    with st.sidebar:
        st.divider()
        st.markdown(f"### {t('analysis_history', lang)}")

        analyses = load_analyses(user_id, limit=5)
        if not analyses:
            st.caption(t('no_analysis_history', lang))
            return

        # 저장된 구매 이력 수
        purchase_count = get_purchase_count(user_id)
        st.caption(f"{t('saved_purchases', lang)}: {purchase_count}{t('count_unit', lang)}")

        for a in analyses:
            created = a.get('created_at', '')[:10]
            avg_score = a.get('average_regret_score', 0)
            count = a.get('purchase_count', 0)
            label = f"{created} | {count}{t('count_unit', lang)} | {t('regret_label', lang)} {avg_score:.0f}{t('score_unit', lang)}"

            with st.expander(label, expanded=False):
                if a.get('psychology_analysis'):
                    st.markdown(a['psychology_analysis'][:300] + "..." if len(a.get('psychology_analysis', '')) > 300 else a.get('psychology_analysis', ''))
                if a.get('smart_insights'):
                    st.markdown("---")
                    st.markdown(a['smart_insights'][:300] + "..." if len(a.get('smart_insights', '')) > 300 else a.get('smart_insights', ''))


def display_login_screen():
    """로그인 화면 표시"""
    # 로그인 화면에서는 툴바 숨기기
    st.markdown("""
    <style>
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="manage-app-button"] {display: none !important;}
        .stDeployButton {display: none !important;}
        .stAppDeployButton {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

    # 로그인 전에도 언어 선택 가능
    with st.sidebar:
        lang_options = {'한국어': 'ko', '日本語': 'ja'}
        lang_labels = list(lang_options.keys())
        current_lang = get_lang()
        current_index = lang_labels.index('日本語') if current_lang == 'ja' else 0
        selected_lang_label = st.selectbox(
            t('language', current_lang),
            lang_labels,
            index=current_index,
            key='login_lang'
        )
        new_lang = lang_options[selected_lang_label]
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()

    lang = get_lang()
    st.markdown(f"""
    <div class="main-header">
        <h1>{t('page_title', lang)}</h1>
        <p class="subtitle">{t('page_subtitle', lang)}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.info(t('login_required', lang))

    # 2열 레이아웃
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"### {t('login', lang)}")

        st.markdown(t('free_plan_desc', lang))
        st.markdown(t('premium_plan_desc', lang))

        # Google 로그인 버튼 (새 탭에서 열림)
        login_url = get_login_url()
        st.link_button(f"🔐 {t('google_login', lang)}", login_url, use_container_width=True, type="primary")

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(t('terms_agree', lang))


def display_usage_limit_screen(remaining):
    """사용 횟수 제한 화면"""
    lang = get_lang()
    st.warning(f"⚠️ {t('usage_warning', lang).format(remaining)}")

    if remaining == 0:
        st.error(f"❌ {t('usage_exhausted', lang)}")

        st.markdown(f"### {t('upgrade_title', lang)}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(t('free_plan_features', lang))

        with col2:
            st.markdown(t('premium_plan_features', lang))

        if st.button(t('btn_subscribe', lang), type="primary", use_container_width=True):
            st.info(f"💳 {t('payment_coming', lang)}")
            st.caption(t('payment_demo', lang))

        return False

    return True


def upload_csv():
    """CSV 파일 업로드 처리"""
    lang = get_lang()
    uploaded_file = st.file_uploader(
        t('csv_upload', lang),
        type=['csv'],
        help=t('csv_help', lang)
    )

    if uploaded_file is not None:
        try:
            # 새 파일 감지 (파일명 비교)
            if st.session_state.get('last_uploaded_file') != uploaded_file.name:
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.new_analysis = True

            # CSV 읽기 (인코딩 자동 감지)
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding='cp949')

            st.success(f"{t('csv_upload_success', lang)} ({len(df)}건)")

            # 데이터 검증
            is_valid, error_message = validate_csv(df)

            if not is_valid:
                st.error(f"❌ {t('csv_invalid', lang)}: {error_message}")
                return None

            st.success(t('csv_valid', lang))

            # 데이터 전처리
            processed_df = process_csv_data(df)

            # 후회 점수 계산
            with st.spinner(f'🧮 {t("calculating_regret", lang)}'):
                processed_df = add_regret_scores_to_dataframe(processed_df)

            st.success(t('regret_calc_complete', lang))

            return processed_df

        except Exception as e:
            st.error(f"❌ {t('file_error', lang)}: {str(e)}")
            return None

    return None


def expense_tracker():
    """가계부 - 지출 기록 + 누적 데이터 조회/삭제 + 분석"""
    lang = get_lang()
    user_id = st.session_state.get('db_user_id')
    has_db = user_id and DB_AVAILABLE and is_db_available()

    # ===== 1. 빠른 기록 폼 =====
    st.markdown(f"### {t('quick_add', lang)}")

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input(
            t('product_name', lang),
            placeholder=t('product_placeholder', lang),
            help=t('product_help', lang)
        )

        amount = st.number_input(
            t('amount', lang),
            min_value=0,
            step=1000,
            value=0,
            help=t('amount_help', lang)
        )

        thinking_days = st.number_input(
            t('thinking_days', lang),
            min_value=0,
            max_value=999,
            value=0,
            help=t('thinking_help', lang)
        )

    with col2:
        categories = t('categories', lang)
        category_options = categories + [t('category_custom', lang)]
        category_select = st.selectbox(
            t('category', lang),
            options=category_options,
            help=t('category_help', lang)
        )

        if category_select == t('category_custom', lang):
            category = st.text_input(
                t('category_custom_label', lang),
                placeholder=t('category_custom_placeholder', lang)
            )
        else:
            category = category_select

        purchase_date = st.date_input(
            t('purchase_date', lang),
            value=pd.Timestamp.now().date(),
            max_value=pd.Timestamp.now().date(),
            help=t('purchase_date_help', lang)
        )

        repurchase_will = st.radio(
            t('repurchase', lang),
            options=[t('repurchase_yes', lang), t('repurchase_no', lang)],
            horizontal=True,
            help=t('repurchase_help', lang)
        )

    usage_freq = st.slider(
        t('usage_freq', lang),
        min_value=1,
        max_value=5,
        value=3,
        help=t('usage_help', lang)
    )

    repurchase_bool = (repurchase_will == t('repurchase_yes', lang))
    necessity = calculate_necessity_from_input(thinking_days, repurchase_bool)
    necessity_labels = t('necessity_labels', lang)

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
                padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
        <p style='margin: 0; color: #4338ca; font-weight: 600;'>
            {t('necessity_auto', lang)}: {necessity} ({necessity_labels[necessity-1]})
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 저장 버튼
    save_btn = st.button(t('btn_save', lang), type="primary", use_container_width=True)

    if save_btn:
        if not product_name.strip():
            st.error(f"❌ {t('input_error_product', lang)}")
        elif not category.strip():
            st.error(f"❌ {t('input_error_category', lang)}")
        elif amount <= 0:
            st.error(f"❌ {t('input_error_amount', lang)}")
        else:
            item = {
                '날짜': str(purchase_date),
                '카테고리': category,
                '상품명': product_name,
                '금액': amount,
                '필요도': necessity,
                '사용빈도': usage_freq,
                '고민기간': thinking_days,
                '재구매의향': '예' if repurchase_bool else '아니오'
            }

            if has_db:
                save_single_purchase(user_id, item)
            else:
                # DB 없을 때 세션 fallback
                if 'manual_items' not in st.session_state:
                    st.session_state.manual_items = []
                item['날짜'] = pd.to_datetime(purchase_date)
                st.session_state.manual_items.append(item)

            st.success(f"✅ '{product_name}' {t('purchase_saved', lang)}")
            st.balloons()
            st.rerun()

    st.divider()

    # ===== 2. 누적 데이터 목록 =====
    st.markdown(f"### {t('my_purchases', lang)}")

    # 기간 필터
    from datetime import timedelta
    period_options = {
        t('period_1m', lang): 30,
        t('period_3m', lang): 90,
        t('period_6m', lang): 180,
        t('period_all', lang): 0
    }
    selected_period = st.radio(
        t('period_filter', lang),
        options=list(period_options.keys()),
        horizontal=True,
        index=3  # 기본: 전체
    )
    days = period_options[selected_period]

    # DB에서 데이터 로드
    purchases_df = None
    if has_db:
        date_from = None
        if days > 0:
            date_from = (pd.Timestamp.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        purchases_df = load_purchases(user_id, date_from=date_from, include_id=True)
    else:
        # DB 없을 때 세션 fallback
        if st.session_state.get('manual_items'):
            purchases_df = pd.DataFrame(st.session_state.manual_items)
            if '날짜' in purchases_df.columns:
                purchases_df['날짜'] = pd.to_datetime(purchases_df['날짜'])

    if purchases_df is not None and len(purchases_df) > 0:
        st.caption(f"{t('total_records', lang)}: {len(purchases_df)}{t('count_unit', lang)}")

        # 표시용 DataFrame
        display_cols = ['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도']
        display_df = purchases_df[[c for c in display_cols if c in purchases_df.columns]].copy()
        display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
        display_df['금액'] = display_df['금액'].apply(lambda x: f"₩{x:,.0f}")

        # 삭제용 체크박스 (DB 모드에서만)
        if has_db and '_id' in purchases_df.columns:
            display_df.insert(0, '✓', False)
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                hide_index=True,
                disabled=[c for c in display_df.columns if c != '✓'],
                column_config={'✓': st.column_config.CheckboxColumn(t('select_to_delete', lang))}
            )

            # 삭제 버튼
            selected_rows = edited_df[edited_df['✓'] == True]
            if len(selected_rows) > 0:
                if st.button(f"🗑️ {t('delete_selected', lang)} ({len(selected_rows)}{t('count_unit', lang)})", type="secondary"):
                    ids_to_delete = purchases_df.iloc[selected_rows.index]['_id'].tolist()
                    delete_purchases(user_id, ids_to_delete)
                    st.success(f"🗑️ {len(ids_to_delete)}{t('purchases_deleted', lang)}")
                    st.rerun()
        else:
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.divider()

        # ===== 3. 분석 버튼 =====
        if st.button(f"🚀 {t('analyze_accumulated', lang)}", type="primary", use_container_width=True):
            with st.spinner(f'🧮 {t("processing_data", lang)}'):
                # 분석용 데이터 준비 (_id 제외)
                analysis_df = purchases_df.drop(columns=['_id'], errors='ignore').copy()

                # 기존 파이프라인 실행
                is_valid, error_message = validate_csv(analysis_df)
                if not is_valid:
                    st.error(f"❌ {t('validation_failed', lang)}: {error_message}")
                    return None

                processed_df = process_csv_data(analysis_df)
                processed_df = add_regret_scores_to_dataframe(processed_df)

                st.success(f"✅ {t('analysis_done', lang)}")
                st.session_state.new_analysis = True
                return processed_df

    else:
        st.info(t('no_purchases_yet', lang))

    return None


def display_raw_data(df: pd.DataFrame):
    """원본 데이터 테이블 표시"""
    lang = get_lang()
    st.header(t('data_preview', lang))

    # 표시할 컬럼 선택 (고민기간/재구매의향이 있으면 포함)
    base_columns = ['날짜', '카테고리', '상품명', '금액']
    if '고민기간' in df.columns and '재구매의향' in df.columns:
        base_columns += ['고민기간', '재구매의향', '필요도', '사용빈도']
    else:
        base_columns += ['필요도', '사용빈도']
    display_columns = [c for c in base_columns if c in df.columns]
    display_df = df[display_columns].copy()

    # 날짜 포맷팅
    display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')

    # 금액 포맷팅 (천 단위 쉼표)
    display_df['금액'] = display_df['금액'].apply(lambda x: f"₩{x:,.0f}")

    # 데이터 테이블 표시
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )

    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(t('total_purchases', lang), f"{len(df):,}")

    with col2:
        total_amount = df['금액'].sum()
        st.metric(t('total_amount', lang), f"₩{total_amount:,.0f}")

    with col3:
        avg_amount = df['금액'].mean()
        st.metric(t('avg_amount', lang), f"₩{avg_amount:,.0f}")

    with col4:
        categories = df['카테고리'].nunique()
        st.metric(t('num_categories', lang), f"{categories}")


def display_category_analysis(df: pd.DataFrame):
    """카테고리별 분석 표시"""
    lang = get_lang()
    st.header(t('category_analysis', lang))

    # 카테고리 집계
    category_summary = get_category_summary(df)

    # 차트 타입 선택
    col1, col2 = st.columns([3, 1])

    with col2:
        chart_type = st.radio(
            t('chart_type', lang),
            [t('pie_chart', lang), t('bar_chart', lang)],
            horizontal=True
        )

    # 차트 표시
    chart_type_map = {t('pie_chart', lang): "pie", t('bar_chart', lang): "bar"}
    fig = create_category_chart(category_summary, chart_type_map[chart_type])

    st.plotly_chart(fig, use_container_width=True)

    # 카테고리 집계 테이블
    st.subheader(t('category_detail', lang))

    # 테이블 포맷팅
    display_summary = category_summary.copy()
    display_summary['총_금액'] = display_summary['총_금액'].apply(lambda x: f"₩{x:,.0f}")
    display_summary['평균_금액'] = display_summary['평균_금액'].apply(lambda x: f"₩{x:,.0f}")
    display_summary.columns = [t('col_category', lang), t('col_total_amount', lang), t('col_avg_amount', lang), t('col_count', lang), t('col_avg_necessity', lang), t('col_avg_usage', lang)]

    st.dataframe(
        display_summary,
        use_container_width=True,
        hide_index=True
    )


def display_additional_charts(df: pd.DataFrame):
    """추가 차트 표시"""
    lang = get_lang()
    st.header(t('deep_analysis', lang))

    # 2개 컬럼 레이아웃
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t('amount_dist', lang))
        fig_amount = create_amount_chart(df)
        st.plotly_chart(fig_amount, use_container_width=True)

    with col2:
        st.subheader(t('monthly_trend', lang))
        fig_timeline = create_timeline_chart(df)
        st.plotly_chart(fig_timeline, use_container_width=True)

    # 필요도 vs 사용빈도 산점도
    st.subheader(t('necessity_usage', lang))
    st.markdown(t('scatter_guide', lang))
    fig_scatter = create_necessity_usage_scatter(df)
    st.plotly_chart(fig_scatter, use_container_width=True)


def display_regret_score_analysis(df: pd.DataFrame):
    """후회 점수 분석 표시"""
    lang = get_lang()
    st.header(t('regret_score', lang))

    # 전체 분석
    if '후회점수' not in df.columns:
        st.warning(f"⚠️ {t('regret_not_calculated', lang)}")
        return

    analysis = get_overall_regret_analysis(df)

    # 전체 후회 점수
    st.subheader(f"{analysis['interpretation']['emoji']} {t('overall_regret', lang)}: {analysis['avg_regret_score']}/100")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**{analysis['interpretation']['grade']}**")
        st.info(analysis['interpretation']['message'])

    with col2:
        # 진행률 바
        import plotly.graph_objects as go

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=analysis['avg_regret_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': analysis['interpretation']['color']},
                'steps': [
                    {'range': [0, 20], 'color': "lightgreen"},
                    {'range': [20, 35], 'color': "lightyellow"},
                    {'range': [35, 50], 'color': "yellow"},
                    {'range': [50, 65], 'color': "orange"},
                    {'range': [65, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))

        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 통계 메트릭
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            t('regret_ratio', lang),
            f"{analysis['regret_ratio']:.1f}%",
            delta=f"{analysis['regret_count']}",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            t('regret_amount', lang),
            f"₩{analysis['regret_amount']:,}",
            delta=f"{analysis['regret_amount_ratio']:.1f}%",
            delta_color="inverse"
        )

    with col3:
        cause_names_map = t('cause_names', lang)
        cause_display = cause_names_map.get(analysis['main_cause']['name'], analysis['main_cause']['name'])

        st.metric(
            t('main_cause', lang),
            cause_display,
            delta=f"{analysis['main_cause']['score']:.1f}"
        )

    with col4:
        very_satisfied = analysis['distribution']['very_satisfied']
        st.metric(
            t('satisfied_count', lang),
            f"{very_satisfied}",
            delta=f"{(very_satisfied/analysis['total_purchases']*100):.1f}%",
            delta_color="normal"
        )

    st.divider()

    # 등급별 분포
    st.subheader(t('grade_dist', lang))

    dist = analysis['distribution']
    grade_labels = t('grade_labels', lang)
    col_grade = t('col_grade', lang)
    col_count = t('col_count_short', lang)
    dist_df = pd.DataFrame({
        col_grade: grade_labels,
        col_count: [dist['very_satisfied'], dist['satisfied'], dist['neutral'], dist['regretful'], dist['very_regretful']],
        '색상': ['#90EE90', '#FFFFE0', '#FFD700', '#FFA500', '#FF6B6B']
    })

    import plotly.express as px

    fig = px.bar(
        dist_df,
        x=col_grade,
        y=col_count,
        color='색상',
        color_discrete_map={color: color for color in dist_df['색상']},
        text=col_count
    )

    fig.update_traces(
        textposition='outside',
        hovertemplate='%{x}<br>' + t('hover_count', lang) + ': %{y}' + t('count_unit', lang) + '<extra></extra>'
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title='',
        yaxis_title=t('axis_purchase_count', lang),
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 후회 점수 TOP 10
    st.subheader(t('top_regret', lang))

    top_regret_df = df.nlargest(10, '후회점수')[
        ['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도', '후회점수']
    ].copy()

    top_regret_df['날짜'] = top_regret_df['날짜'].dt.strftime('%Y-%m-%d')
    top_regret_df['금액'] = top_regret_df['금액'].apply(lambda x: f"₩{x:,.0f}")
    top_regret_df['후회점수'] = top_regret_df['후회점수'].apply(lambda x: f"{x:.1f}")

    # 후회 점수에 따라 배경색 적용
    def highlight_regret_score(row):
        score = float(row['후회점수'])
        if score > 65:
            return ['background-color: #ffcccc'] * len(row)
        elif score > 50:
            return ['background-color: #ffe6cc'] * len(row)
        else:
            return [''] * len(row)

    st.dataframe(
        top_regret_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # 만족 점수 TOP 10
    st.subheader(t('top_satisfied', lang))

    top_satisfied_df = df.nsmallest(10, '후회점수')[
        ['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도', '후회점수']
    ].copy()

    top_satisfied_df['날짜'] = top_satisfied_df['날짜'].dt.strftime('%Y-%m-%d')
    top_satisfied_df['금액'] = top_satisfied_df['금액'].apply(lambda x: f"₩{x:,.0f}")
    top_satisfied_df['후회점수'] = top_satisfied_df['후회점수'].apply(lambda x: f"{x:.1f}")

    st.dataframe(
        top_satisfied_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # 후회 점수 요인 분석
    st.subheader(t('factor_analysis', lang))

    factor_scores = {
        t('factor_necessity_gap', lang): df['후회점수_필요도갭'].mean(),
        t('factor_time_decay', lang): df['후회점수_시간경과'].mean(),
        t('factor_amount', lang): df['후회점수_금액'].mean(),
        t('factor_recency', lang): df['후회점수_최근성'].mean(),
        t('factor_repeat', lang): df['후회점수_반복구매'].mean(),
        t('factor_night', lang): df['후회점수_새벽구매'].mean(),
        t('factor_impulse', lang): df['후회점수_충동패턴'].mean()
    }

    col_factor = t('col_factor', lang)
    col_avg_score = t('col_avg_score', lang)
    factor_df = pd.DataFrame({
        col_factor: list(factor_scores.keys()),
        col_avg_score: list(factor_scores.values())
    }).sort_values(col_avg_score, ascending=False)

    fig = px.bar(
        factor_df,
        x=col_avg_score,
        y=col_factor,
        orientation='h',
        text=col_avg_score,
        color=col_avg_score,
        color_continuous_scale='Reds'
    )

    fig.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        hovertemplate='%{y}<br>' + t('hover_avg', lang) + ': %{x:.1f}' + t('score_unit', lang) + '<extra></extra>'
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title=col_avg_score,
        yaxis_title='',
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # 각 요인 설명
    with st.expander(t('factor_explain', lang)):
        st.markdown(t('factor_explain_text', lang))


def display_ai_analysis(df: pd.DataFrame):
    """AI 기반 통합 분석 (심리 분석 + 스마트 인사이트)"""
    lang = get_lang()
    st.header(t('ai_analysis', lang))
    st.caption(t('ai_caption', lang))

    # OpenAI 모듈 및 API 키 확인
    if not OPENAI_AVAILABLE:
        api_available = False
        api_message = t('openai_not_installed', lang)
    else:
        api_available, api_message = check_api_key_available()

    if not api_available:
        st.warning(f"{api_message}")
        st.info(t('openai_setup_guide', lang))

        # API 키 없이도 기본 팁 제공
        if '후회점수' in df.columns:
            analysis = get_overall_regret_analysis(df)
            avg_score = analysis['avg_regret_score']

            st.subheader(t('basic_tips', lang))

            if OPENAI_AVAILABLE:
                openai_service = get_openai_service()
                if openai_service:
                    tips = openai_service.generate_quick_tips(avg_score)
                else:
                    tips = None
            else:
                tips = None

            if not tips:
                tips = t('default_tips', lang)

            for tip in tips:
                st.markdown(f"- {tip}")

        return

    # 후회 점수 확인
    if '후회점수' not in df.columns:
        st.warning(t('regret_not_calculated', lang))
        return

    # 전체 분석 데이터 준비
    analysis = get_overall_regret_analysis(df)
    insights_data = prepare_smart_insights_data(df)

    # 카테고리별 통계
    category_stats = insights_data['category_breakdown']

    # 상위 후회 항목
    top_regret = df.nlargest(5, '후회점수')
    top_regret_items = []
    for _, row in top_regret.iterrows():
        top_regret_items.append({
            'category': row['카테고리'],
            'product': row['상품명'],
            'amount': int(row['금액']),
            'score': float(row['후회점수'])
        })

    # 통합 AI 분석 생성 버튼
    if st.button(t('btn_ai', lang), type="primary", use_container_width=True):
        with st.spinner(t('ai_analyzing', lang)):
            if not OPENAI_AVAILABLE:
                st.error(t('openai_not_installed', lang))
                return

            openai_service = get_openai_service()
            if not openai_service:
                st.error(t('openai_init_error', lang))
                return

            # 주요 원인 변환
            cause_names = t('cause_names', lang)
            main_cause = cause_names.get(
                analysis['main_cause']['name'],
                analysis['main_cause']['name']
            )

            total_tokens_used = 0

            # --- 1) 심리 분석 ---
            feedback_result = openai_service.generate_ai_feedback(
                overall_score=analysis['avg_regret_score'],
                total_purchases=analysis['total_purchases'],
                total_amount=df['금액'].sum(),
                regret_ratio=analysis['regret_ratio'],
                main_cause=main_cause,
                top_regret_items=top_regret_items,
                category_breakdown=category_stats,
                language=lang
            )

            # --- 2) 스마트 인사이트 ---
            insights_result = openai_service.generate_smart_insights(
                overall_score=analysis['avg_regret_score'],
                total_purchases=analysis['total_purchases'],
                total_amount=df['금액'].sum(),
                target_items=insights_data['target_items'],
                category_spending=insights_data['category_spending'],
                category_breakdown=category_stats,
                language=lang
            )

            # 결과 저장
            if feedback_result['success']:
                st.session_state.ai_feedback = feedback_result['feedback']
                st.session_state.ai_usage = feedback_result.get('usage', {})

            if insights_result['success']:
                st.session_state.smart_insights = insights_result['insights']
                st.session_state.smart_insights_usage = insights_result.get('usage', {})

            if feedback_result['success'] or insights_result['success']:
                st.success(t('ai_complete', lang))

                # DB에 분석 결과 저장
                user_id = st.session_state.get('db_user_id')
                if user_id and DB_AVAILABLE and is_db_available():
                    high_regret = int((df['후회점수'] >= 50).sum()) if '후회점수' in df.columns else 0
                    analysis_id = save_analysis(user_id, {
                        'purchase_count': len(df),
                        'total_spent': int(df['금액'].sum()),
                        'average_regret_score': round(analysis['avg_regret_score'], 2),
                        'high_regret_count': high_regret,
                        'psychology_analysis': feedback_result.get('feedback', ''),
                        'smart_insights': insights_result.get('insights', '')
                    })

                    # AI 사용량 로깅
                    if feedback_result.get('usage'):
                        log_ai_usage(user_id, analysis_id, 'psychology', feedback_result['usage'])
                    if insights_result.get('usage'):
                        log_ai_usage(user_id, analysis_id, 'smart_insights', insights_result['usage'])

                # 심리 분석 결과 표시
                if feedback_result['success']:
                    st.markdown("---")
                    st.markdown(feedback_result['feedback'])

                # 스마트 인사이트 결과 표시
                if insights_result['success']:
                    st.markdown("---")
                    st.markdown(insights_result['insights'])
                    st.markdown("---")

                    # 저축 시뮬레이터
                    display_savings_calculator(df)

                # 합산 API 사용량 표시
                with st.expander(t('api_usage', lang)):
                    usage1 = feedback_result.get('usage', {})
                    usage2 = insights_result.get('usage', {})
                    total_prompt = usage1.get('prompt_tokens', 0) + usage2.get('prompt_tokens', 0)
                    total_completion = usage1.get('completion_tokens', 0) + usage2.get('completion_tokens', 0)
                    total_all = total_prompt + total_completion

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(t('token_input', lang), f"{total_prompt:,}")
                    with col2:
                        st.metric(t('token_output', lang), f"{total_completion:,}")
                    with col3:
                        st.metric(t('token_total', lang), f"{total_all:,}")

                    prompt_cost = total_prompt * 0.15 / 1_000_000
                    completion_cost = total_completion * 0.60 / 1_000_000
                    total_cost = prompt_cost + completion_cost
                    st.info(f"{t('cost_estimate', lang)}: ${total_cost:.6f} (≈ ₩{total_cost * 1300:.2f})")
            else:
                error_msg = feedback_result.get('error', '') or insights_result.get('error', '')
                st.error(f"{error_msg}")
                st.info(t('api_retry', lang))

    # 이전에 생성된 결과가 있으면 표시
    elif 'ai_feedback' in st.session_state or 'smart_insights' in st.session_state:
        st.info(t('ai_prev_result', lang))

        if 'ai_feedback' in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state.ai_feedback)

        if 'smart_insights' in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state.smart_insights)
            st.markdown("---")
            display_savings_calculator(df)

    else:
        st.info(t('ai_guide', lang))

        with st.expander(t('ai_preview', lang)):
            st.markdown(t('preview_psychology', lang))
            st.markdown(t('preview_insights', lang))


def prepare_smart_insights_data(df):
    """스마트 인사이트용 데이터 준비"""
    # Top 5 후회 항목
    top_regret = df.nlargest(5, '후회점수')

    # Top 3 고가 항목
    top_expensive = df.nlargest(3, '금액')

    # 중복 제거 (최대 8건)
    combined_indices = list(set(top_regret.index.tolist() + top_expensive.index.tolist()))
    target_df = df.loc[combined_indices]

    target_items = []
    for _, row in target_df.iterrows():
        target_items.append({
            'category': row['카테고리'],
            'product': row['상품명'],
            'amount': int(row['금액']),
            'score': float(row['후회점수']),
            'necessity': int(row['필요도']),
            'usage': int(row['사용빈도'])
        })

    # 카테고리별 지출
    category_spending = df.groupby('카테고리')['금액'].sum().to_dict()

    # 카테고리별 통계
    category_stats = {}
    for category in df['카테고리'].unique():
        cat_df = df[df['카테고리'] == category]
        category_stats[category] = {
            'count': len(cat_df),
            'amount': int(cat_df['금액'].sum())
        }

    return {
        'target_items': target_items,
        'category_spending': category_spending,
        'category_breakdown': category_stats
    }


def display_savings_calculator(df):
    """카테고리별 저축 효과 시뮬레이터"""
    lang = get_lang()
    st.subheader(t('savings_sim', lang))

    # 데이터 기간 계산 (월 단위)
    date_range = (df['날짜'].max() - df['날짜'].min()).days
    months = max(date_range / 30, 1)

    category_monthly = df.groupby('카테고리')['금액'].sum() / months

    # 절감 비율 슬라이더
    reduction = st.slider(t('reduction_rate', lang), min_value=10, max_value=50, value=30, step=5)

    # 카테고리별 저축 효과 계산
    savings_data = []
    for cat, monthly_avg in category_monthly.items():
        annual_saving = monthly_avg * (reduction / 100) * 12
        savings_data.append({
            t('col_category', lang): cat,
            t('col_monthly_avg', lang): f"₩{monthly_avg:,.0f}",
            f'{reduction}{t("col_annual_saving", lang)}': f"₩{annual_saving:,.0f}"
        })

    st.dataframe(pd.DataFrame(savings_data), use_container_width=True, hide_index=True)

    total_annual_saving = sum(
        val * (reduction / 100) * 12
        for val in category_monthly
    )
    st.metric(t('annual_saving', lang), f"₩{total_annual_saving:,.0f}")



def display_adsense_ad():
    """Google AdSense 광고 표시"""
    lang = get_lang()
    ad_code = f"""
    <div style="text-align: center; padding: 20px 0;">
        <p style="color: gray; font-size: 12px; margin-bottom: 10px;">{t('ad_sponsored', lang)}</p>

        <!-- Google AdSense 광고 코드 -->
        <!--
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXX"
             crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-XXXXXXXX"
             data-ad-slot="XXXXXXXXXX"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
        -->

        <div style="background-color: #f0f0f0; padding: 60px 20px; border-radius: 5px; border: 1px dashed #ccc;">
            <p style="color: #666; margin: 0;">
                📢 {t('ad_area', lang)}<br>
                <small>{t('ad_placeholder', lang)}</small>
            </p>
        </div>
    </div>
    """

    components.html(ad_code, height=200)


def display_insights(df: pd.DataFrame):
    """기본 인사이트 표시"""
    lang = get_lang()
    st.header(t('summary', lang))

    stats = get_basic_stats(df)

    # 후회 구매 감지 (필요도 > 사용빈도 + 1)
    regret_purchases = df[df['필요도'] - df['사용빈도'] >= 2]
    regret_ratio = (len(regret_purchases) / len(df)) * 100 if len(df) > 0 else 0
    regret_amount = regret_purchases['금액'].sum() if len(regret_purchases) > 0 else 0

    # 좋은 구매 감지 (사용빈도 >= 필요도)
    good_purchases = df[df['사용빈도'] >= df['필요도']]
    good_ratio = (len(good_purchases) / len(df)) * 100 if len(df) > 0 else 0

    # 메트릭 표시
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            t('regret_purchase_ratio', lang),
            f"{regret_ratio:.1f}%",
            delta=f"{len(regret_purchases)}",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            t('regret_purchase_amount', lang),
            f"₩{regret_amount:,.0f}",
            delta=f"{(regret_amount/stats['총_지출금액']*100):.1f}%",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            t('good_purchase_ratio', lang),
            f"{good_ratio:.1f}%",
            delta=f"{len(good_purchases)}",
            delta_color="normal"
        )

    # 상위 후회 구매 표시
    if len(regret_purchases) > 0:
        st.subheader(t('top_regret_5', lang))

        regret_purchases_sorted = regret_purchases.copy()
        regret_purchases_sorted['후회도'] = (regret_purchases_sorted['필요도'] - regret_purchases_sorted['사용빈도']) * regret_purchases_sorted['금액'] / 1000
        regret_purchases_sorted = regret_purchases_sorted.nlargest(5, '후회도')

        display_regret = regret_purchases_sorted[['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도']].copy()
        display_regret['날짜'] = display_regret['날짜'].dt.strftime('%Y-%m-%d')
        display_regret['금액'] = display_regret['금액'].apply(lambda x: f"₩{x:,.0f}")

        st.dataframe(
            display_regret,
            use_container_width=True,
            hide_index=True
        )

    # 상위 좋은 구매 표시
    if len(good_purchases) > 0:
        st.subheader(t('top_good_5', lang))

        good_purchases_sorted = good_purchases.copy()
        good_purchases_sorted['만족도'] = (good_purchases_sorted['사용빈도'] - good_purchases_sorted['필요도'] + 5) * good_purchases_sorted['사용빈도']
        good_purchases_sorted = good_purchases_sorted.nlargest(5, '만족도')

        display_good = good_purchases_sorted[['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도']].copy()
        display_good['날짜'] = display_good['날짜'].dt.strftime('%Y-%m-%d')
        display_good['금액'] = display_good['금액'].apply(lambda x: f"₩{x:,.0f}")

        st.dataframe(
            display_good,
            use_container_width=True,
            hide_index=True
        )


def main():
    """메인 함수"""
    # 커스텀 CSS 로드
    load_custom_css()

    # 세션 상태 초기화
    init_session_state()

    # ===== OAuth 콜백 처리 =====
    # URL에 code 파라미터가 있으면 OAuth 콜백 처리
    query_params = st.query_params

    if 'code' in query_params:
        code = query_params['code']
        user_info = handle_oauth_callback(code)

        if user_info:
            st.session_state.user_info = user_info
            save_session(user_info)  # 세션 파일 저장 (새로고침 유지)
            # URL 정리 (콜백 파라미터 제거)
            st.query_params.clear()
            st.rerun()

    # ===== 로그인 체크 =====
    if 'user_info' not in st.session_state:
        # 저장된 세션 확인 (새로고침 시 자동 로그인)
        saved_session = load_session()
        if saved_session:
            st.session_state.user_info = saved_session
            st.rerun()
        else:
            display_login_screen()
            return

    # 로그인됨 → 사용자 정보 가져오기
    user_info = st.session_state.user_info
    user_email = user_info['email']

    # ===== DB 사용자 연동 =====
    if DB_AVAILABLE and is_db_available() and 'db_user_id' not in st.session_state:
        db_user = get_or_create_user(user_info)
        if db_user:
            st.session_state.db_user_id = db_user['id']
            st.session_state.is_admin = db_user.get('is_admin', False)
            # 세션 파일에도 db_user_id 저장
            user_info['db_user_id'] = db_user['id']
            save_session(user_info)

    # ===== 관리자가 아니면 Streamlit 툴바 숨기기 =====
    if not st.session_state.get('is_admin', False):
        st.markdown("""
        <style>
            [data-testid="stToolbar"] {display: none !important;}
            [data-testid="stStatusWidget"] {display: none !important;}
            .stDeployButton {display: none !important;}
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
        </style>
        """, unsafe_allow_html=True)

    # ===== 사용 횟수 체크 (관리자는 무제한) =====
    if st.session_state.get('is_admin', False):
        can_use, remaining, is_subscribed = True, -1, True
    else:
        can_use, remaining, is_subscribed = check_usage_limit(user_email)

    # 헤더 표시
    display_header()

    # 모바일용 계정 expander (사이드바 접근 어려울 때)
    with st.expander(f"👤 {user_info['name']} | {t('my_account', lang)}"):
        exp_col1, exp_col2 = st.columns([3, 1])
        with exp_col1:
            st.caption(user_info['email'])
            if is_subscribed:
                st.success(t('premium', lang))
            else:
                st.info(f"{t('free_plan', lang)}: {remaining}{t('remaining', lang)}")
        with exp_col2:
            if st.button(t('logout', lang), key="mobile_logout", use_container_width=True):
                logout()
                st.rerun()

    # 사이드바에 언어 선택 + 사용자 정보 표시
    with st.sidebar:
        # 언어 선택
        lang_options = {'한국어': 'ko', '日本語': 'ja'}
        lang_labels = list(lang_options.keys())
        current_lang = get_lang()
        current_index = lang_labels.index('日本語') if current_lang == 'ja' else 0
        selected_lang_label = st.selectbox(
            t('language', current_lang),
            lang_labels,
            index=current_index
        )
        new_lang = lang_options[selected_lang_label]
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()

        lang = get_lang()

        st.divider()

        st.markdown(f"### {t('my_account', lang)}")

        # 프로필 사진
        if user_info.get('picture'):
            st.image(user_info['picture'], width=60)

        st.markdown(f"**{user_info['name']}**")
        st.caption(user_info['email'])

        # 사용 횟수 표시
        if is_subscribed:
            st.success(t('premium', lang))
        else:
            st.info(f"{t('free_plan', lang)}: {remaining}{t('remaining', lang)}")

        # 로그아웃 버튼
        if st.button(t('logout', lang), use_container_width=True):
            logout()
            st.rerun()

        st.divider()

    # 사이드바 나머지 (기존)
    display_sidebar()

    # 분석 이력 (DB 연동 시)
    display_analysis_history()

    # 사용 횟수 소진 체크
    if not can_use:
        display_usage_limit_screen(remaining)
        return

    # ===== 기존 메인 로직 =====
    lang = get_lang()

    # 데이터 입력 (탭)
    st.header(t('data_input', lang))

    tab1, tab2 = st.tabs([t('expense_tracker', lang), t('tab_csv', lang)])

    processed_df = None

    with tab1:
        processed_df = expense_tracker()

    with tab2:
        csv_result = upload_csv()
        if csv_result is not None:
            processed_df = csv_result
            # CSV 업로드 시 DB에도 저장
            user_id = st.session_state.get('db_user_id')
            if user_id and DB_AVAILABLE and is_db_available():
                save_purchases(user_id, csv_result, 'csv')

    if processed_df is not None:
        # 세션 상태에 저장
        st.session_state.processed_df = processed_df

        # 새 분석인 경우에만 사용 횟수 증가 (중복 방지)
        if st.session_state.get('new_analysis', False):
            increment_usage_count(user_email)
            st.session_state.new_analysis = False

    # 데이터가 있으면 분석 표시
    if st.session_state.processed_df is not None:
        df = st.session_state.processed_df

        st.divider()

        # 원본 데이터 표시
        display_raw_data(df)

        st.divider()

        # 카테고리 분석
        display_category_analysis(df)

        st.divider()

        # 추가 차트
        display_additional_charts(df)

        st.divider()

        # 후회 점수 분석
        display_regret_score_analysis(df)

        st.divider()

        # Google AdSense 광고
        display_adsense_ad()

        st.divider()

        # AI 통합 분석 (심리 분석 + 스마트 인사이트)
        display_ai_analysis(df)

        st.divider()

        # 기본 인사이트
        display_insights(df)

        st.divider()

        # 완료 메시지
        st.success(t('analysis_complete', lang))

    else:
        # 데이터가 없을 때 안내 메시지
        st.info(t('no_data', lang))


if __name__ == "__main__":
    main()
