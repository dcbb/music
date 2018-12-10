import mido
from music import *
import collections
import time
import curses
from itertools import *

# how many log messages did we have so far?
log_counter = 0
# queue of log message history to display
log_messages = collections.deque(maxlen=10)
# list of status messages to display
status_messages = ['' for _ in range(10)]
# queue of MIDI CC messages (and other control messages)
cc_queue = collections.deque()


def has_cc(cc):
    """
    Checks the message queue for the given message. Returns True and removes the message, if found.
    """
    if cc in cc_queue:
        cc_queue.remove(cc)
        return True
    else:
        return False


def log(message):
    """Display a messgage in the log on the screen."""
    global log_counter
    log_messages.append(f'{log_counter: 4d} {message}')
    log_counter += 1


def show_status(slot, status):
    """Display a permanent status on the screen in the given status slot."""
    if slot >= len(status_messages):
        log(f'Slot {slot} exceeds status message limit.')
    else:
        status_messages[slot] = status


def clock_mon(inport, callback):
    clocks = 0
    running = True
    log('Waiting for start...')
    for msg in inport:
        # if msg.type != 'clock':
        #    log('?', msg.type, msg)
        if msg.type == 'start':
            running = True
            log('Start!')
        elif msg.type == 'stop':
            running = False
            log('Stop!')
        elif msg.type == 'control_change' and running:
            log(cc, msg)
            cc_queue.append(msg)
        elif msg.type == 'clock' and running:
            callback(clocks, cc_queue)
            clocks += 1


def create_clock(bpm):
    def clock(inport, callback):
        delta_t = 60 / bpm / 24
        for clocks in count():
            callback(clocks, cc_queue)
            time.sleep(delta_t)

    return clock


len2tick = {
    1: 64,
    2: 48,
    4: 24,
    8: 12,
    16: 6,
    32: 3,
}


class Voice:

    def __init__(self,
                 outport,
                 inport,
                 event_callback=None,
                 note_callback=None,
                 note_length_callback=None,
                 velocity_callback=None,
                 stdscr=None
                 ):
        """

        :param outport:
            A MIDO outport name.
        :param inport:
            A MIDO inport name.
        :param event_callback:
            A function f(tick_count, cc_message_queue) -> (note, note_length, velocity),
            or an Iterable that yields (note, note_length, velocity).
        :param note_callback:
            A function f(tick_count, cc_message_queue) -> note, or an Iterable that yields a note.
        :param note_length_callback:
            A function f(tick_count, cc_message_queue) -> note_length, or an Iterable that yields a note_length.
        :param velocity_callback:
            A function f(tick_count, cc_message_queue) -> velocity, or an Iterable that yields a velocity.
        :param stdscr:
            A curses stdscr.
        """
        self.outport = outport
        self.inport = inport
        self.last_note_on = None
        # when do we need to turn sth on?
        self.next_on_tick = 0
        # when do we need to turn sth off?
        self.next_off_tick = None

        # for terminal based UI
        self.stdscr = stdscr
        stdscr.nodelay(True)
        self.piano_roll_row = 0

        if event_callback is not None:
            log('event callback mode')
            if isinstance(event_callback, collections.Iterable):
                log('event callback is an Iterable')
                # if we have an Iterable, we create an ad-hoc lambda to have the right signature
                self.event_callback = lambda t, q: next(event_callback)
            else:
                self.event_callback = event_callback

        else:
            log('separate callbacks')
            self.event_callback = None

            if note_length_callback is None:
                note_length_callback = repeat(8)
            if velocity_callback is None:
                velocity_callback = repeat(64)

            if isinstance(note_callback, collections.Iterable):
                log('note callback is an Iterable')
                self.note_callback = lambda t, q: next(note_callback)
            else:
                self.note_callback = note_callback

            if isinstance(note_length_callback, collections.Iterable):
                log('note length callback is an Iterable')
                self.note_length_callback = lambda t, q: next(note_length_callback)
            else:
                self.note_length_callback = note_callback

            if isinstance(velocity_callback, collections.Iterable):
                log('velocity callback callback is an Iterable')
                self.velocity_callback = lambda t, q: next(velocity_callback)
            else:
                self.velocity_callback = velocity_callback

    def tick(self, tick, cc_queue):
        scr = self.stdscr

        if tick == self.next_off_tick and self.last_note_on:
            # turn the current note off
            self.outport.send(mido.Message('note_off', note=self.last_note_on))

        try:
            key = scr.getkey()
            if key == 'q':
                exit()
            cc_queue.append(key)
            scr.addstr(2, 1, f'Commands: {" ".join(cc_queue)}')
        except curses.error:
            pass

        if tick == self.next_on_tick:

            if self.event_callback is None:
                note = self.note_callback(tick, cc_queue)
                note_len = len2tick[self.note_length_callback(tick, cc_queue)]
                velocity = self.velocity_callback(tick, cc_queue)
            else:
                note, note_len, velocity = self.event_callback(tick, cc_queue)

            self.next_off_tick = tick + note_len // 2  # this is essentially gate length, could be a param
            self.next_on_tick = tick + note_len
            if note is not None and velocity is not None:
                self.last_note_on = note
                self.outport.send(mido.Message('note_on', note=note, velocity=velocity))

            ########################################
            # HANDLING THE UI
            #
            # write log to screen
            w = min(curses.COLS - 2, max(len(m) for m in log_messages))
            for i, message in enumerate(log_messages):
                scr.addstr(4 + i, 1, message + (w - len(message)) * ' ')

            # clear screen if we reached the bottom with the piano roll
            if self.piano_roll_row == 0:
                scr.clear()
            if note:
                # write "piano roll" to screen if we have a note
                note_name = name_simple(note)
                col = min(note + 20, curses.COLS - 1)
                if note_name.endswith('#'):
                    scr.addstr(self.piano_roll_row, col, note_name[0])
                else:
                    scr.addstr(self.piano_roll_row, col, note_name[0], curses.A_STANDOUT)
            scr.refresh()
            self.piano_roll_row = (self.piano_roll_row + 1) % curses.LINES

            # write status infos to screen
            w = min(curses.COLS - 2, max(len(m) for m in status_messages))
            for i, message in enumerate(status_messages):
                if len(message) > 0:
                    scr.addstr(curses.LINES - 1 - len(status_messages) + i, 1, message + (w - len(message)) * ' ')
            #
            ########################################


