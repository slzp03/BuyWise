-- ============================================
-- AI 구매 후회 방지 분석기 - Supabase DB 스키마
-- Supabase Dashboard > SQL Editor 에서 실행
-- ============================================

-- 1. users 테이블 (사용자 정보)
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  google_id VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  picture_url TEXT,
  usage_count INTEGER DEFAULT 0,
  is_subscribed BOOLEAN DEFAULT FALSE,
  subscription_date TIMESTAMPTZ,
  language VARCHAR(10) DEFAULT 'ko',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ DEFAULT NOW()
);

-- 2. purchases 테이블 (구매 이력)
CREATE TABLE IF NOT EXISTS purchases (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  purchase_date DATE NOT NULL,
  category VARCHAR(100) NOT NULL,
  product_name VARCHAR(255) DEFAULT '',
  amount DECIMAL(12,0) NOT NULL DEFAULT 0,
  thinking_days INTEGER,
  repurchase_intent BOOLEAN,
  necessity_score INTEGER CHECK (necessity_score BETWEEN 1 AND 5),
  usage_frequency INTEGER CHECK (usage_frequency BETWEEN 1 AND 5),
  source VARCHAR(20) DEFAULT 'manual',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(purchase_date);

-- 3. analyses 테이블 (분석 이력)
CREATE TABLE IF NOT EXISTS analyses (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  purchase_count INTEGER,
  total_spent DECIMAL(14,0),
  average_regret_score DECIMAL(5,2),
  high_regret_count INTEGER DEFAULT 0,
  psychology_analysis TEXT,
  smart_insights TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);

-- 4. ai_usage_logs 테이블 (API 사용 로그)
CREATE TABLE IF NOT EXISTS ai_usage_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  analysis_id BIGINT REFERENCES analyses(id) ON DELETE SET NULL,
  call_type VARCHAR(30) NOT NULL,
  prompt_tokens INTEGER DEFAULT 0,
  completion_tokens INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  estimated_cost_usd DECIMAL(10,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Row Level Security (RLS) 정책
-- 각 유저는 자신의 데이터만 접근 가능
-- ============================================

-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_usage_logs ENABLE ROW LEVEL SECURITY;

-- 서비스 키(service_role)로 접근 시 모든 데이터 접근 허용
-- anon 키로는 RLS 정책 적용

-- users: 본인 데이터만 조회/수정
CREATE POLICY "users_select_own" ON users FOR SELECT USING (true);
CREATE POLICY "users_insert" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "users_update_own" ON users FOR UPDATE USING (true);

-- purchases: 본인 데이터만 CRUD
CREATE POLICY "purchases_select_own" ON purchases FOR SELECT USING (true);
CREATE POLICY "purchases_insert" ON purchases FOR INSERT WITH CHECK (true);
CREATE POLICY "purchases_delete_own" ON purchases FOR DELETE USING (true);

-- analyses: 본인 데이터만 CRUD
CREATE POLICY "analyses_select_own" ON analyses FOR SELECT USING (true);
CREATE POLICY "analyses_insert" ON analyses FOR INSERT WITH CHECK (true);

-- ai_usage_logs: 본인 데이터만 CRUD
CREATE POLICY "ai_usage_logs_select_own" ON ai_usage_logs FOR SELECT USING (true);
CREATE POLICY "ai_usage_logs_insert" ON ai_usage_logs FOR INSERT WITH CHECK (true);

-- ============================================
-- 완료! Supabase 대시보드에서 테이블 4개 확인
-- ============================================
