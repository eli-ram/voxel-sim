import multiprocessing as mp
import typing as t
from queue import Empty
from random import randint
from textwrap import dedent
from time import sleep

IS_MAIN = (__name__ == "__main__")
IS_MP_MAIN = (__name__ == "__mp_main__")


class Props:
    def __init__(self, index: int):
        self.index = index
        self.sleep = randint(1, 20) * 0.5
        self.text = dedent(f"""
            {IS_MAIN=}
            {IS_MP_MAIN=}
            Sleep duration: {self.sleep}
            Process index: {self.index}
        """)

    def suspend(self):
        sleep(self.sleep)

    def log(self):
        print(self.text)


class Packet(t.NamedTuple):
    uuid: int
    path: str
    data: t.Any


class Comms(t.NamedTuple):
    requests: 'mp.Queue[t.Optional[Packet]]'
    resolved: 'mp.Queue[Packet]'


class Worker:
    patch: 'mp.Queue[Packet]'
    process: mp.Process

    def __init__(self, comms: Comms) -> None:
        self.patch = mp.Queue()
        self.process = mp.Process(
            target=_target,
            args=(comms, self.patch)
        )


def _route(packet: Packet):
    sleep(0.5)
    print("[req]", packet.data)


def _patch(patch: 'mp.Queue[Packet]'):
    try:
        # Perform patch if avaliable
        _route(patch.get_nowait())
    except Empty:
        pass


def _target(comms: Comms, patch: 'mp.Queue[Packet]'):
    # Unpack comms
    RQ, RS = comms

    # Perform tasks
    while req := RQ.get():
        _patch(patch)
        _route(req)
        RS.put(req)

    # Propagate closing
    RQ.put(None)


class Manager:

    def __init__(self, pool_size: t.Optional[int] = None) -> None:
        self.pid = 0
        self.size = pool_size or mp.cpu_count()
        self.comms = Comms(mp.Queue(), mp.Queue())
        self.workers = [Worker(self.comms) for _ in range(self.size)]

    def start(self):
        for worker in self.workers:
            worker.process.start()

    def shutdown(self):
        self.comms.requests.put(None)
        for worker in self.workers:
            worker.process.join()
        self.comms.requests.get()

    def patch(self, path: str, data: t.Any):
        packet = Packet(0, path, data)
        for worker in self.workers:
            worker.patch.put(packet)

    def request(self, path: str, data: t.Any):
        packet = Packet(self.pid, path, data)
        self.pid += 1
        self.comms.requests.put(packet)

    def _poll(self):
        try:
            return self.comms.resolved.get_nowait()
        except Empty:
            return None

    def poll(self):
        while res := self._poll():
            print("[res]", res.data)


if __name__ == '__main__':
    print("Initializing...")

    manager = Manager()
    manager.request("", "first!")
    manager.start()
    manager.patch("", "hello world")
    for i in range(manager.size):
        manager.request("", f"[{i}] another one!")
    sleep(0.5)
    manager.poll()
    manager.shutdown()

    print("Exiting...")
    manager.poll()
