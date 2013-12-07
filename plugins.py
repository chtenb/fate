"""This module loads all standard plugins."""
from .session import Session
from . import filetype_system
from . import undo_system
from . import labeling_system

import logging
logging.info("All plugins are loaded.")
