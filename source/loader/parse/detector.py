from threading import Thread, currentThread
from typing import Any, Callable, Optional, TypeVar

from .generic import Generic
from .parsable import Parsable
from .indent import Format

import io
import os
import yaml
import time
import traceback    


class FileChangeDetector:

    def __init__(self, file: str):
        self.timestamp = None
        self.file = file

    def changed(self) -> bool:
        last = self.timestamp
        next = os.path.getmtime(self.file)
        self.timestamp = next
        return last != next

    def read(self):
        return open(self.file, 'r')


P = TypeVar('P', bound=Parsable)
F = Format(prefix=' |', list_unchanged=False, list_errors=True).init()


class ParsableDetector(Generic[P]):
    LOG = True
    _thread: Optional[Thread] = None
    _callback: Any

    def __init__(self, callback: Callable[[P], None]):
        self._callback = callback

    def __call__(self, filename: str, *_):
        all: Any = (*_, filename)
        filename, *args = all
        self._file = os.path.abspath(filename)
        self._args = args
        self.start()

    def logParsed(self, parser: P):
        print(
            f"\n[#] Parsed: '{self._file}'"
            f"\n[V] Result: {parser.format(F)}"
            f"\n[A] Changed: {parser.changed}"
            f"\n[#] Error: {parser.error}"
        )

    def loadFile(self, file: io.TextIOWrapper) -> Any:
        return yaml.safe_load(file)

    def run(self):
        file = FileChangeDetector(self._file)
        args = self._args
        thread = currentThread()
        parsable = Generic.get(self)()
        callback = self._callback

        print(f"Staring: {self}")
        # Run loop
        while self._thread is thread:

            # Await File change
            if not file.changed():
                time.sleep(1.0)
                continue

            try:
                # Read content 
                with file.read() as f:
                    data = self.loadFile(f)
                    changed, error = parsable.parse(data)
                    if self.LOG and (changed or error):
                        self.logParsed(parsable)
                    if changed and not error:
                        callback(*args, parsable)

            except Exception:
                # log exceptions
                traceback.print_exc()

        print(f"Stopped: {self}")

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(file: '{self._file}')"

    def start(self):
        assert self._thread is None, f"{self} is already running!"
        T = self._thread = Thread(target=self.run)
        T.setName(str(self))
        T.setDaemon(True)
        T.start()

    def join(self):
        if thread := self._thread:
            self._thread = None
            thread.join()

    def restart(self):
        self.join()
        self.start()
