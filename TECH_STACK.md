# 기술 스택 상세 명세

## 백엔드 기술 스택

### 코어 프레임워크
| 기술 | 버전 | 용도 | 선택 이유 |
|------|------|------|-----------|
| **Python** | 3.10+ | 메인 언어 | 데이터 처리에 강점, pandas/OpenAI SDK 지원 |
| **FastAPI** | 0.109+ | 웹 프레임워크 | 빠른 개발, 자동 API 문서화, 비동기 지원 |
| **Uvicorn** | 0.27+ | ASGI 서버 | FastAPI 권장 서버, 고성능 |
| **Pydantic** | 2.5+ | 데이터 검증 | 타입 안정성, FastAPI 통합 |

### 데이터 처리
| 기술 | 버전 | 용도 |
|------|------|------|
| **pandas** | 2.2+ | CSV 파싱, 데이터 분석 |
| **numpy** | 1.26+ | 수치 계산 (후회 점수 알고리즘) |

### AI/ML
| 기술 | 버전 | 용도 |
|------|------|------|
| **openai** | 1.10+ | OpenAI API 호출 |
| **tiktoken** | 0.5+ | 토큰 카운팅 (비용 최적화) |

### 유틸리티
| 기술 | 용도 |
|------|------|
| **python-dotenv** | 환경 변수 관리 |
| **python-multipart** | 파일 업로드 처리 |
| **structlog** | 구조화된 로깅 |

### 테스팅
| 기술 | 용도 |
|------|------|
| **pytest** | 단위/통합 테스트 |
| **httpx** | FastAPI 테스트 클라이언트 |
| **pytest-asyncio** | 비동기 테스트 |

---

## 프론트엔드 기술 스택

### 코어 프레임워크
| 기술 | 버전 | 용도 | 선택 이유 |
|------|------|------|-----------|
| **React** | 18.2+ | UI 라이브러리 | 컴포넌트 재사용, 생태계 |
| **Vite** | 5.0+ | 빌드 도구 | CRA보다 10배 빠름 |
| **TypeScript** | 5.0+ | 타입 시스템 | 런타임 에러 방지 (선택사항) |

### 스타일링
| 기술 | 용도 |
|------|------|
| **Tailwind CSS** | 유틸리티 기반 스타일링 |
| **@headlessui/react** | 접근성 높은 UI 컴포넌트 |

### 데이터 페칭
| 기술 | 용도 |
|------|------|
| **axios** | HTTP 클라이언트 |
| **@tanstack/react-query** | 서버 상태 관리, 캐싱 |

### UI 컴포넌트
| 기술 | 용도 |
|------|------|
| **react-dropzone** | 파일 드래그앤드롭 |
| **recharts** | 차트 시각화 |
| **react-hot-toast** | 알림 토스트 |
| **framer-motion** | 애니메이션 (선택사항) |

### 라우팅
| 기술 | 용도 |
|------|------|
| **react-router-dom** | 클라이언트 라우팅 |

---

## 데이터베이스 (확장용)

### Phase 2+에서 사용
| 기술 | 용도 |
|------|------|
| **PostgreSQL** | 메인 데이터베이스 |
| **SQLAlchemy** | ORM |
| **Alembic** | 마이그레이션 도구 |
| **asyncpg** | 비동기 PostgreSQL 드라이버 |

### 스키마 설계 (미래)
```sql
-- users 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW()
);

-- analyses 테이블
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id UUID UNIQUE NOT NULL,
    overall_regret_score FLOAT,
    total_purchases INTEGER,
    total_amount FLOAT,
    ai_insight TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- purchases 테이블
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id),
    date DATE NOT NULL,
    category VARCHAR(100),
    product_name VARCHAR(255),
    amount FLOAT,
    necessity_score INTEGER CHECK (necessity_score BETWEEN 1 AND 5),
    usage_frequency INTEGER CHECK (usage_frequency BETWEEN 1 AND 5),
    regret_score FLOAT
);
```

---

## 인증 (확장용)

### JWT 기반 인증
| 기술 | 용도 |
|------|------|
| **python-jose** | JWT 토큰 생성/검증 |
| **passlib** | 비밀번호 해싱 |
| **bcrypt** | 해싱 알고리즘 |

---

## 결제 (확장용)

### Phase 3+에서 사용
| 기술 | 용도 |
|------|------|
| **Stripe API** | 구독 결제 처리 |
| **stripe-python** | Python SDK |
| **@stripe/react-stripe-js** | React 결제 UI |

