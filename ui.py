from curses import wrapper
import time
import curses
from random import random

def main(stdscr):
    # Clear screen
    stdscr.clear()
    stdscr.nodelay(True)

    while True:
        x = curses.COLS // 2
        char = 'o'
        for r in range(curses.LINES):
            c = stdscr.getch()
            if 0 <= c <= 255:
                char = chr(c)
            stdscr.addstr(r, x, char, curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1/30)
            x += 1 if random() > 0.5 else -1
            x %= curses.COLS
        stdscr.clear()


wrapper(main)
