"""An implementation of a simple event system"""
import logging

class Event:
    """Simple event class"""
    def __init__(self):
        self._handlers = []

    def add(self, handler):
        """Add a handler to the event."""
        if not handler in self._handlers:
            self._handlers.append(handler)

    def remove(self, handler):
        """remove handler from the event."""
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    def fire(self, *args):
        """Launch the event by calling all handlers with self as argument."""
        for handler in self._handlers:
            try:
                handler(*args)
            except Exception as e:
                logging.error(e, exc_info=True)
