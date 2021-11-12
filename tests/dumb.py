from random import shuffle, sample
from typing import Any, List
from inspect import cleandoc as c
from sys import argv

nums = list("12345678912325685678")
toks = list("+*-+-")

def splits(N: int, M: int):
    return sorted(sample(range(1, N-1), M))


def split(L: List[Any], N: int):
    S = len(L)
    I = splits(S, N)
    for l, h in zip([0] + I, I + [S]):
        yield L[l:h]

class Dumb:

    def __init__(self, target: int):
        self.target = target
        self.runs = 0
        self.eq = ""

    def hit(self):
        return eval(f"({self.eq}) == ({self.target})")

    def shot(self):
        shuffle(nums)
        shuffle(toks)
        S = split(nums, len(toks))
        T = toks + [""]
        C = (a + [b] for a, b in zip(S, T))
        D = (a for b in C for a in b)
        self.eq = "".join(D)

    def run(self):
        runs = 0
        while not self.hit():
            self.shot()
            runs += 1 
        print(c(f"""
            -----------------------
            Runs:   {runs}
            Target: {self.target}
            Result: {self.eq}
        """))
        

if __name__ == '__main__':
    for arg in argv[1:]:
        Dumb(int(arg)).run()
