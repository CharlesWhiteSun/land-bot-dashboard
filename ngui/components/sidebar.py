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

    with ui.left_drawer(fixed=True).props('width=300').style('''
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

            # Home Page 按鈕
            CountdownButton('Home Page',
                            icon='home',
                            color='#00120B',
                            on_click=render_main,
                            style_fmt=style_fmt_ctx)

            # Charts 開關狀態
            charts_visible = {'value': True}

            # 放 Charts 按鈕和子按鈕的容器（讓他們綁在一起）
            with ui.column().classes('w-[100%] items-left').style('gap:0.75rem'):

                # 開關子選單的函式
                def toggle_charts():
                    charts_visible['value'] = not charts_visible['value']
                    charts_buttons_container.style(f'display: {"block" if charts_visible["value"] else "none"};')

                # Charts 按鈕（會觸發 toggle）
                ui.button('Charts',
                    icon='bar_chart',
                    color='#00120B',
                    on_click=toggle_charts) \
                    .style('min-width: max-content; padding: 0 1rem;')

                # 子選單區域（預設隱藏）
                charts_buttons_container = ui.column().classes('w-[100%] items-left').style('gap: 1.5rem; padding-left: 1.5rem; display: block;')

                # 子按鈕們
                with charts_buttons_container:
                    btn_style = 'min-width: max-content; padding: 0 1rem; margin-bottom: 0.5rem;'
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

    # Sidebar Toggle 按鈕
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
