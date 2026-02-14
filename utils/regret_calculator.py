"""
후회 점수 계산 로직

후회 점수는 0-100 사이의 값으로, 높을수록 후회 가능성이 높음
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List

# 식비 관련 카테고리 키워드
FOOD_KEYWORDS = {'식비', '음식', '배달', '카페', '커피', '외식', '식료품', '간식', '식사', '음료'}


def is_food_category(category: str) -> bool:
    """카테고리가 식비 관련인지 판단"""
    category_lower = category.strip()
    return any(keyword in category_lower for keyword in FOOD_KEYWORDS)


def calculate_necessity_usage_gap_score(necessity: float, usage: float) -> float:
    """
    필요도 vs 사용빈도 갭 점수 계산 (핵심 지표)

    Args:
        necessity: 구매 당시 필요도 (1-5)
        usage: 실제 사용빈도 (1-5)

    Returns:
        갭 점수 (0-30)
    """
    gap = necessity - usage

    if gap <= 0:
        # 사용빈도가 필요도보다 높거나 같으면 후회 없음
        return 0
    elif gap == 1:
        return 5  # 약간의 후회
    elif gap == 2:
        return 12  # 중간 후회
    elif gap == 3:
        return 20  # 높은 후회
    else:  # gap >= 4
        return 30  # 매우 높은 후회


def calculate_time_decay_score(days_since_purchase: int, usage: float) -> float:
    """
    시간 경과 대비 사용빈도 점수

    오래된 구매인데 사용빈도가 낮으면 후회 점수 증가

    Args:
        days_since_purchase: 구매 후 경과 일수
        usage: 실제 사용빈도 (1-5)

    Returns:
        시간 감쇠 점수 (0-15)
    """
    if days_since_purchase < 7:
        # 1주일 미만은 판단하기 이름
        return 0

    # 경과 일수별 가중치
    if days_since_purchase < 30:
        time_weight = 0.3
    elif days_since_purchase < 90:
        time_weight = 0.6
    elif days_since_purchase < 180:
        time_weight = 0.9
    else:
        time_weight = 1.2

    # 사용빈도가 낮을수록 점수 증가
    usage_penalty = (5 - usage) / 4  # 0-1 범위로 정규화

    score = usage_penalty * time_weight * 12
    return min(score, 15)


def calculate_price_weight_score(amount: float, avg_amount: float, max_amount: float) -> float:
    """
    금액 가중치 점수

    고가 제품일수록 후회 시 심리적 부담이 크므로 가중치 증가

    Args:
        amount: 구매 금액
        avg_amount: 평균 구매 금액
        max_amount: 최대 구매 금액

    Returns:
        금액 가중치 점수 (0-20)
    """
    if amount <= 10000:
        # 1만원 이하는 후회 부담 적음
        return 2

    # 평균 대비 비율
    price_ratio = amount / avg_amount if avg_amount > 0 else 1

    # 최대값 대비 비율
    max_ratio = amount / max_amount if max_amount > 0 else 0

    # 로그 스케일로 변환 (급격한 증가 방지)
    log_amount = np.log10(amount / 1000)  # 1000원 단위로 정규화

    score = (price_ratio * 4 + max_ratio * 6 + log_amount * 2)
    return min(score, 20)


def calculate_recency_score(days_since_purchase: int) -> float:
    """
    최근성 점수 (최근 구매일수록 높음)

    최근 구매는 아직 판단하기 이르지만, 충동 구매 가능성이 높음

    Args:
        days_since_purchase: 구매 후 경과 일수

    Returns:
        최근성 점수 (0-10)
    """
    if days_since_purchase <= 3:
        return 8  # 매우 최근 (충동 구매 의심)
    elif days_since_purchase <= 7:
        return 6
    elif days_since_purchase <= 14:
        return 4
    elif days_since_purchase <= 30:
        return 2
    else:
        return 0  # 충분한 시간 경과


def calculate_category_repetition_score(
    category: str,
    category_purchase_dates: List[datetime],
    current_date: datetime
) -> float:
    """
    동일 카테고리 반복 구매 점수

    짧은 시간 내 같은 카테고리 반복 구매 시 충동 구매 가능성 증가

    Args:
        category: 카테고리명
        category_purchase_dates: 해당 카테고리의 모든 구매 날짜
        current_date: 현재 구매 날짜

    Returns:
        반복 구매 점수 (0-15)
    """
    if len(category_purchase_dates) <= 1:
        return 0

    # 현재 구매 전후 30일 이내의 구매 건수
    nearby_purchases = [
        d for d in category_purchase_dates
        if d != current_date and abs((d - current_date).days) <= 30
    ]

    nearby_count = len(nearby_purchases)

    if nearby_count >= 3:
        return 15  # 한 달 내 4건 이상 (현재 포함)
    elif nearby_count == 2:
        return 10  # 한 달 내 3건
    elif nearby_count == 1:
        return 5   # 한 달 내 2건
    else:
        return 0


def calculate_late_night_score(purchase_datetime: datetime) -> float:
    """
    새벽 시간대 구매 점수

    새벽(00:00-05:00) 구매는 충동 구매 가능성이 높음

    Args:
        purchase_datetime: 구매 일시

    Returns:
        새벽 구매 점수 (0-10)

    Note:
        CSV에 시간 정보가 없는 경우 0을 반환
    """
    try:
        purchase_time = purchase_datetime.time()

        # 새벽 시간대 (00:00 - 05:00)
        if time(0, 0) <= purchase_time < time(5, 0):
            return 10
        # 심야 시간대 (23:00 - 24:00)
        elif time(23, 0) <= purchase_time:
            return 7
        # 늦은 밤 (21:00 - 23:00)
        elif time(21, 0) <= purchase_time < time(23, 0):
            return 4
        else:
            return 0
    except:
        # 시간 정보가 없는 경우
        return 0


def calculate_impulse_buying_pattern_score(
    purchase_date: datetime,
    all_purchase_dates: List[datetime]
) -> float:
    """
    충동 구매 패턴 점수

    같은 날 여러 구매 또는 연속된 날짜에 구매 시 충동 구매 패턴 감지

    Args:
        purchase_date: 현재 구매 날짜
        all_purchase_dates: 모든 구매 날짜 리스트

    Returns:
        충동 구매 패턴 점수 (0-10)
    """
    # 같은 날 구매 건수
    same_day_count = sum(1 for d in all_purchase_dates if d.date() == purchase_date.date())

    if same_day_count >= 4:
        return 10  # 하루에 4건 이상
    elif same_day_count == 3:
        return 7   # 하루에 3건
    elif same_day_count == 2:
        return 4   # 하루에 2건

    # 연속 3일 이내 구매 건수
    consecutive_purchases = sum(
        1 for d in all_purchase_dates
        if 0 <= (purchase_date - d).days <= 3 and d != purchase_date
    )

    if consecutive_purchases >= 5:
        return 8
    elif consecutive_purchases >= 3:
        return 5
    elif consecutive_purchases >= 2:
        return 3

    return 0


def calculate_regret_score(
    necessity: float,
    usage: float,
    amount: float,
    purchase_date: datetime,
    category: str,
    df: pd.DataFrame,
    current_date: datetime = None
) -> Dict[str, float]:
    """
    종합 후회 점수 계산

    Args:
        necessity: 필요도 (1-5)
        usage: 사용빈도 (1-5)
        amount: 구매 금액
        purchase_date: 구매 날짜
        category: 카테고리
        df: 전체 구매 데이터 DataFrame
        current_date: 기준 날짜 (기본값: 현재)

    Returns:
        점수 상세 딕셔너리
        {
            'total_score': 총 후회 점수 (0-100),
            'necessity_gap': 필요도-사용빈도 갭 점수,
            'time_decay': 시간 경과 점수,
            'price_weight': 금액 가중치 점수,
            'recency': 최근성 점수,
            'category_repetition': 카테고리 반복 점수,
            'late_night': 새벽 구매 점수,
            'impulse_pattern': 충동 구매 패턴 점수
        }
    """
    if current_date is None:
        current_date = pd.Timestamp.now()

    # 경과 일수 계산
    days_since = (current_date - purchase_date).days

    # 통계값 계산
    avg_amount = df['금액'].mean()
    max_amount = df['금액'].max()

    # 카테고리별 구매 날짜
    category_dates = df[df['카테고리'] == category]['날짜'].tolist()
    all_dates = df['날짜'].tolist()

    # 각 요소별 점수 계산
    food = is_food_category(category)
    scores = {
        'necessity_gap': 0 if food else calculate_necessity_usage_gap_score(necessity, usage),
        'time_decay': 0 if food else calculate_time_decay_score(days_since, usage),
        'price_weight': calculate_price_weight_score(amount, avg_amount, max_amount),
        'recency': calculate_recency_score(days_since),
        'category_repetition': calculate_category_repetition_score(category, category_dates, purchase_date),
        'late_night': calculate_late_night_score(purchase_date),
        'impulse_pattern': calculate_impulse_buying_pattern_score(purchase_date, all_dates)
    }

    # 총 점수 계산 (최대 100점)
    total = sum(scores.values())
    scores['total_score'] = min(total, 100)

    return scores


def add_regret_scores_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame의 모든 행에 후회 점수 추가

    Args:
        df: 구매 데이터 DataFrame

    Returns:
        후회 점수가 추가된 DataFrame
    """
    result_df = df.copy()

    # 각 행별로 후회 점수 계산
    regret_data = []

    for idx, row in result_df.iterrows():
        scores = calculate_regret_score(
            necessity=row['필요도'],
            usage=row['사용빈도'],
            amount=row['금액'],
            purchase_date=row['날짜'],
            category=row['카테고리'],
            df=result_df
        )
        regret_data.append(scores)

    # 점수를 DataFrame에 추가
    regret_df = pd.DataFrame(regret_data)

    result_df['후회점수'] = regret_df['total_score']
    result_df['후회점수_필요도갭'] = regret_df['necessity_gap']
    result_df['후회점수_시간경과'] = regret_df['time_decay']
    result_df['후회점수_금액'] = regret_df['price_weight']
    result_df['후회점수_최근성'] = regret_df['recency']
    result_df['후회점수_반복구매'] = regret_df['category_repetition']
    result_df['후회점수_새벽구매'] = regret_df['late_night']
    result_df['후회점수_충동패턴'] = regret_df['impulse_pattern']

    return result_df


