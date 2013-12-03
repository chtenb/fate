"""Macros are compositions of selectors and operators"""
from .selectors import next_full_line, previous_full_line, previous_char, next_char
from .operators import interval_operator
import re
import logging


#TODO fix open line when no indentation

def open_line_after(selection):
    """A higher level operator which opens a line after the first
    new line character, for each interval"""
    def get_indent(line):
        m = re.match('\s', line)
        return m.group(0) if m else ''

    @interval_operator
    def add_new_line(content):
        indent = get_indent(content)
        return content + indent + '\n'

    # How to compose easily with extensions and reductions?
    new_line = previous_full_line(add_new_line(next_full_line(selection)))
    return new_line.reduce(previous_char(new_line))


def open_line_before(selection):
    """A higher level operator which opens a line before the first
    new line character, for each interval"""
    def get_indent(line):
        m = re.match('\s', line)
        return m.group(0) if m else ''

    @interval_operator
    def add_new_line(content):
        indent = get_indent(content)
        return indent + '\n' + content

    new_line = next_full_line(add_new_line(next_full_line(selection)))
    return new_line.reduce(previous_char(new_line))
