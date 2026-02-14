"""
데이터 시각화 모듈
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def create_category_chart(summary_df: pd.DataFrame, chart_type: str = 'pie') -> go.Figure:
    """
    카테고리별 지출 금액 차트 생성

    Args:
        summary_df: 카테고리 집계 DataFrame
        chart_type: 차트 타입 ('pie' 또는 'bar')

    Returns:
        plotly Figure 객체
    """
    if chart_type == 'pie':
        fig = px.pie(
            summary_df,
            values='총_금액',
            names='카테고리',
            title='카테고리별 지출 비율',
            hole=0.3,  # 도넛 차트
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>금액: ₩%{value:,.0f}<br>비율: %{percent}<extra></extra>'
        )

    else:  # bar
        fig = px.bar(
            summary_df,
            x='카테고리',
            y='총_금액',
            title='카테고리별 총 지출 금액',
            color='총_금액',
            color_continuous_scale='Blues',
            text='총_금액'
        )

        fig.update_traces(
            texttemplate='₩%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>금액: ₩%{y:,.0f}<extra></extra>'
        )

        fig.update_layout(
            xaxis_title='카테고리',
            yaxis_title='지출 금액 (원)',
            showlegend=False
        )

    fig.update_layout(
        font=dict(size=12),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    return fig


def create_amount_chart(df: pd.DataFrame) -> go.Figure:
    """
    구매 금액 분포 차트 생성

    Args:
        df: 처리된 DataFrame

    Returns:
        plotly Figure 객체
    """
    fig = px.histogram(
        df,
        x='금액',
        nbins=20,
        title='구매 금액 분포',
        color_discrete_sequence=['#636EFA'],
        labels={'금액': '구매 금액 (원)', 'count': '구매 건수'}
    )

    fig.update_traces(
        hovertemplate='금액: ₩%{x:,.0f}<br>건수: %{y}<extra></extra>'
    )

    fig.update_layout(
        xaxis_title='구매 금액 (원)',
        yaxis_title='구매 건수',
        font=dict(size=12),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        showlegend=False
    )

    return fig


def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """
    월별 지출 추이 차트 생성

    Args:
        df: 처리된 DataFrame

    Returns:
        plotly Figure 객체
    """
    # 월별 집계
    monthly_df = df.copy()
    monthly_df['연월'] = monthly_df['날짜'].dt.to_period('M').astype(str)

    monthly_summary = monthly_df.groupby('연월').agg({
        '금액': 'sum',
        '날짜': 'count'
    }).reset_index()
    monthly_summary.columns = ['연월', '총_금액', '구매_건수']

    # 이중 축 차트
    fig = go.Figure()

    # 금액 바 차트
    fig.add_trace(go.Bar(
        x=monthly_summary['연월'],
        y=monthly_summary['총_금액'],
        name='총 지출 금액',
        marker_color='lightblue',
        yaxis='y',
        hovertemplate='%{x}<br>지출: ₩%{y:,.0f}<extra></extra>'
    ))

    # 구매 건수 라인 차트
    fig.add_trace(go.Scatter(
        x=monthly_summary['연월'],
        y=monthly_summary['구매_건수'],
        name='구매 건수',
        mode='lines+markers',
        marker=dict(size=8, color='red'),
        line=dict(width=2, color='red'),
        yaxis='y2',
        hovertemplate='%{x}<br>건수: %{y}건<extra></extra>'
    ))

    fig.update_layout(
        title='월별 지출 추이',
        xaxis=dict(title='연월'),
        yaxis=dict(
            title=dict(text='지출 금액 (원)', font=dict(color='lightblue')),
            tickfont=dict(color='lightblue')
        ),
        yaxis2=dict(
            title=dict(text='구매 건수', font=dict(color='red')),
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
