from midi import play_with_voice
from music import *
from itertools import *
from helpers import *
from math import copysign
from random import random


def fprint(message):
    print(message, flush=True)


def falling_permutations():
    print('weird', flush=True)
    pattern_len = 5
    chords = [Scale(C - 12, major).chord(i - 1, pattern_len) for i in [2, 1, 0, -1, -2, -3, -4]]
    # another sequence
    # chords = [Scale(C, major).subset(i-1,[0,0,1,-1,5]) for i in [2,1,0,-1,-2,-3,-4]]
    generators = cycle([chain.from_iterable(permutations(chord, pattern_len)) for chord in chords])
    g_current = next(generators)
    for i in count(start=1):
        n = next(g_current)
        yield n
        if i % pattern_len == 0:
            g_current = next(generators)


def falling_permutations_2():
    print('weird', flush=True)
    pattern_len = 5
    chords = cycle([Scale(C - 12, major).chord(i - 1, pattern_len) for i in [2, 1, 0, -1, -2, -3, -4]])
    chords = cycle([Scale(C - 12, major).subset(i-1,[0,0,1,-1,5]) for i in [2, 1, 0, -1, -2, -3, -4]])
    perms = permutations(range(pattern_len))

    # iterate over chords
    chord = next(chords)
    # iterate over permutations of sequences of length pattern_len
    perm = next(perms)
    # apply current permutation to current chord and provider iterator over permuted chord
    current_chord = iter([chord[i] for i in perm])
    for i in count(start=1):
        yield next(current_chord)
        if i % pattern_len == 0:
            chord = next(chords)
            perm = next(perms)
            current_chord = iter([chord[i] for i in perm])


# KEEP THIS!
def monotonic_permutations():
    chord = Scale(C - 12, major).chord(1, 6)
    chord = Scale(C - 12, dorian).chord(0, 6)
    gen = chain.from_iterable(permutations(chord, 3))
    for note in gen:
        if True or random()>0.3:
            yield note


two16_permutations = cycle(chain.from_iterable(permutations([8, 8, 8, 16, 16]))) #[8, 8, 8, 16, 16, 16, 32, 32]

simple_rhythm = cycle([8, 8, 8, 16, 16])


def filled_chord_permutations_bach_like():
    c_major = Scale(C,major)
    roots = cycle(r for r in [0,1,-2,-3])
    perms = permutations(range(4))
    for permutation in cycle(permutations(range(4))):
        if True: # only use permutation starting with root note
            if permutation[0] != 0:
                continue
        do_fill = random() < 0.5
        root = next(roots)
        chord = [root + offset for offset in [0,2,0,4]]
        chord = [chord[i] for i in permutation]
        chord.append(chord[0]+7)
        print([name(c_major[i]) for i in chord])
        for i, i_next in zip(chord, chord[1:]):
            direction = sign(i_next - i)
            fill = c_major[i+(i_next-i)//2]
            yield c_major[i]
            # yield c_major[int(i - direction)] if random()<0.5 else None
            yield c_major[int(i + direction)] if random()<0.5 else None
            #yield fill if i_next != i and fill != c_major[i] and do_fill else None #random()<0.5 else None

def filled_chord_permutations():
    c_major = Scale(C,major)
    roots = cycle(r for r in [0,-1,-2,-3])
    perms = permutations(range(4))
    for permutation in cycle(permutations(range(4))):
        if permutation[0] != 0:
            continue
        root = next(roots)
        chord = [root + offset for offset in [0,2,0,4]]
        chord = [chord[i] for i in permutation]
        chord.append(chord[0]) # was + 7
        for i, i_next in zip(chord, chord[1:]):
            direction = sign(i_next - i)
            yield c_major[i]
            if one_in(4):
                if one_in(2):
                    yield c_major[i] + int(direction)
                else:
                    yield c_major[i_next] - int(direction)
            else:
                yield None


def one_falling():
    c_major = Scale(C,major)
    drops = cycle(c_major.iterate(-6,6))
    while True:
        for note in [C,C,C,None]:
            if note is None:
                res = next(drops)
            else:
                res = note
            yield res

if __name__ == '__main__':
    print('xxx')

    if False:
        play_with_voice(
                event_callback=filled_chord_permutations_2(),
                outport_name=None, # 'USB MIDI Interface'
                internal_clock=140)


    if False:
        play_with_voice(
                note_callback=filled_chord_permuçtations(),
                note_length_callback=repeat(8),
                velocity_callback=cycle([64,40]),
                outport_name=None, # 'USB MIDI Interface'
                internal_clock=140)

    else:
        play_with_voice(note_callback=cycle(monotonic_permutations()),
                        note_length_callback=repeat(16),
                        velocity_callback=cycle([64,40,40,40]),
                        outport_name=None, # 'USB MIDI Interface'
                        internal_clock=120)
