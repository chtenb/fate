from ..document import Document
from ..navigation import position_to_coord, coord_to_position
from logging import info, error
from .client import YcmdHandle, Event
from tempfile import gettempdir


def start_ycm_server(doc):
    info('Trying to start ycm server...')

    server = YcmdHandle.StartYcmdAndReturnHandle()
    doc.completer = server
    info('Ycm server started successfully...')
    doc.OnQuit.add(exit_ycm_server)


def exit_ycm_server(doc):
    doc.completer.Shutdown()

Document.OnDocumentInit.add(start_ycm_server)
Document.completer = None


def save_tmp_file(doc):
    tempfile = gettempdir() + '/' + doc.filename.replace('/', '_') + '.fatemp'
    with open(tempfile, 'w') as fd:
        fd.write(doc.text)
    return tempfile


def parse_file(doc):
    if doc.completer.IsReady():
        doc.tempfile = save_tmp_file(doc)
        doc.completer.SendEventNotification(Event.FileReadyToParse,
                                            test_filename=doc.tempfile,
                                            filetype=doc.filetype)


def complete(doc):
    if doc.completer.IsReady():
        line, column = position_to_coord(doc.mode.cursor_position(doc), doc.text)
        info((line, column))
        result = doc.completer.SendCodeCompletionRequest(test_filename=doc.tempfile,
                                                         filetype=doc.filetype,
                                                         line_num=line,
                                                         column_num=column)
        info(result)
        completions = [item['insertion_text'] for item in result['completions']]
        start_column = result['completion_start_column']
        start_position = coord_to_position(line, start_column, doc.text)
        return start_position, completions
