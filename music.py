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


def reverse(iterable):
    return list(reversed(list(iterable)))



note_names = 'C,C#,D,D#,E,F,F#,G,G#,A,A#,B'.split(',')
name_to_note = {name: num for num, name in enumerate(note_names)}


def name(note_or_notes):
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
        return self.root + self.intervals[index%self.size] + 12 * (index//self.size)

    @property
    def size(self):
        return len(self.intervals)

    def __repr__(self):
        return ', '.join(name([self[i] for i in range(self.size)]))

    def transpose(self, semitones):
        return Scale(self.root + semitones, self.intervals)

    def subset(self, root, indices):
        return [self[root + i] for i in indices]
        
    def chord(self, root, n=3):
        offsets = islice((2*o for o in count()), n)
        return self.subset(root, offsets)



major      = [ n - 60 for n in [60, 62, 64, 65, 67, 69, 71] ]
dorian     = mode(major, 1)
phrygian   = mode(major, 2)
lydian     = mode(major, 3)
mixolydian = mode(major, 4)
aolian     = mode(major, 5)
locrian    = mode(major, 6)
minor      = aolian



C  = note('C')
Cs = note('C#')
D  = note('D')
Ds = note('D#')
E  = note('E')
F  = note('F')
Fs = note('F#')
G  = note('G')
Gs = note('G#')
A  = note('A')
As = note('A#')
B  = note('B')


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

    print(name(c_major.chord(0,5)))

