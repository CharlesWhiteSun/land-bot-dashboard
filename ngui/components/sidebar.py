from nicegui import ui
from ngui.components.countdown_button import CountdownButton
from ngui.components.main_area import *

def render_sidebar():
    with ui.left_drawer(fixed=True).props('width=300').style('''
        background-color: #454851; 
        padding: 1rem;
    '''):

        ui.label('📊 Function Menu').style('''
            font-size: 1.3rem; 
            font-weight: 600; 
            color: white;
        ''')

        with ui.column().classes('w-[100%] h-screen items-left').style('gap:0.75rem'):

            style_fmt_ctx = 'min-width: max-content; padding: 0 1rem;'

            # Home Page 按鈕
            CountdownButton('Home Page',
                            icon='home',
                            color='#00120B',
                            on_click=render_main,
                            style_fmt=style_fmt_ctx)

            # Charts expansion（代替原本的 toggle + 子按鈕）
            with ui.expansion('Charts', icon='bar_chart', value=True).classes('w-[100%]'):
                btn_style = 'min-width: max-content; padding: 0 1rem;'

                CountdownButton('不動產分佈圖',
                                icon='analytics',
                                color='#00120B',
                                on_click=render_data_distribution,
                                style_fmt=btn_style)

                CountdownButton('多縣市 3D 分佈圖',
                                icon='analytics',
                                color='#00120B',
                                on_click=render_multi_city_3d,
                                style_fmt=btn_style)

                CountdownButton('不動產年度趨勢圖',
                                icon='analytics',
                                color='#00120B',
                                on_click=render_data_trends,
                                style_fmt=btn_style)

                CountdownButton('複合年度比較趨勢圖',
                                icon='analytics',
                                color='#00120B',
                                on_click=render_multi_year_trends,
                                style_fmt=btn_style)

    # Sidebar Toggle 按鈕（保持固定）
    ui.button(icon='menu') \
        .props('flat round dense') \
        .style('''
            position: fixed; 
            top: 1rem; 
            right: 1rem; 
            z-index: 9999; 
            background-color: white; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ''')
