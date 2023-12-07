from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.decorators import saving_to_file
from src.loggers import logger
from src.utils import check_date


@saving_to_file()
def spending_by_category(df: pd.DataFrame, category: str, date: str | None = None) -> pd.DataFrame | None:
    """
    Функция возвращает траты по заданной категории за последние 3 месяца (от переданной даты).

    :param df: DataFrame с данными о транзакциях.
    :param category: Категория трат, которую следует проанализировать.
    :param date: Дата окончания периода анализа в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или None для использования текущей даты.
    :return: DataFrame с отфильтрованными транзакциями по указанной
    категории за заданный период или None в случае ошибки.
    """
    filtered_df = None
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
        for column in ["Дата операции", "Категория"]:
            if column not in df.columns:
                raise ValueError("Проблема с переданным объектом DataFrame, нет столбцов по которым происходит отбор")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        back_date_dt = user_date_dt - relativedelta(months=3)
        filtered_df = df[
            (df["Статус"] == "OK") &
            (df["Дата операции"] >= back_date_dt) &
            (df["Дата операции"] <= user_date_dt) &
            (df["Сумма операции"] < 0) &
            (df["Категория"] == category)
        ]
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return filtered_df


@saving_to_file()
def spending_by_weekday(df: pd.DataFrame, date: str | None = None) -> pd.DataFrame:
    """
    Функция возвращает средние траты в каждый из дней недели за последние 3 месяца (от переданной даты).

    :param df: DataFrame с данными о транзакциях.
    :param date: Дата окончания периода анализа в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или None для использования текущей даты.
    :return: DataFrame с подсчитанными данными за заданный период
    """
    result_df = {
            "Дни недели": [],
            "Средняя сумма платежей": []
        }
    try:
        if date is None:
            user_date_dt: datetime | None = datetime.now()
        else:
            user_date_dt = check_date(date)
        if not isinstance(user_date_dt, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Передан неверный формат объекта с транзакциями, ожидается DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        back_date_dt = user_date_dt - relativedelta(months=3)
        filtered_df = df[
            (df["Статус"] == "OK") &
            (df["Дата операции"] >= back_date_dt) &
            (df["Дата операции"] <= user_date_dt) &
            (df["Сумма операции"] < 0)
        ]
        group_by_weekday = filtered_df.groupby(df["Дата операции"].dt.weekday)
        avg_sum_by_weekday = group_by_weekday["Сумма платежа"].mean()
        week_days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
            ]
        if isinstance(avg_sum_by_weekday, pd.Series) and not avg_sum_by_weekday.empty:
            for i, mean_pay in avg_sum_by_weekday.items():
                result_df["Дни недели"].append(week_days[i])
                result_df["Средняя сумма платежей"].append(round(abs(mean_pay), 2))
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return pd.DataFrame(result_df)


@saving_to_file()
def spending_workday_weekend(df: pd.DataFrame, date: str | None = None) -> pd.DataFrame:
    """
    Функция выводит средние траты в рабочий и в выходной день за последние 3 месяца (от переданной даты).

    :param df: DataFrame с данными о транзакциях.
    :param date: Дата окончания периода анализа в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или None для использования текущей даты.
    :return: DataFrame с подсчитанными данными за заданный период
    """
    workday_pays = 0.0
    weekend_pays = 0.0
    result_df = {
        "Дни недели": ["Рабочие", "Выходные"],
        "Средняя сумма платежей": [0.0, 0.0]
    }
    try:
        if date is None:
            user_date_dt: datetime | None = datetime.now()
        else:
            user_date_dt = check_date(date)
        if not isinstance(user_date_dt, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Передан неверный формат объекта с транзакциями, ожидается DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        back_date_dt = user_date_dt - relativedelta(months=3)
        filtered_df = df[
            (df["Статус"] == "OK") &
            (df["Дата операции"] >= back_date_dt) &
            (df["Дата операции"] <= user_date_dt) &
            (df["Сумма операции"] < 0)
            ]
        group_by_weekday = filtered_df.groupby(df["Дата операции"].dt.weekday)
        avg_sum_by_weekday = group_by_weekday["Сумма платежа"].mean()

        if isinstance(avg_sum_by_weekday, pd.Series) and not avg_sum_by_weekday.empty:
            for i, mean_pay in avg_sum_by_weekday.items():
                if i in [5, 6]:
                    weekend_pays += abs(mean_pay)
                else:
                    workday_pays += abs(mean_pay)
            else:
                result_df["Средняя сумма платежей"][0] = round(workday_pays, 2)
                result_df["Средняя сумма платежей"][1] = round(weekend_pays, 2)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return pd.DataFrame(result_df)
