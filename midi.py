import mido
from itertools import *
from random import sample, choices
from music import *
import collections
# import numpy as np
import math
import random
import time
import curses

log_counter = 0
log_messages = collections.deque(maxlen=10)
status_messages = ['' for _ in range(10)]
cc_queue = collections.deque()


def has_cc(cc):
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
    """Display a permaent status on the screen in the given status slot."""
    if slot >= len(status_messages):
        log(f'Slot {slot} exceeds status message limit.')
    else:
        status_messages[slot] = status


def clock_mon(inport, callback):
    clocks = 0
    running = True
    log('Waiting for start...')
    for msg in inport:
        #if msg.type != 'clock':
        #    log('?', msg.type, msg)
        if msg.type == 'start':
            running = True
            log('Start!')
        elif msg.type == 'stop':
            running = False
            log('Stop!')
        elif msg.type == 'control_change' and running:
            log(cc,msg)
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
                 note_callback=None,
                 note_length_callback=None,
                 velocity_callback=None,
                 event_callback=None,
                 stdscr=None
                 ):
        self.outport = outport
        self.inport = inport
        self.last_note_on = None
        # when do we need to turn sth on?
        self.next_on_tick = 0
        # when do we need to turn sth off?
        self.next_off_tick = None

        self.stdscr = stdscr
        stdscr.nodelay(True)
        self.piano_roll_row = 0

        if event_callback is not None:
            log('event callback mode')

            if isinstance(event_callback, collections.Iterable):
                log('event callback is an Iterable')
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
            self.outport.send(mido.Message('note_off', note=self.last_note_on))

        try:
            key = scr.getkey()
            if key=='q':
                exit()
            cc_queue.append(key)
            scr.addstr(2,1, f'Commands: {" ".join(cc_queue)}')
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
            w = min(curses.COLS-2, max(len(m) for m in log_messages))
            for i, message in enumerate(log_messages):
                scr.addstr(4+i,1, message + (w - len(message)) * ' ')

            # clear screen if we reached the bottom with the piano roll
            if self.piano_roll_row==0:
                scr.clear()
            if note:
                # write "piano roll" to screen if we have a note
                note_name = name_simple(note)
                col = min(note+20, curses.COLS-1)
                if note_name.endswith('#'):
                    scr.addstr(self.piano_roll_row, col, note_name[0])
                else:
                    scr.addstr(self.piano_roll_row, col, note_name[0], curses.A_STANDOUT)
            scr.refresh()
            self.piano_roll_row = (self.piano_roll_row+1) % curses.LINES

            # write status infos to screen
            w = min(curses.COLS-2, max(len(m) for m in status_messages))
            for i, message in enumerate(status_messages):
                if len(message) > 0:
                    scr.addstr(curses.LINES - 1 - len(status_messages) +i, 1, message + (w - len(message)) * ' ')
            #
            ########################################


class Cycles:

    def __init__(self):
        self.last_note = None
        self.scale = 8.0

    def get_note(self, tick, cc_queue):
        if len(cc_queue) > 0:
            cc = cc_queue.pop()
            if cc.control == 70:
                self.scale = (cc.value / 127) * 16 + 0.1
            cc_queue.clear()

        # 24 is one cycle per quarter
        quarters = tick / (24 * self.scale)
        s = math.sin(quarters * math.pi) * 0.5 + 0.5  # 0 to 1
        i = round(s * (len(self.cycle_scale) - 1))
        log(f'{self.scale:0.2f}', 'O' * i)
        new_note = self.cycle_scale[i]
        if new_note == self.last_note:
            play_note = None
        else:
            play_note = new_note
        self.last_note = new_note
        return play_note


def up(n):
    return range(n)


def down(n):
    return reverse(range(n))


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
    log(arp, flush=True)
    return arp


digitone_in = 'Elektron Digitone Digitone in 1'
digitone_out = 'Elektron Digitone Digitone out 1'
usb_interface_out = 'USB MIDI Interface'


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


def port_test():
    print('port test')

    print('output ports: ', mido.get_output_names())
    print('input ports: ', mido.get_input_names())

    return

    with mido.open_input('Elektron Digitone Digitone in 1') as inport:
        for msg in inport:
            print(msg)


if __name__ == '__main__':
    print('output ports: ', mido.get_output_names())
    print('input ports: ', mido.get_input_names())
