# AI 구매 후회 방지 분석기 - 시스템 아키텍처 (MVP)

## 프로젝트 개요
해커톤 제출용 AI 기반 구매 후회 방지 분석 웹앱
- 사용자의 구매 데이터(CSV)를 분석하여 후회 점수를 계산
- OpenAI API를 활용한 개인화된 소비 심리 분석 제공
- Streamlit 기반 빠른 프로토타이핑
- 추후 유료 구독 모델로 확장 가능한 구조

---

## 1. 전체 시스템 구조

### 아키텍처 개요
```
[사용자] ←→ [Streamlit 웹앱] ←→ [OpenAI API]
                 ↓
            [유틸리티 모듈]
                 ↓
            [데이터 처리]
```

**Streamlit 올인원 앱**:
- 프론트엔드 + 백엔드가 하나의 Python 앱으로 통합
- 별도의 REST API 서버 불필요
- 빠른 개발 및 배포에 최적화

---

## 2. 디렉토리 구조

### 실제 구현된 구조
```
project/
├── app.py                       # 메인 Streamlit 애플리케이션
├── utils/                       # 유틸리티 모듈
│   ├── __init__.py
│   ├── csv_processor.py         # CSV 파싱 및 검증
│   ├── visualizer.py            # Plotly 차트 생성
│   ├── regret_calculator.py     # 후회 점수 계산 로직
│   └── openai_service.py        # OpenAI API 호출 로직
├── requirements.txt             # Python 패키지 의존성
├── .env                         # 환경 변수 (API 키 등)
├── .env.example                 # 환경 변수 템플릿
├── .gitignore                   # Git 제외 파일
├── sample_purchases.csv         # 샘플 데이터
├── README.md                    # 프로젝트 소개
├── QUICKSTART.md                # 빠른 시작 가이드
├── ARCHITECTURE.md              # 이 파일
├── PROJECT_SPEC.md              # 프로젝트 명세서
├── TECH_STACK.md                # 기술 스택 상세
├── REGRET_SCORE_GUIDE.md        # 후회 점수 계산 가이드
├── OPENAI_SETUP_GUIDE.md        # OpenAI API 설정 가이드
└── API_KEY_SETUP.md             # API 키 빠른 설정

docs/ (선택사항)                 # 추가 문서
tests/ (선택사항)                # 테스트 코드
```

---

## 3. 기술 스택

### 웹 프레임워크
- **Streamlit 1.31+**: Python 기반 웹앱 프레임워크
  - 장점: 빠른 프로토타이핑, 자동 UI 생성, 내장 위젯
  - 단점: 커스터마이징 제한적, 대규모 앱에는 비효율적

### 데이터 처리
- **pandas 2.2+**: CSV 파싱 및 데이터 분석
- **numpy 1.26+**: 수치 계산

### 시각화
- **Plotly 5.18+**: 인터랙티브 차트 생성
  - 게이지 차트, 파이 차트, 바 차트, 산점도 등

### AI 통합
- **OpenAI Python SDK 1.10+**: GPT-4o-mini API 호출
- **python-dotenv 1.0+**: 환경 변수 관리

---

## 4. 앱 구조 (app.py)

### 페이지 섹션 (단일 페이지 앱)
```python
app.py
├── 헤더: 프로젝트 소개
├── 사이드바: CSV 형식 가이드, 샘플 다운로드
├── 1단계: CSV 파일 업로드
├── 2단계: 업로드된 데이터 확인
├── 3단계: 카테고리별 분석
├── 4단계: 추가 분석 (금액 분포, 월별 추이, 필요도 vs 사용빈도)
├── 5단계: 후회 점수 분석 ⭐ 핵심 기능
│   ├── 전체 후회 점수 게이지
│   ├── 등급별 분포
│   ├── 후회 점수 TOP 10
│   ├── 만족도 TOP 10
│   └── 요인별 기여도 분석
├── 6단계: AI 소비 심리 분석 🤖 OpenAI 통합
│   ├── API 키 확인
│   ├── AI 분석 생성 버튼
│   ├── 프롬프트 기반 피드백 생성
│   └── 토큰 사용량 및 비용 표시
└── 7단계: 기본 인사이트
```

### 주요 함수
```python
# 초기화
init_session_state()              # 세션 상태 초기화

# UI 표시
display_header()                  # 헤더
display_sidebar()                 # 사이드바

# 데이터 처리
upload_csv()                      # CSV 업로드 및 검증
display_raw_data(df)              # 데이터 테이블 표시
display_category_analysis(df)     # 카테고리 분석
display_additional_charts(df)     # 추가 차트
display_regret_score_analysis(df) # 후회 점수 분석
display_ai_analysis(df)           # AI 심리 분석
display_insights(df)              # 기본 인사이트
```

