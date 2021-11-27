
from traceback import format_exc
from timeit import default_timer as tick
from typing import Any, TypeVar

Func = TypeVar('Func')

def time(prefix: str):
    def wrapper(func: Func) -> Func:
        def wrap(*args: Any, **kwargs: Any) -> Any:
            try:
                print(f"[{prefix}] Started")
                start = tick()
                out: Any = func(*args, **kwargs) # type: ignore
                stop = tick()
                print(f"[{prefix}] Done")
                print(f"Time Used: {stop - start:3.3f}")
                return out
            except Exception:
                print(f"[{prefix}] Error")
                print(format_exc())
        return wrap # type: ignore
    return wrapper