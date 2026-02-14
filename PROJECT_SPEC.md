# AI 구매 후회 방지 분석기 - 프로젝트 명세서

## 프로젝트 정보
- **프로젝트명**: AI 구매 후회 방지 분석기 (AI Purchase Regret Analyzer)
- **목적**: 해커톤 제출용 MVP
- **개발 기간**: 2-3일 (빠른 프로토타이핑)
- **타겟 사용자**: 충동 구매 후회를 경험하는 20-30대

---

## 핵심 기능 명세

### 1. CSV 업로드 기능
**요구사항**:
- 사용자가 구매 내역 CSV 파일을 업로드
- 드래그앤드롭 + 파일 선택 두 가지 방식 지원
- 파일 크기 제한: 5MB
- 지원 형식: CSV only

**검증 규칙**:
- 필수 컬럼: 날짜, 카테고리, 금액, 필요도, 사용빈도
- 날짜 형식: YYYY-MM-DD
- 금액: 숫자형 (0 이상)
- 필요도/사용빈도: 1-5 정수

**에러 처리**:
- 잘못된 형식 → 사용자에게 샘플 CSV 제공
- 누락된 컬럼 → 구체적인 오류 메시지
- 파일 초과 → "5MB 이하 파일만 업로드 가능합니다"

---

### 2. 후회 점수 계산 로직

#### 알고리즘 (v1)
```
후회 점수 = Σ(각 구매 항목의 후회도) / 총 구매 건수 * 100

개별 항목 후회도 계산:
- 필요도-사용빈도 갭: gap = |필요도 - 사용빈도|
- 금액 가중치: weight = log(금액 / 1000)
- 시간 감쇠: time_factor = 1 - (경과일수 / 365) * 0.3
- 항목 후회도 = gap * weight * time_factor
```

#### 점수 구간별 해석
- **0-20점**: 🟢 매우 합리적인 소비
- **21-40점**: 🟡 양호한 소비 패턴
- **41-60점**: 🟠 주의 필요
- **61-80점**: 🔴 개선 필요
- **81-100점**: 🔴 위험 수준

#### 카테고리별 분석
- 각 카테고리별 후회 점수 계산
- 상위 3개 후회 카테고리 표시
- 카테고리별 총 지출 금액

---

### 3. OpenAI API 통합

#### 입력 데이터
```json
{
  "overall_regret_score": 65,
  "total_purchases": 25,
  "total_amount": 1250000,
  "regret_ratio": 40,
  "top_regret_categories": [
    {"name": "전자제품", "score": 85, "amount": 450000},
    {"name": "의류", "score": 72, "amount": 320000},
    {"name": "취미", "score": 68, "amount": 180000}
  ],
  "user_profile": {
    "avg_purchase_amount": 50000,
    "most_frequent_category": "식비",
    "impulse_buy_count": 10
  }
}
```

#### OpenAI 프롬프트 템플릿
```
Role: 당신은 소비 심리 전문가이자 재무 상담가입니다.

Context:
사용자의 최근 구매 데이터를 분석한 결과입니다:
- 전체 후회 점수: {overall_regret_score}/100
- 총 구매 건수: {total_purchases}건
- 총 지출 금액: {total_amount:,}원
- 후회 구매 비율: {regret_ratio}%
- 주요 후회 카테고리: {top_regret_categories}

Task:
다음 형식으로 친근하고 공감적인 톤으로 응답하세요:

## 📊 당신의 소비 패턴
(2-3문장으로 전체적인 소비 패턴 요약)

## 🔍 후회 구매의 주요 원인
1. [카테고리명]: [구체적인 원인 분석]
2. [카테고리명]: [구체적인 원인 분석]
3. [카테고리명]: [구체적인 원인 분석]

## 💡 실천 가능한 개선 방안
1. [즉시 실천 가능한 구체적 팁]
2. [습관 개선 제안]
3. [심리적 접근 방법]

## 🎯 이번 달 목표
(SMART 기준 목표 1개 제안)

Constraints:
- 총 300자 이내
- 비난하지 않는 톤
- 실천 가능한 조언만 제공
- 이모지 적절히 사용
```

#### API 설정
```python
{
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1.0,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.3
}
```

---

### 4. 결과 시각화

#### 대시보드 구성
1. **헤더 섹션**
   - 전체 후회 점수 (큰 게이지 차트)
   - 총 지출 금액
   - 분석 기간

2. **카테고리 분석**
   - 파이 차트: 카테고리별 지출 비율
   - 바 차트: 카테고리별 후회 점수

3. **타임라인**
   - 월별 지출 추이
   - 후회 구매 발생 패턴

4. **AI 인사이트**
   - OpenAI 생성 분석 문구
   - 개선 방안 카드

