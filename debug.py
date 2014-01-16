import curses
import ipdb

def breakpoint():
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    ipdb.set_trace()
