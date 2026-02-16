"""
Google OAuth 2.0 인증 및 사용자 관리 모듈
- Supabase DB 우선 사용, 연결 실패 시 로컬 JSON fallback
"""

import os
import json
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Tuple

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Streamlit Cloud 프록시 대응

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

# DB 모듈 (선택적)
try:
    from utils.database import (
        is_db_available, get_or_create_user, get_user_by_email,
        get_usage_count, increment_usage, update_language
    )
    DB_MODULE_AVAILABLE = True
except ImportError:
    DB_MODULE_AVAILABLE = False


def get_google_oauth_flow():
    """
    Google OAuth Flow 객체 생성

    Returns:
        Flow: Google OAuth Flow 객체
    """
    # 환경에 따라 redirect URI 결정 (배포 URL 또는 localhost)
    redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8501")

    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=redirect_uri
    )

    return flow


def get_login_url() -> str:
    """
    Google 로그인 URL 생성

    Returns:
        str: Google 로그인 URL
    """
    flow = get_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    # state를 세션에 저장 (CSRF 방지)
    st.session_state.oauth_state = state

    return authorization_url


def handle_oauth_callback(code: str) -> Optional[Dict]:
    """
    OAuth 콜백 처리 및 사용자 정보 반환

    Args:
        code: OAuth authorization code

    Returns:
        dict: 사용자 정보 (email, name, picture, sub) 또는 None
    """
    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(code=code)

        credentials = flow.credentials

        # ID 토큰에서 사용자 정보 추출
        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request,
            os.getenv("GOOGLE_CLIENT_ID")
        )

        user_info = {
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'picture': id_info.get('picture'),
            'sub': id_info.get('sub')  # Google User ID
        }

        # DB에 사용자 등록/업데이트
        _use_db = DB_MODULE_AVAILABLE and is_db_available()
        if _use_db:
            db_user = get_or_create_user(user_info)
            if db_user:
                user_info['db_user_id'] = db_user['id']

        return user_info

    except Exception as e:
        st.error(f"로그인 처리 중 오류: {str(e)}")
        return None


# 사용자 데이터 저장 경로 (JSON fallback용)
USER_DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"
SESSION_FILE = Path(__file__).parent.parent / "data" / "session.json"


def _use_db() -> bool:
    """DB 사용 가능 여부"""
    return DB_MODULE_AVAILABLE and is_db_available()


def save_session(user_info: Dict) -> None:
    """로그인 세션 저장 (새로고침 시 유지용)"""
    try:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_info, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_session() -> Optional[Dict]:
    """저장된 세션 로드"""
    if not SESSION_FILE.exists():
        return None
    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            session = json.load(f)

        # DB 연결 가능하면 db_user_id 복원
        if _use_db() and 'db_user_id' not in session:
            db_user = get_user_by_email(session.get('email', ''))
            if db_user:
                session['db_user_id'] = db_user['id']

        return session
    except Exception:
        return None


def clear_session() -> None:
    """세션 파일 삭제"""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


# ============================================
# JSON Fallback 함수들 (DB 불가 시 사용)
# ============================================

def _load_user_data_json() -> Dict:
    """로컬 JSON에서 사용자 데이터 로드"""
    if not USER_DATA_FILE.exists():
        USER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {}
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_user_data_json(data: Dict) -> None:
    """로컬 JSON에 사용자 데이터 저장"""
    try:
        USER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============================================
# 통합 인터페이스 (DB 우선, JSON fallback)
# ============================================

def check_usage_limit(user_email: str) -> Tuple[bool, int, bool]:
    """
    사용 횟수 제한 체크 (DB 우선, JSON fallback)

    Returns:
        tuple: (사용 가능 여부, 남은 횟수, 구독 상태)
    """
    # DB 사용 가능 시
    if _use_db():
        db_user = get_user_by_email(user_email)
        if db_user:
            return get_usage_count(db_user['id'])

    # JSON fallback
    users = _load_user_data_json()

    if user_email not in users:
        users[user_email] = {
            'usage_count': 0,
            'is_subscribed': False,
            'subscription_date': None
        }
        _save_user_data_json(users)

    user = users[user_email]

    if user['is_subscribed']:
        return True, -1, True

    remaining = 5 - user['usage_count']
    if remaining > 0:
        return True, remaining, False
    else:
        return False, 0, False


def increment_usage_count(user_email: str) -> None:
    """
    사용 횟수 1 증가 (DB 우선, JSON fallback)
    """
    # DB 사용 가능 시
    if _use_db():
        db_user = get_user_by_email(user_email)
        if db_user:
            increment_usage(db_user['id'])
            return

    # JSON fallback
    users = _load_user_data_json()
    if user_email in users:
        if not users[user_email].get('is_subscribed', False):
            users[user_email]['usage_count'] += 1
            _save_user_data_json(users)


def logout() -> None:
    """
    로그아웃 처리 (세션 초기화)
    """
    # 세션 파일 삭제
    clear_session()

    # 세션 상태 초기화
    keys_to_delete = ['user_info', 'oauth_state', 'processed_df', 'manual_items',
                      'ai_feedback', 'ai_usage', 'smart_insights', 'smart_insights_usage',
                      'db_user_id']

    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
