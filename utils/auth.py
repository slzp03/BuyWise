"""
Google OAuth 2.0 인증 및 사용자 관리 모듈
"""

import os
import json
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Tuple
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests


def get_google_oauth_flow():
    """
    Google OAuth Flow 객체 생성

    Returns:
        Flow: Google OAuth Flow 객체
    """
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8501"]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri="http://localhost:8501"
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

        return user_info

    except Exception as e:
        st.error(f"로그인 처리 중 오류: {str(e)}")
        return None


# 사용자 데이터 저장 경로
USER_DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"
SESSION_FILE = Path(__file__).parent.parent / "data" / "session.json"


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
            return json.load(f)
    except Exception:
        return None


def clear_session() -> None:
    """세션 파일 삭제"""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def load_user_data() -> Dict:
    """
    사용자 데이터 로드

    Returns:
        dict: 사용자 데이터 딕셔너리
    """
    if not USER_DATA_FILE.exists():
        USER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {}

    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"사용자 데이터 로드 실패: {str(e)}")
        return {}


def save_user_data(data: Dict) -> None:
    """
    사용자 데이터 저장

    Args:
        data: 저장할 사용자 데이터 딕셔너리
    """
    try:
        USER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"사용자 데이터 저장 실패: {str(e)}")


def check_usage_limit(user_email: str) -> Tuple[bool, int, bool]:
    """
    사용 횟수 제한 체크

    Args:
        user_email: 사용자 이메일

    Returns:
        tuple: (사용 가능 여부, 남은 횟수, 구독 상태)
               - 사용 가능 여부: True/False
               - 남은 횟수: 0-5 (구독자는 -1)
               - 구독 상태: True/False
    """
    users = load_user_data()

    if user_email not in users:
        # 신규 사용자
        users[user_email] = {
            'usage_count': 0,
            'is_subscribed': False,
            'subscription_date': None
        }
        save_user_data(users)

    user = users[user_email]

    # 구독자는 무제한
    if user['is_subscribed']:
        return True, -1, True

    # 무료 사용자 (5회 제한)
    remaining = 5 - user['usage_count']

    if remaining > 0:
        return True, remaining, False
    else:
        return False, 0, False


def increment_usage_count(user_email: str) -> None:
    """
    사용 횟수 1 증가

    Args:
        user_email: 사용자 이메일
    """
    users = load_user_data()

    if user_email in users:
        # 구독자는 카운트 증가 안함
        if not users[user_email].get('is_subscribed', False):
            users[user_email]['usage_count'] += 1
            save_user_data(users)


def logout() -> None:
    """
    로그아웃 처리 (세션 초기화)
    """
    # 세션 파일 삭제
    clear_session()

    # 세션 상태 초기화
    keys_to_delete = ['user_info', 'oauth_state', 'processed_df', 'manual_items',
                      'ai_feedback', 'ai_usage', 'smart_insights', 'smart_insights_usage']

    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
