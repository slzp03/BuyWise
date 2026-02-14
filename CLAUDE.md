# Claude 프로젝트 컨텍스트

> 이 파일은 Claude가 프로젝트를 이해하고 계속 작업할 수 있도록 하는 전체 컨텍스트입니다.

---

## 📋 프로젝트 개요

### 프로젝트명
**AI 구매 후회 방지 분석기** (AI Purchase Regret Analyzer)

### 목적
- 해커톤 제출용 MVP
- CSV 구매 내역 분석 → 후회 점수 계산 → AI 심리 분석
- 충동 구매 방지 및 소비 습관 개선

### 타겟
- 20-30대 MZ세대
- 충동 구매로 후회한 경험이 있는 사람
- 데이터 기반 재무 관리를 원하는 사람

---

## 🛠 현재 기술 스택 (실제 구현)

### 웹 프레임워크
- **Streamlit 1.31+**: Python 올인원 웹앱
- **이유**: 빠른 프로토타이핑, 해커톤 시연 용이성

### 데이터 처리
- **pandas 2.2+**: CSV 파싱 및 분석
- **numpy 1.26+**: 수치 계산

### 시각화
- **Plotly 5.18+**: 인터랙티브 차트 (게이지, 파이, 바, 산점도 등)

### AI
- **OpenAI Python SDK 1.10+**: GPT-4o-mini API
- **python-dotenv 1.0+**: 환경 변수 관리

---

## 📁 현재 디렉토리 구조

```
project/
├── app.py                       # 메인 Streamlit 애플리케이션 (1440+ 줄)
├── utils/                       # 유틸리티 모듈
│   ├── __init__.py
│   ├── csv_processor.py         # CSV 검증 및 전처리 (225+ 줄) - 두 형식 지원
│   ├── visualizer.py            # Plotly 차트 생성 (200+ 줄)
│   ├── regret_calculator.py     # 후회 점수 계산 로직 (500+ 줄)
│   ├── openai_service.py        # OpenAI API 호출 (500+ 줄) - 심리분석 + 스마트인사이트
│   └── auth.py                  # Google OAuth 인증 + 세션 유지 (250+ 줄)
├── data/                        # 사용자 데이터
│   ├── .gitignore              # users.json, session.json 제외
│   ├── users.json              # 사용자 데이터 (자동 생성)
│   └── session.json            # 로그인 세션 (자동 생성, 새로고침 유지용)
├── requirements.txt             # 패키지 의존성
├── .env                         # 환경 변수 (API 키, OAuth) ⚠️ Git 제외
├── .gitignore                   # Git 제외 파일
├── sample_purchases.csv         # 샘플 데이터 (30건)
├── CLAUDE.md                    # 이 파일
├── README.md                    # 프로젝트 소개
├── ARCHITECTURE.md              # 시스템 아키텍처 (Streamlit 구조)
├── QUICKSTART.md                # 빠른 시작 가이드
├── REGRET_SCORE_GUIDE.md        # 후회 점수 계산 가이드
├── API_KEY_SETUP.md             # OpenAI API 설정 가이드
├── OPENAI_SETUP_GUIDE.md        # OpenAI API 상세 가이드
└── .claude-project-config.json  # 프로젝트 설정
```

---

## 🎯 구현 완료 기능

### 1. CSV 업로드 및 검증
- Streamlit `file_uploader` 위젯
- UTF-8, CP949 자동 인코딩 감지
- **두 가지 CSV 형식 지원**:
  - 새 형식: 날짜, 카테고리, 상품명, 금액, **고민기간, 재구매의향**, 사용빈도 (수동 입력과 동일)
  - 기존 형식: 날짜, 카테고리, 상품명, 금액, 필요도, 사용빈도 (하위 호환)
- 데이터 타입 검증 및 에러 메시지

### 2. 데이터 전처리
- 날짜 변환 (datetime)
- 경과 일수 계산
- 숫자 타입 변환
- 결측값 처리
- **새 형식 CSV**: 고민기간+재구매의향 → 필요도 자동 계산 (`calculate_necessity_from_input` 재사용)

