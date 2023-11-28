import logging.config
import os
from datetime import datetime


def my_logger():
    log_file = os.path.join("!=log_config.ini")
    if os.path.isfile(log_file):
        logging.config.fileConfig(log_file)
        my_logger = logging.getLogger("my_logger")
    else:
        my_logger = logging.getLogger("logger")
        my_logger.setLevel("DEBUG")
        log_name = os.path.join("logs", f'log_{datetime.today().strftime("%d_%m_%Y")}.log')
        file_handler = logging.FileHandler(filename=log_name, mode="a", encoding="UTF-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(filename)s-%(funcName)s: %(message)s", datefmt="%d.%m.%Y-%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        my_logger.addHandler(file_handler)
    return my_logger
    

logger = my_logger()
