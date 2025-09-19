from datetime import datetime
from nicegui import ui

from enums.constants import SystemType
from ngui.components.countdown_button import *
from ngui.components.main_chart_func import *
from ngui.components.main_sql import *
from utils.logger import *
from ngui.components.countdown_button import CountdownButton

MAIN_CTX_STYLE = 'padding: 1rem; font-size: 1rem;'
MAIN_LABEL_STYLE = 'font-size: 1.3rem; font-weight: 600;'

MAIN_CONTENT = ui.column().classes('w-full').style(MAIN_CTX_STYLE) # 全域主內容容器
CHART_CONTAINER = ui.column().classes('w-full items-center')  # 放圖表的區塊

def render_main():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()
    
    with MAIN_CONTENT:
        ui.label('🏙️ Welcome!').style(MAIN_LABEL_STYLE)
        ui.markdown(f'''
            - 歡迎使用 {SystemType.TITLE_NAME.value}
            - 這裡整合、視覺化一些內政部不動產實際資料供應系統的成交案件資料
            - 關於不動產資料都歸於 內政部地政司(Dept of Land Administration M.O.I.) 所有
            - 本儀表板僅供學術研究與個人使用，請勿用於商業用途
        ''')
        ui.markdown()

        ui.separator()

        ui.label('🗺️ Instructions').style(MAIN_LABEL_STYLE)
        ui.markdown('''
            - Menu, Charts 可收放子選單；右上按鈕可收放 Side Bar 選單
            - 有任何問題，請先確認資料來源是否正確
            - 其他建議或需求，請聯繫開發者
            - 後續若有其他資料如成交車位等查詢需求，可再視狀況更新
        ''')
        ui.markdown()

        ui.separator()

        ui.label('⚠️ Notice').style(MAIN_LABEL_STYLE)
        ui.markdown('''
            - 為維護系統穩定與公平使用，請勿進行以下行為：
                <div style="margin-left: 20px;">
                大量、頻繁重複查詢以導致系統負載異常<br>
                自動化工具或爬蟲行為存取資料<br>
                以不當方式干擾他人使用或測試系統弱點<br>
                </div>
            - 系統設有黑名單機制，違反上述規定者會被限制存取一段時間
            - 使用時請遵守基本網路禮儀，尊重開發者與其他使用者
        ''')

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

ROW_STYLE_NORMAL = 'gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 8px;'
MAIN_CTX_STYLE = """
    padding: 1rem;
    font-size: 1rem;
"""

