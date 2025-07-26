import datetime
from nicegui import ui

from ngui.components.main_chart import *
from ngui.components.main_sql import query_city_data


main_content = ui.column().classes('w-full') # 全域主內容容器
chart_container = ui.column().classes('w-full items-center')  # 放圖表的區塊

def render_main():
    main_content.clear()
    with main_content:
        ui.label('🏙️ Welcome!').style('font-size: 1.25rem; font-weight: 600;')
        ui.markdown('''
            - 歡迎使用 Housing Insight Dashboard
            - 這裡整合了一些內政部不動產實際資料供應系統的成交案件資料
            - 關於不動產資料都歸於 內政部地政司(Dept of Land Administration M.O.I.) 所有
            - 本儀表板僅供學術研究與個人使用，請勿用於商業用途
            
        ''')
        ui.markdown()

        ui.separator()
        ui.label('🗺️ Instructions').style('font-size: 1.25rem; font-weight: 600;')
        ui.markdown('''
            - 點選左側選單可切換頁面
            - 有任何問題，請先確認資料來源是否正確
            - 其他建議或需求，請聯繫開發者
            
        ''')
        ui.markdown()


# 分析頁面
def render_data_analysis():
    main_content.clear()
    with main_content:
        with ui.row().classes('items-center q-gutter-md'):
            current_year = datetime.datetime.now().year
            year_options = [str(year) for year in range(current_year, 2011, -1)] + ['~2011']

            ui.label('成交年份：')
            year_select = ui.select(year_options, label=None)

            ui.label('縣市：')
            city_select = ui.select(["基隆", "臺北", "新北", "桃園", "新竹", "苗栗", "臺中", "南投", "彰化", "雲林",
                       "嘉義", "臺南", "高雄", "屏東", "宜蘭", "花蓮", "臺東", "澎湖", "金門", "連江"], label=None)

            ui.label('分類：')
            type_select = ui.select(["房地", "土地", "車位", "其他"], label=None)

            ui.label('屋況：')
            status_select = ui.select(["新屋", "新古屋", "中古屋", "老屋"], label=None)

            def on_search_click():
                year_value = year_select.value
                city_value = city_select.value
                type_value = type_select.value
                status_value = status_select.value

                # 檢查年份與縣市是否有填
                if not year_value and not city_value:
                    ui.notify('[成交年份] 與 [縣市] 皆為必要搜尋條件', type='warning', position='top')
                    return
                if not year_value:
                    ui.notify('[成交年份] 為必要搜尋條件', type='warning', position='top')
                    return
                if not city_value:
                    ui.notify('[縣市] 為必要搜尋條件', type='warning', position='top')
                    return

                # 印出所有選項的值供檢查
                print()
                print(f" - 成交年份: {year_value}")
                print(f" - 縣市: {city_value}")
                print(f" - 分類: {type_value}")
                print(f" - 屋況: {status_value}")

                df = query_city_data(year_value, city_value, type_value, status_value)
                if df.empty:
                    msg = f" {year_value} {city_value} "
                    if type_value:
                        msg += f"{type_value}分類 "
                    if status_value:
                        msg += f"{status_value} "
                    ui.notify(f'查無 {msg} 資料', type='warning', position='top')
                    return
                
                fig = create_price_distribution_chart(df)

                chart_container.clear()  # 清除舊圖表
                with chart_container:
                    ui.plotly(fig).classes('w-full')

            ui.button('搜尋', icon='search', on_click=on_search_click)

# 主內容畫面渲染
def apply_main_body_styles():
    ui.add_body_html('''
    <style>
        .q-page {
            background-color: black !important;
            color: white !important;
            padding: 1.5rem;
        }
    </style>
    ''')

# 初始化樣式
apply_main_body_styles()
