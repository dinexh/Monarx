"""Logging configuration for MacMonitor."""

import logging
import os
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Setup logging configuration for MacMonitor.
    
    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / "Library" / "Logs" / "MacMonitor"
    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "macmonitor.log"
    else:
        log_file = None
    
    # Configure logging
    handlers = [logging.StreamHandler()]  # Always log to console
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        handlers.append(file_handler)
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    handlers[0].setFormatter(console_formatter)
    
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('macmonitor')
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    
    return logger

