from nicegui import ui

# 主內容畫面渲染
def apply_main_body_styles():
    ui.add_body_html('''
    <style>
    .q-page {
        background-color: #edf2ef !important;
        color: #000000;
        padding: 1.5rem;
    }
    </style>
    ''')

# 全域主內容容器
main_content = ui.column().classes('w-full')

def render_main():
    main_content.clear()
    with main_content:
        ui.label('🏙️ Welcome!').style('font-size: 1.25rem; font-weight: 600;')
        ui.markdown('''
            - 歡迎使用建物資料分析儀表板  
            - 這裡整合了一些內政部不動產實際資料供應系統的成交案件資料
            - 關於不動產資料都歸於 內政部地政司(Dept of Land Administration M.O.I.) 所有
            - 您可以從左側選單點擊操作項目
        ''')
        ui.separator()
        ui.label('🗺️ Instructions').style('font-size: 1.25rem; font-weight: 600;')
        ui.markdown('''
            - 點選左側選單可切換頁面
            - 後續將整合實價登錄、地區分析、價格變動趨勢等資訊
        ''')

style = '''
    font-size: 1rem; 
    font-weight: 600; 
    color: #00120B;
    margin-bottom: 0.75rem;
'''

# 分析頁面
def render_data_analysis():
    main_content.clear()
    with main_content:
        with ui.row().classes('items-center justify-start').style('gap: 1rem'):
            ui.select(['選項A1', '選項A2', '選項A3'], label='Key 1').style(style)
            ui.select(['選項B1', '選項B2', '選項B3'], label='Key 2').style(style)
            ui.select(['選項C1', '選項C2', '選項C3'], label='Key 3').style(style)
            ui.button('搜尋', icon='search').style(style)

# 初始化樣式
apply_main_body_styles()
