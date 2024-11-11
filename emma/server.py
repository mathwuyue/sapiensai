import sys
from fastapi import FastAPI
import uvicorn
import serve
from serve import *
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
import uvicorn.logging

# # Configure logging
# logging.basicConfig(
#     handlers=[RotatingFileHandler('err.log', maxBytes=100000, backupCount=5)],
#     level=logging.ERROR,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# Custom middleware to log err
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s [%(name)s] %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(asctime)s [%(name)s] '
                   '%(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "detailed": {
            "fmt": "%(asctime)s - %(name)s - %(levelname)s"
                      "[%(filename)s:%(lineno)d] - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "err_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "../logs/err.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "detailed",
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "../logs/uvicorn.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "detailed",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default", "access_file"],
            "level": "INFO",
            "propagate": True,
        },
        "uvicorn.error": {
            "handlers": ["default", "err_file"],
            "level": "ERROR",
        },
        "uvicorn.access": {
            "handlers": ["access", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# Function to configure logging
def configure_logging():
    # Apply the logging configuration
    dictConfig(LOGGING_CONFIG)
    
    # Optional: Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('../logs/perf.log'),
            # logging.StreamHandler(sys.stdout)
        ]
    )


app = FastAPI(title="Capybara API Server")

# load all modules in serve/webapi.py
for mod in dir(serve):
    c = getattr(serve, mod, None)
    init_app = getattr(c, "init_app", None)
    if init_app:
        init_app(app)


if __name__ == "__main__":
    configure_logging()
    # uvicorn.run("server:app", host="0.0.0.0", port=9066, log_config=LOGGING_CONFIG, reload=True)
    uvicorn.run("server:app", host="0.0.0.0", port=9066, reload=True)