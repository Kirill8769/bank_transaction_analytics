import json
import os

import pandas as pd

from src.config import path_project
from src.loggers import logger


def get_df_operations() -> pd.DataFrame | None:
    """
    Возвращает DataFrame с данными операций пользователя из файла.

    :return: Путь к файлу с операциями пользователя
    :raises ValueError: Если файл с операциями пользователя не найден.
    :raises Exception: Если возникает неожиданная ошибка при чтении файла.
    """
    df_operations = None
    try:
        file_operations = os.path.join(path_project, "data", "operations.xls")
        if not os.path.isfile(file_operations):
            raise ValueError("Файл с операциями пользователя не найден")
        df_operations = pd.read_excel(file_operations)
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return df_operations


def get_user_settings() -> str:
    """
    Возвращает настройки пользователя в формате JSON.

    :return: Строка с настройками пользователя в формате JSON или None, если файл не найден.
    :raises ValueError: Если файл с настройками пользователя не найден.
    :raises Exception: Если возникает неожиданная ошибка при чтении файла.
    """
    settings = ""
    try:
        settings_file = os.path.join(path_project, "user_settings.json")
        if not os.path.isfile(settings_file):
            raise ValueError("Файл с настройками пользователя не найден")
        with open(settings_file, encoding="UTF-8") as file:
            settings = json.load(file)
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return settings


user_settings = get_user_settings()
