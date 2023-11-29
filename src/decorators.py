import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from config import path_project


def saving_to_file(filename: str | None = None) -> Callable:
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: tuple, **kwargs: dict) -> Any:
            result = func(*args, **kwargs)
            if not filename:
                filename = f"{func.__name__}_{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}"
            file_path = os.path.join(path_project, "data", filename)
            with open(file_path, "w", encoding="UTF-8") as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            return result
        return inner
    return wrapper