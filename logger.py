"""
Logger facility module
"""

import logging
import settings
import os


class AppLogger:
    def __init__(self, name):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(settings.DEFAULT_LOG_LEVEL)
        self.__name = name
        self.__verify_log_file(settings.LOG_FILE_PATH)
        fh = logging.FileHandler(settings.LOG_FILE_PATH)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)
        self.__logger.addHandler(logging.StreamHandler())

    @staticmethod
    def __verify_log_file(path_to_file):
        try:
            open(path_to_file, 'w')
        except PermissionError:
            logging.exception(f'Wrong permission for file {path_to_file}')
        except FileNotFoundError as e:
            logging.exception(f'Wrong permission for file {path_to_file}')


    @staticmethod
    def debug(msg):
        logging.debug(msg=msg)

    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def critical(msg):
        logging.critical(msg)

    @staticmethod
    def warning(msg):
        logging.warning(msg)

    @staticmethod
    def exception(msg):
        logging.exception(msg)
