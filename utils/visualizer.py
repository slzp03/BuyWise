"""
데이터 시각화 모듈
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional
from utils.translations import currency_symbol, format_currency, from_krw


def create_category_chart(summary_df: pd.DataFrame, chart_type: str = 'pie', lang: str = 'ko') -> go.Figure:
    """
    카테고리별 지출 금액 차트 생성

    Args:
        summary_df: 카테고리 집계 DataFrame
        chart_type: 차트 타입 ('pie' 또는 'bar')
        lang: 언어 코드 ('ko' 또는 'ja')

    Returns:
        plotly Figure 객체
    """
    sym = currency_symbol(lang)
    unit = '円' if lang == 'ja' else '원'

    # 일본어 모드: 표시용 금액 변환 (JPY)
    display_df = summary_df.copy()
    display_df['총_금액'] = display_df['총_금액'].apply(lambda x: from_krw(x, lang))

    if chart_type == 'pie':
        fig = px.pie(
            display_df,
            values='총_금액',
            names='카테고리',
            title='カテゴリ別支出割合' if lang == 'ja' else '카테고리별 지출 비율',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate=f'<b>%{{label}}</b><br>金額: {sym}%{{value:,.0f}}<br>割合: %{{percent}}<extra></extra>'
            if lang == 'ja' else
            f'<b>%{{label}}</b><br>금액: {sym}%{{value:,.0f}}<br>비율: %{{percent}}<extra></extra>'
        )

    else:  # bar
        fig = px.bar(
            display_df,
            x='카테고리',
            y='총_금액',
            title='カテゴリ別総支出' if lang == 'ja' else '카테고리별 총 지출 금액',
            color='총_금액',
            color_continuous_scale='Blues',
            text='총_금액'
        )

        fig.update_traces(
            texttemplate=f'{sym}%{{text:,.0f}}',
            textposition='outside',
            hovertemplate=f'<b>%{{x}}</b><br>金額: {sym}%{{y:,.0f}}<extra></extra>'
            if lang == 'ja' else
            f'<b>%{{x}}</b><br>금액: {sym}%{{y:,.0f}}<extra></extra>'
        )

        fig.update_layout(
            xaxis_title='カテゴリ' if lang == 'ja' else '카테고리',
            yaxis_title=f'支出金額 ({unit})' if lang == 'ja' else f'지출 금액 ({unit})',
            showlegend=False
        )

    fig.update_layout(
        font=dict(size=12),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    return fig


def create_amount_chart(df: pd.DataFrame, lang: str = 'ko') -> go.Figure:
    """
    구매 금액 분포 차트 생성

    Args:
        df: 처리된 DataFrame
        lang: 언어 코드 ('ko' 또는 'ja')

    Returns:
        plotly Figure 객체
    """
    sym = currency_symbol(lang)
    unit = '円' if lang == 'ja' else '원'

    display_df = df.copy()
    display_df['금액'] = display_df['금액'].apply(lambda x: from_krw(x, lang))

    fig = px.histogram(
        display_df,
        x='금액',
        nbins=20,
        title='購入金額分布' if lang == 'ja' else '구매 금액 분포',
        color_discrete_sequence=['#636EFA'],
        labels={'금액': f'購入金額 ({unit})' if lang == 'ja' else f'구매 금액 ({unit})', 'count': '購入件数' if lang == 'ja' else '구매 건수'}
    )

    fig.update_traces(
        hovertemplate=f'金額: {sym}%{{x:,.0f}}<br>件数: %{{y}}<extra></extra>'
        if lang == 'ja' else
        f'금액: {sym}%{{x:,.0f}}<br>건수: %{{y}}<extra></extra>'
    )

    fig.update_layout(
        xaxis_title=f'購入金額 ({unit})' if lang == 'ja' else f'구매 금액 ({unit})',
        yaxis_title='購入件数' if lang == 'ja' else '구매 건수',
        font=dict(size=12),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        showlegend=False
    )

    return fig


def create_timeline_chart(df: pd.DataFrame, lang: str = 'ko') -> go.Figure:
    """
    월별 지출 추이 차트 생성

    Args:
        df: 처리된 DataFrame
        lang: 언어 코드 ('ko' 또는 'ja')

    Returns:
        plotly Figure 객체
    """
    sym = currency_symbol(lang)
    unit = '円' if lang == 'ja' else '원'

    # 월별 집계
    monthly_df = df.copy()
    monthly_df['연월'] = monthly_df['날짜'].dt.to_period('M').astype(str)

    monthly_summary = monthly_df.groupby('연월').agg({
        '금액': 'sum',
        '날짜': 'count'
    }).reset_index()
    monthly_summary.columns = ['연월', '총_금액', '구매_건수']

    # 일본어 모드: JPY로 변환
    monthly_summary['총_금액'] = monthly_summary['총_금액'].apply(lambda x: from_krw(x, lang))

    # 이중 축 차트
    fig = go.Figure()

    # 금액 바 차트
    fig.add_trace(go.Bar(
        x=monthly_summary['연월'],
        y=monthly_summary['총_금액'],
        name='総支出金額' if lang == 'ja' else '총 지출 금액',
        marker_color='lightblue',
        yaxis='y',
        hovertemplate=f'%{{x}}<br>支出: {sym}%{{y:,.0f}}<extra></extra>'
        if lang == 'ja' else
        f'%{{x}}<br>지출: {sym}%{{y:,.0f}}<extra></extra>'
    ))

    # 구매 건수 라인 차트
    fig.add_trace(go.Scatter(
        x=monthly_summary['연월'],
        y=monthly_summary['구매_건수'],
        name='購入件数' if lang == 'ja' else '구매 건수',
        mode='lines+markers',
        marker=dict(size=8, color='red'),
        line=dict(width=2, color='red'),
        yaxis='y2',
        hovertemplate='%{x}<br>件数: %{y}件<extra></extra>'
        if lang == 'ja' else
        '%{x}<br>건수: %{y}건<extra></extra>'
    ))

    fig.update_layout(
        title='月別支出推移' if lang == 'ja' else '월별 지출 추이',
        xaxis=dict(title='年月' if lang == 'ja' else '연월'),
        yaxis=dict(
            title=dict(text=f'支出金額 ({unit})' if lang == 'ja' else f'지출 금액 ({unit})', font=dict(color='lightblue')),
            tickfont=dict(color='lightblue')
        ),
        yaxis2=dict(
            title=dict(text='購入件数' if lang == 'ja' else '구매 건수', font=dict(color='red')),
            tickfont=dict(color='red'),
            overlaying='y',
            side='right'
        ),
        font=dict(size=12),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    return fig


def create_necessity_usage_scatter(df: pd.DataFrame) -> go.Figure:
    """
    필요도 vs 사용빈도 산점도 차트

    Args:
        df: 처리된 DataFrame

    Returns:
        plotly Figure 객체
    """
    fig = px.scatter(
        df,
        x='필요도',
        y='사용빈도',
        size='금액',
        color='카테고리',
        hover_data=['상품명', '금액', '날짜'],
        title='필요도 vs 사용빈도 분석',
        labels={'필요도': '구매 당시 필요도', '사용빈도': '실제 사용 빈도'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # 대각선 추가 (필요도 = 사용빈도)
    fig.add_trace(go.Scatter(
        x=[1, 5],
        y=[1, 5],
        mode='lines',
        line=dict(color='gray', dash='dash', width=1),
        name='이상적인 구매',
        showlegend=True,
        hoverinfo='skip'
    ))

    fig.update_layout(
        font=dict(size=12),
        height=500,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis=dict(range=[0.5, 5.5], dtick=1),
        yaxis=dict(range=[0.5, 5.5], dtick=1)
    )

    return fig
