import asyncio
from asyncio.futures import Future
from asyncio.tasks import Task
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Iterable, Iterator, TypeVar

T = TypeVar('T')
Func = Callable[..., T]


class Tasks:

    def __init__(self):
        self._executor = ThreadPoolExecutor()
        self._loop = asyncio.get_event_loop()

    def parallel_map(self, func: Func[T], *iterables: Iterable[Any]) -> Iterator[Future[T]]:
        futures = [self.parallel(func, *args) for args in zip(*iterables)]
        return asyncio.as_completed(futures, loop=self._loop)

    def parallel(self, func: Func[T], *args: Any) -> Future[T]:
        return self._loop.run_in_executor(self._executor, func, *args)

    def task(self, coroutine: Coroutine[Any, None, T]) -> Task[T]:
        return self._loop.create_task(coroutine)

    def run(self, coroutine: Coroutine[Any, None, T]) -> T:
        return self._loop.run_until_complete(coroutine)


def test():
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

        t.task(ticks())

        names = repeat(name)
        times = range(10)

        for result in t.parallel_map(p, names, times):
            print("Async", await result)


    t.run(main("elias"))
