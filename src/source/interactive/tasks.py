from queue import Queue
from threading import Event, Thread
from typing import List, Set, Optional, Callable, TypeVar

V = TypeVar('V')


class Task:
    tag: Optional[str] = None
    def compute(self): ...
    def complete(self): ...


class FunctionalTask(Task):
    def __init__(
        self,
        compute: Callable[[], V],
        complete: Callable[[V], None],
        tag: Optional[str] = None,
    ):
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

    def __init__(self, num_workers: int = 2):
        self.queue = Queue[Task]()
        self.done = Queue[Task]()
        self.running = set()
        for _ in range(num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def add(self, task: Task):
        if T := task.tag:
            if T in self.running:
                print(f"Task tagged '{task.tag}' is already running")
                return
            self.running.add(T)

        self.queue.put(task)

    def run(self, compute: Callable[[], V], complete: Callable[[V], None], tag: Optional[str] = None):
        self.add(FunctionalTask(compute, complete, tag))

    def dispatch(self, synchronize: Callable[[], V], tag: Optional[str] = None) -> Callable[[], V]:
        """ Dispatch a task to execute on the main thread get an Event back """
        processed = Event()

        # Construct capture
        value: V = None  # type: ignore

        # Construct event
        def complete(_: None):
            nonlocal value
            value = synchronize()
            processed.set()

        # run the event
        self.run(lambda: None, complete, tag)

        # return awaiter
        def wait():
            processed.wait()
            return value

        return wait

    def sync(self, synchronize: Callable[[], None], tag: Optional[str] = None):
        """ Make a task execute on the main thread and wait for it to finish """
        self.dispatch(synchronize, tag).wait()

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
            # get & run next task
            task = self.queue.get()
            task.compute()
            # close task if tagged
            # why do we need to key-guard a set ??
            if T := task.tag:
                if T in self.running:
                    self.running.remove(T)
            # return task
            self.done.put(task)
            self.queue.task_done()