def get_regret_score_interpretation(score: float) -> Dict[str, str]:
    """
    후회 점수 해석

    Args:
        score: 후회 점수 (0-100)

    Returns:
        해석 딕셔너리 (등급, 색상, 메시지)
    """
    if score <= 20:
        return {
            'grade': '매우 만족',
            'emoji': '🟢',
            'color': 'green',
            'message': '훌륭한 구매입니다! 돈이 아깝지 않네요.'
        }
    elif score <= 35:
        return {
            'grade': '만족',
            'emoji': '🟡',
            'color': 'lightgreen',
            'message': '괜찮은 구매입니다. 대체로 만족스럽네요.'
        }
    elif score <= 50:
        return {
            'grade': '보통',
            'emoji': '🟡',
            'color': 'yellow',
            'message': '그저 그런 구매입니다. 좀 더 신중할 필요가 있어요.'
        }
    elif score <= 65:
        return {
            'grade': '아쉬움',
            'emoji': '🟠',
            'color': 'orange',
            'message': '아쉬운 구매입니다. 다음엔 더 신중하게 결정하세요.'
        }
    elif score <= 80:
        return {
            'grade': '후회',
            'emoji': '🔴',
            'color': 'red',
            'message': '후회되는 구매입니다. 왜 샀는지 다시 생각해보세요.'
        }
    else:
        return {
            'grade': '매우 후회',
            'emoji': '🔴',
            'color': 'darkred',
            'message': '매우 후회되는 구매입니다. 충동 구매 패턴을 개선해야 합니다.'
        }


