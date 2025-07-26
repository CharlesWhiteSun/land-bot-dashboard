from nicegui import ui
from ngui.components.footer import render_footer
from ngui.components.header import render_header
from ngui.components.main_area import render_main
from ngui.components.sidebar import render_sidebar


render_header()
render_sidebar()
render_main()
render_footer()

ui.run(
    title='🏡 House Dashboard',
    dark=True,
    show=False,
    port=8080,
)
