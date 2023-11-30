# 1. Траты по категории

# Функция принимает на вход:

# датафрейм с транзакциями
# название категории
# опциональную дату
# Если дата не передана, то берется текущая дата.

# Функция возвращает траты по заданной категории за последние 3 месяца (от переданной даты).

 

# Интерфейс Траты по категории
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd

from src.decorators import saving_to_file
from src.loggers import logger
from src.utils import check_date


@saving_to_file()
def spending_by_category(df: pd.DataFrame,
                         category: str,
                         date: str = None) -> pd.DataFrame:
    try:
        if not date:
            date = datetime.now()
        else:
            date = check_date(date)
        if not isinstance(date, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Передан неверный формат объекта с транзакциями, ожидается DataFrame")
        if not isinstance(category, str):
            raise TypeError("Передан неверный формат категории, ожидается тип данных str")
        
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")
        back_date = date - relativedelta(months=3)
        filtered_transactions = df[(df["Категория"] == category)
                                       & (df["Дата платежа"] >= back_date)
                                       & (df["Дата платежа"] <= date)]
        return filtered_transactions
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
