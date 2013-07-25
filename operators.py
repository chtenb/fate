"""An operator takes a selection (and optional additional arguments) and returns an operation"""
from operation import Operation

def insert_after(session, selection, string):
    old_content = session.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(s + string)
    return Operation(session, selection, new_content)

def insert_before(session, selection, string):
    old_content = session.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string + s)
    return Operation(session, selection, new_content)

def insert_in_place(session, selection, string):
    old_content = session.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string)
    return Operation(session, selection, new_content)

def insert_around(session, selection, string):
    old_content = session.selection_content(selection)
    new_content = []
    for s in old_content:
        new_content.append(s + string + s)
    return Operation(session, selection, new_content)
