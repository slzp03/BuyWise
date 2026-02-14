# AI 구매 후회 방지 분석기

> 해커톤 제출용 MVP - Streamlit 기반 AI 소비 패턴 분석 웹앱

## 🎯 프로젝트 개요

CSV 구매 내역을 업로드하면 AI가 당신의 소비 패턴을 분석하고 후회 없는 구매를 위한 조언을 제공합니다.

## ✨ 주요 기능

- 📤 **CSV 업로드**: 드래그앤드롭으로 간편 업로드
- 🎯 **후회 점수**: 7가지 요소 기반 0-100점 계산
- 📊 **시각화**: Plotly 인터랙티브 차트
- 🤖 **AI 분석**: OpenAI GPT-4o-mini 소비 심리 분석
- 💡 **실천 조언**: 구체적인 개선 방안 제시

## 🛠 기술 스택

- **Streamlit 1.31+**: 웹앱 프레임워크
- **pandas 2.2+**: 데이터 처리
- **Plotly 5.18+**: 시각화
- **OpenAI API**: GPT-4o-mini

## 🚀 빠른 시작

\`\`\`bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. (선택) API 키 설정
# .env 파일에 OPENAI_API_KEY 추가

# 3. 앱 실행
streamlit run app.py
\`\`\`

## 📋 CSV 형식

\`\`\`csv
날짜,카테고리,상품명,금액,필요도,사용빈도
2024-01-15,전자제품,무선이어폰,89000,3,5
\`\`\`

## 📚 문서

- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작
- [ARCHITECTURE.md](ARCHITECTURE.md) - 아키텍처
- [API_KEY_SETUP.md](API_KEY_SETUP.md) - API 설정

## 💰 비용

- 1회 AI 분석: $0.0003 (₩0.4)
- 100회: $0.03 (₩40)

---

**버전**: 1.0.0 | **날짜**: 2024-02-11
