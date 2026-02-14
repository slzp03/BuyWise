"""
CSV 파일 처리 및 검증 모듈
"""

import pandas as pd
from datetime import datetime
from typing import Tuple, Optional
from utils.translations import JA_TO_KO_COLUMNS


def convert_ja_columns(df: pd.DataFrame) -> pd.DataFrame:
    """일본어 CSV 컬럼을 한국어로 변환"""
    rename_map = {ja: ko for ja, ko in JA_TO_KO_COLUMNS.items() if ja in df.columns}
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def validate_csv(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    CSV 데이터 검증

    두 가지 CSV 형식 지원:
    1. 새 형식: 날짜, 카테고리, 상품명, 금액, 고민기간, 재구매의향, 사용빈도 (수동 입력과 동일)
    2. 기존 형식: 날짜, 카테고리, 상품명, 금액, 필요도, 사용빈도 (하위 호환)

    Args:
        df: pandas DataFrame

    Returns:
        (유효성 여부, 에러 메시지)
    """
    # 일본어 컬럼 자동 변환
    df = convert_ja_columns(df)

    # 새 형식 (고민기간 + 재구매의향) 감지
    has_new_format = '고민기간' in df.columns and '재구매의향' in df.columns
    has_old_format = '필요도' in df.columns

    if has_new_format:
        required_columns = ['날짜', '카테고리', '금액', '고민기간', '재구매의향', '사용빈도']
    elif has_old_format:
        required_columns = ['날짜', '카테고리', '금액', '필요도', '사용빈도']
    else:
        return False, "필수 컬럼이 누락되었습니다. '고민기간, 재구매의향' 또는 '필요도' 컬럼이 필요합니다."

    # 필수 컬럼 체크
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"

    # 빈 데이터 체크
    if df.empty:
        return False, "CSV 파일에 데이터가 없습니다."

    # 날짜 형식 검증
    try:
        pd.to_datetime(df['날짜'], errors='raise')
    except Exception as e:
        return False, f"날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요. ({str(e)})"

    # 금액 검증
    if not pd.api.types.is_numeric_dtype(df['금액']):
        try:
            df['금액'] = pd.to_numeric(df['금액'], errors='raise')
        except:
            return False, "금액은 숫자여야 합니다."

    if (df['금액'] < 0).any():
        return False, "금액은 0 이상이어야 합니다."

    if has_new_format:
        # 고민기간 검증
        if not pd.api.types.is_numeric_dtype(df['고민기간']):
            try:
                df['고민기간'] = pd.to_numeric(df['고민기간'], errors='raise')
            except:
                return False, "고민기간은 숫자(일)여야 합니다."

        if (df['고민기간'] < 0).any():
            return False, "고민기간은 0 이상이어야 합니다."

        # 재구매의향 검증 (예/아니오 또는 Y/N 또는 1/0 또는 はい/いいえ)
        valid_yes = {'예', 'y', 'yes', '1', 'true', 'o', 'はい'}
        valid_no = {'아니오', 'n', 'no', '0', 'false', 'x', 'いいえ'}
        valid_values = valid_yes | valid_no

        for idx, val in df['재구매의향'].items():
            if str(val).strip().lower() not in valid_values:
                return False, f"재구매의향은 '예/아니오' 또는 'Y/N'으로 입력해주세요. (오류 값: {val})"
    else:
        # 필요도 검증 (기존 형식)
        if not pd.api.types.is_numeric_dtype(df['필요도']):
            try:
                df['필요도'] = pd.to_numeric(df['필요도'], errors='raise')
            except:
                return False, "필요도는 1-5 사이의 정수여야 합니다."

        if not df['필요도'].between(1, 5).all():
            return False, "필요도는 1-5 사이의 정수여야 합니다."

    # 사용빈도 검증
    if not pd.api.types.is_numeric_dtype(df['사용빈도']):
        try:
            df['사용빈도'] = pd.to_numeric(df['사용빈도'], errors='raise')
        except:
            return False, "사용빈도는 1-5 사이의 정수여야 합니다."

    if not df['사용빈도'].between(1, 5).all():
        return False, "사용빈도는 1-5 사이의 정수여야 합니다."

    return True, None


def process_csv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    CSV 데이터 전처리

    새 형식(고민기간+재구매의향)이면 필요도를 자동 계산합니다.
    기존 형식(필요도 직접 입력)도 하위 호환합니다.

    Args:
        df: 원본 DataFrame

    Returns:
        전처리된 DataFrame
    """
    # 복사본 생성
    processed_df = df.copy()

    # 일본어 컬럼 자동 변환
    processed_df = convert_ja_columns(processed_df)

    # 날짜를 datetime으로 변환
    processed_df['날짜'] = pd.to_datetime(processed_df['날짜'])

    # 숫자 타입 변환
    processed_df['금액'] = pd.to_numeric(processed_df['금액'])
    processed_df['사용빈도'] = pd.to_numeric(processed_df['사용빈도'])

    # 새 형식: 고민기간 + 재구매의향 → 필요도 자동 계산
    if '고민기간' in processed_df.columns and '재구매의향' in processed_df.columns:
        processed_df['고민기간'] = pd.to_numeric(processed_df['고민기간'])

        # 재구매의향 문자열 → bool 변환
        valid_yes = {'예', 'y', 'yes', '1', 'true', 'o', 'はい'}
        processed_df['재구매의향_bool'] = processed_df['재구매의향'].astype(str).str.strip().str.lower().isin(valid_yes)

        # 필요도 자동 계산
        processed_df['필요도'] = processed_df.apply(
            lambda row: calculate_necessity_from_input(
                int(row['고민기간']), bool(row['재구매의향_bool'])
            ), axis=1
        )

        # 임시 컬럼 제거
        processed_df = processed_df.drop(columns=['재구매의향_bool'])
    else:
        processed_df['필요도'] = pd.to_numeric(processed_df['필요도'])

    # 상품명이 없는 경우 카테고리로 대체
    if '상품명' in processed_df.columns:
        processed_df['상품명'] = processed_df['상품명'].fillna(processed_df['카테고리'])
    else:
        processed_df['상품명'] = processed_df['카테고리']

    # 날짜 기준 정렬
    processed_df = processed_df.sort_values('날짜', ascending=False)

    # 경과 일수 계산
    today = pd.Timestamp.now()
    processed_df['경과일수'] = (today - processed_df['날짜']).dt.days

    return processed_df


def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    카테고리별 집계 데이터 생성

    Args:
        df: 처리된 DataFrame

    Returns:
        카테고리별 집계 DataFrame
    """
    summary = df.groupby('카테고리').agg({
        '금액': ['sum', 'mean', 'count'],
        '필요도': 'mean',
        '사용빈도': 'mean'
    }).round(1)

    # 컬럼명 평탄화
    summary.columns = ['총_금액', '평균_금액', '구매_건수', '평균_필요도', '평균_사용빈도']
    summary = summary.reset_index()

    # 총 금액 기준 내림차순 정렬
    summary = summary.sort_values('총_금액', ascending=False)

    return summary


def get_basic_stats(df: pd.DataFrame) -> dict:
    """
    기본 통계 정보 계산

    Args:
        df: 처리된 DataFrame

    Returns:
        통계 정보 딕셔너리
    """
    stats = {
        '총_구매건수': len(df),
        '총_지출금액': int(df['금액'].sum()),
        '평균_구매금액': int(df['금액'].mean()),
        '최고_구매금액': int(df['금액'].max()),
        '최저_구매금액': int(df['금액'].min()),
        '카테고리_수': df['카테고리'].nunique(),
        '평균_필요도': round(df['필요도'].mean(), 1),
        '평균_사용빈도': round(df['사용빈도'].mean(), 1),
        '분석_기간_시작': df['날짜'].min().strftime('%Y-%m-%d'),
        '분석_기간_종료': df['날짜'].max().strftime('%Y-%m-%d'),
    }

    return stats


def calculate_necessity_from_input(thinking_days: int, repurchase_will: bool) -> int:
    """
    사용자 입력으로부터 필요도 자동 계산

    Args:
        thinking_days: 구매 전 고민 기간(일) (0-999)
        repurchase_will: 재구매 의향 (True/False)

    Returns:
        필요도 점수 (1-5)

    로직:
        1. 고민 기간 기반 base_score 계산
           - 0일 (충동 구매): 1점
           - 1-6일 (약간 신중): 2점
           - 7-29일 (보통): 3점
           - 30일 이상 (신중함): 4점

        2. 재구매 의향으로 보정
           - 재구매 의향 있음: +1점 (최대 5점)
           - 재구매 의향 없음: 그대로

    예시:
        - 0일 + 재구매 X → 1점 (완전 충동)
        - 7일 + 재구매 O → 4점 (신중하고 만족)
        - 30일 + 재구매 O → 5점 (매우 신중하고 만족)
    """
    # Base score 계산
    if thinking_days == 0:
        base_score = 1  # 충동 구매
    elif thinking_days < 7:
        base_score = 2  # 약간 신중
    elif thinking_days < 30:
        base_score = 3  # 보통
    else:  # >= 30
        base_score = 4  # 신중함

    # 재구매 의향 보정
    if repurchase_will:
        base_score = min(base_score + 1, 5)

    return base_score


def create_dataframe_from_manual_input(items: list) -> Optional[pd.DataFrame]:
    """
    수동 입력 항목들을 DataFrame으로 변환

    Args:
        items: 수동 입력 항목 리스트
               [{'상품명': ..., '카테고리': ..., ...}, ...]

    Returns:
        CSV 형식과 동일한 구조의 DataFrame
        항목이 없으면 None 반환
    """
    if not items:
        return None

    # DataFrame 생성
    df = pd.DataFrame(items)

    # 필수 컬럼 순서 맞추기
    df = df[['날짜', '카테고리', '상품명', '금액', '필요도', '사용빈도']]

    return df
