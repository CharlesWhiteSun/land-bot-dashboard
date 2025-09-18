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

    fig.update_layout(
        title=f"{year} 年 {trade_type or ''} {house_status or ''} 平均總價走勢",
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

    fig.update_layout(
        title=f"{year} 年 {trade_type or ''} {house_status or ''} 多年份趨勢（月對齊）",
        xaxis_title='月份',
        yaxis_title='平均總價 (萬元)',
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        template='plotly_dark',
        height=500
    )
    return fig


def create_single_year_multi_city_trend_chart_3d(df: pd.DataFrame, year: str, trade_type: str, house_status: str):
    fig = go.Figure()

    # 每個縣市一條線，x軸屋齡，y軸月份（可用月份作為 y 軸區分，但你的需求是 y 軸縣市，這邊用縣市作 y 軸分組，但3D座標無法直接用字串作軸，需轉成類別數字）
    # 但 Plotly 3D座標只能是數字，無法直接用字串當軸 => 需把縣市轉成數字作為 y 軸，再用 ticktext 顯示名稱

    cities = sorted(df['city'].unique())
    city_to_y = {city: i for i, city in enumerate(cities)}  # 縣市映射成數字 y 軸

    for city in cities:
        city_df = df[df['city'] == city]
        fig.add_trace(go.Scatter3d(
            x=city_df['house_age'],
            y=[city_to_y[city]] * len(city_df),
            z=city_df['avg_price_million'],
            mode='lines+markers',
            name=city,
            line=dict(width=4),
            marker=dict(size=4),
            hovertemplate=(
                f"<b>{city} ({year})</b><br>" +
                "屋齡: %{x} 年<br>" +
                "平均總價: %{z} 萬元"
            )
        ))

    # 設定 y 軸的 ticktext 與 tickvals，顯示縣市名稱
    fig.update_layout(
        title=f"{year} 年 {trade_type or ''} {house_status or ''} 多縣市屋齡 3D 趨勢圖",
        scene=dict(
            xaxis=dict(title='屋齡（年）'),
            yaxis=dict(
                title='縣市',
                tickmode='array',
                tickvals=list(city_to_y.values()),
                ticktext=list(city_to_y.keys())
            ),
            zaxis=dict(title='平均總價 (萬元)'),
        ),
        height=700,
        template='plotly_dark',
        margin=dict(l=0, r=0, b=0, t=50)
    )

    return fig

