import sqlite3
import pandas as pd
import plotly.graph_objects as go
from nicegui import ui


DB_PATH = 'ngui/database/real_estate.sqlite'


def query_avg_price(trade_object, year, house_type):
    conn = sqlite3.connect(DB_PATH)

    sql = '''
        SELECT `交易年月日`, AVG(`總價元`) as avg_price
        FROM `基隆`
        WHERE 1=1
            AND `交易標的` = ? 
            AND `交易年` = ? 
            AND `屋況` = ?
        GROUP BY `交易年月日`
        ORDER BY `交易年月日`
    '''
    df = pd.read_sql_query(sql, conn, params=(trade_object, year, house_type))
    conn.close()
    return df


def render_data_analysis():
    container = ui.column().classes('w-full')

    with container:
        ui.label('📈 房價資料分析').style('font-size: 1.25rem; font-weight: bold;')
        LABEL_TEXT_STYLE = 'label-color=black'

        # ➤ 搜尋欄位
        with ui.row():
            trade_object_select = ui.select(
                ['房地', '土地', '車位'],
                label='交易標的'
            ).classes('w-48').props(LABEL_TEXT_STYLE)

            year_select = ui.select(
                [str(y) for y in range(2012, 2026)],
                label='年度'
            ).classes('w-48').props(LABEL_TEXT_STYLE)

            house_type_select = ui.select(
                ['新屋', '新古屋', '中古屋', '老屋', '預售屋'],
                label='屋況'
            ).classes('w-48').props(LABEL_TEXT_STYLE)

        # ➤ 圖表區塊
        chart_container = ui.column().classes('w-full')

        # ➤ 查詢與繪圖邏輯
        def refresh_chart():
            if not all([trade_object_select.value, year_select.value, house_type_select.value]):
                chart_container.clear()
                with chart_container:
                    ui.label('請完整選取交易標的、年度與屋況').style('color: red;')
                return

            df = query_avg_price(
                trade_object_select.value,
                year_select.value,
                house_type_select.value
            )

            chart_container.clear()
            if df.empty:
                with chart_container:
                    ui.label('查無資料').style('color: red;')
                return

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['交易年月日'],
                y=df['avg_price'],
                mode='lines+markers',
                name='平均總價'
            ))
            fig.update_layout(
                title=f'{trade_object_select.value} {year_select.value} 年 {house_type_select.value} 平均總價走勢',
                xaxis_title='交易日期',
                yaxis_title='平均總價 (元)',
                template='plotly_white',
                height=450,
            )

            with chart_container:
                ui.plotly(fig)

        # ➤ 查詢按鈕
        ui.button('搜尋', icon='search', on_click=refresh_chart).classes('mt-2 bg-green-700 text-white')

        # ➤ 空的圖表容器佔位
        chart_container

    return container