### 3. 후회 점수 계산 ⭐ 핵심
**7가지 요소 (총 100점)**:
1. **필요도-사용빈도 갭** (최대 30점) - 핵심 지표
2. **시간 경과** (최대 15점) - 오래됐는데 안 쓰는 경우
3. **금액 가중치** (최대 20점) - 고가 제품
4. **최근성** (최대 10점) - 최근 구매 충동성
5. **반복 구매** (최대 15점) - 같은 카테고리 반복
6. **새벽 구매** (최대 10점) - 새벽 시간대 충동 구매
7. **충동 패턴** (최대 10점) - 짧은 시간 내 여러 구매

**점수 해석**:
- 0-20: 매우 만족
- 21-35: 만족
- 36-50: 보통
- 51-65: 아쉬움
- 66-100: 후회

### 4. 시각화 (Plotly 차트 6종)
1. **후회 점수 게이지**: 0-100 게이지 차트
2. **카테고리 차트**: 파이/바 차트 전환 가능
3. **금액 분포**: 히스토그램
4. **월별 추이**: 이중 축 (금액 + 건수)
5. **필요도 vs 사용빈도**: 산점도 (대각선 기준선)
6. **요인별 기여도**: 가로 막대 차트

### 5. OpenAI API 통합 (통합 AI 분석)
- **모델**: gpt-4o-mini
- **비용**: 1회 약 $0.0006 (₩0.8) — 2회 API 호출 합산
- **통합 분석**: 버튼 1개로 심리 분석 + 스마트 인사이트 동시 생성
- **심리 분석 프롬프트**:
  - Role: 20년 경력 소비 심리 전문가
  - Task: 소비 패턴 요약, 후회 원인 3가지, 개선 방안 3가지, 월간 목표
- **스마트 인사이트 프롬프트**:
  - Task: 소비패턴 분류, 유사 사용자 재구매율, 장기 저축 효과, 추천 구매목록 TOP 5
  - 추천 TOP 5: 실제 브랜드+모델명 포함, 쿠팡 검색 링크 (`https://www.coupang.com/np/search?q=`)
- **에러 핸들링**: API 키 없어도 기본 팁 제공

### 6. Streamlit 앱 구조
```
데이터 입력 → 데이터 미리보기 → 카테고리 분석 → 심층 분석
→ 후회 점수 → AI 종합 분석 → 종합 요약
```

### 7. 수동 입력 폼 ✏️ (2단계)
- **자동 필요도 계산**: 고민 기간 + 재구매 의향 기반
  - 0일 = 충동구매(1점), 7일 = 보통(3점), 30일+ = 신중(4점)
  - 재구매 의향 있음 → +1점 (최대 5점)
- **다중 항목 누적 입력**: 여러 항목 저장 후 일괄 분석
- **실시간 필요도 표시**: 입력하면 자동 계산된 점수 즉시 표시
- **카테고리 드롭다운**: 자주 쓰는 카테고리 + 직접 입력
- **CSV 파이프라인 재사용**: 기존 검증/분석 로직 그대로 활용

### 8. Google OAuth 로그인 시스템 (3단계)
- **Google OAuth 2.0**: google-auth-oauthlib 사용
- **사용 횟수 제한**: 무료 5회 → 프리미엄 무제한
- **로컬 JSON 저장**: data/users.json (Phase 4 DB 전까지)
- **로그인 화면**: Google 로그인 버튼, 플랜 설명
- **사용자 정보 표시**: 사이드바에 프로필, 이메일, 남은 횟수
- **구독 유도 화면**: 5회 소진 시 프리미엄 안내 (결제 UI만, 실제 결제 없음)
- **로그인 세션 유지**: 새로고침 시에도 로그인 상태 유지 (data/session.json)
  - `save_session()`, `load_session()`, `clear_session()` (auth.py)
- **사용 횟수 중복 카운트 버그 수정 완료** ✅
  - `new_analysis` 플래그 패턴으로 해결 (upload_csv, manual_input_form에서 설정, main에서 소비 후 리셋)

