import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_distribution_chart(df: pd.DataFrame):
    hover_cols = ["鄉鎮市區", "建物型態", "建物每坪單價萬元", "主要用途", "房齡", "屋況"]
    df[hover_cols] = df[hover_cols].fillna("")

    fig = px.scatter(
        df,
        template="plotly_dark",
        title="價格分佈圖",
        x="建物坪數",
        y="建物總價萬元",
        labels={"建物坪數": "面積(坪)", "建物總價萬元": "總價(萬元)"},
        hover_data=hover_cols,
        color="屋況",
        opacity=0.8,
        render_mode='webgl',  # 加入 WebGL 模式
    )
    fig.update_traces(marker=dict(size=5))
    return fig

def create_price_trend_chart(df: pd.DataFrame, city: str, trade_type: str, year: str, house_status: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ym'],
        y=df['avg_price_million'],
        mode='lines+markers',
        name='平均總價 (萬元)'
    ))
    fig.update_layout(
        title=f"{city} - {trade_type} - {year} 年 - {house_status} 平均總價走勢",
        xaxis_title='交易年月',
        yaxis_title='平均總價 (萬元)',
        xaxis_type='category',
        template='plotly_dark',
        height=450
    )
    return fig
