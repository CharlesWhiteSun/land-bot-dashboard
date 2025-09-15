from nicegui import ui, app
from ip_blacklist import IPBlacklistMiddleware

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
    with main_content:
        render_data_analysis()

# 畫面組成
render_header()

# 儲存 sidebar 引用物件
sidebar = ui.left_drawer().props('show-if-above').style('background-color: #454851; padding: 1rem;')

with sidebar:
    ui.label('📊 功能選單').style('font-size: 1rem; font-weight: 600; color: white; margin-bottom: 0.75rem;')
    with ui.column().style('gap: 0.5rem;'):
        ui.button('首　　頁', icon='home', color='white', on_click=show_home).style('width: 100%;')
        ui.button('更新資料', icon='download', color='white', on_click=lambda: ui.notify('準備下載資料...', position='top')).style('width: 100%;')
        ui.button('資料分析', icon='analytics', color='white', on_click=show_data_analysis).style('width: 100%;')

show_home()
render_footer()

# 新增右上角按鈕切換 sidebar
def toggle_sidebar():
    try:
        sidebar.toggle()
    except Exception:
        try:
            mv = sidebar.props_dict.get('model-value', None)
        except AttributeError:
            mv = None
        if mv is not None:
            sidebar.props(f'model-value={str(not mv).lower()}')
            sidebar.update()
        else:
            try:
                sidebar.hide()
            except:
                sidebar.show()

ui.button(icon='menu', on_click=toggle_sidebar) \
    .props('flat round dense') \
    .style('position: fixed; top: 1rem; right: 1rem; z-index: 9999; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);')

# 掛載 IP 黑名單中介軟體
app.add_middleware(IPBlacklistMiddleware)

ui.run(
    title='🏡 房價分析儀表板',
    reload=False,
    dark=False,
    show=False,
    port=8080,
)
