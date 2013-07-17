"""An operator takes a selection (and optional additional arguments) and returns a derived operation"""
from operation import Operation

def insert_after(text, selection, string):
    old_content = text.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(s + string)
    return Operation(text, selection, new_content)

def insert_before(text, selection, string):
    old_content = text.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string + s)
    return Operation(text, selection, new_content)

def insert_in_place(text, selection, string):
    old_content = text.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string)
    return Operation(text, selection, new_content)

def insert_around(text, selection, string):
    old_content = text.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(s + string + s)
    return Operation(text, selection, new_content)
