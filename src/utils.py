import logging.config
import os


def my_logger():
    log_file = os.path.join("logging_config.ini")
    if os.path.isfile(log_file):
        print("logger_file")
        logging.config.fileConfig(log_file)
        my_logger = logging.getLogger("my_logger")
        return my_logger
    else:
        print("logger_console")
        my_logger = logging.getLogger("logger")
        my_logger.setLevel("DEBUG")
        file_handler = logging.FileHandler(filename="logging.log", mode="w", encoding="UTF-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(filename)s-%(funcName)s: %(message)s", datefmt="%d.%m.%Y-%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        my_logger.addHandler(file_handler)
        return my_logger
    

logger = my_logger()
