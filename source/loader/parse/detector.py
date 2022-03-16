from io import TextIOWrapper
from threading import Thread
import traceback
from typing import Any
from .parsable import Parsable
from .indent import Format

import os
import yaml
import time


class Detector:
    thread: Thread
    format = Format(prefix=' |', list_unchanged=False, list_errors=True).init()

    def __init__(self, filename: str, parser: Parsable, delay: float = 1.0):
        self.timestamp = 0.0
        self.filename = filename
        self.parser = parser
        self.delay = delay
        self.alive = False

    def onParsed(self, parsed: Parsable):
        """ Respond to Parsed Config """
        pass

    def loadFile(self, file: TextIOWrapper) -> Any:
        return yaml.safe_load(file)

    def refresh(self):
        while self.shouldWait():
            time.sleep(self.delay)

        with open(self.filename, 'r') as file:
            data = self.loadFile(file)

        P = self.parser
        F = self.format
        print("\n[#] Parsing:", self.filename)
        P.parse(data)
        print(f"[#] Result: \n V{P.format(F)}\n A")
        print(f"[#] Changed: {P.changed}")
        print(f"[#] Error: {P.error}")

        if P.changed:
            self.onParsed(P)

    def shouldWait(self):
        last = self.timestamp
        next = os.path.getmtime(self.filename)
        self.timestamp = next
        return last == next

    def run(self):
        assert not self.alive, "Do not start multiple detectors"
        self.alive = True
        while self.alive:
            try:
                self.refresh()
            except Exception:
                traceback.print_exc()

    def start(self):
        thread = Thread(target=self.run)
        thread.setName(f"Detector(file='{self.filename}')")
        thread.setDaemon(True)
        thread.start()
        self.thread = thread

    def kill(self):
        if self.alive:
            self.alive = False
            self.thread.join()
