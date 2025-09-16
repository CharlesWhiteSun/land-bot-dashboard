from datetime import datetime
from nicegui import ui

from enums.constants import SystemType
from ngui.components.countdown_button import *
from ngui.components.main_chart_func import *
from ngui.components.main_sql import *


MAIN_CONTENT = ui.column().classes('w-full') # 全域主內容容器
CHART_CONTAINER = ui.column().classes('w-full items-center')  # 放圖表的區塊

def render_main():
    MAIN_CONTENT.clear()
    with MAIN_CONTENT:
        ui.label('🏙️ Welcome!').style('font-size: 1.3rem; font-weight: 600;')
        ui.markdown(f'''
            - 歡迎使用 {SystemType.TITLE_NAME.value}
            - 這裡整合、視覺化一些內政部不動產實際資料供應系統的成交案件資料
            - 關於不動產資料都歸於 內政部地政司(Dept of Land Administration M.O.I.) 所有
            - 本儀表板僅供學術研究與個人使用，請勿用於商業用途
            
        ''')
        ui.markdown()

        ui.separator()
        ui.label('🗺️ Instructions').style('font-size: 1.3rem; font-weight: 600;')
        ui.markdown('''
            - 點選左側選單可切換頁面
            - 有任何問題，請先確認資料來源是否正確
            - 其他建議或需求，請聯繫開發者
            - 後續若有成交車位查詢需求，可再視狀況更新
        ''')
        ui.markdown()

# 地區分類結構
AREA_GROUPS = {
    "北部": ["臺北", "新北", "基隆", "桃園", "新竹"],
    "中部": ["苗栗", "臺中", "南投", "彰化", "雲林"],
    "南部": ["嘉義", "臺南", "高雄", "屏東"],
    "東部": ["宜蘭", "花蓮", "臺東"],
    "離島": ["澎湖", "金門", "連江"]
}

# 年份、分類、屋況
CURRENT_YEAR = datetime.now().year
YEAR_SELECTIONS = [str(year) for year in range(CURRENT_YEAR, 2010, -1)] + ['~2010']
TYPE_SELECTIONS = ["房地", "土地"]
HOUSE_STATUS_SELECTIONS = ["預售屋", "新屋", "新古屋", "中古屋", "老屋"]


# 查詢價格分佈圖
def render_data_distribution():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        # 第一列：區域 + 縣市
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center;'):
            ui.html('<span style="color:red">*</span>區域：')
            area_select = ui.select(
                list(AREA_GROUPS.keys()),
                value=None,
            ).classes('w-48')

            ui.html('<span style="color:red">*</span>縣市：')
            city_select = ui.select([], value=None).classes('w-48')
            city_select.disable()

        def on_area_change():
            selected_area = area_select.value
            if selected_area in AREA_GROUPS:
                city_select.options = AREA_GROUPS[selected_area]
                city_select.value = None
                city_select.enable()
            else:
                city_select.options = []
                city_select.value = None
                city_select.disable()
            city_select.update()

        area_select.on('update:model-value', on_area_change)

        # 查詢按鈕
        def on_search_click() -> bool:
            with MAIN_CONTENT:
                year_value = year_select.value
                city_value = city_select.value
                type_value = type_select.value
                status_value = status_select.value

                # 檢查年份與縣市是否有填
                if not year_value and not city_value:
                    ui.notify('[成交年份] 與 [縣市] 皆為必要搜尋條件', type='warning', position='top')
                    return False
                if not year_value:
                    ui.notify('[成交年份] 為必要搜尋條件', type='warning', position='top')
                    return False
                if not city_value:
                    ui.notify('[縣市] 為必要搜尋條件', type='warning', position='top')
                    return False

                # 印出所有選項的值供檢查
                print()
                print(f" - 成交年份: {year_value}")
                print(f" - 縣市: {city_value}")
                print(f" - 分類: {type_value}")
                print(f" - 屋況: {status_value}")

                df = query_distribution_data(year_value, city_value, type_value, status_value)
                if df.empty:
                    msg = f" {year_value} {city_value} "
                    if type_value:
                        msg += f"{type_value}分類 "
                    if status_value:
                        msg += f"{status_value} "
                    ui.notify(f'查無 {msg} 資料', type='warning', position='top')
                    return False
                
                CHART_CONTAINER.clear()
                fig = create_distribution_chart(df)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')
                return True
            
        # 第二列：成交年份 + 分類 + 屋況
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center; margin-top: 12px;'):
            ui.html('<span style="color:red">*</span>成交年份：')
            year_select = ui.select(YEAR_SELECTIONS, value=None).classes('w-36')

            ui.label('分類：')
            type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

            ui.label('屋況：')
            status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

            NotifyDisableButton('搜尋', icon='search', on_click=on_search_click)


