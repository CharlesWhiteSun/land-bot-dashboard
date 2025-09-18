from nicegui import ui
from ngui.components.countdown_button import CountdownButton
from ngui.components.main_area import *

BTN_COLOR = '#00120B'
SIDE_BG_COLOR = '#454851'
MAIN_CTX_STYLE = f"""
    background-color: {SIDE_BG_COLOR};
    font-size: 1.3rem;
    font-weight: 600;
"""

def render_sidebar():
    with ui.left_drawer(fixed=True).props('width=300').style(f'''
        background-color: {SIDE_BG_COLOR}; 
        padding: 1rem;
    ''') as drawer:
    
        with ui.expansion('Menu', icon='settings', value=True).classes('w-[100%]').style(MAIN_CTX_STYLE):

            style_fmt_ctx = 'min-width: max-content;'

            # Home Page 按鈕
            CountdownButton('Home Page',
                            icon='home',
                            color=BTN_COLOR,
                            on_click=render_main,
                            style_fmt=style_fmt_ctx)

        with ui.column().classes('w-[100%] h-screen items-left').style('gap:0.75rem'):

            # Charts expansion
            with ui.expansion('Charts', icon='bar_chart', value=True).classes('w-[100%]').style(MAIN_CTX_STYLE):
                btn_style = 'min-width: max-content; padding: 0 1rem;'

                CountdownButton('縣市價坪分佈圖',
                                icon='analytics',
                                color=BTN_COLOR,
                                on_click=render_data_distribution,
                                style_fmt=btn_style)

                CountdownButton('多縣市 3D 價坪分佈圖',
                                icon='analytics',
                                color=BTN_COLOR,
                                on_click=render_multi_city_3d,
                                style_fmt=btn_style)

                CountdownButton('縣市價格年度趨勢圖',
                                icon='analytics',
                                color=BTN_COLOR,
                                on_click=render_data_trends,
                                style_fmt=btn_style)

                CountdownButton('多年度價格趨勢圖',
                                icon='analytics',
                                color=BTN_COLOR,
                                on_click=render_multi_year_trends,
                                style_fmt=btn_style)
                
                CountdownButton('多縣市年度 3D 屋齡價格趨勢圖',
                                icon='analytics',
                                color=BTN_COLOR,
                                on_click=render_3D_multi_year_trends,
                                style_fmt=btn_style)

    # Sidebar Toggle 按鈕（保持固定）
    ui.button(icon='menu') \
        .props('flat round dense') \
        .on('click', lambda: drawer.toggle()) \
        .style('''
            position: fixed; 
            top: 1rem; 
            right: 1rem; 
            z-index: 9999; 
            background-color: white; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ''')
