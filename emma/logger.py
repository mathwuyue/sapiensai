import logging
from datetime import datetime
from pathlib import Path


log_dir = Path.home() / 'logs'

# Set up main logger
logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)  # Capture all levels

# Create performance file handler for normal logging
file_perf_handler = logging.FileHandler(log_dir / 'perf.log', encoding='utf-8')
file_perf_handler.setLevel(logging.INFO)

# Create error file handler for error logging
file_error_handler = logging.FileHandler(log_dir / 'err.log', encoding='utf-8')
file_error_handler.setLevel(logging.ERROR)

# Create formatter with custom format and date format
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add formatter to handlers
file_perf_handler.setFormatter(formatter)
file_error_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_perf_handler)
logger.addHandler(file_error_handler)

# Usage example:
# logger.info("Performance log message")  # Goes to perf.log
# logger.error("Error log message")       # Goes to err.log