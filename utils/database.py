"""
Supabase 데이터베이스 연동 모듈
- 사용자, 구매 이력, 분석 결과, AI 사용 로그 CRUD
- DB 연결 실패 시 None 반환 (auth.py에서 JSON fallback 처리)
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Supabase SDK (선택적 임포트)
try:
    from supabase import create_client, Client
    SUPABASE_SDK_AVAILABLE = True
except ImportError:
    SUPABASE_SDK_AVAILABLE = False

# 싱글톤 클라이언트
_supabase_client: Optional[object] = None


def get_supabase_client() -> Optional[object]:
    """
    Supabase 클라이언트 싱글톤 반환

    Returns:
        Supabase Client 또는 None (연결 불가 시)
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_SDK_AVAILABLE:
        return None

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        return None

    try:
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception:
        return None


def is_db_available() -> bool:
    """DB 연결 가능 여부 체크"""
    return get_supabase_client() is not None


# ============================================
# Users CRUD
# ============================================

def get_or_create_user(user_info: Dict) -> Optional[Dict]:
    """
    로그인 시 사용자 조회/생성

    Args:
        user_info: {email, name, picture, sub}

    Returns:
        DB user row dict 또는 None
    """
    client = get_supabase_client()
    if not client:
        return None

    email = user_info.get('email')
    if not email:
        return None

    try:
        # 기존 사용자 조회
        result = client.table('users').select('*').eq('email', email).execute()

        if result.data:
            # 기존 사용자 → last_login 업데이트
            user = result.data[0]
            client.table('users').update({
                'last_login': datetime.utcnow().isoformat(),
                'name': user_info.get('name', user.get('name')),
                'picture_url': user_info.get('picture', user.get('picture_url'))
            }).eq('id', user['id']).execute()
            return user
        else:
            # 신규 사용자 생성
            new_user = {
                'email': email,
                'google_id': user_info.get('sub'),
                'name': user_info.get('name', ''),
                'picture_url': user_info.get('picture', ''),
                'usage_count': 0,
                'is_subscribed': False,
                'language': 'ko'
            }
            result = client.table('users').insert(new_user).execute()
            if result.data:
                return result.data[0]
            return None

    except Exception:
        return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """이메일로 사용자 조회"""
    client = get_supabase_client()
    if not client:
        return None

    try:
        result = client.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def get_usage_count(user_id: str) -> Tuple[bool, int, bool]:
    """
    사용 횟수 확인

    Returns:
        (사용 가능 여부, 남은 횟수, 구독 상태)
    """
    client = get_supabase_client()
    if not client:
        return True, 5, False  # DB 없으면 기본값

    try:
        result = client.table('users').select('usage_count, is_subscribed').eq('id', user_id).execute()
        if not result.data:
            return True, 5, False

        user = result.data[0]
        if user['is_subscribed']:
            return True, -1, True

        remaining = 5 - user['usage_count']
        return (remaining > 0), max(remaining, 0), False

    except Exception:
        return True, 5, False


def increment_usage(user_id: str) -> None:
    """사용 횟수 +1"""
    client = get_supabase_client()
    if not client:
        return

    try:
        # 현재 값 조회 후 +1
        result = client.table('users').select('usage_count, is_subscribed').eq('id', user_id).execute()
        if result.data and not result.data[0].get('is_subscribed', False):
            current = result.data[0]['usage_count']
            client.table('users').update({
                'usage_count': current + 1
            }).eq('id', user_id).execute()
    except Exception:
        pass


def update_language(user_id: str, lang: str) -> None:
    """언어 설정 저장"""
    client = get_supabase_client()
    if not client:
        return

    try:
        client.table('users').update({'language': lang}).eq('id', user_id).execute()
    except Exception:
        pass


# ============================================
# Purchases CRUD
# ============================================

