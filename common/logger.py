import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from enum import Enum
# import threading
# import time


logger = logging.getLogger('ddtt_monitor')
logger.propagate = False


class LogType(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class Log:
    LOG_FILE = 'monitor.log'
    file_path = ''

    @staticmethod
    def configure():
        # self.lock.acquire()
        exe_parent_path = os.path.split(sys.argv[0])[0]
        Log.file_path = os.path.join(exe_parent_path, 'log', Log.LOG_FILE)
        file_directory = os.path.join(exe_parent_path, 'log')  # os.path.dirname(file_path)
        # print("log directory: " + file_directory)
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        # if logger.hasHandlers():
        #     logger.removeHandler(logger.handlers[0])
        if not logger.hasHandlers():
            handler = RotatingFileHandler(
                Log.file_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=5
            )
            fmt = '%(asctime)s-%(filename)s:%(funcName)s:%(lineno)s => %(message)s'
            formatter = logging.Formatter(fmt)
            color_formatter = ColorFormatter(fmt)
            # handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            stream_handler = StreamHandler()
            stream_handler.setFormatter(color_formatter)
            # stream_handler.setLevel(logging.DEBUG)
            logger.addHandler(stream_handler)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        # self.lock.release()


class ColorFormatter(logging.Formatter):
    # ANSI color formats 8-bit: "\033[1;31;m {message}\033[m"
    # ESC[38;5;⟨n⟩m Select foreground color      where n is a number from the table below
    # ESC[48;5;⟨n⟩m Select background color
    # 0-  7:  standard colors (as in ESC[ 30–37 m)
    # 8- 15:  high intensity colors (as in ESC[ 90–97 m)
    # 16-231:  6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
    # 232-255:  grayscale from dark to light in 24 steps
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__(fmt)

    def format(self, record):
        fmt = super().format(record)
        formats = {
            logging.DEBUG: self.grey + fmt + self.reset,
            logging.INFO: self.blue + fmt + self.reset,
            logging.WARNING: self.yellow + fmt + self.reset,
            logging.ERROR: self.red + fmt + self.reset,
            logging.CRITICAL: self.bold_red + fmt + self.reset
        }
        log_fmt = formats.get(record.levelno)

        return log_fmt
