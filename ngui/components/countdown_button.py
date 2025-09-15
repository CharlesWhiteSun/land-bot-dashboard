import asyncio
from nicegui import ui
from typing import Callable, Optional


class CountdownButton:
    def __init__(self,
                 label: str,
                 icon: str = '',
                 color: str = '#00120B',
                 class_fmt: str='',
                 style_fmt: str = '',
                 countdown: int = 3,
                 on_click: Optional[Callable] = None,):
        self.label = label
        self.countdown = countdown
        self.on_click = on_click

        self.button = ui.button(label, icon=icon, color=color, on_click=self._handle_click)
        self.button.classes(class_fmt)
        self.button.style(style_fmt)

    async def run_countdown(self):
        for s in range(self.countdown, 0, -1):
            self.button.set_text(f'{self.label} ({s})')
            await asyncio.sleep(1)
        self.button.text = self.label
        self.button.enable()

    async def _handle_click(self):
        self.button.disable()
        asyncio.create_task(self.run_countdown())

        if asyncio.iscoroutinefunction(self.on_click):
            await self.on_click()
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.on_click)

class NotifyDisableButton:
    def __init__(self,
                 label: str,
                 icon: str = '',
                 color: str = '#00120B',
                 class_fmt: str = '',
                 style_fmt: str = '',
                 on_click: Optional[Callable] = None,):
        self.label = label
        self.on_click = on_click

        self.button = ui.button(label, icon=icon, color=color, on_click=self._handle_click)
        self.button.classes(class_fmt)
        self.button.style(style_fmt)

    async def _handle_click(self):
        self.button.disable()
        success = False

        if self.on_click:
            if asyncio.iscoroutinefunction(self.on_click):
                success = await self.on_click()
            else:
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(None, self.on_click)

        if success:
            ui.notify("任務已完成", position="top", type="positive")
        self.button.enable()
        