# 縣市價坪分佈圖
def render_data_distribution():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()
   
    with MAIN_CONTENT:
        with ui.expansion('縣市價坪分佈圖', icon='description', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            ui.markdown('''
                - 這個區域讓您根據成交年份、縣市、分類與屋況查詢不同的不動產價格分佈
                - 成交年份與縣市是必要的查詢條件，請確保選擇後再進行查詢
                - 在選擇分類(如房地或土地)和屋況(如預售屋、新屋、中古屋等)後，系統將顯示相關資料
            ''')
            
            ui.markdown('''
            - 以下進階選項可協助您提升圖表的可讀性與資料品質：
                <div style="margin-left: 20px;">
                移除價格最高邊界值(%)：排除極端高價的資料點，避免過度拉高平均值<br>
                移除價格為 0 的物件：可過濾異常或填寫錯誤的資料，提升準確性<br>
                僅保留總價 < 1 億資料：可排除大宗交易或特殊物件的干擾
                </div>
            ''')

            ui.markdown('''
            - 若查詢結果為空，可能是因為：
                <div style="margin-left: 20px;">
                選擇的條件過於嚴格，導致無符合資料<br>
                部分縣市在該年份下無成交紀錄<br>
                所選屋況或交易標的尚無統計資料
                </div>
            ''')

        with ui.expansion('搜尋條件', icon='list', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            # 第一列
            with ui.row().style(ROW_STYLE_NORMAL):
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

            async def on_search_click() -> bool:
                year_value = year_select.value
                city_value = city_select.value
                type_value = type_select.value
                status_value = status_select.value
                remove_percent = remove_outliers_slider.value / 100
                remove_zero = remove_zero_checkbox.value
                limit_100m = filter_under_100m_checkbox.value

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

                try:
                    df = query_distribution_data(
                        year_value, city_value, type_value, status_value, 
                        remove_percent, remove_zero, limit_100m)
                except Exception as e:
                    ui.notify('查詢失敗，請反應給站長協助處理', type='negative', position='top')
                    log_warning(f'查詢 [不動產分佈圖] 失敗：{str(e)}')
                    return False

                if df.empty:
                    msg = f" {year_value} {city_value} "
                    if type_value:
                        msg += f"{type_value}分類 "
                    if status_value:
                        msg += f"{status_value} "
                    ui.notify(f'查無 {msg} 資料', type='warning', position='top')
                    return False
                
                CHART_CONTAINER.clear()
                fig = create_distribution_chart(df, city_value, year_value)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')
                return True
                
            # 第二列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>成交年份：')
                year_select = ui.select(YEAR_SELECTIONS, value=None).classes('w-36')

                ui.label('分類：')
                type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

                ui.label('屋況：')
                status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')


            # 第三列
            with ui.row().style(ROW_STYLE_NORMAL):
                remove_zero_checkbox = ui.checkbox('移除價格為 0')
                filter_under_100m_checkbox = ui.checkbox('僅保留總價 < 1 億資料')

            # 第四列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.label('移除價格最高邊界值(%)').style('font-weight: 600; margin-right: 12px;')
                remove_outliers_slider = ui.slider(min=0, max=25, value=0, step=1).classes('w-72')
                percentage_label = ui.label(f'{remove_outliers_slider.value}%').style('min-width: 30px; text-align: left; margin-left: 8px;')
                def update_label(event):
                    val = event.args  # 直接用 event.args
                    percentage_label.set_text(f'{val}%')
                remove_outliers_slider.on('update:model-value', update_label)

                CountdownButton('搜尋', icon='search', on_click=on_search_click, color='primary')

        ui.separator()


# 多縣市 3D 價坪分佈圖
def render_multi_city_3d():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        with ui.expansion('多縣市 3D 價坪分佈圖', icon='description', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            ui.markdown('''
                - 選擇多個縣市與單一年份，將顯示建物坪數、總價與房齡的 3D 分佈圖
                - 成交年份與縣市(2~3)是必要的查詢條件，請確保選擇後再進行查詢
                - 在選擇分類(如房地或土地)和屋況(如預售屋、新屋、中古屋等)後，系統將顯示相關資料
            ''')

            ui.markdown('''
            - 以下進階選項可協助您提升圖表的可讀性與資料品質：
                <div style="margin-left: 20px;">
                移除價格最高邊界值(%)：排除極端高價的資料點，避免過度拉高平均值<br>
                移除價格為 0 的物件：可過濾異常或填寫錯誤的資料，提升準確性<br>
                僅保留總價 < 1 億資料：可排除大宗交易或特殊物件的干擾
                </div>
            ''')

            ui.markdown(''' 
            - 若查詢結果為空，可能是因為：
                <div style="margin-left: 20px;">
                選擇的條件過於嚴格，導致無符合資料<br>
                部分縣市在該年份下無成交紀錄<br>
                所選屋況或交易標的尚無統計資料
                </div>
            ''')

        with ui.expansion('搜尋條件', icon='list', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            # 第一列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>縣市：')
                city_checkboxes = {}
                city_list = [
                    "臺北", "新北", "基隆", "桃園", "新竹",
                    "苗栗", "臺中", "南投", "彰化", "雲林",
                    "嘉義", "臺南", "高雄", "屏東",
                    "宜蘭", "花蓮", "臺東",
                    "澎湖", "金門", "連江"
                ]
                for city in city_list:
                    city_checkboxes[city] = ui.checkbox(city).classes('w-20')

            # 第二列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>成交年份：')
                year_select = ui.select(YEAR_SELECTIONS[:-1], value=None).classes('w-36')  # 不含 ~2010

                ui.label('分類：')
                type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

                ui.label('屋況：')
                status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

            # 第三列
            with ui.row().style(ROW_STYLE_NORMAL):
                remove_zero_checkbox = ui.checkbox('移除價格為 0')
                filter_under_100m_checkbox = ui.checkbox('僅保留總價 < 1 億資料')

            # 搜尋按鈕
            async def on_search_click():
                selected_cities = [city for city, checkbox in city_checkboxes.items() if checkbox.value]
                selected_year = year_select.value
                type_value = type_select.value
                status_value = status_select.value
                remove_percent = remove_outliers_slider.value / 100
                remove_zero = remove_zero_checkbox.value
                limit_100m = filter_under_100m_checkbox.value

                # 驗證輸入條件
                if not selected_cities or not selected_year:
                    ui.notify('[成交年份] 與 [縣市] 皆為必要搜尋條件', type='warning', position='top')
                    return
                if len(selected_cities) < 2:
                    ui.notify('請至少選擇 2 個縣市選項', type='warning', position='top')
                    return
                if len(selected_cities) > 3:
                    ui.notify('縣市選項請選擇 3 個(含)以內', type='warning', position='top')
                    return

                try:
                    df = query_multi_city_3d_data(
                        selected_cities, selected_year, type_value, status_value, 
                        remove_percent, remove_zero, limit_100m)
                except Exception as e:
                    ui.notify('查詢失敗，請反應給站長協助處理', type='negative', position='top')
                    log_warning(f'查詢 [多縣市3D圖] 失敗：{str(e)}')
                    return

                if df.empty:
                    ui.notify('查無資料', type='warning', position='top')
                    return

                CHART_CONTAINER.clear()
                with CHART_CONTAINER:
                    fig = create_3d_distribution_chart(df, selected_cities, selected_year)
                    ui.plotly(fig).classes('w-full')

            # 第四列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.label('移除價格最高邊界值(%)').style('font-weight: 600; margin-right: 12px;')
                remove_outliers_slider = ui.slider(min=0, max=25, value=0, step=1).classes('w-72')
                percentage_label = ui.label(f'{remove_outliers_slider.value}%').style(
                    'min-width: 30px; text-align: left; margin-left: 8px;'
                )
                def update_label(event):
                    val = event.args
                    percentage_label.set_text(f'{val}%')
                remove_outliers_slider.on('update:model-value', update_label)

                CountdownButton('搜尋', icon='search', on_click=on_search_click, color='primary')

        ui.separator()


# 縣市價格年度趨勢圖
def render_data_trends():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        with ui.expansion('縣市價格年度趨勢圖', icon='description', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            ui.markdown(''' 
            - 這個區域讓您根據成交年份、縣市、分類與屋況查詢單一年份的房價走勢
            - 成交年份與縣市是必要的查詢條件，請確保選擇後再進行查詢
            - 在選擇分類(如房地或土地)和屋況(如預售屋、新屋、中古屋等)後，系統將顯示相關資料
            ''')
            
            ui.markdown(''' 
            - 若查詢結果為空，可能是因為：
                <div style="margin-left: 20px;">
                選擇的條件過於嚴格，導致無符合資料<br>
                部分縣市在該年份下無成交紀錄<br>
                所選屋況或交易標的尚無統計資料
                </div>
            ''')

        with ui.expansion('搜尋條件', icon='list', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            # 第一列
            with ui.row().style(ROW_STYLE_NORMAL):
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
            async def on_search_click():
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
                    ui.notify('查詢失敗，請反應給站長協助處理', type='negative', position='top')
                    log_warning(f'查詢 [不動產年度趨勢圖] 失敗：{str(e)}')
                    return

                if df.empty:
                    ui.notify('查無資料', type='warning', position='top')
                    return

                CHART_CONTAINER.clear()
                fig = create_price_trend_chart(df, city_value, trade_type, year_value, house_status)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')

            # 第二列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>成交年份：')
                year_select = ui.select(YEAR_SELECTIONS, value=None).classes('w-36')

                ui.label('分類：')
                type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

                ui.label('屋況：')
                status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

                CountdownButton('搜尋', icon='search', on_click=on_search_click, color='primary')

            ui.separator()


# 多年度價格趨勢圖
def render_multi_year_trends():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        with ui.expansion('多年度價格趨勢圖', icon='description', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            ui.markdown(''' 
            - 這個區域讓您查詢跨年份的房價變化趨勢，協助觀察長期市場走向
            - 成交年份(可選 2~5 個項目)與縣市是必要的查詢條件，請確保選擇後再進行查詢
            - 在選擇分類(如房地或土地)和屋況(如預售屋、新屋、中古屋等)後，系統將顯示相關資料
            ''')

            ui.markdown(''' 
            - 若查詢結果為空，可能是因為：
                <div style="margin-left: 20px;">
                選擇的條件過於嚴格，導致無符合資料<br>
                部分縣市在該年份下無成交紀錄<br>
                所選屋況或交易標的尚無統計資料
                </div>
            ''')

        with ui.expansion('搜尋條件', icon='list', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            # 第一列
            with ui.row().style(ROW_STYLE_NORMAL):
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

            # 第二列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>成交年份：')
                year_checkboxes = {}
                for year in YEAR_SELECTIONS[:-1]:
                    year_checkboxes[year] = ui.checkbox(str(year)).classes('w-20')

            async def on_search():
                city = city_select.value
                trade_type = trade_type_select.value
                selected_years = [year for year, checkbox in year_checkboxes.items() if checkbox.value]
                house_status = house_status_select.value

                # 驗證必要欄位
                if not selected_years and not city:
                    ui.notify('[縣市] 與 [成交年份] 皆為必要搜尋條件', type='warning', position='top')
                    return False
                if not city:
                    ui.notify('請選擇縣市', type='warning', position='top')
                    return
                if len(selected_years) < 2:
                    ui.notify('請至少選擇 2 個成交年份選項', type='warning', position='top')
                    return
                if len(selected_years) < 2 or len(selected_years) > 5:
                    ui.notify('成交年份選項請選擇 5 個(含)以內', type='warning', position='top')
                    return

                try:
                    df = query_multi_year_price(city, trade_type, selected_years, house_status)
                except Exception as e:
                    ui.notify('查詢失敗，請反應給站長協助處理', type='negative', position='top')
                    log_warning(f'查詢 [複合年度比較趨勢圖] 失敗：{str(e)}')
                    return

                if df.empty:
                    ui.notify('查無資料', type='warning', position='top')
                    return

                CHART_CONTAINER.clear()
                fig = create_multi_year_trend_chart(df, city, trade_type, house_status)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')

            # 第三列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.label('交易標的：')
                trade_type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

                ui.label('屋況：')
                house_status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

                CountdownButton('搜尋', icon='search', on_click=on_search, color='primary')
            
        ui.separator()


# 多縣市年度 3D 屋齡價格趨勢圖
def render_3D_multi_year_trends():
    MAIN_CONTENT.clear()
    CHART_CONTAINER.clear()

    with MAIN_CONTENT:
        with ui.expansion('多縣市年度 3D 屋齡價格趨勢圖', icon='description', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            ui.markdown(''' 
            - 這個區域讓您查詢多縣市單一年份中，不同屋齡與平均房價之間的關係，藉由 3D 趨勢圖視覺化呈現
            - 透過比較多個縣市的同年成交資料，可觀察各地屋齡與價格的整體分佈與趨勢變化
            - 成交年份(可選 2~5 個項目)與縣市是必要的查詢條件，請確保選擇後再進行查詢
            - 可依需求選擇「交易標的」與「屋況」，進一步篩選符合條件的物件類型
            ''')

            ui.markdown('''
            - 以下進階選項可協助您提升圖表的可讀性與資料品質：
                <div style="margin-left: 20px;">
                移除價格最高邊界值(%)：排除極端高價的資料點，避免過度拉高平均值<br>
                使用中位數取代平均值：能有效避免少數高價物件對趨勢線造成扭曲<br>
                移除價格為 0 的物件：可過濾異常或填寫錯誤的資料，提升準確性<br>
                僅保留總價 < 1 億資料：可排除大宗交易或特殊物件的干擾
                </div>
            ''')

            ui.markdown(''' 
            - 若查詢結果為空，可能是因為：
                <div style="margin-left: 20px;">
                選擇的條件過於嚴格，導致無符合資料<br>
                部分縣市在該年份下無成交紀錄<br>
                所選屋況或交易標的尚無統計資料
                </div>
            ''')

        with ui.expansion('搜尋條件', icon='list', value=True).classes('w-full').style(MAIN_CTX_STYLE):
            # 第一列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>縣市：')
                city_checkboxes = {}
                city_list = [
                    "臺北", "新北", "基隆", "桃園", "新竹",
                    "苗栗", "臺中", "南投", "彰化", "雲林",
                    "嘉義", "臺南", "高雄", "屏東",
                    "宜蘭", "花蓮", "臺東",
                    "澎湖", "金門", "連江"
                ]
                for city in city_list:
                    city_checkboxes[city] = ui.checkbox(city).classes('w-20')

            # 第二列
            with ui.row().style(ROW_STYLE_NORMAL):
                ui.html('<span style="color:red">*</span>成交年份：')
                year_select = ui.select(YEAR_SELECTIONS[:-1], value=None).classes('w-48')

                ui.label('交易標的：')
                trade_type_select = ui.select(TYPE_SELECTIONS, value=None, clearable=True).classes('w-36')

                ui.label('屋況：')
                house_status_select = ui.select(HOUSE_STATUS_SELECTIONS, value=None, clearable=True).classes('w-36')

            # 第三列
            with ui.row().style(ROW_STYLE_NORMAL):
                use_median_checkbox = ui.checkbox('使用中位數取代平均值')
                remove_zero_checkbox = ui.checkbox('移除價格為 0')
                filter_under_100m_checkbox = ui.checkbox('僅保留總價 < 1 億資料')

            async def on_search():
                selected_year = year_select.value
                selected_cities = [city for city, cb in city_checkboxes.items() if cb.value]
                trade_type = trade_type_select.value
                house_status = house_status_select.value
                remove_percent = remove_outliers_slider.value / 100
                use_median = use_median_checkbox.value
                remove_zero = remove_zero_checkbox.value
                limit_100m = filter_under_100m_checkbox.value

                if not selected_year:
                    ui.notify('請選擇成交年份', type='warning', position='top')
                    return
                if len(selected_cities) < 2:
                    ui.notify('請至少選擇 2 個縣市', type='warning', position='top')
                    return
                if len(selected_cities) > 5:
                    ui.notify('縣市選擇請勿超過 5 個', type='warning', position='top')
                    return

                try:
                    df = query_multi_city_price_with_age(
                        selected_cities, selected_year,
                        trade_type, house_status,
                        remove_percent,
                        use_median, remove_zero, limit_100m
                    )
                except Exception as e:
                    ui.notify('查詢失敗，請反應給站長協助處理', type='negative', position='top')
                    log_warning(f'查詢失敗：{str(e)}')
                    return

                if df.empty:
                    ui.notify('查無資料', type='warning', position='top')
                    return

                CHART_CONTAINER.clear()
                fig = create_single_year_multi_city_trend_chart_3d(df, selected_year, trade_type, house_status)
                with CHART_CONTAINER:
                    ui.plotly(fig).classes('w-full')

            # 第四列
            with ui.row().style(ROW_STYLE_NORMAL):
                remove_outliers_slider = ui.slider(min=0, max=25, value=0, step=1).classes('w-72')
                ui.label('移除價格最高邊界值(%)').style('font-weight: 600; margin-right: 12px;')
                percentage_label = ui.label(f'{remove_outliers_slider.value}%').style('min-width: 30px; text-align: left; margin-left: 8px;')

                def update_label(event):
                    val = event.args
                    percentage_label.set_text(f'{val}%')
                remove_outliers_slider.on('update:model-value', update_label)

                CountdownButton('搜尋', icon='search', on_click=on_search, color='primary')
            
        ui.separator()


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
