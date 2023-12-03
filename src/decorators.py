import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable

import pandas as pd

from src.config import path_project
from src.loggers import logger


def saving_to_file(filename: str | None = None) -> Callable:
    """
    Декоратор для для записи отчётов в файл.

    :param filename: Имя файла записи отчётов.
    :return: Декорированная функция.
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: tuple, **kwargs: dict) -> Any:
            try:
                result: pd.DataFrame = func(*args, **kwargs)
                if not isinstance(result, pd.DataFrame):
                    raise TypeError("Декоратор не получил результат функции с типом данных pd.DataFrame")
                if filename:
                    if not isinstance(filename, str):
                        raise TypeError("Передан неверный тип данных filename, ожидается str")
                    filename_edit = f"{filename}.xlsx"
                else:
                    filename_edit = f'{func.__name__}_{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.xlsx'
                file_path = os.path.join(path_project, "reports", filename_edit)
                result.to_excel(file_path, index=False)
                return result
            except TypeError as type_ex:
                logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
            except Exception as ex:
                logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

        return inner

    return wrapper