### 9. 수익 모델 구현 💰
- **Buy Me a Coffee**: 사이드바 후원 버튼
  - 위치: 사이드바 하단
  - 배지 스타일 링크
  - 계정 설정 가이드 포함
- **Google AdSense**: 반응형 디스플레이 광고
  - 위치: 후회 점수 분석과 AI 분석 사이
  - 전용 함수로 구현 (`display_adsense_ad()`)
  - 승인 전 플레이스홀더 표시
  - 설정 가이드 주석 포함

---

## 🔑 중요 설계 결정

### 1. FastAPI+React → Streamlit 전환
**결정 시점**: 1단계 구현 시작 시
**이유**:
- 해커톤 목표: 빠른 프로토타이핑 최우선
- 시연 중심: UI 있어야 데모 가능
- 개발 시간: 2-3일 → 몇 시간으로 단축
- 완성도: 완전히 동작하는 앱 보장

**트레이드오프**:
- 장점: 빠른 개발, 간단한 배포, 즉각적인 시연 가능
- 단점: UI 커스터마이징 제한, 대규모 앱에는 비효율적

**향후 계획**:
- Phase 4에서 FastAPI 백엔드 분리 가능
- 현재 utils/ 모듈은 그대로 재사용 가능

### 2. 세션 기반 (DB 없음)
**이유**: MVP 단계, 빠른 구현
**구현**: Streamlit `session_state` 사용
**향후**: Phase 2에서 PostgreSQL 도입 예정

### 3. 환경 변수로 API 키 관리
**파일**: `.env` (Git 제외)
**형식**:
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800
```

---

## 📊 CSV 형식

### 새 형식 (권장, 수동 입력과 동일)
```csv
날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도
2024-01-15,전자제품,무선이어폰,89000,7,예,5
2024-02-10,전자제품,스마트워치,280000,0,아니오,1
```

- **날짜**: YYYY-MM-DD
- **카테고리**: 텍스트
- **금액**: 숫자 (0 이상)
- **고민기간**: 구매 전 고민한 일수 (0 = 충동구매)
- **재구매의향**: 예/아니오 (Y/N, yes/no, 1/0 도 가능)
- **사용빈도**: 1-5 정수 (실제 사용 빈도)
- **상품명**: 선택사항
- **필요도**: 고민기간+재구매의향으로 **자동 계산됨**

### 기존 형식 (하위 호환)
```csv
날짜,카테고리,상품명,금액,필요도,사용빈도
2024-01-15,전자제품,무선이어폰,89000,3,5
```
- 필요도를 직접 1-5로 입력하는 방식도 여전히 지원

---

## 🔐 환경 변수 및 보안

### API 키 설정
- **위치**: `.env` 파일
- **현재 상태**: ✅ API 키 설정 완료 ($5 충전, 자동충전 OFF)
- **보안**: `.gitignore`에 `.env` 포함

### Git 제외 항목
```
.env
__pycache__/
venv/
*.pyc
.streamlit/
```

---

## 🚀 실행 방법

### 로컬 실행
```bash
# 1. 가상 환경 활성화 (선택)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. 패키지 설치 (최초 1회)
pip install -r requirements.txt

# 3. 앱 실행
streamlit run app.py

