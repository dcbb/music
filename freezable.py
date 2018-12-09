from random import random
from collections import deque


class FreezableRandom:

    def __init__(self, freeze_len=0):
        self.queue = deque(maxlen=16)
        self.freeze_len = 0
        self.pos = 0
        if freeze_len>0:
            self.freeze(freeze_len)

    def freeze(self, length):
        self.freeze_len = length
        self.pos = 0

    def is_frozen(self):
        return self.freeze_len>0

    def float(self):
        if self.freeze_len==0:
            val = random()
            self.queue.append(val)
        elif len(self.queue)==self.freeze_len:
            val = self.queue[self.pos]
            self.pos += 1
            self.pos %= len(self.queue)
        elif len(self.queue)<self.freeze_len:
            val = random()
            self.queue.append(val)
        elif len(self.queue)>self.freeze_len:
            assert self.pos == 0
            while len(self.queue)>self.freeze_len:
                self.queue.popleft()
            return self.float()

        return val

    def int(self, upto=12):
        return int(self.float()*(upto+1))

    def coin(self, prob_true=0.5):
        return self.float() <= prob_true


if __name__ == '__main__':

    fr = FreezableRandom()
    fr.freeze(3)
    for i in range(16):
        print(f'{i+1:02d} -->', fr.int())
    fr.freeze(5)    
    for i in range(16, 32):
        print(f'{i+1:02d} -->', fr.int())
    fr.freeze(3)    
    for i in range(32, 48):
        print(f'{i+1:02d} -->', fr.int())

