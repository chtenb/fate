"""Implements a simple linear undo system"""
from ..session import Session
import logging


def store_last_operation(session, operation):
    """Store most recent operation, unless it is an undo or a redo"""
    if not session.performing_undo_or_redo:
        del session.operation_list[session.last_operation + 1:]
        session.operation_list.append(operation)
        session.last_operation += 1
    session.performing_undo_or_redo = False


def undo(self):
    """Apply the last operation reversely"""
    if self.last_operation >= 0:
        self.performing_undo_or_redo = True
        self.apply(self.operation_list[self.last_operation].inverse())
        self.last_operation -= 1
Session.undo = undo


def redo(self):
    """Redo the next operation in the list"""
    if self.last_operation < len(self.operation_list) - 1:
        self.performing_undo_or_redo = True
        self.last_operation += 1
        self.apply(self.operation_list[self.last_operation])
Session.redo = redo


Session.OnApplyOperation.add(store_last_operation)
Session.operation_list = []
Session.last_operation = -1
Session.performing_undo_or_redo = False

logging.info('undo system loaded')
