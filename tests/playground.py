import __init__
from inspect import getmembers, isfunction
import sys

from source.interactive.Tasks import m_test

def test_tasks():
    m_test()


# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            print(f"Running: {name}")
            func()
