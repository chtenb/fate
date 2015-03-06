from ..document import Document
from ..navigation import position_to_coord
from logging import info
from .client import YcmdHandle, Event
from tempfile import gettempdir


def init_ycm_server(doc):
    info('Trying to start server...')
    server = YcmdHandle.StartYcmdAndReturnHandle()
    server.WaitUntilReady()
    doc.completer = server
    info('Server started successfully...')


def exit_ycm_server(doc):
    doc.server.Shutdown()

Document.OnDocumentInit.add(init_ycm_server)
Document.OnQuit.add(exit_ycm_server)


def save_tmp_file(doc):
    tempfile = gettempdir() + '/' + doc.filename.replace('/', '_') + '.fatemp'
    with open(tempfile, 'w') as fd:
        fd.write(doc.text)
    return tempfile


def parse_file(doc):
    doc.tempfile = save_tmp_file(doc)
    doc.completer.SendEventNotification(Event.FileReadyToParse,
                                        test_filename=doc.tempfile,
                                        filetype=doc.filetype)


def complete(doc):
    line, column = position_to_coord(doc.selection[0][0], doc.text)
    doc.completer.SendCodeCompletionRequest(test_filename=doc.tempfile,
                                            filetype=doc.filetype,
                                            line_num=line,
                                            column_num=column)

Document.OnTextChanged.add(parse_file)
