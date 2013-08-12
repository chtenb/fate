import logging

class Event:
    """An implementation of a simple event system"""
    def __init__(self):
        self._handlers = []

    def add(self, handler):
        if not handler in self._handlers:
            self._handlers.append(handler)

    def remove(self, handler):
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    def fire(self, *args):
        for handler in self._handlers:
            try:
                handler(*args)
            except Exception as e:
                logging.error(e, exc_info=True)