5. **상세 테이블**
   - 모든 구매 항목 리스트
   - 정렬 및 필터링 기능

---

## 기술 스펙

### 백엔드
```python
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pandas==2.2.0
openai==1.10.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.0
httpx==0.26.0
```

### 프론트엔드
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dropzone": "^14.2.3",
    "recharts": "^2.10.0",
    "axios": "^1.6.0",
    "react-query": "^3.39.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

### 환경 변수
```env
# .env
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
MAX_FILE_SIZE_MB=5
ALLOWED_ORIGINS=http://localhost:5173
RATE_LIMIT_PER_MINUTE=10

# 확장용 (MVP에서는 미사용)
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-secret-key
STRIPE_API_KEY=sk_test_...
```

---

## 데이터 모델

### Purchase (구매 항목)
```python
{
    "date": "2024-01-15",
    "category": "전자제품",
    "product_name": "무선이어폰",
    "amount": 89000,
    "necessity_score": 3,  # 1-5
    "usage_frequency": 5,  # 1-5
    "regret_score": 12.5,  # 계산된 값
    "days_since_purchase": 28
}
```

### AnalysisResult (분석 결과)
```python
{
    "session_id": "uuid-v4",
    "created_at": "2024-02-11T10:30:00Z",
    "overall_regret_score": 65,
    "total_purchases": 25,
    "total_amount": 1250000,
    "regret_ratio": 40,
    "category_breakdown": [
        {
            "category": "전자제품",
            "count": 5,
            "total_amount": 450000,
            "avg_regret_score": 85
        }
    ],
    "ai_insight": "...",  # OpenAI 생성 문구
    "recommendations": ["...", "...", "..."]
}
```

---

## API 스펙

### POST /api/analyze
**Request**:
```
Content-Type: multipart/form-data
Body: file=@purchases.csv
```

**Response (200)**:
```json
{
    "success": true,
    "data": {
        "session_id": "abc-123",
        "overall_regret_score": 65,
        "analysis": { ... },
        "ai_insight": "..."
    }
}
```

**Response (400)**:
```json
{
    "success": false,
    "error": {
        "code": "INVALID_CSV_FORMAT",
        "message": "필수 컬럼이 누락되었습니다: 필요도",
        "details": {
            "required": ["날짜", "카테고리", "금액", "필요도", "사용빈도"],
            "missing": ["필요도"]
        }
    }
}
```

---

## 테스트 시나리오

### 1. CSV 업로드
- ✅ 정상 CSV 파일 업로드
- ✅ 잘못된 형식 파일 업로드 → 에러 메시지
- ✅ 5MB 초과 파일 → 크기 제한 메시지
- ✅ 빈 파일 → 에러 핸들링

### 2. 후회 점수 계산
- ✅ 다양한 시나리오의 CSV 데이터로 점수 검증
- ✅ 엣지 케이스: 모든 항목이 완벽한 구매
- ✅ 엣지 케이스: 모든 항목이 후회 구매

### 3. OpenAI API
- ✅ 정상 응답 수신
- ✅ API 키 없음 → 에러 핸들링
- ✅ 타임아웃 → 재시도 로직
- ✅ Rate limit 초과 → 사용자 알림

---

## 배포 전략

### MVP 배포
- **프론트엔드**: Vercel (자동 배포)
- **백엔드**: Railway 또는 Render (무료 티어)
- **도메인**: Vercel 기본 도메인 사용

### 배포 체크리스트
- [ ] 환경 변수 설정 (.env → 배포 플랫폼)
- [ ] CORS 설정 (프로덕션 도메인 추가)
- [ ] OpenAI API 키 검증
- [ ] 에러 로깅 설정
- [ ] 헬스체크 엔드포인트 테스트

---

## 성공 지표 (해커톤)

### 데모 시연 포인트
1. ✨ **UI/UX**: 5초 이내에 CSV 업로드 → 결과 표시
2. 🤖 **AI 활용**: OpenAI 생성 인사이트 강조
3. 📊 **시각화**: 직관적인 차트 및 대시보드
4. 💡 **가치 제안**: "이 서비스가 실제 문제를 어떻게 해결하는가"
5. 🚀 **확장성**: 구독 모델 로드맵 설명

### 심사위원 질문 대비
- **"왜 이 서비스가 필요한가?"** → 충동 구매 통계, 타겟 사용자 페인포인트
- **"수익 모델은?"** → 프리미엄 구독, 분석 횟수 제한
- **"기술적 차별점은?"** → OpenAI 활용한 개인화 분석
- **"확장 계획은?"** → 자동 카드 연동, ML 예측 모델

---

## 참고 자료
- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- OpenAI API 문서: https://platform.openai.com/docs
- Recharts (차트 라이브러리): https://recharts.org/