---

## 5. 유틸리티 모듈

### csv_processor.py
**역할**: CSV 파일 검증 및 전처리

**주요 함수**:
- `validate_csv(df)`: CSV 데이터 검증 (필수 컬럼, 데이터 타입)
- `process_csv_data(df)`: 데이터 전처리 (날짜 변환, 경과 일수 계산)
- `get_category_summary(df)`: 카테고리별 집계
- `get_basic_stats(df)`: 기본 통계 계산

### visualizer.py
**역할**: Plotly 차트 생성

**주요 함수**:
- `create_category_chart(df, type)`: 카테고리 차트 (파이/바)
- `create_amount_chart(df)`: 금액 분포 히스토그램
- `create_timeline_chart(df)`: 월별 지출 추이 (이중 축)
- `create_necessity_usage_scatter(df)`: 필요도 vs 사용빈도 산점도

### regret_calculator.py
**역할**: 후회 점수 계산 (핵심 로직)

**계산 요소** (총 7가지):
1. **필요도-사용빈도 갭** (최대 30점) - 핵심 지표
2. **시간 경과** (최대 15점) - 오래됐는데 안 쓰는 경우
3. **금액 가중치** (최대 20점) - 고가 제품
4. **최근성** (최대 10점) - 최근 구매 충동성
5. **반복 구매** (최대 15점) - 같은 카테고리 반복
6. **새벽 구매** (최대 10점) - 새벽 시간대 충동 구매
7. **충동 패턴** (최대 10점) - 짧은 시간 내 여러 구매

**주요 함수**:
- `calculate_regret_score()`: 개별 항목 후회 점수 계산
- `add_regret_scores_to_dataframe(df)`: DataFrame에 점수 추가
- `get_regret_score_interpretation(score)`: 점수 해석 (등급, 메시지)
- `get_overall_regret_analysis(df)`: 전체 분석 요약

### openai_service.py
**역할**: OpenAI API 호출 및 AI 피드백 생성

**OpenAIService 클래스**:
- `__init__()`: API 키 확인 및 클라이언트 초기화
- `build_analysis_prompt()`: 프롬프트 생성
- `generate_ai_feedback()`: AI 분석 생성 (메인 함수)
- `generate_quick_tips()`: API 없이 기본 팁 제공

**프롬프트 구조**:
```
Role: 20년 경력 소비 심리 전문가
Context: 후회 점수, 카테고리 통계, 상위 후회 항목
Task: 4개 섹션 생성
  1. 소비 패턴 요약
  2. 주요 후회 원인 3가지
  3. 실천 가능한 개선 방안 3가지
  4. SMART 기준 월간 목표
Tone: 친근하고 공감적, 비난 없음
```

---

## 6. 데이터 흐름

### CSV 업로드 → 분석 결과 전체 흐름
```
1. [사용자] CSV 파일 업로드
      ↓
2. [Streamlit] st.file_uploader()로 파일 수신
      ↓
3. [csv_processor] validate_csv() → 검증
      ↓
4. [csv_processor] process_csv_data() → 전처리
      ↓
5. [regret_calculator] add_regret_scores_to_dataframe() → 후회 점수 계산
      ↓
6. [visualizer] create_*_chart() → 차트 생성
      ↓
7. [Streamlit] st.plotly_chart() → 차트 표시
      ↓
8. [사용자] "AI 분석 생성" 버튼 클릭
      ↓
9. [openai_service] generate_ai_feedback() → OpenAI API 호출
      ↓
10. [OpenAI GPT-4o-mini] 소비 심리 분석 생성
      ↓
11. [Streamlit] st.markdown() → AI 피드백 표시
      ↓
12. [사용자] 분석 결과 확인
```

### 세션 상태 관리
```python
st.session_state = {
    'processed_df': DataFrame,      # 처리된 데이터
    'ai_feedback': str,              # AI 생성 피드백
    'ai_usage': dict                 # 토큰 사용량
}
```

---

## 7. OpenAI API 통합

### 모델
- **gpt-4o-mini**: 비용 효율적, 빠른 응답
  - 입력: $0.15 / 1M 토큰
  - 출력: $0.60 / 1M 토큰
  - 1회 분석: 약 $0.0003 (₩0.4)

### API 호출 파라미터
```python
{
    "model": "gpt-4o-mini",
    "temperature": 0.7,        # 일관성과 창의성 균형
    "max_tokens": 800,         # 출력 길이 제한
    "frequency_penalty": 0.3,  # 반복 감소
    "presence_penalty": 0.3    # 다양성 증가
}
```

