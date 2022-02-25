from queue import Queue
from threading import Thread
from typing import Any, Set, Optional, Callable, TypeVar

T = TypeVar('T')

class Task:
    tag: Optional[str] = None
    def compute(self): ...
    def complete(self): ...

class FunctionalTask(Task):
    _value: Any

    def __init__(self, compute: Callable[[], T], complete: Callable[[T], None], tag: Optional[str] = None):
        self.tag = tag
        self._compute = compute
        self._complete = complete

    def compute(self):
        self._value = self._compute()

    def complete(self):
        self._complete(self._value)

class TaskQueue:
    running: Set[str]

    def __init__(self, num_workers: int = 1):
        self.queue = Queue[Task]()
        self.done = Queue[Task]()
        self.running = set()
        for _ in range(num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def add(self, task: Task):
        if task.tag in self.running:
            print(f"Task tagged '{task.tag}' is already running")
            return

        if task.tag:
            self.running.add(task.tag)

        self.queue.put(task)            

    def run(self, compute: Callable[[], T], complete: Callable[[T], None], tag: Optional[str] = None):
        self.add(FunctionalTask(compute, complete, tag))

    def update(self):
        if not self.done.empty():
            task = self.done.get()
            task.complete()
            self.running.remove(task.tag)
            self.done.task_done()

    def worker(self):
        while True:
            task = self.queue.get()
            task.compute()
            self.done.put(task)
            self.queue.task_done()