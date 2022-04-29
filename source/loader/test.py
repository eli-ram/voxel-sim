# pyright: reportUnknownVariableType=false
from ..utils.directory import script_dir, cwd
from .parse.detector import ParsableDetector
from .configuration import Configuration
import time


@ParsableDetector[Configuration]
def config(C: Configuration):
    print(" // // ")


def sleep():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting....")


@cwd(script_dir(__file__), '..', '..', 'configurations')
def main():
    config('test_1.yaml')
    sleep()
    config.join()


def test_load():
    main()
