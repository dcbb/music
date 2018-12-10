from itertools import *


def transpose(scale, offset=12):
    # Transpose, i.e. add offset semitones.
    return [n + offset for n in scale]


def shift(scale, offset):
    return scale[offset:] + scale[:offset]


def interleave(*args):
    iterators = [iter(iterable) for iterable in args]
    while iterators:
        for it in iterators:
            el = next(it, None)
            if el:
                yield el
            else:
                iterators.remove(it)


note_names = 'C,C#,D,D#,E,F,F#,G,G#,A,A#,B'.split(',')
name_to_note = {name: num for num, name in enumerate(note_names)}
name_to_note['E#'] = name_to_note['F']
name_to_note['B#'] = name_to_note['C']


def name_simple(note: int) -> str:
    """
    Returns the name of a note as a string, excluding MIDI number.
    """
    return note_names[(note - 60) % 12]


def name(note_or_notes):
    """
    Returns the name of a note as a string, including the MIDI note value. Works on single notes
    and lists.
    """

    def name_(note_):
        return f'{note_names[(note_-60)%12]}:{note_}'

    if isinstance(note_or_notes, list):
        return [name_(note) for note in note_or_notes]
    else:
        return name_(note_or_notes)


def note(name, octave=60):
    return name_to_note[name] + octave


def mode(intervals, start_at):
    shifted = shift(intervals, start_at)
    root = shifted[0]
    return [off - root if off >= root else off - root + 12 for off in shifted]


class Scale:

    def __init__(self, root, intervals):
        self.root = root
        self.intervals = intervals

    def __getitem__(self, index):
        return self.root + self.intervals[index % self.size] + 12 * (index // self.size)

    def iterate(self, start, end):
        def generator():
            for i in range(start, end + 1):
                yield self[i]

        return generator()

    @property
    def size(self):
        return len(self.intervals)

    def __repr__(self):
        return ', '.join(name([self[i] for i in range(self.size)]))

    def transpose(self, semitones):
        return Scale(self.root + semitones, self.intervals)

    def subset(self, root, indices):
        return [self[root + i] for i in indices]

    def diatonic_chord(self, root, n=3):
        """
        Get an n note diatonic chord starting at root, e.g. C E G B for C major, root=0 and n=4.
        """
        offsets = islice((2 * o for o in count()), n)
        return self.subset(root, offsets)

    def chord_formula(self, formula: str):
        """
        Get a chord from a formula like "1 b3 5 b7".
        Numbers relate to scale degrees (one-based indexing). "b" subtracts and "#" adds a semitone.
        Double modifiers ("bb") NOT supported currently.
        """
        chord = []
        for note_str in formula.split(' '):
            if note_str.startswith('b'):
                offset = -1
                degree = int(note_str[1:])
            elif note_str.startswith('#'):
                offset = 1
                degree = int(note_str[1:])
            else:
                offset = 0
                degree = int(note_str)
            chord.append(self[degree - 1] + offset)
        return chord


major = [n - 60 for n in [60, 62, 64, 65, 67, 69, 71]]
ionian = major
dorian = mode(major, 1)
phrygian = mode(major, 2)
lydian = mode(major, 3)
mixolydian = mode(major, 4)
aolian = mode(major, 5)
locrian = mode(major, 6)
minor = aolian

all_modes = [ionian, dorian, phrygian, lydian, mixolydian, aolian, locrian]

C = note('C')
Cs = note('C#')
D = note('D')
Ds = note('D#')
E = note('E')
Es = note('E#')
F = note('F')
Fs = note('F#')
G = note('G')
Gs = note('G#')
A = note('A')
As = note('A#')
B = note('B')
Bs = note('B#')

circle_of_fifths = [C, G, D, A, E, B, Fs, Cs, Gs, Ds, As, Es, Bs]

_1 = 0
_2 = 1
_3 = 2
_4 = 3
_5 = 4
_6 = 5
_7 = 6
_8 = 7
_9 = 8
_10 = 9
_11 = 10
_12 = 11
_13 = 12

if __name__ == '__main__':
    print(major)
    print(dorian)
    print(phrygian)
    print(lydian)
    print(minor)

    print()

    c_major = Scale(C, major)
    print(c_major)
    print(c_major.transpose(2))
    print(c_major.transpose(-1))

    print(Scale(D, dorian))
    print(name(Scale(E, phrygian)[7]))

    print(name(c_major.diatonic_chord(0, 5)))

    print('')
    print(Scale(D, dorian))
    print(Scale(F, lydian))

    print('')
    s = Scale(C, major)
    print(name(s.chord_formula('1 b3 5')))
    print(name(s.chord_formula('1 3 5 7')))
    print(name(s.chord_formula('1 3 #5 b7')))
    print(name(s.chord_formula('1 4 5')))
    print(name(s.chord_formula('1 2 5')))
