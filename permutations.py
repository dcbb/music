from midi import play_with_voice
from music import *
from itertools import *


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


def monotonic_permutations():
    print('weird', flush=True)
    k = 5
    chord = Scale(C - 24, major).chord(2 - 1, k)
    gen = chain.from_iterable(permutations(chord, k))
    return gen


two16_permutations = cycle(chain.from_iterable(permutations([8, 8, 8, 8, 16, 16]))) #[8, 8, 8, 16, 16, 16, 32, 32]

simple_rhythm = cycle([8, 8, 8, 16, 16])

if __name__ == '__main__':
    play_with_voice(cycle(falling_permutations_2()),
                    two16_permutations,
                    outport_name='USB MIDI Interface',
                    internal_clock=120)
