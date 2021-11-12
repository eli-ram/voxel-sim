# pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false, reportUnknownVariableType=false
from typing import List
from timeit import default_timer as tick
import numpy as np


class Sieve:

    def __init__(self, size: int):
        self.size = size
        self.bits = np.ones((size+1) // 2, dtype=np.bool_)

    def run(self):

        B = self.bits
        Q = np.sqrt(self.size) // 2
        factor = 1

        while factor <= Q:
            factor += 1 + np.argmax(B[factor:])
            F = factor * 2
            L = F * (factor - 1)
            S = F - 1
            B[L::S] = False

    def count(self):
        return np.sum(self.bits)

    def primes(self) -> List[int]:
        P = np.nonzero(self.bits)[0] * 2 + 1
        P[0] = 2
        return P

SETS = [
    # Historical data for validating our results - the number of primes
    # to be found under some limit, such as 168 primes under 1000
    (10, 4),                 
    (100, 25),                
    (1_000, 168),
    (10_000, 1229),
    (100_000, 9592),
    (1_000_000, 78498),
    (10_000_000, 664579),
    (100_000_000, 5761455),
]


def main():
    print("--- VALIDATING ---")
    for size, count in SETS:
        print(f"{size=:<10} | {count=}")
        sieve = Sieve(size)
        sieve.run()
        assert sieve.count() == count

    start = tick()
    limit = 1000000
    timeout = 5
    passed = 0       
    print("--- RUNNING ---")
    while (tick() - start) < timeout:
        S = Sieve(limit)
        S.run()
        passed += 1
    
    delta = tick() - start
    effective = passed / delta
    print(f"{limit=} {passed=} {delta=} {effective=}")

    ## TLDR: python is slow ...!

if __name__ == '__main__':
    main()
