"""
인증 및 사용자 관리 모듈
- Google OAuth 2.0 + 로컬 ID/PW 회원가입/로그인
- Supabase DB 우선 사용, 연결 실패 시 로컬 JSON fallback
"""

import os
import re
import json
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Tuple

import bcrypt

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Streamlit Cloud 프록시 대응

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

# DB 모듈 (선택적)
try:
    from utils.database import (
        is_db_available, get_or_create_user, get_user_by_email,
        get_user_by_username, create_local_user,
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
        include_granted_scopes='true'
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


# ============================================
# 로컬 ID/PW 회원가입 & 로그인
# ============================================

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')


def validate_username(username: str) -> Optional[str]:
    """
    아이디 유효성 검사

    Returns:
        에러 메시지 또는 None (유효)
    """
    if len(username) < 4:
        return 'username_too_short'
    if len(username) > 50:
        return 'username_too_long'
    if not USERNAME_PATTERN.match(username):
        return 'username_invalid'
    return None


def validate_password(password: str) -> Optional[str]:
    """
    비밀번호 유효성 검사

    Returns:
        에러 메시지 또는 None (유효)
    """
    if len(password) < 6:
        return 'password_too_short'
    return None


def register_local(username: str, password: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    로컬 회원가입

    Returns:
        (성공 여부, 메시지 키, user_info dict 또는 None)
    """
    # 유효성 검사
    err = validate_username(username)
    if err:
        return False, err, None

    err = validate_password(password)
    if err:
        return False, err, None

    # 비밀번호 해시
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # DB 사용 가능 시
    if _use_db():
        existing = get_user_by_username(username)
        if existing:
            return False, 'username_exists', None

        db_user = create_local_user(username, pw_hash, name)
        if db_user:
            user_info = {
                'email': f'{username}@local',
                'name': name,
                'picture': '',
                'sub': f'local-{username}',
                'db_user_id': db_user['id']
            }
            return True, 'register_success', user_info
        return False, 'register_fail', None

    # JSON fallback
    users = _load_user_data_json()
    local_email = f'{username}@local'

    if local_email in users and users[local_email].get('password_hash'):
        return False, 'username_exists', None

    users[local_email] = {
        'usage_count': 0,
        'is_subscribed': True,
        'subscription_date': None,
        'password_hash': pw_hash,
        'name': name,
        'auth_method': 'local'
    }
    _save_user_data_json(users)

    user_info = {
        'email': local_email,
        'name': name,
        'picture': '',
        'sub': f'local-{username}'
    }
    return True, 'register_success', user_info


def login_local(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    로컬 로그인

    Returns:
        (성공 여부, 메시지 키, user_info dict 또는 None)
    """
    # DB 사용 가능 시
    if _use_db():
        db_user = get_user_by_username(username)
        if not db_user or not db_user.get('password_hash'):
            return False, 'login_fail', None

        if not bcrypt.checkpw(password.encode('utf-8'), db_user['password_hash'].encode('utf-8')):
            return False, 'login_fail', None

        user_info = {
            'email': db_user['email'],
            'name': db_user.get('name', username),
            'picture': db_user.get('picture_url', ''),
            'sub': f'local-{username}',
            'db_user_id': db_user['id']
        }
        return True, 'login_success', user_info

    # JSON fallback
    users = _load_user_data_json()
    local_email = f'{username}@local'

    if local_email not in users or not users[local_email].get('password_hash'):
        return False, 'login_fail', None

    stored_hash = users[local_email]['password_hash']
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return False, 'login_fail', None

    user_info = {
        'email': local_email,
        'name': users[local_email].get('name', username),
        'picture': '',
        'sub': f'local-{username}'
    }
    return True, 'login_success', user_info


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
