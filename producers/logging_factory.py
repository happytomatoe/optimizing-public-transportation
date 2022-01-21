import logging
import logging.config
import os
from pathlib import Path


class LoggerFactory(object):
    _configured = False

    @staticmethod
    def __configure():
        if not LoggerFactory._configured:
            path = f"{Path(__file__).parents[0]}/logging.ini"
            assert os.path.exists(path), f"File not exists {path}"
            logging.config.fileConfig(path)
            LoggerFactory._configured = True

    @staticmethod
    def get_logger(name: str):
        """
        A static method called by other modules to initialize logger in
        their own module
        """
        LoggerFactory.__configure()
        return logging.getLogger(name)
