# pyright: reportUnknownMemberType=false
from typing import Any

from source.interactive.buttons import Buttons
from source.interactive.tasks import TaskQueue
from .context import glfw, UninitializedException
from .keys import Keys
from dataclasses import dataclass

def callback(func: Any) -> None:  
    def wrap(cls: Any, window: Any, *args: Any):
        self: Window = glfw.get_window_user_pointer(window)
        func(self, *args)
    return wrap # type: ignore

@dataclass
class Cache:
    window_pos: tuple[int, int] = (0, 0)
    window_size: tuple[int, int] = (0, 0)
    cursor_pos: tuple[float, float] = (0, 0)

class Window:
    " Wrapper for GLFW to allow simple usage "

    def __init__(self, width: int, height: int, title: str):
        self.window = glfw.create_window(width, height, title, None, None)
        UninitializedException.check(self.window, "window")
        self.keys = Keys()
        self.buttons = Buttons()
        self.tasks = TaskQueue()

        # Binding some default actions
        self.keys.action("ESCAPE")(self.close)
        self.keys.action("F11")(self.toggle_fullscreen)

        # Binding event callbacks
        glfw.make_context_current(self.window)
        glfw.set_window_user_pointer(self.window, self)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.button_callback)
        glfw.set_window_size_callback(self.window, self.resize_callback)
        glfw.set_window_pos_callback(self.window, self.position_callback)
        glfw.set_window_refresh_callback(self.window, self.refresh_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)

        # Internal prop cache
        self._cache = Cache()

    def show_cursor(self, visible: bool):
        mode = glfw.CURSOR_NORMAL if visible else glfw.CURSOR_DISABLED
        glfw.set_input_mode(self.window, glfw.CURSOR, mode)

    def set_cursor(self, x: float, y: float):
        glfw.set_cursor_pos(self.window, x, y)

    def set_position(self, x: int, y: int):
        glfw.set_window_pos(self.window, x, y)

    def setup(self): ...
    def resize(self, width: int, height: int): ...
    def update(self, time: float, delta: float): ...
    def render(self): ...
    def cursor(self, x: float, y: float, dx: float, dy: float): ...
    def scroll(self, value: float): ...

    def spin(self):
        window = self.window

        glfw.make_context_current(window)
        glfw.set_time(0.0)
        self.prev_time = 0.0
        self.setup()
        width, height = glfw.get_window_size(self.window)
        self.resize(width, height)
        self._half_size = (width // 2, height // 2)
        while not glfw.window_should_close(window):
            self.frame()
            glfw.poll_events()
            self.tasks.update()

    def frame(self):
        now = glfw.get_time()
        self.update(now, now - self.prev_time)
        self.render()
        glfw.swap_buffers(self.window)
        self.prev_time = now

    def close(self):
        glfw.set_window_should_close(self.window, True)

    def toggle_fullscreen(self):
        if not glfw.get_window_monitor(self.window):
            self._cache.window_pos = glfw.get_window_pos(self.window)
            self._cache.window_size = glfw.get_window_size(self.window)

            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            pos = (0, 0)
            size: tuple[int, int] = mode.size
            rate = mode.refresh_rate

        else:
            monitor = None
            pos = self._cache.window_pos
            size = self._cache.window_size
            rate = 0

        glfw.set_window_monitor(
            self.window,
            monitor,
            *pos,
            *size,
            rate,
        )

    @callback
    def key_callback(self, key: int, code: int, action: int, mods: int):
        self.keys.trigger(key, code, action, mods)

    @callback
    def button_callback(self, button: int, action: int, mods: int):
        self.buttons.trigger(button, action, mods)

    @callback
    def resize_callback(self, width: int, height: int):
        if width <= 0 or height <= 0:
            return

        self._half_size = (width // 2, height // 2)
        self.resize(width, height)
        self.frame()

    @callback
    def position_callback(self, x: int, y: int):
        self.frame()

    @callback
    def refresh_callback(self):
        self.frame()

    @callback
    def cursor_enter_callback(self, entered: bool):
        if entered:
            x, y = glfw.get_cursor_pos(self.window)
            self._cache.cursor_pos = (x, y)

    @callback
    def cursor_callback(self, x: float, y: float):
        px, py = self._cache.cursor_pos
        self.cursor(x, y, x - px, y - py)
        self._cache.cursor_pos = (x, y)

    @callback
    def scroll_callback(self, side_scroll: float, scroll: float):
        self.scroll(scroll)

if __name__ == '__main__':
    window = Window(800, 800, "Test-Window")
    window.spin()
