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
        save_purchases, load_purchases, get_purchase_count,
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
    page_title="Smart Purchase Analyzer",
    page_icon="📊",
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

        # 샘플 CSV 데이터
        if lang == 'ja':
            sample_data = """日付,カテゴリ,商品名,金額,検討期間,再購入意向,使用頻度
2024-01-15,電子製品,ワイヤレスイヤホン,89000,7,はい,5
2024-01-20,衣類,冬コート,150000,14,いいえ,2
2024-02-01,食費,デリバリー,25000,0,いいえ,1
2024-02-05,趣味,ボードゲーム,45000,3,はい,4
2024-02-10,電子製品,スマートウォッチ,280000,0,いいえ,1"""
        else:
            sample_data = """날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도
2024-01-15,전자제품,무선이어폰,89000,7,예,5
2024-01-20,의류,겨울코트,150000,14,아니오,2
2024-02-01,식비,배달음식,25000,0,아니오,1
2024-02-05,취미,보드게임,45000,3,예,4
2024-02-10,전자제품,스마트워치,280000,0,아니오,1
2024-02-15,의류,운동화,120000,30,예,5
2024-03-01,식비,커피,4500,0,아니오,3
2024-03-05,취미,책,18000,7,예,4
2024-03-10,전자제품,키보드,95000,5,예,5
2024-03-15,의류,티셔츠,35000,2,아니오,3"""

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
        st.markdown("""
        <div class="support-section">
            <h3>이 서비스가 도움이 되셨나요?</h3>
            <p>커피 한 잔으로 후원해주세요!</p>
            <a href="https://www.buymeacoffee.com/yourname" target="_blank">
                <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee">
            </a>
            <br><br>
            <small style="color: #78350f;">
            후원 링크 활성화: <a href="https://www.buymeacoffee.com" target="_blank">계정 생성</a> 후 app.py Line 135에서 'yourname' 변경
            </small>
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
        st.markdown(f"### {t('analysis_history', lang) if 'analysis_history' in TRANSLATIONS.get(lang, {}) else '분석 이력'}")

        analyses = load_analyses(user_id, limit=5)
        if not analyses:
            st.caption("아직 분석 이력이 없습니다." if lang == 'ko' else "分析履歴がありません。")
            return

        # 저장된 구매 이력 수
        purchase_count = get_purchase_count(user_id)
        st.caption(f"{'저장된 구매' if lang == 'ko' else '保存された購入'}: {purchase_count}건")

        for a in analyses:
            created = a.get('created_at', '')[:10]
            avg_score = a.get('average_regret_score', 0)
            count = a.get('purchase_count', 0)
            label = f"{created} | {count}건 | 후회 {avg_score:.0f}점"

            with st.expander(label, expanded=False):
                if a.get('psychology_analysis'):
                    st.markdown(a['psychology_analysis'][:300] + "..." if len(a.get('psychology_analysis', '')) > 300 else a.get('psychology_analysis', ''))
                if a.get('smart_insights'):
                    st.markdown("---")
                    st.markdown(a['smart_insights'][:300] + "..." if len(a.get('smart_insights', '')) > 300 else a.get('smart_insights', ''))


def display_login_screen():
    """로그인 화면 표시"""
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

        st.markdown("""
        **무료 플랜**:
        - 분석 5회 무료 제공
        - 모든 기능 이용 가능

        **프리미엄 플랜** (월 5,000원):
        - 무제한 분석
        - AI 심리 분석 우선 지원
        - 광고 제거
        """)

        # Google 로그인 버튼
        login_url = get_login_url()

        st.markdown(f"""
        <a href="{login_url}" target="_self">
            <button style="
                background-color: #4285f4;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                     style="width: 20px; margin-right: 10px;">
                {t('google_login', lang)}
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("로그인 시 [이용약관] 및 [개인정보 처리방침]에 동의하는 것으로 간주됩니다.")


def display_usage_limit_screen(remaining):
    """사용 횟수 제한 화면"""
    st.warning(f"⚠️ 무료 사용 횟수가 {remaining}회 남았습니다.")

    if remaining == 0:
        st.error("❌ 무료 사용 횟수를 모두 소진하셨습니다.")

        st.markdown("### 프리미엄 플랜으로 업그레이드")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **무료 플랜**
            - 분석 5회 제공
            - 기본 기능 이용
            - 광고 표시
            """)

        with col2:
            st.markdown("""
            **프리미엄 플랜** (월 5,000원)
            - ✅ 무제한 분석
            - ✅ AI 심리 분석 우선 지원
            - ✅ 광고 제거
            - ✅ 데이터 무제한 저장
            """)

        if st.button("프리미엄 구독하기", type="primary", use_container_width=True):
            st.info("💳 결제 시스템은 곧 오픈 예정입니다!")
            st.caption("현재는 데모 버전으로, 실제 결제는 베타 출시 후 가능합니다.")

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
            with st.spinner('🧮 후회 점수 계산 중...'):
                processed_df = add_regret_scores_to_dataframe(processed_df)

            st.success("후회 점수 계산 완료!")

            return processed_df

        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류 발생: {str(e)}")
            return None

    return None


def manual_input_form():
    """수동 입력 폼 처리"""
    lang = get_lang()
    st.markdown(f"### {t('manual_title', lang)}")
    st.markdown(t('manual_desc', lang))

    # 세션 상태에 수동 입력 리스트 초기화
    if 'manual_items' not in st.session_state:
        st.session_state.manual_items = []

    # 입력 폼 (2열 레이아웃)
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
        # 카테고리 (드롭다운 + 직접 입력)
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

    # 사용빈도 (전체 너비)
    usage_freq = st.slider(
        t('usage_freq', lang),
        min_value=1,
        max_value=5,
        value=3,
        help=t('usage_help', lang)
    )

    # 필요도 자동 계산 (실시간 표시)
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

    # 버튼 (2열)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])

    with btn_col1:
        save_btn = st.button(t('btn_save', lang), type="primary", use_container_width=True)

    with btn_col2:
        reset_btn = st.button(t('btn_reset', lang), use_container_width=True)

    # 저장 버튼 처리
    if save_btn:
        # 필수 필드 검증
        if not product_name.strip():
            st.error("❌ 상품명을 입력해주세요.")
        elif not category.strip():
            st.error("❌ 카테고리를 선택하거나 입력해주세요.")
        elif amount <= 0:
            st.error("❌ 금액은 0보다 커야 합니다.")
        else:
            # 데이터 저장
            item = {
                '날짜': pd.to_datetime(purchase_date),
                '카테고리': category,
                '상품명': product_name,
                '금액': amount,
                '필요도': necessity,
                '사용빈도': usage_freq
            }
            st.session_state.manual_items.append(item)
            st.success(f"✅ '{product_name}' 저장 완료! (총 {len(st.session_state.manual_items)}건)")
            st.balloons()

    # 초기화 버튼 처리
    if reset_btn:
        st.rerun()

    # 저장된 항목 표시
    if st.session_state.manual_items:
        st.divider()
        st.markdown(f"### {t('saved_items', lang)}")

        # 테이블로 표시
        display_items = pd.DataFrame(st.session_state.manual_items)
        display_items['날짜'] = display_items['날짜'].dt.strftime('%Y-%m-%d')
        display_items['금액'] = display_items['금액'].apply(lambda x: f"₩{x:,.0f}")

        st.dataframe(
            display_items,
            use_container_width=True,
            hide_index=True
        )

        # 분석 시작 버튼
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

        with btn_col1:
            analyze_btn = st.button(
                t('btn_analyze', lang),
                type="primary",
                use_container_width=True
            )

        with btn_col2:
            clear_all_btn = st.button(
                t('btn_clear', lang),
                use_container_width=True
            )

        # 분석 시작 버튼 처리
        if analyze_btn:
            with st.spinner('🧮 데이터 처리 및 후회 점수 계산 중...'):
                # DataFrame 생성
                df = create_dataframe_from_manual_input(st.session_state.manual_items)

                # 기존 파이프라인 재사용
                # 1. 검증 (수동 입력이므로 이미 검증됨, 하지만 안전하게 한번 더)
                is_valid, error_message = validate_csv(df)

                if not is_valid:
                    st.error(f"❌ 데이터 검증 실패: {error_message}")
                    return None

                # 2. 전처리
                processed_df = process_csv_data(df)

                # 3. 후회 점수 계산
                processed_df = add_regret_scores_to_dataframe(processed_df)

                st.success("✅ 분석 완료!")
                st.session_state.manual_items = []  # 분석 후 초기화
                st.session_state.new_analysis = True  # 새 분석 플래그

                return processed_df

        # 전체 삭제 버튼 처리
        if clear_all_btn:
            st.session_state.manual_items = []
            st.success("🗑️ 모든 항목이 삭제되었습니다.")
            st.rerun()

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
    display_summary.columns = ['카테고리', '총 금액', '평균 금액', '구매 건수', '평균 필요도', '평균 사용빈도']

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
        st.warning("⚠️ 후회 점수가 계산되지 않았습니다.")
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
    dist_df = pd.DataFrame({
        '등급': grade_labels,
        '건수': [dist['very_satisfied'], dist['satisfied'], dist['neutral'], dist['regretful'], dist['very_regretful']],
        '색상': ['#90EE90', '#FFFFE0', '#FFD700', '#FFA500', '#FF6B6B']
    })

    import plotly.express as px

    fig = px.bar(
        dist_df,
        x='등급',
        y='건수',
        color='색상',
        color_discrete_map={color: color for color in dist_df['색상']},
        text='건수'
    )

    fig.update_traces(
        textposition='outside',
        hovertemplate='%{x}<br>건수: %{y}건<extra></extra>'
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title='',
        yaxis_title='구매 건수',
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
        '필요도-사용빈도 갭': df['후회점수_필요도갭'].mean(),
        '시간 경과': df['후회점수_시간경과'].mean(),
        '금액 가중치': df['후회점수_금액'].mean(),
        '최근성': df['후회점수_최근성'].mean(),
        '반복 구매': df['후회점수_반복구매'].mean(),
        '새벽 구매': df['후회점수_새벽구매'].mean(),
        '충동 패턴': df['후회점수_충동패턴'].mean()
    }

    factor_df = pd.DataFrame({
        '요인': list(factor_scores.keys()),
        '평균 점수': list(factor_scores.values())
    }).sort_values('평균 점수', ascending=False)

    fig = px.bar(
        factor_df,
        x='평균 점수',
        y='요인',
        orientation='h',
        text='평균 점수',
        color='평균 점수',
        color_continuous_scale='Reds'
    )

    fig.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        hovertemplate='%{y}<br>평균: %{x:.1f}점<extra></extra>'
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title='평균 점수',
        yaxis_title='',
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # 각 요인 설명
    with st.expander(t('factor_explain', lang)):
        st.markdown("""
        ### 각 요인이 후회 점수에 미치는 영향

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
           - 같은 날 3건 이상 또는 3일 내 5건 이상 시 높은 점수
        """)


def display_ai_analysis(df: pd.DataFrame):
    """AI 기반 통합 분석 (심리 분석 + 스마트 인사이트)"""
    lang = get_lang()
    st.header(t('ai_analysis', lang))
    st.caption(t('ai_caption', lang))

    # OpenAI 모듈 및 API 키 확인
    if not OPENAI_AVAILABLE:
        api_available = False
        api_message = "OpenAI 라이브러리가 설치되지 않았습니다."
    else:
        api_available, api_message = check_api_key_available()

    if not api_available:
        st.warning(f"{api_message}")
        st.info("""
        **OpenAI API 키 설정 방법**:
        1. `.env` 파일을 프로젝트 루트에 생성
        2. 다음 내용 추가: `OPENAI_API_KEY=sk-your-api-key-here`
        3. OpenAI 플랫폼(https://platform.openai.com/api-keys)에서 API 키 발급
        4. 앱 재시작

        API 키가 없어도 기본 분석은 계속 이용 가능합니다!
        """)

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
                tips = [
                    "구매 전 24시간 고민 시간을 가져보세요.",
                    "구매 목록을 미리 작성하는 습관을 들여보세요.",
                    "장바구니에 담고 3일 후 다시 확인하세요."
                ]

            for tip in tips:
                st.markdown(f"- {tip}")

        return

    # 후회 점수 확인
    if '후회점수' not in df.columns:
        st.warning("후회 점수가 계산되지 않았습니다.")
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
                st.error("OpenAI 라이브러리가 설치되지 않았습니다.")
                return

            openai_service = get_openai_service()
            if not openai_service:
                st.error("OpenAI 서비스를 초기화할 수 없습니다.")
                return

            # 주요 원인 변환
            cause_names = {
                '필요도갭': '필요도-사용빈도 갭',
                '시간경과': '시간 경과 대비 낮은 사용빈도',
                '금액': '고가 제품 구매',
                '최근성': '최근 충동 구매',
                '반복구매': '동일 카테고리 반복 구매',
                '새벽구매': '새벽 시간대 구매',
                '충동패턴': '충동 구매 패턴'
            }
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
                        st.metric("입력 토큰", f"{total_prompt:,}")
                    with col2:
                        st.metric("출력 토큰", f"{total_completion:,}")
                    with col3:
                        st.metric("총 토큰", f"{total_all:,}")

                    prompt_cost = total_prompt * 0.15 / 1_000_000
                    completion_cost = total_completion * 0.60 / 1_000_000
                    total_cost = prompt_cost + completion_cost
                    st.info(f"예상 비용: ${total_cost:.6f} (약 ₩{total_cost * 1300:.2f})")
            else:
                error_msg = feedback_result.get('error', '') or insights_result.get('error', '')
                st.error(f"{error_msg}")
                st.info("API 키를 확인하거나 잠시 후 다시 시도해주세요.")

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
            st.markdown("""
            **소비 심리 분석**
            - 소비 패턴 요약 및 주요 후회 원인 분석
            - 실천 가능한 개선 방안과 월간 도전 과제

            **스마트 인사이트**
            - 각 구매의 소비패턴 분류 (스트레스성, 충동적, 계획적 등)
            - 유사 사용자 재구매율 추정
            - 카테고리별 장기 저축 효과 시뮬레이션
            - 추천 구매목록 TOP 5 (쿠팡 링크 포함)
            """)


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
            '카테고리': cat,
            '월 평균 지출': f"₩{monthly_avg:,.0f}",
            f'{reduction}% 절감 시 연간 저축': f"₩{annual_saving:,.0f}"
        })

    st.dataframe(pd.DataFrame(savings_data), use_container_width=True, hide_index=True)

    total_annual_saving = sum(
        val * (reduction / 100) * 12
        for val in category_monthly
    )
    st.metric(t('annual_saving', lang), f"₩{total_annual_saving:,.0f}")



def display_adsense_ad():
    """Google AdSense 광고 표시"""
    # 광고 코드 (사용자가 실제 Publisher ID와 Ad Slot ID로 변경 필요)
    ad_code = """
    <div style="text-align: center; padding: 20px 0;">
        <p style="color: gray; font-size: 12px; margin-bottom: 10px;">Sponsored</p>

        <!-- Google AdSense 광고 코드 -->
        <!--
        실제 광고를 활성화하려면:
        1. https://www.google.com/adsense 에서 계정 생성 및 승인 대기
        2. 광고 단위 생성 후 아래 주석을 해제하고 실제 코드로 교체
        3. ca-pub-XXXXXXXX를 본인의 Publisher ID로 변경
        4. data-ad-slot="XXXXXXXXXX"를 실제 광고 슬롯 ID로 변경
        -->

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
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        -->

        <!-- 임시 플레이스홀더 (실제 광고 승인 전) -->
        <div style="background-color: #f0f0f0; padding: 60px 20px; border-radius: 5px; border: 1px dashed #ccc;">
            <p style="color: #666; margin: 0;">
                📢 광고 영역<br>
                <small>AdSense 승인 후 광고가 표시됩니다</small>
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
            # 세션 파일에도 db_user_id 저장
            user_info['db_user_id'] = db_user['id']
            save_session(user_info)

    # ===== 사용 횟수 체크 =====
    can_use, remaining, is_subscribed = check_usage_limit(user_email)

    # 헤더 표시
    display_header()

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

    tab1, tab2 = st.tabs([t('tab_manual', lang), t('tab_csv', lang)])

    processed_df = None

    with tab1:
        processed_df = manual_input_form()

    with tab2:
        processed_df = upload_csv()

    if processed_df is not None:
        # 세션 상태에 저장
        st.session_state.processed_df = processed_df

        # 새 분석인 경우에만 사용 횟수 증가 (중복 방지)
        if st.session_state.get('new_analysis', False):
            increment_usage_count(user_email)
            st.session_state.new_analysis = False

            # DB에 구매 이력 저장
            user_id = st.session_state.get('db_user_id')
            if user_id and DB_AVAILABLE and is_db_available():
                source = 'csv' if st.session_state.get('last_uploaded_file') else 'manual'
                save_purchases(user_id, processed_df, source)

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
