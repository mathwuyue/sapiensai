import logging
from datetime import datetime

# Set up error logger
file_error_logger = logging.getLogger('error_logger')
file_error_logger.setLevel(logging.ERROR)

# Create file handler that logs to err.log
file_handler = logging.FileHandler('err.log')
file_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
file_error_logger.addHandler(file_handler)