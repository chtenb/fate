def insert_after(text, selection, string):
    for (beg, end) in selection:
        text.set_interval(end, end, string)

def insert_before(text, selection, string):
    for (beg, end) in selection:
        text.set_interval(beg, beg, string)

def insert_in_place(text, selection, string):
    for (beg, end) in selection:
        text.set_interval(beg, end, string)

def insert_around(text, selection, string):
    insert_before(text, selection, string)
    insert_after(text, selection, string)