# 브라우저 자동 실행: http://localhost:8501
```

### 테스트
1. Google 로그인
2. 샘플 CSV 다운로드 (사이드바) 또는 수동 입력
3. CSV 업로드 또는 수동 입력 → 분석 시작
4. 데이터 미리보기 → 카테고리 분석 → 심층 분석 → 후회 점수 확인
5. "AI 분석 시작" 버튼 클릭 → 심리 분석 + 스마트 인사이트 확인
6. 새로고침 → 로그인 유지 확인

---

## 📝 코드 주요 위치

### app.py (주요 함수)
- `init_session_state()` - 세션 초기화
- `display_sidebar()` - 사이드바 (CSV 형식 안내, 샘플 다운로드, Buy Me a Coffee)
- `display_login_screen()` - Google OAuth 로그인 화면
- `upload_csv()` - CSV 업로드 및 검증 (새 형식/기존 형식 자동 감지)
- `manual_input_form()` - 수동 입력 폼 (고민기간+재구매의향 → 필요도 자동 계산)
- `display_raw_data()` - 데이터 미리보기 (고민기간/재구매의향 컬럼 포함)
- `display_category_analysis()` - 카테고리 분석
- `display_additional_charts()` - 심층 분석 (금액 분포, 월별 추이, 산점도)
- `display_regret_score_analysis()` - 후회 점수
- `display_ai_analysis()` - **AI 종합 분석** (심리 분석 + 스마트 인사이트 통합)
- `prepare_smart_insights_data()` - 스마트 인사이트용 데이터 준비
- `display_savings_calculator()` - 저축 시뮬레이터 (절감 비율 슬라이더)
- `display_adsense_ad()` - Google AdSense 광고
- `display_insights()` - 종합 요약
- `main()` - 메인 함수 (OAuth → 사용 횟수 체크 → 데이터 입력 → 분석 플로우)

### utils/csv_processor.py
- `validate_csv()` - CSV 검증 (새 형식: 고민기간+재구매의향 / 기존 형식: 필요도)
- `process_csv_data()` - 전처리 (새 형식이면 필요도 자동 계산)
- `calculate_necessity_from_input()` - 고민기간+재구매의향 → 필요도 계산
- `create_dataframe_from_manual_input()` - 수동 입력 → DataFrame 변환

### utils/openai_service.py
- `build_analysis_prompt()` - 심리 분석 프롬프트 생성
- `generate_ai_feedback()` - 심리 분석 API 호출
- `build_smart_insights_prompt()` - 스마트 인사이트 프롬프트 (TOP 5 쿠팡 링크 포함)
- `generate_smart_insights()` - 스마트 인사이트 API 호출

### utils/auth.py
- `get_login_url()` - Google OAuth 로그인 URL 생성
- `handle_oauth_callback()` - OAuth 콜백 처리
- `check_usage_limit()` - 사용 횟수 확인
- `increment_usage_count()` - 사용 횟수 증가
- `logout()` - 로그아웃 (세션 파일 삭제 포함)
- `save_session()` / `load_session()` / `clear_session()` - 로그인 세션 파일 관리

---

## 💰 수익 모델 상세 가이드

### 1. Buy Me a Coffee 설정
**위치**: [app.py:128-146](app.py#L128-L146) 사이드바 하단

**설정 방법**:
1. https://www.buymeacoffee.com 접속
2. 무료 계정 생성 (5분)
3. 본인의 계정명 확인 (예: `yourname`)
4. [app.py:137](app.py#L137)에서 `yourname`을 본인 계정명으로 변경
   ```python
   <a href="https://www.buymeacoffee.com/yourname" target="_blank">
   # ↓ 변경
   <a href="https://www.buymeacoffee.com/실제계정명" target="_blank">
   ```

**수익 구조**:
- 기본: ₩5,000 (커피 1잔)
- 수수료: 5% (Buy Me a Coffee)
- 입금: PayPal, Stripe 연동 가능

**예상 수익** (해커톤 후 베타 출시 기준):
- 월 사용자 100명 중 1% 후원 → 월 ₩5,000
- 월 사용자 1,000명 중 1% 후원 → 월 ₩50,000

### 2. Google AdSense 설정
**위치**:
- 함수: [app.py:759-799](app.py#L759-L799)
- 호출: [app.py:882-883](app.py#L882-L883) 후회 점수 ↔ AI 분석 사이

**설정 방법**:
1. https://www.google.com/adsense 접속
2. 계정 생성 및 사이트 등록
3. 승인 대기 (보통 1-2주)
4. 광고 단위 생성 후 코드 복사
5. [app.py:775-787](app.py#L775-L787) 주석 해제 및 ID 변경
   ```html
   <!-- 주석 제거 -->
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-실제ID"
        crossorigin="anonymous"></script>
   <ins class="adsbygoogle"
        style="display:block"
        data-ad-client="ca-pub-실제ID"
        data-ad-slot="실제슬롯ID"
        ...
   ```

**수익 구조**:
- CPC (클릭당): ₩100-500
- CPM (1,000회 노출당): ₩500-2,000
- CTR (클릭률): 보통 0.5-2%

**예상 수익** (해커톤 후 베타 출시 기준):
- 월 방문자 1,000명 → 광고 노출 3,000회 → 클릭 30회 → 월 ₩3,000-15,000
- 월 방문자 10,000명 → 광고 노출 30,000회 → 클릭 300회 → 월 ₩30,000-150,000

### 3. 수익 모델 조합 전략
**초기 단계 (해커톤 ~ 베타)**:
- Buy Me a Coffee: 핵심 지지자 확보
- Google AdSense: 일반 사용자 대상 광고 수익

**성장 단계 (베타 ~ 정식 출시)**:
- 무료 플랜: AdSense 광고 표시
- 프리미엄 플랜 (월 ₩5,000): 광고 제거 + 추가 기능

**예상 월 수익 (6개월 후)**:
- Buy Me a Coffee: ₩50,000 (1,000 사용자 기준)
- Google AdSense: ₩100,000 (10,000 방문자 기준)
- **합계: ₩150,000/월**

### 4. 주의사항
- **AdSense 정책**: 클릭 유도 금지, 부적절한 콘텐츠 금지
- **사용자 경험**: 광고 과다 배치 금지 (현재 1개만 배치)
- **개인정보**: 결제 정보는 Buy Me a Coffee/AdSense에서 관리

---

## 🐛 알려진 이슈 및 주의사항

### 1. CSV 시간 정보
- **이슈**: CSV에 시간 정보가 없으면 새벽 구매 점수 0점
- **현재 상태**: 정상 동작 (시간 없으면 자동으로 0점 처리)

### 2. OpenAI API 키
- **주의**: API 키가 코드에 노출되지 않도록 주의
- **현재**: `.env` 파일로 안전하게 관리 중

### 3. 대용량 CSV
- **제한**: 파일 크기 5MB 제한
- **성능**: ~1000행 기준 1초 미만 처리

### 4. Google OAuth 사용 횟수 중복 카운트 ✅ 해결 완료
- **이전 증상**: 1회 분석 시 2회 차감됨 (5회 → 3회)
- **원인**: 리렌더링 시 `increment_usage_count()` 중복 호출
- **해결**: `new_analysis` 플래그 패턴
  ```python
  # upload_csv() / manual_input_form()에서 새 데이터 생성 시
  st.session_state.new_analysis = True

  # main()에서 한 번만 카운트 후 리셋
  if st.session_state.get('new_analysis', False):
      increment_usage_count(user_email)
      st.session_state.new_analysis = False
  ```

---

## 🎯 다음 할 일 (우선순위)

### Phase 1: MVP 완료 ✅
- [x] Streamlit 앱 구현
- [x] CSV 업로드 및 검증
- [x] 후회 점수 계산 (7가지 요소)
- [x] 시각화 대시보드 (6개 차트)
- [x] OpenAI API 통합
- [x] AI 소비 심리 분석
- [x] 수익 모델 구현 (Buy Me a Coffee + Google AdSense)
- [x] 문서화 (현재 구조 반영)

### Phase 2: 수동 입력 기능 완료 ✅
- [x] 자동 필요도 계산 알고리즘 (고민 기간 + 재구매 의향)
- [x] 다중 항목 누적 입력 UI
- [x] 실시간 필요도 표시
- [x] 기존 CSV 파이프라인 재사용

### Phase 3: Google OAuth 로그인 완료 ✅
- [x] Google OAuth 2.0 통합
- [x] 로그인/로그아웃 기능
- [x] 사용 횟수 제한 (무료 5회)
- [x] 로컬 JSON 사용자 데이터 저장
- [x] 구독 유도 UI (결제 없음)
- [x] **버그 수정**: 사용 횟수 중복 카운트 (`new_analysis` 플래그)
- [x] 로그인 세션 유지 (새로고침 시 자동 로그인)
- [ ] 배포용 redirect_uri 추가

### Phase 3.5: 스마트 인사이트 + UI 개선 ✅
- [x] 스마트 인사이트 4가지 (소비패턴 분류, 재구매율, 저축 효과, 추천 TOP 5)
- [x] 추천 TOP 5에 쿠팡 실제 링크 포함 (브랜드+모델명)
- [x] AI 분석 2개 → 1개 통합 (심리 분석 + 스마트 인사이트)
- [x] 저축 시뮬레이터 (절감 비율 슬라이더)
- [x] 헤더 정리 ("1단계~7단계" 제거 → 깔끔한 한국어 헤더)
- [x] 불필요한 이모지 정리
- [x] CSV 형식을 수동 입력과 통일 (고민기간+재구매의향 → 필요도 자동 계산)
- [x] 기존 CSV 형식 하위 호환 유지

### Phase 4: 데이터베이스 설계 및 구현 📊
**목표**: 로컬 JSON → PostgreSQL 마이그레이션

**4.1 DB 설계 (서브 에이전트 활용)**
- [ ] Plan 에이전트로 DB 스키마 설계
  - 사용자 테이블 (users)
  - 구매 이력 테이블 (purchases)
  - 분석 이력 테이블 (analyses)
  - AI 사용 이력 테이블 (ai_usage_logs)
- [ ] 필요 데이터 검토
  - 계정별 OAuth 정보
  - 계정별 AI 사용 횟수 (무료 5회 제한)
  - 계정별 구매 이력 (CSV/수동 입력 데이터)
  - 계정별 후회 점수 히스토리
  - 분석 날짜/시간 타임스탬프

**4.2 DB 구현**
- [ ] PostgreSQL 설치 및 설정
- [ ] SQLAlchemy ORM 모델 작성
- [ ] users.json → DB 마이그레이션 스크립트
- [ ] CRUD 함수 구현 (utils/database.py)
- [ ] 기존 auth.py와 통합

**4.3 배포 환경 대비**
- [ ] Supabase 또는 Railway DB 설정
- [ ] 환경 변수에 DATABASE_URL 추가
- [ ] 연결 풀링 및 에러 핸들링

### Phase 5: Git Commit 및 배포 (해커톤 제출) 🚀
**목표**: GitHub 저장소 정리 및 Streamlit Cloud 배포

**5.1 Git 정리**
- [ ] .gitignore 최종 검토
  - .env, data/users.json 제외 확인
  - __pycache__, venv 제외 확인
- [ ] Git 커밋
  ```bash
  git add .
  git commit -m "feat: Add manual input, Google OAuth, and monetization"
  git push origin main
  ```

**5.2 Streamlit Cloud 배포**
- [ ] Streamlit Cloud 계정 생성
- [ ] GitHub 저장소 연결
- [ ] Secrets 설정
  - OPENAI_API_KEY
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - (DATABASE_URL - Phase 4 완료 시)
- [ ] Google Cloud Console OAuth 설정 업데이트
  - redirect_uri에 Streamlit 앱 URL 추가
  - 예: `https://your-app.streamlit.app`

