from nicegui import ui
from ngui.components.header import render_header
from ngui.components.sidebar import render_sidebar
from ngui.components.footer import render_footer
from ngui.components.data_analysis import render_data_analysis

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

# 全域主內容容器
main_content = ui.column().classes('w-full')

def show_home():
    main_content.clear()
    with main_content:
        ui.label('🏙️ 歡迎使用房價資料探索工具').style('font-size: 1.25rem; font-weight: 600;')
        ui.label('您可以從左側選單選取操作項目，如下載資料、檢視分析結果等。')
        ui.separator()
        ui.label('🗺️ 使用說明').style('font-size: 1.25rem; font-weight: 600;')
        ui.markdown('''
            - 點選左側選單可切換頁面  
            - 後續將整合實價登錄、地區分析、價格變動趨勢等資訊
        ''')

def show_data_analysis():
    main_content.clear()
    render_data_analysis()

# 樣式與結構
render_header()
render_sidebar()

# 修改 sidebar 的 callback
with ui.left_drawer().style('background-color: #454851; padding: 1rem;'):
    ui.label('📊 功能選單').style('font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.75rem;')
    with ui.column().style('gap: 0.5rem;'):
        ui.button('首　　頁', icon='home', color='#00120B', on_click=show_home).style('width: 100%;')
        ui.button('更新資料', icon='download', color='#00120B', on_click=lambda: ui.notify('準備下載資料...', position='top')).style('width: 100%;')
        ui.button('資料分析', icon='analytics', color='#00120B', on_click=show_data_analysis).style('width: 100%;')

# 主內容畫面
show_home()

# Footer
render_footer()

# 啟動
ui.run(title='🏡 房價分析儀表板', dark=True, show=False, port=8080)
