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
    fig.update_layout(height=600)
    return fig

def create_3d_distribution_chart(df: pd.DataFrame):
    import plotly.express as px

    hover_cols = ["縣市", "鄉鎮市區", "建物型態", "主要用途", "屋況"]
    df[hover_cols] = df[hover_cols].fillna("")

    fig = px.scatter_3d(
        df,
        x="建物坪數",
        y="房齡",
        z="建物總價萬元",
        color="縣市",
        hover_data=hover_cols,
        template="plotly_dark",
        title="多縣市 3D 價格分佈圖",
        opacity=1,
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        height=1000,
        scene=dict(
            xaxis_title="建物坪數",
            yaxis_title="房齡（年）",
            zaxis_title="建物總價萬元"
        )
    )
    return fig


def create_price_trend_chart(df: pd.DataFrame, city: str, trade_type: str, year: str, house_status: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ym'],
        y=df['avg_price_million'],
        mode='lines+markers',
        name='平均總價 (萬元)'
    ))

    title_parts = [city]
    if trade_type:
        title_parts.append(trade_type)
    title_parts.append(f"{year} 年")
    if house_status:
        title_parts.append(house_status)
    title_text = " - ".join(title_parts) + " 平均總價走勢"

    fig.update_layout(
        title=title_text,
        xaxis_title='交易年月',
        yaxis_title='平均總價 (萬元)',
        xaxis_type='category',
        template='plotly_dark',
        height=450
    )
    return fig


def create_multi_year_trend_chart(df: pd.DataFrame, city: str, trade_type: str, house_status: str):
    fig = go.Figure()

    # 以年份排序（新到舊），然後畫圖
    for year, year_df in df.groupby('year'):
        year_df['year'] = int(year)  # 確保是 int

    # 排序年份：從大到小（新→舊）
    for year in sorted(df['year'].unique(), reverse=True):
        year_df = df[df['year'] == year]
        fig.add_trace(go.Scatter(
            x=year_df['month'],
            y=year_df['avg_price_million'],
            mode='lines+markers',
            name=str(year)
        ))

    # 動態組裝 title
    title_parts = [city]
    if trade_type:
        title_parts.append(trade_type)
    if house_status:
        title_parts.append(house_status)
    title_text = " - ".join(title_parts) + " 多年份趨勢（月對齊）"

    fig.update_layout(
        title=title_text,
        xaxis_title='月份',
        yaxis_title='平均總價 (萬元)',
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        template='plotly_dark',
        height=500
    )
    return fig