**5.3 해커톤 제출 준비**
- [ ] 샘플 데이터로 시연 연습
- [ ] 시연 영상 제작 (1-2분)
  - 00:00-00:15 인트로 (프로젝트 소개)
  - 00:15-00:30 로그인 (Google OAuth)
  - 00:30-00:50 수동 입력 (자동 필요도 계산)
  - 00:50-01:10 CSV 업로드 및 분석
  - 01:10-01:30 AI 심리 분석 생성
  - 01:30-01:45 후회 점수 차트
  - 01:45-02:00 핵심 가치 및 수익 모델
- [ ] README.md 최종 점검
- [ ] 배포 URL 확인 및 테스트
- [ ] 해커톤 제출

### Phase 6: 고급 기능 (해커톤 이후)
- [ ] FastAPI 백엔드 분리
- [ ] React 프론트엔드
- [ ] 자동 은행 연동
- [ ] ML 예측 모델
- [ ] Stripe 실제 결제 통합

---

## 💡 해커톤 심사 포인트

### 1. 실제 작동하는 프로덕트 ✅
- Streamlit 앱 완전 동작
- CSV → 분석 → AI 피드백 전체 플로우

### 2. OpenAI API 활용 ✅
- GPT-4o-mini 소비 심리 분석
- 프롬프트 엔지니어링
- 실시간 AI 피드백

