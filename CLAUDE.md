# Claude 프로젝트 컨텍스트

> Claude가 프로젝트를 이해하고 작업을 이어갈 수 있는 전체 컨텍스트.

---

## 프로젝트 개요

**AI 구매 후회 방지 분석기** (Smart Purchase Analyzer)

- 해커톤 제출용 MVP
- CSV/수동 입력 구매 내역 분석 → 후회 점수 계산 → AI 심리 분석
- 충동 구매 방지 및 소비 습관 개선
- 다국어 지원 (한국어, 일본어)

---

## 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| 웹 프레임워크 | Streamlit 1.31+ | 올인원 웹앱 |
| 데이터 처리 | pandas 2.2+, numpy 1.26+ | CSV 파싱 및 분석 |
| 시각화 | Plotly 5.18+ | 인터랙티브 차트 6종 |
| AI | OpenAI SDK (GPT-4o-mini) | 소비 심리 분석 |
| DB | Supabase (PostgreSQL) | 사용자/구매/분석 이력 저장 |
| 인증 | Google OAuth 2.0 | 로그인, 사용 횟수 관리 |
| 배포 | Streamlit Cloud (예정) | GitHub 연동 자동 배포 |

---

## 디렉토리 구조

```
project/
├── app.py                    # 메인 Streamlit 앱 (1550+ 줄)
├── utils/
│   ├── __init__.py
│   ├── csv_processor.py      # CSV 검증/전처리, 일본어 CSV 지원
│   ├── visualizer.py         # Plotly 차트 6종
│   ├── regret_calculator.py  # 후회 점수 7요소 알고리즘 + 식비 특별 로직
│   ├── openai_service.py     # GPT-4o-mini 심리분석 + 스마트인사이트
│   ├── auth.py               # Google OAuth + DB/JSON fallback
│   ├── database.py           # Supabase CRUD (users, purchases, analyses, ai_usage_logs)
│   └── translations.py       # 다국어 번역 (ko/ja) + CSV 컬럼 매핑
├── data/
│   └── .gitkeep              # users.json, session.json은 Git 제외
├── supabase_schema.sql       # DB 테이블 생성 SQL (Supabase SQL Editor에서 실행)
├── sample_purchases.csv      # 샘플 데이터 35건 (후회성 구매 포함)
├── requirements.txt          # 패키지 의존성
├── .env                      # 환경 변수 (Git 제외)
├── .gitignore
├── CLAUDE.md                 # 이 파일
└── README.md
```

---

