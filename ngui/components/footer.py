from datetime import datetime
from nicegui import ui

def render_footer():
    start_year = 2025
    current_year = datetime.now().year
    year_text = f"{start_year}" if start_year == current_year else f"{start_year}-{current_year}"

    with ui.footer().style('''
        background-color: #00120B; 
        color: white; 
        display: flex;
        justify-content: center;
        width: 100%;
    '''):
        
        ui.label(f'Copyright © {year_text} Charles. All rights reserved.')