digitone_in = 'Elektron Digitone Digitone in 1'
digitone_out = 'Elektron Digitone Digitone out 1'
usb_interface = 'USB MIDI Interface'
internal_bus = 'IAC Driver IAC Bus 1'


def play_with_voice(stdscr,
                    note_callback=None,
                    note_length_callback=None,
                    velocity_callback=None,
                    event_callback=None,
                    inport_name=None,
                    outport_name=None,
                    internal_clock=None
                    ):
    clock_func = create_clock(bpm=internal_clock) if isinstance(internal_clock, int) else clock_mon
    if isinstance(internal_clock, int):
        log(f'using internal clock @ {internal_clock} bpm')
    else:
        log('using external clock')
    log('trying to open inport...')
    with mido.open_input(inport_name) as inport:
        log('trying to open outport...')
        with mido.open_output(outport_name) as outport:
            voice = Voice(
                outport,
                inport,
                note_callback=note_callback,
                note_length_callback=note_length_callback,
                velocity_callback=velocity_callback,
                event_callback=event_callback,
                stdscr=stdscr
            )
            log('running clock...')
            clock_func(inport, voice.tick)


def list_ports():
    print('Listing ports known to MIDO')
    print('Output ports: ', mido.get_output_names())
    print('Input ports: ', mido.get_input_names())


def input_message_test():
    with mido.open_input('Elektron Digitone Digitone in 1') as inport:
        for msg in inport:
            print(msg)


def voice_test(stdscr):
    import music
    import random

    rhythm = random.sample([4, 8, 8, 16, 16, 16], k=6)
    log(f'rhythm: {rhythm}')

    scale = music.Scale(D, minor)
    notes = cycle(
        chain(scale.diatonic_chord(0), scale.diatonic_chord(1), scale.diatonic_chord(5), scale.diatonic_chord(4))
    )

    play_with_voice(stdscr,
                    note_callback=notes,
                    velocity_callback=cycle([64, 32, 32, 32, 32]),
                    note_length_callback=cycle(rhythm),
                    outport_name=internal_bus,
                    internal_clock=120)


if __name__ == '__main__':
    list_ports()
    curses.wrapper(voice_test)
