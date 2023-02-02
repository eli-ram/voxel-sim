from queue import Queue
from threading import Event, Thread
from typing import Any, List, Set, Optional, Callable, TypeVar


Value = TypeVar('Value')

class Task:
    tag: Optional[str] = None
    def compute(self): ...
    def complete(self): ...

class FunctionalTask(Task):
    _value: Any

    def __init__(self, compute: Callable[[], Value], complete: Callable[[Value], None], tag: Optional[str] = None):
        self.tag = tag
        self._compute = compute
        self._complete = complete

    def compute(self):
        self._value = self._compute()

    def complete(self):
        self._complete(self._value)

class SequenceTask(Task):
    active: Task

    def __init__(self, queue: 'TaskQueue', tasks: List[Task], tag: Optional[str] = None):
        self.tag = tag
        self.queue = queue
        self.tasks = tasks

    def next(self):
        if not self.tasks:
            return
        self.active = self.tasks.pop(0)
        self.queue.add(self)

    def compute(self):
        self.active.compute()

    def complete(self):
        self.active.complete()
        self.next()

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

    def run(self, compute: Callable[[], Value], complete: Callable[[Value], None], tag: Optional[str] = None):
        self.add(FunctionalTask(compute, complete, tag))

    def sync(self, value: Value, synchronize: Callable[[Value], None], tag: Optional[str] = None):
        """ Make a task execute on the main thread and wait for it to finish """
        processed = Event()
        def complete(value: Value):
            synchronize(value)
            processed.set()
        self.run(lambda:value, complete, tag)
        processed.wait()


    def sequence(self, *tasks: Task, tag: Optional[str] = None):
        SequenceTask(self, list(tasks), tag).next()

    def update(self):
        if self.done.empty():
            return

        task = self.done.get()
        task.complete()
        
        if task.tag:
            self.running.remove(task.tag)
        
        self.done.task_done()

    def worker(self):
        while True:
            task = self.queue.get()
            task.compute()
            self.done.put(task)
            self.queue.task_done()