### 에러 핸들링
- API 키 없음 → 기본 팁 제공, 설정 안내
- API 호출 실패 → 에러 메시지, 재시도 안내
- 타임아웃 → 30초 제한

---

## 8. 확장 전략

### Phase 1: MVP (현재) ✅
- Streamlit 단일 앱
- CSV 업로드 + 즉시 분석
- 후회 점수 계산
- OpenAI 기반 심리 분석
- 세션 기반 (DB 없음)

### Phase 2: 베타 출시
- 사용자 인증 추가 (Streamlit Auth)
- SQLite/PostgreSQL 데이터베이스 도입
- 분석 이력 저장
- 대시보드 개선

### Phase 3: 유료 구독
- Stripe 결제 통합
- 구독 플랜 (무료/프리미엄)
- 사용량 제한 미들웨어

### Phase 4: 고급 기능
- FastAPI 백엔드 분리 (API 제공)
- React 프론트엔드 개발 (고급 UI)
- 자동 은행/카드 연동
- 머신러닝 예측 모델
- 모바일 앱

---

## 9. Streamlit vs FastAPI+React 비교

| 항목 | Streamlit (현재) | FastAPI+React (원래 설계) |
|------|-----------------|-------------------------|
| **개발 속도** | ⚡⚡⚡⚡⚡ 매우 빠름 | ⚡⚡ 느림 |
| **코드 복잡도** | 낮음 (단일 파일) | 높음 (분리된 구조) |
| **UI 커스터마이징** | 제한적 | 자유로움 |
| **확장성** | 중간 | 매우 높음 |
| **배포** | 간단 (Streamlit Cloud) | 복잡 (2개 서버) |
| **해커톤 적합성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **프로덕션 준비** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 왜 Streamlit을 선택했나?
1. **해커톤 목표**: 빠른 프로토타이핑이 최우선
2. **시연 중심**: UI가 있어야 데모 가능
3. **완성도**: 2-3일 내 완전히 동작하는 앱 완성
4. **확장 가능**: 추후 FastAPI로 전환 가능

---

## 10. 보안 및 성능

### 보안
- ✅ 환경 변수로 API 키 관리 (.env)
- ✅ .gitignore에 .env 포함
- ✅ 파일 타입/크기 검증 (CSV, 5MB)
- ✅ Rate limiting (분당 10회 제한 가능)

### 성능
- CSV 처리: pandas (충분히 빠름, ~1000행 기준 1초 미만)
- OpenAI API: 5-10초 응답 시간
- 차트 렌더링: Plotly (클라이언트 사이드)

---

## 11. 배포

### Streamlit Cloud (권장)
```bash
# 1. GitHub 저장소에 푸시
git push origin main

# 2. Streamlit Cloud 접속
https://share.streamlit.io

# 3. GitHub 저장소 연결
# 4. app.py 선택
# 5. 환경 변수 추가 (OPENAI_API_KEY)
# 6. Deploy 클릭
```

### 로컬 실행
```bash
# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py

# 브라우저 자동 실행: http://localhost:8501
```

---

## 12. 해커톤 심사 포인트

### 1. 실제 작동하는 프로덕트 ✅
- Streamlit 앱 완전 동작
- CSV 업로드 → 분석 → 결과 표시 전체 플로우

### 2. OpenAI API 활용 ✅
- GPT-4o-mini로 소비 심리 분석
- 프롬프트 엔지니어링 적용
- 실시간 AI 피드백 생성

### 3. 완성도 ✅
- 직관적인 UI/UX
- 에러 핸들링
- 반응형 디자인
- 샘플 데이터 제공

### 4. 비즈니스 가치 ✅
- 실제 문제 해결 (충동 구매 후회)
- 수익 모델 (구독 서비스 확장 가능)
- 시장 타겟 명확 (MZ세대)

### 5. 기술 스택 ✅
- 최신 Python 프레임워크 (Streamlit)
- AI 통합 (OpenAI)
- 데이터 과학 (pandas, plotly)
- 모듈화된 구조 (확장 가능)

---

## 다음 단계

1. ✅ 아키텍처 설계 완료 (Streamlit 구조)
2. ✅ 전체 기능 구현 완료
3. ✅ OpenAI API 통합 완료
4. 🔄 테스트 및 버그 수정
5. 🔄 시연 영상 제작
6. 🔄 해커톤 제출

---

**업데이트**: 2024-02-11
**버전**: 2.0.0 (Streamlit 구조로 전환)
