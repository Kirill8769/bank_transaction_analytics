import logging.config
import os
from datetime import datetime

from src.config import path_project


def my_logger() -> logging.Logger:
    log_file = os.path.join(path_project, "!=log_config.ini")
    if os.path.isfile(log_file):
        logging.config.fileConfig(log_file)
        config_logger = logging.getLogger("my_logger")
        return config_logger
    else:
        file_logger = logging.getLogger("logger")
        file_logger.setLevel("DEBUG")
        log_file = os.path.join(path_project, "logs", f'log_{datetime.today().strftime("%d_%m_%Y")}.log')
        file_handler = logging.FileHandler(filename=log_file, encoding="UTF-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(filename)s-%(funcName)s: %(message)s", datefmt="%d.%m.%Y-%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        file_logger.addHandler(file_handler)
        return file_logger


logger = my_logger()