## 환경 변수 (.env)

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
```

---

## 핵심 기능

### 1. 후회 점수 계산 (7요소, 100점 만점)
| 요소 | 최대 점수 | 설명 |
|------|-----------|------|
| 필요도-사용빈도 갭 | 30 | 핵심 지표 |
| 금액 가중치 | 20 | 고가 제품 |
| 반복 구매 | 15 | 같은 카테고리 반복 |
| 시간 경과 | 15 | 오래됐는데 안 쓰는 경우 |
| 최근성 | 10 | 최근 충동 구매 |
| 새벽 구매 | 10 | 새벽 시간대 |
| 충동 패턴 | 10 | 짧은 시간 내 여러 구매 |

- 식비 카테고리: 필요도갭/시간경과 점수를 0으로 처리 (먹으면 끝이므로)
- 점수 해석: 0-20 매우만족, 21-35 만족, 36-50 보통, 51-65 아쉬움, 66-100 후회

### 2. AI 통합 분석 (GPT-4o-mini)
- 버튼 1개로 2회 API 동시 호출:
  - **심리 분석**: 소비 패턴 요약, 후회 원인 3가지, 개선 방안, 월간 목표
  - **스마트 인사이트**: 소비패턴 분류, 재구매율, 저축 효과, 추천 TOP 5 (쿠팡 링크), 절약 추천 TOP 5
- 일본어 모드: 프롬프트/응답 전부 일본어, Amazon.co.jp 링크
- 비용: 1회 약 $0.0006

### 3. Supabase DB (Phase 4 완료)
4개 테이블:
- `users`: 사용자 정보 (OAuth, 사용횟수, 구독, 언어)
- `purchases`: 구매 이력 (CSV/수동 입력 영구 저장)
- `analyses`: AI 분석 결과 이력
- `ai_usage_logs`: API 토큰 사용량/비용 추적

DB 불가 시 기존 JSON 방식 자동 fallback.

### 4. 다국어 (한국어/일본어)
- `translations.py`: `t(key, lang)` 헬퍼 함수로 UI 텍스트 전환
- CSV: 일본어 컬럼명 자동 감지/변환 (`日付`→`날짜`, `カテゴリ`→`카테고리` 등)
- 사이드바에서 언어 전환 (로그인 전/후 모두)

### 5. 수동 입력
- 고민기간 + 재구매의향 → 필요도 자동 계산
- 다중 항목 누적 입력 후 일괄 분석
- CSV 파이프라인 재사용

### 6. Google OAuth + 사용 횟수 제한
- 무료 5회, 프리미엄 무제한
- 세션 유지 (새로고침 시 자동 로그인)
- `new_analysis` 플래그로 중복 카운트 방지

### 7. 수익 모델
- Buy Me a Coffee (사이드바)
- Google AdSense (후회 점수 ↔ AI 분석 사이)

---

## 주요 코드 위치

### app.py
- `main()` - OAuth → 사용 횟수 → DB 연동 → 데이터 입력 → 분석
- `upload_csv()` / `manual_input_form()` - 데이터 입력 + DB 저장
- `display_ai_analysis()` - AI 분석 + DB에 결과/사용량 저장
- `display_analysis_history()` - 사이드바 분석 이력 (DB)

### utils/database.py
- `get_or_create_user()` - 로그인 시 DB 유저 생성/조회
- `save_purchases()` / `load_purchases()` - 구매 이력 CRUD
- `save_analysis()` / `load_analyses()` - 분석 결과 CRUD
- `log_ai_usage()` - API 사용량 기록

### utils/auth.py
- DB 우선, JSON fallback 패턴
- `check_usage_limit()` / `increment_usage_count()` - 통합 인터페이스

### utils/regret_calculator.py
- `is_food_category()` - 식비 감지
- `calculate_regret_score()` - 7요소 점수 계산
- `add_regret_scores_to_dataframe()` - DataFrame에 점수 추가

### utils/openai_service.py
- `generate_ai_feedback()` - 심리 분석 (language 파라미터)
- `generate_smart_insights()` - 스마트 인사이트 + 절약 추천

---

## CSV 형식

### 권장 형식 (수동 입력과 동일)
```csv
날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도
2024-01-15,전자제품,무선이어폰,89000,7,예,5
```
- 필요도는 고민기간+재구매의향으로 자동 계산

### 기존 형식 (하위 호환)
```csv
날짜,카테고리,상품명,금액,필요도,사용빈도
```

### 일본어 CSV
```csv
日付,カテゴリ,商品名,金額,検討期間,再購入意向,使用頻度
```

---

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
# http://localhost:8501
```

---

## Git 정보

- **Repository**: https://github.com/slzp03/BuyWise
- **Branch**: master
- **커밋 스타일**: `feat:`, `fix:`, `docs:`, `refactor:`

---

## 완료된 Phase

| Phase | 내용 | 상태 |
|-------|------|------|
| 1 | MVP (CSV, 후회점수, 시각화, AI분석) | 완료 |
| 2 | 수동 입력 (자동 필요도 계산) | 완료 |
| 3 | Google OAuth + 사용 횟수 제한 | 완료 |
| 3.5 | 스마트 인사이트 + UI 개선 + 일본어 | 완료 |
| 4 | Supabase DB 통합 (4개 테이블) | 완료 |

## 다음 단계

### Phase 5: 배포 (해커톤 제출)
- [ ] Streamlit Cloud 배포
- [ ] Google OAuth redirect_uri 업데이트
- [ ] 시연 영상 제작

### Phase 6: 고급 기능 (해커톤 이후)
- [ ] FastAPI 백엔드 분리
- [ ] React 프론트엔드
- [ ] Stripe 결제 통합

---

## Claude에게

- **Streamlit 올인원 앱** (FastAPI+React 아님)
- 코드 수정 시 **utils/ 모듈 구조** 유지
- 모든 API 키는 **.env**로 관리
- DB는 **Supabase 우선, JSON fallback**
- UI 텍스트는 **t(key, lang)** 함수 사용
- CSV는 **한국어/일본어/기존 형식** 모두 지원

---

**마지막 업데이트**: 2026-02-14
**버전**: 2.0.0
**상태**: MVP + 수동입력 + OAuth + AI분석 + 다국어 + Supabase DB 완료
