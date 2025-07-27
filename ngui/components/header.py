from nicegui import ui

from enums.constants import SystemType

def render_header():
    with ui.header().style('''
        background-color: #00120B; 
        color: white; 
    '''):
        ui.label(f'{SystemType.TITLE_LOGO.value} {SystemType.TITLE_NAME.value} {SystemType.VERSION.value}').style('''
            font-size: 1.5rem; 
            font-weight: bold; 
            padding: 0.5rem 1rem;
        ''')
