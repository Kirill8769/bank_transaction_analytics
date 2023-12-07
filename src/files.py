import json
import os
from typing import Any

import pandas as pd

from src.config import PATH_PROJECT
from src.loggers import logger


def get_df_operations() -> pd.DataFrame | None:
    """
    Возвращает DataFrame с данными операций пользователя из файла.

    :return: Путь к файлу с операциями пользователя или None в случае ошибки
    :raises ValueError: Если файл с операциями пользователя не найден.
    :raises Exception: Если возникает неожиданная ошибка при чтении файла.
    """
    df_operations = None
    try:
        file_operations = os.path.join(PATH_PROJECT, "data", "operations.xls")
        if not os.path.isfile(file_operations):
            raise ValueError("Файл с операциями пользователя не найден")
        df_operations = pd.read_excel(file_operations)
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return df_operations


def get_user_settings() -> dict:
    """
    Возвращает настройки пользователя в формате JSON.

    :return: Строка с настройками пользователя в формате JSON или None, если файл не найден.
    :raises ValueError: Если файл с настройками пользователя не найден.
    :raises Exception: Если возникает неожиданная ошибка при чтении файла.
    """
    settings = {}
    try:
        settings_file = os.path.join(PATH_PROJECT, "user_settings.json")
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


def save_result_in_json(filename: str, json_obj: dict[Any, Any]) -> None:
    """
    Сохраняет переданный Список словарей в файл в формате JSON.

    :param filename: Имя файла
    :param json_obj: JSON объект python
    :return: None
    """
    try:
        if not isinstance(filename, str):
            raise TypeError("Переден неверный тип данных объекта filename, ожидатется строка")
        if not isinstance(json_obj, list | dict):
            raise TypeError("Переден неверный тип данных объекта json_obj, ожидатется список словарей")
        file_path = os.path.join(PATH_PROJECT, "results", filename)
        with open(file_path, "w", encoding="UTF-8") as file:
            json.dump(json_obj, file, indent=4, ensure_ascii=False)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)


user_settings = get_user_settings()
