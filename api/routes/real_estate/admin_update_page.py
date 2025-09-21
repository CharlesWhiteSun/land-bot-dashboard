from nicegui import ui
from ngui.components.sidebar import update_data  # 假設你原本的更新流程在這裡

def create_admin_update_page():
    @ui.page('/admin/update')
    async def admin_update_page():
        # 直接呼叫更新流程
        await update_data()
        # 回傳一個簡單頁面提示
        with ui.card():
            ui.label('✅ 更新流程已觸發，請稍候檢查結果。')
