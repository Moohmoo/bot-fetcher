"""Setup logging configuration for the project."""

import logging
import sys


def setup_logging(level=logging.INFO):
    """Configures the root logger explicitly, removing existing handlers.

    Parameters:
    ----------
        level : int
            The logging level to set for the root logger
            (default is logging.INFO).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Delete existing handlers if any
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    log_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