### 3. 완성도 ✅
- 직관적 UI/UX
- 에러 핸들링
- 샘플 데이터 제공

### 4. 비즈니스 가치 ✅
- 실제 문제 해결 (충동 구매 후회)
- 수익 모델 (구독 확장 가능)
- 타겟 시장 명확

### 5. 기술 스택 ✅
- Streamlit (빠른 프로토타이핑)
- OpenAI (AI 통합)
- pandas/Plotly (데이터 과학)

---

## 📚 문서 참조

### 사용자 가이드
- **README.md**: 프로젝트 소개 (간결)
- **QUICKSTART.md**: 5분 빠른 시작
- **API_KEY_SETUP.md**: OpenAI API 설정 (5분)

### 개발자 문서
- **ARCHITECTURE.md**: 시스템 아키텍처 (Streamlit 구조)
- **REGRET_SCORE_GUIDE.md**: 후회 점수 계산 로직 상세
- **OPENAI_SETUP_GUIDE.md**: OpenAI API 상세 가이드
- **.claude-project-config.json**: 프로젝트 설정

---

## 🔄 개발 히스토리

### 2024-02-11
1. **아키텍처 설계**: FastAPI + React 구조 설계
2. **1단계 구현 결정**: Streamlit으로 전환
3. **CSV 처리**: 업로드, 검증, 전처리 구현
4. **시각화**: Plotly 차트 6종 구현
5. **후회 점수**: 7가지 요소 알고리즘 구현
6. **OpenAI 통합**: GPT-4o-mini API 연결
7. **문서 업데이트**: 현재 구조 반영

