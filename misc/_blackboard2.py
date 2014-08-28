"""
Things to explain:
    definition command

    definition mode (=stateful command)

    why using modes as opposed to using while loop inside command

    how commands can be decorated

    why stateful commands have to be classes or some function that
    creates objects, because we want them to be able to be used
    across documents at the same time


To be decided upon:
    Why we can have commands as input instead of characters
    What to do with mouse input etc

"""

#
# -------------------------------------------------------------------
#

import logging

"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a document.

To make modifications to a document, we define commands.
A command is an abstract object that can make a modification to a
document. A command must therefore be executable (read: callable)
and accept a document as argument.
"""

"""
For instance, consider a very simple implementation of a command that
saves the text of the document to a file.
"""


def save(document):
    """Save document text to file."""
    if document.filename:
        try:
            with open(filename, 'w') as fd:
                fd.write(document.text)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(str(e))
    else:
        logging.error('No filename')


"""
Can we also make commands which are incrementally constructed by the
user while getting feedback, like an insertion operation?
"""

"""
Let us take a simple example command which lets the user set the filename.
One way to do this would be as follows.
Suppose that we can get a character from the user by calling document.ui.getkey().
"""


def setfilename(document):
    filename = ''
    while 1:
        key = document.ui.getkey()
        if key == 'Esc':
            break
        elif key == '\n':
            document.filename = filename
            return
        elif key == '\b':
            filename = filename[:-1]
        else:
            filename += key


"""
One good thing about this definition is that it's easy to write and understand.
But there are several major drawbacks.

Most importantly it blocks the entire thread and as such doesn't allow the user
to do something else, like switching to another document, until this command is finished.
A possible solution to this would be to give each document its own command thread.
But this is complicated, likely to give lots of crossthreading bugs, and removes
the possibility to write commands that operate on multiple documents.
An example of such a command could be a search/replace command over all documents.

...
"""

"""
Another approach to implemented these kind of commands is by making them stateful.
Such a stateful command is then stored somewhere in the document object,
and is called each time there is input to process.
Let us call a stateful commands a 'mode' and assume it is stored in document.mode.
"""

class SetFileName:
    def __init__(self, document):
        document.mode = self

    def processinput(self, userinput):
        pass
