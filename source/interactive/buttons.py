# pyright: reportUnknownMemberType=false
from typing import Callable, Dict, Any
from .context import glfw
    
class NotAButton(Exception):
    " The key could not be found "

    @classmethod
    def convert(cls, b: str):
        button = glfw.__dict__.get(f"MOUSE_BUTTON_{b.upper()}", None)
        if button is None:
            raise cls(b)
        return button

ToggleCallback = Callable[[bool], Any]
ActionCallback = Callable[[], Any]


class Buttons:

    def __init__(self):
        self.lut: Dict[Any, ToggleCallback] = dict()

    def toggle(self, b: str):
        button = NotAButton.convert(b)

        def call(func: ToggleCallback):
            self.lut[button] = func
            return func
        return call

    def action(self, b: str):
        button = NotAButton.convert(b)
        def call(func: ActionCallback):
            def trigger(press: bool):
                if press:
                    func()
            self.lut[button] = trigger
            return func
        return call

    def trigger(self, button: int, action: int, mods: int):
        if action == glfw.REPEAT:
            return

        func = self.lut.get(button)
        pressed = action == glfw.PRESS

        if not func:
            act = 'PRESSED' if pressed else 'RELEASED'
            print(f"Unbound button: <{button}/{act}>")
            return

        try:
            func(pressed)
        except Exception as e:
            print(e)
