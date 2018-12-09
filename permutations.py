from midi import play_with_voice
import midi
from music import *
from itertools import *
from helpers import *
from math import copysign
from random import random
from getch import getch
from freezable import *

#from pynput.keyboard import Key, Listener
#import curses, time






last_control = None


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
    # chord = Scale(C - 12, major).chord(1, 6)
    chord = Scale(C - 12, dorian).chord(0, 6)
    gen = chain.from_iterable(permutations(chord, 3)) # was 3
    for note in gen:
        if True or random()>0.3:
            yield note


def monotonic_permutations_2():
    notes = monotonic_permutations()

    def handler(t,ccq):
        return next(notes)

    return handler



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


def rand_branch(gen1, gen2, p):
    while True:
        v1 = next(gen1)
        v2 = next(gen2)
        yield v1 if random() < p else v2


def rand_gate(p, gen):
    return rand_branch(gen, repeat(None), p)


def cycle_scale(scale, indices):
    c = cycle(indices)
    while True:
         yield scale[next(c)]


def coin_flip(p=0.5):
    return random() < p


def gate_diff(gen):
    last = next(gen)
    yield last

    while True:
        v = next(gen)
        yield v if v!=last else None
        last = v

def gate_diff_n(gen, n):
    q = deque(maxlen=n+1)

    while True:
        v = next(gen)
        q.append(v)
        if all(vq==v for vq in q):
            yield None
        else:
            yield v


"""
 C     D     E  F     G     A     B  C     D     E  F     G     A     B  C     D     E  F     G     A     B 
01 02 03 04 05 06 07 08 09 10 11 12 01 02 03 04 05 06 07 08 09 10 11 12 01 02 03 04 05 06 07 08 09 10 11 12
 A                    A                    A                    A                    A                    A

"""

def my_gate(p):
    #all_chord_tones = [3,5,7,4,6,9]
    # all_chord_tones = [1,2,3,4,5,6,7,8,7,6,5,4,3,2,1,1]
    all_chord_tones = [1,3,5,7,9,11,13,2,4,6,8,10,12,14]
    chord_tone_choices = cycle([all_chord_tones[:n] for n in range(1, len(all_chord_tones)+1)])

    chord_tone_cycle = cycle(i-1 for i in next(chord_tone_choices))

    scales = cycle([Scale(root-12, major) for root in circle_of_fifths])
    ticks = 0
    bars = 0
    rnd = FreezableRandom(32)

    while True:

        if ticks % 16 == 0:
            scale = next(scales)
            midi.log(f'switching scale to {scale}')

        if midi.has_cc('d'):
            new_chord_tones = next(chord_tone_choices)
            chord_tone_cycle = cycle(i-1 for i in new_chord_tones)
            midi.log(f'chord tones are {new_chord_tones}')
        if midi.has_cc('2'):
            p += 0.1
        if midi.has_cc('1'):
            p -= 0.1
        if midi.has_cc('f'):
            rnd.freeze(32)
        if midi.has_cc('g'):
            rnd.freeze(0)

        midi.show_status(0, f'prob is {p}')
        midi.show_status(1, 'frozen' if rnd.is_frozen() else 'not frozen')

        maybe_note = next(chord_tone_cycle)
        j = (maybe_note if rnd.coin(p) else None)
        yield scale[j] if j else scale[0] - 12

        ticks += 1
        bars = ticks // 16



def fourths():

    s = [n - 24 for n in islice(Scale(A, minor), 3*7)]
    while True:
        for r in cycle(s):
            for i in range(4):
                yield r + 5*i


def simple():
    # 
    #
    #gen = gate_diff_n( my_gate(0.3), 2)
    gen = my_gate(0.3)

    #gen = fourths()

    return gen


def main(stdscr):
    play_with_voice(
        stdscr,
        note_callback=simple(),
        note_length_callback=cycle([16]),
        velocity_callback=cycle([127,1,1,1]),  #64,48,48,48
        outport_name='USB MIDI Interface', # midi.digitone_out, # 'USB MIDI Interface'
        internal_clock=120)



if __name__ == '__main__':
    import curses
    curses.wrapper(main)

    from threading import Thread
    print('starting')
    #t = Thread(target=watch_input)
    #t.start()





    if False:
        play_with_voice(
                event_callback=filled_chord_permutations_bach_like(),
                outport_name=None, # 'USB MIDI Interface'
                internal_clock=140)


    if False:
        play_with_voice(
                note_callback=filled_chord_permutations(),
                note_length_callback=repeat(8),
                velocity_callback=cycle([64,40]),
                outport_name=None, # 'USB MIDI Interface'
                internal_clock=140)

    elif False:
        play_with_voice(note_callback=cycle(monotonic_permutations()),
                        note_length_callback=repeat(16),
                        velocity_callback=cycle([64,40,40,40]),
                        inport_name=None,
                        outport_name=None, # 'USB MIDI Interface'
                        internal_clock=None) # was 80

    else:
        print('xxx')
        play_with_voice(note_callback=monotonic_permutations_2(),
                        note_length_callback=repeat(16),
                        velocity_callback=cycle([64,40,40,40]),
                        inport_name=None,
                        outport_name=None, # 'USB MIDI Interface'
                        internal_clock=None) # was 80
