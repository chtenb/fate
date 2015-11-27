"""An implementation of a simple event system"""
import logging

class Event:
    """Simple event class"""
    def __init__(self, name):
        self.__name__ = name
        self._handlers = []
        self._temp_handlers = []

    def add(self, handler):
        """
        Add a handler to the event.
        The order in which handlers are added is also the execution order.
        """
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
        logging.debug('Firing event {}'.format(self.__name__))
        for handler in self._handlers:
            try:
                handler(*args)
            except TypeError as e:
                logging.error(e, exc_info=True)

        # Distinct loop to allow adding temp_handlers during event
        for handler in self._temp_handlers:
            try:
                handler(*args)
            except TypeError as e:
                logging.error(e, exc_info=True)

        self._temp_handlers = []
        logging.debug('Finished event {}'.format(self.__name__))

    def add_for_once(self, handler):
        """
        Add a handler to the event, but remove it after the event has been fired.
        These temporary handlers are executed after the normal handlers.
        """
        if not handler in self._temp_handlers:
            self._temp_handlers.append(handler)

