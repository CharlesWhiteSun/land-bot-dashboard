from nicegui import ui

def render_sidebar():
    with ui.left_drawer().style('''
        background-color: #454851; 
        padding: 1rem;
    '''):
        ui.label('📊 功能選單').style('''
            font-size: 1rem; 
            font-weight: 600; 
            color: white;
            margin-bottom: 0.75rem;
        ''')

        with ui.column().style('''
            gap: 0.5rem;
        '''):
            ui.button('首　　頁', icon='home', color='#00120B', on_click=lambda: ui.notify('你在首頁', position='top', timeout=2000)).style('width: 100%;')
            ui.button('更新資料', icon='download', color='#00120B', on_click=lambda: ui.notify('準備下載資料...', position='top', timeout=2000)).style('width: 100%;')
            ui.button('資料分析', icon='analytics', color='#00120B', on_click=lambda: ui.notify('即將進入資料分析...', position='top', timeout=2000)).style('width: 100%;')