def save_purchases(user_id: str, df: pd.DataFrame, source: str = 'manual') -> bool:
    """
    DataFrame의 구매 이력을 DB에 저장

    Args:
        user_id: 사용자 UUID
        df: 구매 데이터 DataFrame
        source: 'csv' 또는 'manual'

    Returns:
        성공 여부
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        rows = []
        for _, row in df.iterrows():
            purchase = {
                'user_id': user_id,
                'purchase_date': str(row.get('날짜', ''))[:10],
                'category': str(row.get('카테고리', '')),
                'product_name': str(row.get('상품명', '')),
                'amount': int(float(row.get('금액', 0))),
                'necessity_score': int(row.get('필요도', 3)),
                'usage_frequency': int(row.get('사용빈도', 3)),
                'source': source
            }

            # 고민기간, 재구매의향 (있는 경우)
            if '고민기간' in row and pd.notna(row['고민기간']):
                purchase['thinking_days'] = int(row['고민기간'])
            if '재구매의향' in row and pd.notna(row['재구매의향']):
                intent = str(row['재구매의향']).strip().lower()
                purchase['repurchase_intent'] = intent in ('예', 'yes', 'y', '1', 'はい')

            rows.append(purchase)

        if rows:
            client.table('purchases').insert(rows).execute()
            return True
        return False

    except Exception:
        return False


def save_single_purchase(user_id: str, purchase_data: dict) -> bool:
    """
    개별 구매 1건을 DB에 저장 (가계부용)

    Args:
        user_id: 사용자 UUID
        purchase_data: {날짜, 카테고리, 상품명, 금액, 필요도, 사용빈도, 고민기간?, 재구매의향?}

    Returns:
        성공 여부
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        row = {
            'user_id': user_id,
            'purchase_date': str(purchase_data.get('날짜', ''))[:10],
            'category': str(purchase_data.get('카테고리', '')),
            'product_name': str(purchase_data.get('상품명', '')),
            'amount': int(float(purchase_data.get('금액', 0))),
            'necessity_score': int(purchase_data.get('필요도', 3)),
            'usage_frequency': int(purchase_data.get('사용빈도', 3)),
            'source': 'manual'
        }

        if purchase_data.get('고민기간') is not None:
            row['thinking_days'] = int(purchase_data['고민기간'])
        if purchase_data.get('재구매의향') is not None:
            intent = str(purchase_data['재구매의향']).strip().lower()
            row['repurchase_intent'] = intent in ('예', 'yes', 'y', '1', 'はい')

        client.table('purchases').insert(row).execute()
        return True

    except Exception:
        return False


