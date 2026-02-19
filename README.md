# AI 구매 후회 방지 분석기 (BuyWise)

> BuyWise - AI 기반 소비 패턴 분석 및 후회 방지 서비스

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red)

## 🎯 프로젝트 개요

일상 소비를 가계부로 기록하고, AI가 구매 패턴을 분석하여 후회 없는 소비 습관을 만들어주는 서비스입니다.

**해결하는 문제**: 충동 구매 후 후회 → 데이터 기반 자기 인식 + AI 심리 분석으로 소비 습관 개선

## ✨ 주요 기능

- 📒 **가계부**: 일일 지출 간편 기록 + 기간별 필터링 + 누적 데이터 관리
- 📤 **CSV 업로드**: 카드·온라인 구매 내역 CSV 업로드 (한국어/일본어 지원)
- 🎯 **후회 점수**: 7가지 요소 기반 0-100점 정밀 계산
- 📊 **시각화**: Plotly 인터랙티브 차트 6종
- 🤖 **AI 분석**: GPT-4o-mini 소비 심리 분석 + 스마트 인사이트
- 🌐 **다국어**: 한국어/일본어 UI + AI 응답 완전 지원
- 📱 **모바일 앱**: Flutter 크로스플랫폼 앱 (같은 DB 공유, 개발 중)

## 🛠 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| 웹 프레임워크 | Streamlit 1.31+ | 올인원 웹앱 |
| 데이터 처리 | pandas 2.2+, numpy 1.26+ | CSV 파싱 및 분석 |
| 시각화 | Plotly 5.18+ | 인터랙티브 차트 6종 |
| AI | OpenAI SDK (GPT-4o-mini) | 소비 심리 분석 |
| DB | Supabase (PostgreSQL) | 클라우드 DB (4개 테이블) |
| 인증 | Google OAuth 2.0 | 로그인, 사용 횟수 관리 |
| 모바일 | Flutter 3.2+ / Dart | iOS/Android 앱 |

## 🏗 아키텍처

```
┌─────────────────┐     ┌─────────────────┐
│  Streamlit 웹   │     │  Flutter 앱     │
│  (Python)       │     │  (Dart)         │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │  Supabase   │
              │ (PostgreSQL)│
              │  4개 테이블  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  OpenAI API │
              │ GPT-4o-mini │
              └─────────────┘
```

## 🚀 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 3. 앱 실행
streamlit run app.py
# http://localhost:8501
```

## 📋 CSV 형식

```csv
# 권장 형식
날짜,카테고리,상품명,금액,고민기간,재구매의향,사용빈도
2024-01-15,전자제품,무선이어폰,89000,7,예,5

# 일본어 CSV
日付,カテゴリ,商品名,金額,検討期間,再購入意向,使用頻度
```

## 📁 디렉토리 구조

```
project/
├── app.py                    # 메인 Streamlit 앱
├── utils/
│   ├── csv_processor.py      # CSV 검증/전처리
│   ├── visualizer.py         # Plotly 차트 6종
│   ├── regret_calculator.py  # 후회 점수 알고리즘
│   ├── openai_service.py     # GPT-4o-mini 연동
│   ├── auth.py               # Google OAuth
│   ├── database.py           # Supabase CRUD
│   └── translations.py       # 다국어 (ko/ja)
├── mobile/                   # Flutter 모바일 앱
│   └── lib/                  # Dart 소스 코드
├── sample_purchases.csv      # 샘플 데이터 35건
├── supabase_schema.sql       # DB 스키마
└── requirements.txt
```

## 💰 비용

- AI 분석 1회: 약 $0.001 (₩1.3)
- $5 예산으로 약 4,000회 분석 가능

---

**버전**: 2.1.0 | **날짜**: 2026-02-15 | **GitHub**: [slzp03/BuyWise](https://github.com/slzp03/BuyWise)
