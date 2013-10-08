"""Implements a very simple undo system"""
from ..session import Session

def store_last_operation(session, operation):
    """Store most recent operation"""
    session.last_operation = operation

def undo(self):
    """Apply the operation reversely"""
    if self.last_operation:
        self.apply(self.last_operation.inverse())

Session.OnApplyOperation.add(store_last_operation)
Session.undo = undo
Session.last_operation = None

import logging
logging.info('undo system loaded')
