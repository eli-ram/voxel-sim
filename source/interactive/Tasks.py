import asyncio
from asyncio.futures import Future
from asyncio.tasks import Task
from typing import Any, Callable, Coroutine, Iterable, Iterator, TypeVar

T = TypeVar('T')
Func = Callable[..., T]

class Tasks:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def parallel_for(self, func: Func[T], *iterables: Iterable[Any]) -> Iterator[Future[T]]:
        futures = [self.parallel(func, *args) for args in zip(*iterables)]
        return asyncio.as_completed(futures)

    def parallel(self, func: Func[T], *args: Any) -> Future[T]:
        return self.loop.run_in_executor(None, func, *args)

    def run(self, coroutine: Coroutine[Any, Any, T]) -> Task[T]:
        return self.loop.create_task(coroutine)

    def run_main_loop(self, coroutine: Coroutine[Any, None, T]) -> T:
        return self.loop.run_until_complete(coroutine)

    async def poll(self):
        await asyncio.sleep(0)

