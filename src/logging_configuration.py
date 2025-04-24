"""Setup logging configuration for the project."""

import logging
import sys 

def setup_logging(level=logging.INFO):
    """Configures the root logger with a specific format and level.
    
    Parameters:
    ----------
        level (int): The logging level to set for the root logger. Default is logging.INFO.
    """
    # Create a formatter with the desired format for log messages
    _ = logging.Formatter("[%(levelname)s] %(message)s")
    # Create a handler for standard output (console)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s", stream=sys.stdout)