def load_purchases(user_id: str, date_from: str = None, date_to: str = None, include_id: bool = False) -> Optional[pd.DataFrame]:
    """
    DB에서 사용자의 구매 이력 로드

    Args:
        user_id: 사용자 UUID
        date_from: 시작일 (YYYY-MM-DD), None이면 전체
        date_to: 종료일 (YYYY-MM-DD), None이면 전체
        include_id: True면 DB id 컬럼 포함 (삭제용)

    Returns:
        구매 이력 DataFrame 또는 None
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        query = (client.table('purchases')
                 .select('*')
                 .eq('user_id', user_id))

        if date_from:
            query = query.gte('purchase_date', date_from)
        if date_to:
            query = query.lte('purchase_date', date_to)

        result = query.order('purchase_date', desc=True).execute()

        if not result.data:
            return None

        # DB 컬럼 → 앱 내부 컬럼명으로 변환
        rows = []
        for r in result.data:
            row = {
                '날짜': r['purchase_date'],
                '카테고리': r['category'],
                '상품명': r['product_name'] or '',
                '금액': float(r['amount']),
                '필요도': r['necessity_score'] or 3,
                '사용빈도': r['usage_frequency'] or 3,
            }
            if include_id:
                row['_id'] = r['id']
            if r.get('thinking_days') is not None:
                row['고민기간'] = r['thinking_days']
            if r.get('repurchase_intent') is not None:
                row['재구매의향'] = '예' if r['repurchase_intent'] else '아니오'
            rows.append(row)

        df = pd.DataFrame(rows)
        df['날짜'] = pd.to_datetime(df['날짜'])
        return df

    except Exception:
        return None


def delete_purchases(user_id: str, purchase_ids: List[int]) -> bool:
    """선택한 구매 이력 삭제"""
    client = get_supabase_client()
    if not client:
        return False

    try:
        for pid in purchase_ids:
            client.table('purchases').delete().eq('id', pid).eq('user_id', user_id).execute()
        return True
    except Exception:
        return False


def get_purchase_count(user_id: str) -> int:
    """사용자의 저장된 구매 이력 수"""
    client = get_supabase_client()
    if not client:
        return 0

    try:
        result = (client.table('purchases')
                  .select('id', count='exact')
                  .eq('user_id', user_id)
                  .execute())
        return result.count or 0
    except Exception:
        return 0


# ============================================
# Analyses CRUD
# ============================================

def save_analysis(user_id: str, analysis_data: Dict) -> Optional[int]:
    """
    분석 결과 저장

    Args:
        user_id: 사용자 UUID
        analysis_data: {
            purchase_count, total_spent, average_regret_score,
            high_regret_count, psychology_analysis, smart_insights
        }

    Returns:
        생성된 analysis id 또는 None
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        row = {
            'user_id': user_id,
            'purchase_count': analysis_data.get('purchase_count', 0),
            'total_spent': analysis_data.get('total_spent', 0),
            'average_regret_score': analysis_data.get('average_regret_score', 0),
            'high_regret_count': analysis_data.get('high_regret_count', 0),
            'psychology_analysis': analysis_data.get('psychology_analysis', ''),
            'smart_insights': analysis_data.get('smart_insights', '')
        }

        result = client.table('analyses').insert(row).execute()
        if result.data:
            return result.data[0]['id']
        return None

    except Exception:
        return None


def load_analyses(user_id: str, limit: int = 10) -> List[Dict]:
    """
    분석 이력 조회 (최신순)

    Returns:
        분석 이력 리스트
    """
    client = get_supabase_client()
    if not client:
        return []

    try:
        result = (client.table('analyses')
                  .select('*')
                  .eq('user_id', user_id)
                  .order('created_at', desc=True)
                  .limit(limit)
                  .execute())
        return result.data or []
    except Exception:
        return []


def load_latest_analysis(user_id: str) -> Optional[Dict]:
    """최근 분석 1건 조회"""
    analyses = load_analyses(user_id, limit=1)
    return analyses[0] if analyses else None


# ============================================
# AI Usage Logs
# ============================================

def log_ai_usage(user_id: str, analysis_id: Optional[int],
                 call_type: str, tokens: Dict) -> None:
    """
    AI API 사용량 기록

    Args:
        user_id: 사용자 UUID
        analysis_id: 연결된 분석 ID (없으면 None)
        call_type: 'psychology' 또는 'smart_insights'
        tokens: {prompt_tokens, completion_tokens, total_tokens}
    """
    client = get_supabase_client()
    if not client:
        return

    try:
        total = tokens.get('total_tokens', 0)
        # gpt-4o-mini 기준 비용 계산 (input: $0.15/1M, output: $0.6/1M)
        prompt_cost = tokens.get('prompt_tokens', 0) * 0.00000015
        completion_cost = tokens.get('completion_tokens', 0) * 0.0000006
        estimated_cost = prompt_cost + completion_cost

        row = {
            'user_id': user_id,
            'analysis_id': analysis_id,
            'call_type': call_type,
            'prompt_tokens': tokens.get('prompt_tokens', 0),
            'completion_tokens': tokens.get('completion_tokens', 0),
            'total_tokens': total,
            'estimated_cost_usd': round(estimated_cost, 6)
        }
        client.table('ai_usage_logs').insert(row).execute()
    except Exception:
        pass
