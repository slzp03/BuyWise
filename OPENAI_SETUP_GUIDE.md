# OpenAI API 설정 가이드

## 📋 목차
1. [OpenAI API 키 발급](#1-openai-api-키-발급)
2. [API 키 설정](#2-api-키-설정)
3. [비용 및 사용량 관리](#3-비용-및-사용량-관리)
4. [문제 해결](#4-문제-해결)

---

## 1. OpenAI API 키 발급

### 1.1 OpenAI 계정 생성

1. **OpenAI 플랫폼 접속**
   - URL: https://platform.openai.com/signup

2. **계정 생성**
   - 이메일 또는 Google/Microsoft 계정으로 가입
   - 전화번호 인증 필요

3. **결제 정보 등록** (필수)
   - API 사용을 위해서는 신용카드 등록 필요
   - 무료 크레딧이 제공될 수 있음 (신규 계정)

### 1.2 API 키 생성

1. **API 키 페이지 접속**
   - URL: https://platform.openai.com/api-keys
   - 또는 대시보드 → "API keys" 메뉴 클릭

2. **새 API 키 생성**
   - "Create new secret key" 버튼 클릭
   - 키 이름 입력 (예: "AI-Purchase-Analyzer")
   - "Create secret key" 클릭

3. **API 키 복사**
   - ⚠️ **중요**: 생성된 키는 한 번만 표시됩니다!
   - 반드시 안전한 곳에 복사해두세요
   - 형식: `sk-proj-...` 또는 `sk-...`

---

## 2. API 키 설정

### 방법 1: .env 파일 사용 (권장)

1. **프로젝트 루트에 `.env` 파일 생성**
   ```
   프로젝트 폴더/
   ├── .env          ← 여기에 생성
   ├── app.py
   ├── requirements.txt
   └── ...
   ```

2. **`.env` 파일에 API 키 추가**
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

   예시:
   ```env
   OPENAI_API_KEY=sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
   ```

3. **앱 재시작**
   ```bash
   # Ctrl+C로 중단 후 다시 실행
   streamlit run app.py
   ```

### 방법 2: 환경 변수로 설정

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-proj-your-api-key"
streamlit run app.py
```

#### Windows (CMD)
```cmd
set OPENAI_API_KEY=sk-proj-your-api-key
streamlit run app.py
```

#### Mac/Linux
```bash
export OPENAI_API_KEY="sk-proj-your-api-key"
streamlit run app.py
```

### 선택사항: 모델 및 파라미터 설정

`.env` 파일에 추가 설정:

```env
# 기본값
OPENAI_API_KEY=sk-proj-your-api-key

# 사용할 모델 (기본: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Temperature (0-2, 기본: 0.7)
# 낮을수록 일관성↑, 높을수록 창의성↑
OPENAI_TEMPERATURE=0.7

# 최대 토큰 (기본: 800)
OPENAI_MAX_TOKENS=800
```

---

## 3. 비용 및 사용량 관리

### 3.1 gpt-4o-mini 요금 (2024년 기준)

| 항목 | 가격 |
|------|------|
| **입력 토큰** | $0.15 / 1M 토큰 |
| **출력 토큰** | $0.60 / 1M 토큰 |

### 3.2 예상 비용

**1회 AI 분석 기준**:
- 평균 입력 토큰: ~600 토큰
- 평균 출력 토큰: ~400 토큰
- **예상 비용**: $0.0003 (약 ₩0.4)

**100회 분석 시**:
- 총 비용: $0.03 (약 ₩40)

### 3.3 사용량 확인

1. **OpenAI 대시보드 접속**
   - URL: https://platform.openai.com/usage

2. **사용량 확인**
   - 일별/월별 사용량 확인
   - 토큰 사용량 및 비용 확인

### 3.4 사용 한도 설정

1. **한도 설정 페이지 접속**
   - URL: https://platform.openai.com/account/billing/limits

2. **월별 한도 설정**
   - "Hard limit" 설정 (예: $5)
   - 한도 초과 시 API 호출 자동 차단

---

## 4. 문제 해결

### 문제 1: "OPENAI_API_KEY가 설정되지 않았습니다"

**원인**:
- `.env` 파일이 없거나 올바른 위치에 없음
- API 키가 비어있음

**해결**:
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. 파일 내용 확인:
   ```env
   OPENAI_API_KEY=sk-proj-...  (실제 키 입력)
   ```
3. 앱 재시작

### 문제 2: "OPENAI_API_KEY 형식이 올바르지 않습니다"

**원인**:
- API 키가 `sk-`로 시작하지 않음

**해결**:
1. API 키 재확인
2. 공백이나 따옴표 없이 입력
   ```env
   # 올바른 예시
   OPENAI_API_KEY=sk-proj-AbCdEf...

   # 잘못된 예시
   OPENAI_API_KEY="sk-proj-AbCdEf..."  ❌ (따옴표 제거)
   OPENAI_API_KEY= sk-proj-AbCdEf...   ❌ (앞 공백 제거)
   ```

### 문제 3: "API 호출 실패" 에러

**가능한 원인**:

1. **API 키 만료 또는 무효**
   - 해결: OpenAI 플랫폼에서 새 키 발급

2. **잔액 부족**
   - 해결: https://platform.openai.com/account/billing 에서 크레딧 충전

3. **사용 한도 초과**
   - 해결: 한도 설정 확인 및 조정

4. **네트워크 오류**
   - 해결: 인터넷 연결 확인 및 재시도

### 문제 4: ".env 파일이 읽히지 않음"

**Windows 사용자**:
- 파일 이름이 `.env.txt`가 아닌 `.env`인지 확인
- Windows 탐색기에서 "파일 확장명" 표시 활성화

**해결**:
1. VS Code나 메모장으로 파일 생성
2. "다른 이름으로 저장" → 파일 이름: `.env`
3. 인코딩: UTF-8

### 문제 5: "Rate limit exceeded" 에러

**원인**:
- 분당 요청 횟수 초과 (기본: 분당 3회)

**해결**:
1. 잠시 기다린 후 재시도
2. Tier 업그레이드 고려
   - URL: https://platform.openai.com/account/limits

---

## 5. 보안 주의사항

### ⚠️ 절대 하지 말아야 할 것

1. **API 키를 Git에 커밋하지 마세요**
   - `.gitignore`에 `.env` 추가 (이미 포함됨)
   - 공개 저장소에 업로드 금지

2. **API 키를 다른 사람과 공유하지 마세요**
   - 개인 계정의 API 키는 개인만 사용

3. **코드에 직접 하드코딩하지 마세요**
   ```python
   # 잘못된 예시 ❌
   api_key = "sk-proj-AbCdEf..."

   # 올바른 예시 ✅
   api_key = os.getenv('OPENAI_API_KEY')
   ```

### ✅ 권장 사항

1. **정기적으로 API 키 갱신**
   - 3-6개월마다 새 키 발급

2. **사용량 모니터링**
   - 주기적으로 대시보드 확인

3. **한도 설정**
   - 예상치 못한 과금 방지

---

## 6. 추가 리소스

- **OpenAI 공식 문서**: https://platform.openai.com/docs
- **API 레퍼런스**: https://platform.openai.com/docs/api-reference
- **요금 안내**: https://openai.com/pricing
- **상태 페이지**: https://status.openai.com

---

## 7. 빠른 체크리스트

시작하기 전 확인:

- [ ] OpenAI 계정 생성
- [ ] 결제 정보 등록
- [ ] API 키 발급 완료
- [ ] `.env` 파일 생성
- [ ] `.env`에 API 키 입력
- [ ] 앱 재시작
- [ ] "🤖 AI 심리 분석 생성" 버튼 클릭 테스트

---

**궁금한 점이 있으면 OpenAI 공식 문서를 참고하거나, 프로젝트 이슈를 남겨주세요!**

**업데이트**: 2024-02-11
