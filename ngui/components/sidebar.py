from nicegui import ui
from ngui.components.main import render_main, render_data_analysis


def render_sidebar():
    with ui.left_drawer(fixed=True).style('''
        background-color: #454851; 
        padding: 1rem;
    '''):
        
        ui.label('📊 功能選單').style('''
            font-size: 1rem; 
            font-weight: 600; 
            color: white;
            margin-bottom: 0.75rem;
        ''')

        with ui.column().style('gap: 0.5rem;'):
            ui.button('首　　頁', icon='home', color='#00120B', on_click=render_main).style('width: 100%;')
            ui.button('資料分析', icon='analytics', color='#00120B', on_click=render_data_analysis).style('width: 100%;')
