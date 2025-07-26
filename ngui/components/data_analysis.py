import sqlite3
import pandas as pd
import plotly.graph_objects as go
from nicegui import ui


DB_PATH = 'ngui/database/real_estate.sqlite'


def query_avg_price(trade_object, year, house_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = '''
        SELECT 交易年月日, AVG(總價元) as avg_price
        FROM '臺北市_不動產買賣'
        WHERE '交易標的' = ? 
            AND '年度' = ? 
            AND '屋況' = ?
        GROUP BY 交易年月日
        ORDER BY 交易年月日
    '''
    df = pd.read_sql_query(sql, conn, params=(trade_object, year, house_type))
    conn.close()
    return df


def render_data_analysis():
    container = ui.column().classes('w-full')

    with container:
        ui.label('📈 房價資料分析').style('font-size: 1.25rem; font-weight: bold;')

        # 篩選條件
        with ui.row():
            city_select = ui.select(
                ['房地', '土地', '車位'],
                label='交易標的'
            ).classes('w-48')

            year_select = ui.select(
                [str(y) for y in range(101, 115)],
                label='年度'
            ).classes('w-48')

            quarter_select = ui.select(
                ['新屋', '新古屋', '中古屋', '老屋', '預售屋'],
                label='屋況'
            ).classes('w-48')

        # 查詢按鈕與圖表容器
        chart_container = ui.column().classes('w-full')

        def refresh_chart():
            quarter_map = {'第1季': 'S1', '第2季': 'S2', '第3季': 'S3', '第4季': 'S4'}
            quarter_code = quarter_map.get(quarter_select.value)

            if not all([city_select.value, year_select.value, quarter_code]):
                chart_container.clear()
                with chart_container:
                    ui.label('請完整選取城市、年度與季別').style('color: red;')
                return

            df = query_avg_price(city_select.value, year_select.value, f"{year_select.value}{quarter_code}")

            chart_container.clear()
            if df.empty:
                with chart_container:
                    ui.label('查無資料').style('color: red;')
                return

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['交易年月日'], y=df['avg_price'], mode='lines+markers', name='平均總價'))
            fig.update_layout(
                title=f'{city_select.value} {year_select.value} 年 {quarter_select.value} 平均總價走勢',
                xaxis_title='交易日期',
                yaxis_title='平均總價 (元)',
                template='plotly_white',
                height=450,
            )

            with chart_container:
                ui.plotly(fig)

        ui.button('搜尋', icon='search', on_click=refresh_chart).classes('mt-2 bg-green-700 text-white')
        chart_container  # 先保留空容器

    return container
