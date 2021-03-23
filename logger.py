"""
Logger facility module
"""

import logging
import settings


class AppLogger:
    def __init__(self, name):
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(settings.DEFAULT_LOG_LEVEL)
        self.__verify_log_file(settings.LOG_FILE_PATH)
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(logging.StreamHandler())  # print to console too

    # todo: should I do this?
    @staticmethod
    def __verify_log_file(path_to_file):
        try:
            open(path_to_file, 'w')
        except PermissionError:
            logging.exception(f'Wrong permission for file {path_to_file}')
        except FileNotFoundError as e:
            logging.exception(f'Wrong permission for file {path_to_file}')

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