def get_overall_regret_analysis(df: pd.DataFrame) -> Dict:
    """
    전체 구매의 후회 점수 분석

    Args:
        df: 후회 점수가 포함된 DataFrame

    Returns:
        전체 분석 결과
    """
    if '후회점수' not in df.columns:
        return {}

    total_purchases = len(df)
    avg_regret_score = df['후회점수'].mean()

    # 등급별 분포
    very_satisfied = len(df[df['후회점수'] <= 20])
    satisfied = len(df[(df['후회점수'] > 20) & (df['후회점수'] <= 35)])
    neutral = len(df[(df['후회점수'] > 35) & (df['후회점수'] <= 50)])
    regretful = len(df[(df['후회점수'] > 50) & (df['후회점수'] <= 65)])
    very_regretful = len(df[df['후회점수'] > 65])

    # 후회 구매 (50점 이상)
    regret_purchases = df[df['후회점수'] > 50]
    regret_amount = regret_purchases['금액'].sum() if len(regret_purchases) > 0 else 0
    total_amount = df['금액'].sum()

    # 주요 후회 원인 분석
    score_columns = [
        '후회점수_필요도갭', '후회점수_시간경과', '후회점수_금액',
        '후회점수_최근성', '후회점수_반복구매', '후회점수_새벽구매', '후회점수_충동패턴'
    ]

    main_causes = {}
    for col in score_columns:
        if col in df.columns:
            main_causes[col] = df[col].mean()

    # 가장 큰 원인 찾기
    if main_causes:
        top_cause = max(main_causes.items(), key=lambda x: x[1])
    else:
        top_cause = ('알 수 없음', 0)

    return {
        'total_purchases': total_purchases,
        'avg_regret_score': round(avg_regret_score, 1),
        'distribution': {
            'very_satisfied': very_satisfied,
            'satisfied': satisfied,
            'neutral': neutral,
            'regretful': regretful,
            'very_regretful': very_regretful
        },
        'regret_count': len(regret_purchases),
        'regret_ratio': round(len(regret_purchases) / total_purchases * 100, 1) if total_purchases > 0 else 0,
        'regret_amount': int(regret_amount),
        'regret_amount_ratio': round(regret_amount / total_amount * 100, 1) if total_amount > 0 else 0,
        'main_cause': {
            'name': top_cause[0].replace('후회점수_', ''),
            'score': round(top_cause[1], 1)
        },
        'interpretation': get_regret_score_interpretation(avg_regret_score)
    }
