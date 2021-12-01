import asyncio
from asyncio.futures import Future
from asyncio.tasks import Task
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Iterable, Iterator, TypeVar

T = TypeVar('T')
Func = Callable[..., T]


class Tasks:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor()
        print("Workers:", self.pool._max_workers)

    def parallel_for(self, func: Func[T], *iterables: Iterable[Any]) -> Iterator[Future[T]]:
        futures = [self.parallel(func, *args) for args in zip(*iterables)]
        return asyncio.as_completed(futures)

    def parallel(self, func: Func[T], *args: Any) -> Future[T]:
        return self.loop.run_in_executor(self.pool, func, *args)

    def run(self, coroutine: Coroutine[Any, Any, T]) -> Task[T]:
        return self.loop.create_task(coroutine)

    def run_main_loop(self, coroutine: Coroutine[Any, None, T]) -> T:
        return self.loop.run_until_complete(coroutine)

    async def poll(self):
        await asyncio.sleep(0)

def m_test():
    from itertools import repeat
    from time import sleep
    from random import randint
    t = Tasks()

    def p(name: str, time: int):
        sleep(randint(0, time))
        print("Parallel", name, time)
        sleep(randint(0, time))
        return f"|{name}-{time}|"

    async def ticks():
        state = True
        while True:
            await asyncio.sleep(0.5)
            print("> tick" if state else "< tock")
            state = not state

    async def main(name: str):

        t.run(ticks())

        names = repeat(name)
        times = range(10)

        for result in t.parallel_for(p, names, times):
            print("Async", await result)


    t.run_main_loop(main("elias"))