---

## 개발 도구

### 코드 품질
| 도구 | 용도 |
|------|------|
| **black** | Python 코드 포매터 |
| **flake8** | Python 린터 |
| **mypy** | 정적 타입 체크 |
| **ESLint** | JavaScript 린터 |
| **Prettier** | JavaScript 포매터 |

### Git Hooks
| 도구 | 용도 |
|------|------|
| **pre-commit** | Git hook 관리 |
| **husky** | 프론트엔드 Git hooks |

---

## 배포 및 인프라

### MVP 배포
| 서비스 | 용도 | 비용 |
|--------|------|------|
| **Vercel** | 프론트엔드 호스팅 | 무료 |
| **Railway** | 백엔드 호스팅 | $5/월 |
| **GitHub** | 코드 저장소 | 무료 |

### 환경 변수 관리
| 도구 | 용도 |
|------|------|
| **Vercel Env Variables** | 프론트엔드 환경 변수 |
| **Railway Env Variables** | 백엔드 환경 변수 |

### CI/CD (선택사항)
| 도구 | 용도 |
|------|------|
| **GitHub Actions** | 자동 테스트/배포 |

---

## 모니터링 (확장용)

### 에러 추적
| 서비스 | 용도 |
|--------|------|
| **Sentry** | 프론트/백엔드 에러 트래킹 |

### 로깅
| 도구 | 용도 |
|------|------|
| **structlog** | 구조화된 로그 (JSON) |
| **Railway Logs** | 서버 로그 확인 |

### 분석
| 서비스 | 용도 |
|--------|------|
| **Google Analytics** | 사용자 행동 분석 |
| **Vercel Analytics** | 웹 성능 분석 |

---

## 개발 환경 설정

### Python 가상 환경
```bash
# venv 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Mac/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### Node.js 환경
```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

### 환경 변수 설정
```bash
# backend/.env
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173

# frontend/.env
VITE_API_URL=http://localhost:8000
```

---

## API 키 및 외부 서비스

### OpenAI API
- **계정**: https://platform.openai.com/signup
- **API 키 발급**: Settings → API Keys
- **모델**: gpt-4o-mini
- **예상 비용**: 입력 $0.15/1M 토큰, 출력 $0.60/1M 토큰
- **MVP 예상 비용**: $5-10 (100회 분석 기준)

### Stripe (확장 시)
- **계정**: https://stripe.com/
- **테스트 모드**: 무료
- **프로덕션 수수료**: 2.9% + $0.30 per transaction

---

## 성능 고려사항

### 백엔드 최적화
- **CSV 처리**: pandas `read_csv(chunksize=1000)` (대용량 파일용)
- **OpenAI API**: 타임아웃 30초, 재시도 3회
- **Rate Limiting**: 분당 10회 제한

### 프론트엔드 최적화
- **Code Splitting**: 라우트별 lazy loading
- **이미지 최적화**: WebP 포맷, 지연 로딩
- **번들 사이즈**: Vite 자동 최적화

---

## 보안 체크리스트

### 백엔드
- [ ] API 키를 환경 변수로 관리
- [ ] CORS 설정 (특정 도메인만 허용)
- [ ] 파일 타입/크기 검증
- [ ] Rate limiting 적용
- [ ] SQL Injection 방지 (SQLAlchemy 사용)
- [ ] XSS 방지 (Pydantic 검증)

### 프론트엔드
- [ ] API 키 노출 방지 (.env 사용)
- [ ] HTTPS 사용 (Vercel 자동 제공)
- [ ] 사용자 입력 검증
- [ ] 민감 정보 로컬 저장 금지

---

## 브라우저 지원

### 타겟 브라우저
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### 폴리필 (필요 시)
- `core-js` (ES6+ 기능)
- `regenerator-runtime` (async/await)

---

## 버전 관리 전략

### Git 브랜치 전략
```
main          → 프로덕션 배포
develop       → 개발 브랜치
feature/*     → 기능 개발
hotfix/*      → 긴급 수정
```

### 커밋 컨벤션
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드/설정 변경
```

---

## 다음 단계
1. ✅ 기술 스택 확정
2. 프로젝트 디렉토리 생성
3. 백엔드 초기 설정 (requirements.txt, main.py)
4. 프론트엔드 초기 설정 (Vite 프로젝트 생성)
5. API 엔드포인트 구현
6. UI 컴포넌트 개발
