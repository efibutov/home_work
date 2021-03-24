"""
Logger facility module
"""

import logging
from logging.handlers import RotatingFileHandler
import settings


class Logger:
    def __init__(self, name):
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(settings.DEFAULT_LOG_LEVEL)
        file_handler = RotatingFileHandler(
            settings.LOG_FILE_PATH,
            maxBytes=settings.LOG_FILE_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT_STRING))
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(logging.StreamHandler())  # print to console too

    def debug(self, msg):
        self.__logger.debug(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def critical(self, msg):
        self.__logger.critical(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def exception(self, msg):
        self.__logger.exception(msg)
