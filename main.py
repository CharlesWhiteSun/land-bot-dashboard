from nicegui import ui
from ngui.components.header import render_header
from ngui.components.sidebar import render_sidebar
from ngui.components.footer import render_footer

# 修改 q-page 樣式（主畫面中間區塊）
ui.add_body_html('''
<style>
.q-page {
    background-color: #edf2ef !important;
    color: #000000;
    padding: 1.5rem;
}
</style>
''')

# 呼叫模組
render_header()
render_sidebar()

# 主畫面內容
with ui.row().style('''
        background-color: #edf2ef; 
        color: black; 
        padding: 1.5rem;
    '''):
    with ui.column():
        ui.label('🏙️ 歡迎使用房價資料探索工具').style('''
            font-size: 1.25rem; 
            font-weight: 600;
        ''')
        ui.label('您可以從左側選單選取操作項目，如下載資料、檢視分析結果等。')
        ui.separator()
        ui.label('🗺️ 使用說明').style('''
            font-size: 1.25rem; 
            font-weight: 600;
        ''')
        ui.markdown('''
            - 點選左側選單可切換頁面  
            - 後續將整合實價登錄、地區分析、價格變動趨勢等資訊
        ''')

# Footer
render_footer()

# 執行應用
ui.run(title='🏡 房價分析儀表板', dark=True, show=False)
