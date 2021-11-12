

from typing import Any


class Animated:

    def __init__(self, consumer: Any, value: Any, step: Any):
        self._consumer = consumer
        self._value = value
        self._step = step 
        self._consumer(self._value)

    def update(self):
        print(self._consumer.__name__, self._value)
        self._consumer(self._value)

    def inc(self):
        self._value += self._step
        self.update()

    def dec(self):
        self._value -= self._step
        self.update()
