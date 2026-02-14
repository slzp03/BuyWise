# 🔑 OpenAI API 키 설정 - 빠른 가이드

## ⚡ 5분 안에 설정하기

### 1단계: API 키 발급 (2분)

1. **OpenAI 플랫폼 접속**
   ```
   https://platform.openai.com/api-keys
   ```

2. **로그인 또는 회원가입**
   - Google/Microsoft 계정으로 빠른 가입 가능

3. **"Create new secret key" 클릭**
   - 키 이름: "AI-Purchase-Analyzer"
   - 생성된 키 복사 (⚠️ 한 번만 표시됨!)

### 2단계: 프로젝트에 설정 (1분)

1. **`.env` 파일 열기**
   ```
   프로젝트 폴더/.env 파일
   ```

2. **API 키 입력**
   ```env
   OPENAI_API_KEY=sk-proj-여기에-복사한-키-붙여넣기
   ```

   예시:
   ```env
   OPENAI_API_KEY=sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
   ```

3. **저장** (Ctrl+S)

### 3단계: 앱 재시작 (1분)

1. **Streamlit 중지**
   - 터미널에서 `Ctrl+C`

2. **앱 재시작**
   ```bash
   streamlit run app.py
   ```

3. **AI 분석 테스트**
   - CSV 업로드 → "🤖 AI 심리 분석 생성" 버튼 클릭

---

## 📋 .env 파일 전체 예시

```env
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

# 선택사항 (기본값이 설정되어 있음)
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800
ENVIRONMENT=development
```

---

## ❓ 자주 묻는 질문

### Q1: API 키는 어디서 발급받나요?
**A**: https://platform.openai.com/api-keys

### Q2: API 키 발급에 비용이 드나요?
**A**: 키 발급은 무료입니다. 사용한 만큼만 과금됩니다.

### Q3: 1회 분석 비용은 얼마인가요?
**A**: 약 $0.0003 (₩0.4). 100회 사용해도 약 ₩40입니다.

### Q4: 신용카드를 등록해야 하나요?
**A**: 네, API 사용을 위해서는 결제 정보 등록이 필수입니다.

### Q5: .env 파일이 안 읽혀요!
**A**:
- 파일 이름이 정확히 `.env`인지 확인 (`.env.txt` ❌)
- 파일이 프로젝트 루트 폴더에 있는지 확인
- 앱을 재시작했는지 확인

### Q6: "API 키가 유효하지 않습니다" 에러가 나요
**A**:
- API 키가 `sk-`로 시작하는지 확인
- 공백이나 따옴표 없이 입력했는지 확인
- OpenAI 플랫폼에서 키가 활성 상태인지 확인

---

## 🔒 보안 주의사항

### ✅ 해야 할 것
- `.env` 파일은 `.gitignore`에 포함 (이미 설정됨)
- API 키는 안전한 곳에 백업

### ❌ 하지 말아야 할 것
- API 키를 코드에 직접 작성
- API 키를 Git에 커밋
- API 키를 다른 사람과 공유

---

## 💰 비용 관리

### 사용 한도 설정 (권장)

1. **한도 설정 페이지**
   ```
   https://platform.openai.com/account/billing/limits
   ```

2. **월 한도 설정**
   - 예: $5 (약 ₩6,500)
   - 한도 도달 시 API 자동 차단

### 사용량 확인

```
https://platform.openai.com/usage
```

---

## 🚨 문제 해결

### 에러: "OPENAI_API_KEY가 설정되지 않았습니다"

**해결 순서**:
1. `.env` 파일 존재 확인
2. `OPENAI_API_KEY=` 뒤에 실제 키 입력했는지 확인
3. 앱 재시작

### 에러: "API 호출 실패"

**해결 순서**:
1. 인터넷 연결 확인
2. OpenAI 잔액 확인
3. 잠시 후 재시도

---

## 📚 상세 가이드

더 자세한 내용은 [OPENAI_SETUP_GUIDE.md](OPENAI_SETUP_GUIDE.md)를 참고하세요.

---

**API 키 없이도 기본 분석은 이용 가능합니다!**
AI 심리 분석만 API 키가 필요합니다.
