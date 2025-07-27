from nicegui import ui
from ngui.components.countdown_button import CountdownButton
from ngui.components.main_area import *


def render_sidebar():
    with ui.left_drawer(fixed=True).props('width=230').style('''
        background-color: #454851; 
        padding: 1rem;
    '''):
        
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
