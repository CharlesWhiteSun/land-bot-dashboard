import sqlite3
import pandas as pd
import plotly.graph_objects as go
from nicegui import ui
from datetime import datetime

DB_PATH = 'ngui/database/real_estate.sqlite'

# 地區分類結構
AREA_GROUPS = {
    "北部": ["臺北", "新北", "基隆", "桃園", "新竹"],
    "中部": ["苗栗", "臺中", "南投", "彰化", "雲林"],
    "南部": ["嘉義", "臺南", "高雄", "屏東"],
    "東部": ["宜蘭", "花蓮", "臺東"],
    "離島": ["澎湖", "金門", "連江"]
}

# SQL 安全白名單
AVAILABLE_AREAS = sum(AREA_GROUPS.values(), [])

def query_avg_price(area, trade_object, year, house_type):
    conn = sqlite3.connect(DB_PATH)

    if area not in AVAILABLE_AREAS:
        raise ValueError(f"Invalid area/table name: {area}")

    sql = f'''
        SELECT 
            SUBSTR(`交易年月日`, 1, 4) || '-' || SUBSTR(`交易年月日`, 5, 2) as ym,
            ROUND(AVG(`總價元`) / 10000.0, 1) as avg_price_million
        FROM `{area}`
        WHERE 1=1
            AND `交易標的` = ?
            AND `交易年` = ?
            AND `屋況` = ?
        GROUP BY ym
        ORDER BY ym
    '''
    df = pd.read_sql_query(sql, conn, params=(trade_object, year, house_type))
    conn.close()
    return df

def render_data_analysis():
    container = ui.column().classes('w-full')

    with container:
        ui.label('📈 房價資料分析').style('font-size: 1.25rem; font-weight: bold;')
        LABEL_TEXT_STYLE = 'label-color=black'

        current_year = datetime.now().year
        year_options = [str(y) for y in range(current_year, 2011, -1)]

        # 第一列：區域、縣市
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center;'):
            area_group_select = ui.select(
                list(AREA_GROUPS.keys()),
                label='區域',
                value=None
            ).classes('w-48').props(LABEL_TEXT_STYLE)

            city_select = ui.select(
                [],
                label='縣市',
                value=None
            ).classes('w-48').props(LABEL_TEXT_STYLE)
            city_select.disable()

        # 第二列：交易標的、年度、屋況
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center;'):
            trade_object_select = ui.select(
                ['房地', '土地', '車位'],
                label='交易標的',
                value=None
            ).classes('w-48').props(LABEL_TEXT_STYLE)

            year_select = ui.select(
                year_options,
                label='年度',
                value=None  # ❗ 無預設值
            ).classes('w-48').props(LABEL_TEXT_STYLE)

            house_type_select = ui.select(
                ['新屋', '新古屋', '中古屋', '老屋', '預售屋'],
                label='屋況',
                value=None
            ).classes('w-48').props(LABEL_TEXT_STYLE)

        chart_container = ui.column().classes('w-full')

        # 當區域選擇改變時更新縣市選單
        def on_area_group_change(e):
            selected_group = area_group_select.value
            if selected_group and selected_group in AREA_GROUPS:
                city_select.options = AREA_GROUPS[selected_group]
                city_select.value = None
                city_select.enable()
            else:
                city_select.options = []
                city_select.value = None
                city_select.disable()
            city_select.update()

        area_group_select.on('update:model-value', on_area_group_change)

        # 查詢與繪圖邏輯
        def refresh_chart():
            if not all([
                city_select.value,
                trade_object_select.value,
                year_select.value,
                house_type_select.value
            ]):
                chart_container.clear()
                ui.notify('請完整選取縣市、交易標的、年度與屋況', type='warning', position='top')
                return

            try:
                df = query_avg_price(
                    city_select.value,
                    trade_object_select.value,
                    year_select.value,
                    house_type_select.value
                )
            except Exception as e:
                chart_container.clear()
                ui.notify(f'查詢錯誤：{str(e)}', type='negative', position='top')
                return

            chart_container.clear()
            if df.empty:
                ui.notify('查無資料', type='warning', position='top')
                return

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['ym'],
                y=df['avg_price_million'],
                mode='lines+markers',
                name='平均總價 (萬元)'
            ))
            fig.update_layout(
                title=f"{city_select.value} - {trade_object_select.value} - {year_select.value} 年 - {house_type_select.value} 平均總價走勢",
                xaxis_title='交易年-月份',
                yaxis_title='平均總價 (萬元)',
                xaxis_type='category',  # ← 加這行，強制以類別顯示，不轉為時間格式
                template='plotly_white',
                height=450,
            )

            with chart_container:
                ui.plotly(fig)

        # 搜尋按鈕
        ui.button('搜尋', icon='search', on_click=refresh_chart).classes('mt-2 bg-green-700 text-white')

        # 空的圖表容器
        chart_container

    return container
