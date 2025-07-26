from nicegui import ui

def render_header():
    with ui.header().style('''
        background-color: #00120B; 
        color: white; 
    '''):
        ui.label('🏡 豪司爹許撥 House Dashboard').style('''
            font-size: 1.25rem; 
            font-weight: bold; 
            padding: 0.5rem 1rem;
        ''')