# 查詢單一年份房價走勢
def render_data_trends():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        # 第一列：區域 + 縣市
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center;'):
            ui.html('<span style="color:red">*</span>區域：')
            area_select = ui.select(
                list(AREA_GROUPS.keys()),
                value=None,
            ).classes('w-48')

            ui.html('<span style="color:red">*</span>縣市：')
            city_select = ui.select([], value=None).classes('w-48')
            city_select.disable()

        def on_area_change():
            selected_area = area_select.value
            if selected_area in AREA_GROUPS:
                city_select.options = AREA_GROUPS[selected_area]
                city_select.value = None
                city_select.enable()
            else:
                city_select.options = []
                city_select.value = None
                city_select.disable()
            city_select.update()

        area_select.on('update:model-value', on_area_change)

        
        # 查詢按鈕
        def on_search_click():
            with MAIN_CONTENT:
                CHART_CONTAINER.clear()
                city_value = city_select.value
                year_value = year_select.value
                trade_type = type_select.value
                house_status = status_select.value

                # 檢查年份與縣市是否有填
                if not year_value and not city_value:
                    ui.notify('[縣市] 與 [成交年份] 皆為必要搜尋條件', type='warning', position='top')
                    return False
                if not year_value:
                    ui.notify('[成交年份] 為必要搜尋條件', type='warning', position='top')
                    return False
                if not city_value:
                    ui.notify('[縣市] 為必要搜尋條件', type='warning', position='top')
                    return False

                try:
                    df = query_avg_price(city_value, trade_type, year_value, house_status)
                except Exception as e:
                    ui.notify(f'查詢失敗：{str(e)}', type='negative', position='top')
                    return

                if df.empty:
                    ui.notify('查無資料', type='warning', position='top')
                    return

                fig = create_price_trend_chart(df, city_value, trade_type, year_value, house_status)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')

        # 第二列：成交年份 + 分類 + 屋況
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center; margin-top: 12px;'):
            ui.html('<span style="color:red">*</span>成交年份：')
            year_select = ui.select(YEAR_SELECTIONS, value=None).classes('w-36')

            ui.label('分類：')
            type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

            ui.label('屋況：')
            status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

            NotifyDisableButton('搜尋', icon='search', on_click=on_search_click)


# 查詢多年份房價走勢
def render_multi_year_trends():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        ui.label('📊 多年份房價走勢圖').style('font-size: 1.3rem; font-weight: bold;')

        # 第一列：區域 + 縣市
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center;'):
            ui.html('<span style="color:red">*</span>區域：')
            area_select = ui.select(list(AREA_GROUPS.keys()), value=None).classes('w-48')

            ui.html('<span style="color:red">*</span>縣市：')
            city_select = ui.select([], value=None).classes('w-48')
            city_select.disable()

        def on_area_change():
            selected_area = area_select.value
            if selected_area in AREA_GROUPS:
                city_select.options = AREA_GROUPS[selected_area]
                city_select.value = None
                city_select.enable()
            else:
                city_select.options = []
                city_select.value = None
                city_select.disable()
            city_select.update()

        area_select.on('update:model-value', on_area_change)

        # 第二列：年份（必要欄位）
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center; margin-top: 12px;'):
            ui.html('<span style="color:red">*</span>成交年份：')
            year_checkboxes = {}
            for year in YEAR_SELECTIONS[:-1]:
                year_checkboxes[year] = ui.checkbox(str(year)).classes('w-20')


        # 第三列：交易標的 + 屋況
        with ui.row().style('gap: 12px; flex-wrap: wrap; align-items: center; margin-top: 12px;'):
            ui.label('交易標的：')
            trade_type_select = ui.select(TYPE_SELECTIONS, value=None).classes('w-36')
            ui.label('屋況：')
            house_status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None).classes('w-36')

            def on_search():
                with CHART_CONTAINER:
                    CHART_CONTAINER.clear()
                    city = city_select.value
                    trade_type = trade_type_select.value
                    selected_years = [year for year, checkbox in year_checkboxes.items() if checkbox.value]
                    house_status = house_status_select.value

                    # 驗證必要欄位
                    if not selected_years and not city:
                        ui.notify('[縣市] 與 [成交年份] 皆為必要搜尋條件', type='warning', position='top')
                        return False
                    if not city:
                        ui.notify('請選擇縣市', type='warning')
                        return
                    if not selected_years:
                        ui.notify('請至少選擇 2 個年份', type='warning')
                        return

                    try:
                        df = query_multi_year_price(city, trade_type, selected_years, house_status)
                    except Exception as e:
                        ui.notify(f'查詢失敗：{e}', type='negative')
                        return

                    if df.empty:
                        ui.notify('查無資料', type='warning')
                        return

                    fig = create_multi_year_trend_chart(df, city, trade_type, house_status)
                    ui.plotly(fig).classes('w-full')

            ui.button('搜尋', icon='search', on_click=on_search).classes('bg-green-700 text-white')


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
