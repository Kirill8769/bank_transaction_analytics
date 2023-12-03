from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.decorators import saving_to_file
from src.loggers import logger
from src.utils import check_date


@saving_to_file()
def spending_by_category(df: pd.DataFrame, category: str, date: str | None = None) -> pd.DataFrame | None:
    filtered_transactions = None
    try:
        if date is None:
            user_date_dt: datetime | None = datetime.now()
        else:
            user_date_dt = check_date(date)
        if not isinstance(user_date_dt, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Передан неверный формат объекта с транзакциями, ожидается DataFrame")
        if not isinstance(category, str):
            raise TypeError("Передан неверный формат категории, ожидается тип данных str")
        for column in ["Дата платежа", "Категория"]:
            if column not in df.columns:
                raise ValueError("Проблема с переданным объектом DataFrame, нет столбцов по которым происходит отбор")
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")
        back_date_dt = user_date_dt - relativedelta(months=3)
        filtered_transactions = df[
            (df["Категория"] == category) & (df["Дата платежа"] >= back_date_dt) & (df["Дата платежа"] <= user_date_dt)
        ]
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return filtered_transactions
