from ..document import Document
from logging import info
from .client import YcmdHandle

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
