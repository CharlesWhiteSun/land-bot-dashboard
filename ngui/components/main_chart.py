import pandas as pd
import plotly.express as px

def create_price_distribution_chart(df: pd.DataFrame):
    hover_cols = ["鄉鎮市區", "建物型態", "建物每坪單價萬元", "主要用途", "房齡", "屋況"]
    df[hover_cols] = df[hover_cols].fillna("")

    fig = px.scatter(
        df,
        title="價格分佈圖",
        x="建物坪數",
        y="建物總價萬元",
        labels={"建物坪數": "面積(坪)", "建物總價萬元": "總價(萬元)"},
        hover_data=hover_cols,
    )
    return fig
