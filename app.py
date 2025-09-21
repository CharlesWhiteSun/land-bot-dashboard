import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from api.routes.real_estate.admin_update_page import create_admin_update_page
create_admin_update_page()

from nicegui import ui, app
from enums.constants import SystemType
from ngui.components.footer import render_footer
from ngui.components.header import render_header
from ngui.components.main_area import render_main
from ngui.components.sidebar import render_sidebar

render_header()
render_sidebar()
render_main()
render_footer()

# 掛載 IP 黑名單中介軟體
from ip_blacklist import IPBlacklistMiddleware
app.add_middleware(IPBlacklistMiddleware)

ui.run(
    title=f"{SystemType.TITLE_LOGO.value} {SystemType.TITLE_NAME.value}",
    dark=True,
    show=False,
    port=7860,
    reload=False,
)
