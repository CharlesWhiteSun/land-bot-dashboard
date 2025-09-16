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

    with ui.left_drawer(fixed=True).props('width=230').style('''
        background-color: #454851; 
        padding: 1rem;
    ''') as sidebar:
        
        ui.label('📊 功能選單').style('''
            font-size: 1.3rem; 
            font-weight: 600; 
            color: white;
        ''')

        with ui.column().classes('w-[100%] h-screen items-center').style('gap:0.75rem'):
            CountdownButton('首　　頁',
                            icon='home',
                            color='#00120B',
                            on_click=render_main,
                            style_fmt='width: 85%;',)
            CountdownButton('資料分佈',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_data_distribution,
                            style_fmt='width: 85%;',)
            CountdownButton('資料趨勢',
                            icon='analytics',
                            color='#00120B',
                            on_click=render_data_trends,
                            style_fmt='width: 85%;',)
            
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
