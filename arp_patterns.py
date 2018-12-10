from itertools import *


def reverse(iterable):
    return list(reversed(list(iterable)))


def up(n):
    return range(n)


def down(n):
    return reversed(range(n))


def zigzag(n):
    return chain(range(0, n, 2), range(1, n, 2))


def funnel(n):
    z = zip(range(n // 2), reverse(range(n // 2, n)))
    return chain.from_iterable(z)


def funnel2(n):
    z = zip(range(n), reverse(range(n)))
    return chain.from_iterable(z)


def arpeggio(notes, offsets, n):
    arp = [notes[off] for off in islice(cycle(offsets(len(notes))), n)]
    return arp
