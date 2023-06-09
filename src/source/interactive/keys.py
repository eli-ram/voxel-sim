# pyright: reportUnknownMemberType=false
from typing import Callable, Dict, Any
from .context import glfw


class NotAKey(Exception):
    "The key could not be found"

    @classmethod
    def convert(cls, k: str | int):
        if isinstance(k, int):
            return k # assume correct key
        
        key = glfw.__dict__.get(f"KEY_{k.upper()}")
        if not key:
            raise cls(k)
        return key


ToggleCallback = Callable[[bool], Any]
ActionCallback = Callable[[], Any]

class Keys:
    _ = glfw

    def __init__(self):
        self.lut = dict[Any, ToggleCallback]()
        self.rep = dict[Any, ActionCallback]()

    def toggle(self, k: str | int):
        key = NotAKey.convert(k)

        def call(func: ToggleCallback):
            self.lut[key] = func
            return func

        return call

    def action(self, k: str):
        key = NotAKey.convert(k)

        def call(func: ActionCallback):
            def trigger(press: bool):
                if press:
                    func()

            self.lut[key] = trigger
            return None

        return call

    def repeat(self, k: str):
        key = NotAKey.convert(k)

        def call(func: ActionCallback):
            def trigger(press: bool):
                if press:
                    func()

            self.rep[key] = func
            self.lut[key] = trigger
            return None

        return call

    def trigger(self, key: int, code: int, action: int, mods: int):
        if action == glfw.REPEAT:
            if func := self.rep.get(key):
                try:
                    func()
                except Exception as e:
                    print(e)
            return

        func = self.lut.get(key)
        pressed = action == glfw.PRESS

        if not func:
            char = chr(key) if key in range(0x110000) else "[?]"
            act = "PRESSED" if pressed else "RELEASED"
            print(f"Unbound key: <{key}/{char}/{act}>")
            return

        try:
            func(pressed)
        except Exception as e:
            print(e)