### 2024-02-12 (오전)
1. **수익 모델 구현**: Buy Me a Coffee + Google AdSense
   - Buy Me a Coffee 버튼 (사이드바)
   - Google AdSense 광고 영역 (후회 점수 ↔ AI 분석 사이)
   - 설정 가이드 및 플레이스홀더 추가

### 2024-02-12 (오후)
2. **수동 입력 기능 구현** (2단계)
   - 자동 필요도 계산 알고리즘 추가 (csv_processor.py)
   - 수동 입력 폼 UI 구현 (app.py)
   - 다중 항목 누적 입력 기능
   - 탭 순서 변경 (수동 입력 우선)

3. **Google OAuth 로그인 시스템 구현** (3단계)
   - utils/auth.py 생성 (7개 함수)
   - Google OAuth 2.0 통합
   - 사용 횟수 제한 (무료 5회)
   - 로컬 JSON 사용자 데이터 저장
   - 로그인/로그아웃 UI
   - 구독 유도 화면 (결제 UI만)
   - **발견된 버그**: 사용 횟수 중복 카운트 (수정 필요)

### 2024-02-14
1. **사용 횟수 중복 카운트 버그 수정** ✅
   - `new_analysis` 플래그 패턴으로 해결
   - upload_csv(), manual_input_form()에서 설정 → main()에서 소비 후 리셋

2. **스마트 인사이트 기능 추가** ✅
   - 소비패턴 분류, 유사 사용자 재구매율, 장기 저축 효과, 추천 구매목록 TOP 5
   - openai_service.py에 `build_smart_insights_prompt()`, `generate_smart_insights()` 추가
   - app.py에 `prepare_smart_insights_data()`, `display_savings_calculator()` 추가
   - 추천 TOP 5: 실제 브랜드+모델명 + 쿠팡 검색 링크

3. **AI 분석 통합** ✅
   - 기존 2개 분석 (심리 분석 + 스마트 인사이트) → 1개 통합 (`display_ai_analysis()`)
   - 버튼 1개로 2회 API 호출 동시 실행, 결과 합산 표시

