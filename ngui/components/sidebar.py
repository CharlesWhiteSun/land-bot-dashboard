from nicegui import ui
from ngui.components.countdown_button import CountdownButton
from ngui.components.main_area import *


# Sidebar 切換功能
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

def render_sidebar():
    global sidebar  # 讓 toggle_sidebar 能抓到這個變數

    with ui.left_drawer(fixed=True).props('width=240').style('''
        background-color: #454851; 
        padding: 1rem;
    ''') as sidebar:
        
        ui.label('📊 Function Menu').style('''
            font-size: 1.3rem; 
            font-weight: 600; 
            color: white;
        ''')

        with ui.column().classes('w-[100%] h-screen items-left').style('gap:0.75rem'):
            style_fmt_ctx = 'min-width: max-content; padding: 0 1rem;'
            CountdownButton('Home Page',
                            icon='home',
                            color='#00120B',
                            on_click=render_main,
                            style_fmt=style_fmt_ctx,)
            CountdownButton('不動產分佈圖',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_data_distribution,
                            style_fmt=style_fmt_ctx,)
            CountdownButton('多縣市 3D 分佈圖',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_multi_city_3d,
                            style_fmt=style_fmt_ctx,)
            CountdownButton('不動產年度趨勢圖',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_data_trends,
                            style_fmt=style_fmt_ctx,)
            CountdownButton('複合年度比較趨勢圖',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_multi_year_trends,
                            style_fmt=style_fmt_ctx,)
            
    # ⏹️ Sidebar Toggle 按鈕
    ui.button(icon='menu', on_click=toggle_sidebar) \
        .props('flat round dense') \
        .style('''
            position: fixed; 
            top: 1rem; 
            right: 1rem; 
            z-index: 9999; 
            background-color: white; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ''')
