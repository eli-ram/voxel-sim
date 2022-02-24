import asyncio
from asyncio.futures import Future
from asyncio.tasks import Task
from queue import Queue
from threading import Thread
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


class Task:
    def compute(self): ...
    def complete(self): ...

class FunctionalTask(Task):
    _value: Any

    def __init__(self, compute: Callable[[], T], complete: Callable[[T], None]):
        self._compute = compute
        self._complete = complete

    def compute(self):
        self._value = self._compute()

    def complete(self):
        self._complete(self._value)

class TaskQueue:

    def __init__(self, num_workers: int = 1):
        self.queue = Queue[Task]()
        self.done = Queue[Task]()
        for _ in range(num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def add(self, task: Task):
        self.queue.put(task)

    def run(self, compute: Callable[[], T], complete: Callable[[T], None]):
        self.add(FunctionalTask(compute, complete))

    def update(self):
        if not self.done.empty():
            task = self.done.get()
            task.complete()
            self.done.task_done()

    def worker(self):
        while True:
            task = self.queue.get()
            task.compute()
            self.done.put(task)
            self.queue.task_done()