4. **로그인 세션 유지** ✅
   - auth.py에 `save_session()`, `load_session()`, `clear_session()` 추가
   - 새로고침 시 data/session.json에서 자동 로그인 복원

5. **UI 개선** ✅
   - 헤더: "1단계~7단계" 제거 → 깔끔한 한국어 (데이터 입력, 데이터 미리보기, 카테고리 분석 등)
   - 불필요한 이모지 정리

6. **CSV 형식 통일** ✅
   - 새 형식: 날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도 (수동 입력과 동일)
   - csv_processor.py: `validate_csv()`, `process_csv_data()` 두 형식 모두 지원
   - sample_purchases.csv 새 형식으로 업데이트
   - 기존 CSV 형식(필요도 직접 입력) 하위 호환 유지

---

## ⚙️ 개발 환경

### Python 버전
- Python 3.10+

### 주요 패키지 버전
```
streamlit==1.31.0
pandas==2.2.0
numpy==1.26.0
plotly==5.18.0
openai==1.10.0
python-dotenv==1.0.0
python-dateutil==2.8.2

# Google OAuth (3단계)
google-auth-oauthlib==1.2.0
google-auth==2.27.0
```

### IDE
- VS Code (추천)
- 또는 PyCharm

---

## 🤝 협업 가이드

### 코드 스타일
- PEP 8 준수
- 독스트링 포함
- 타입 힌트 사용 (선택)

### Git 커밋 메시지
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 코드
```

### 브랜치 전략
```
main        → 프로덕션
develop     → 개발
feature/*   → 기능 개발
```

---

## 📞 참고 링크

- **OpenAI API**: https://platform.openai.com/
- **Streamlit 문서**: https://docs.streamlit.io/
- **Plotly 문서**: https://plotly.com/python/
- **pandas 문서**: https://pandas.pydata.org/docs/

---

## 📌 중요 메모

### OpenAI API 키
- ✅ 발급 완료
- ✅ $5 충전 (약 16,000회 분석 가능)
- ✅ 자동충전 OFF

### 해커톤 조건
1. ✅ 실제로 작동하는 프로덕트 구현
2. 🔄 서비스 소개 (문서 준비됨)
3. 🔄 작동 시연 영상 제출
4. ✅ OpenAI API 1개 이상 활용

---

**마지막 업데이트**: 2024-02-14
**버전**: 1.5.0
**상태**: MVP + 수동입력 + OAuth + 스마트 인사이트 + UI 개선 + CSV 형식 통일 완료

---

## 💬 Claude에게

이 파일을 읽으면 프로젝트의 전체 컨텍스트를 이해할 수 있습니다.
- 현재 구조는 **Streamlit 올인원 앱**입니다 (FastAPI+React 아님)
- **구현 완료**: MVP + 수동 입력 + OAuth + 스마트 인사이트 + UI 개선 + CSV 통일
- **해결 완료**: 사용 횟수 중복 카운트 버그 (`new_analysis` 플래그), 로그인 세션 유지
- **다음 단계**: DB 설계 (Phase 4) → Git Commit & 배포 (Phase 5) → 해커톤 제출
- 코드 수정 시 **utils/ 모듈 구조**를 유지하세요
- OpenAI API, Google OAuth 모두 **환경 변수(.env)** 관리
- CSV는 **두 형식** 모두 지원 (새 형식: 고민기간+재구매의향 / 기존 형식: 필요도 직접)

질문이 있으면 이 파일을 먼저 참조하세요!

---

## 🚨 재시작 시 우선 작업

### 다음 단계 (Phase 4)
1. **DB 설계**: Plan 에이전트 활용
   - users, purchases, analyses, ai_usage_logs 테이블
   - 필요 데이터 검토 및 스키마 설계

### 최종 단계 (Phase 5)
2. **Git Commit & 배포**: Streamlit Cloud
   - .gitignore 검토 (data/session.json 제외 추가)
   - Git push
   - Streamlit Cloud 배포
   - OAuth redirect_uri 업데이트
3. **해커톤 제출 준비**: 시연 영상 제작 (2분)
