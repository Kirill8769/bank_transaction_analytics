import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from src.files import get_df_operations
from src.loggers import logger

load_dotenv()
API_MARKETSTACK = os.getenv("API_MARKETSTACK")


def check_date(date_checked: str) -> datetime | None:
    """
    Проверяет строку с датой на соответствие формату и возвращает объект datetime.

    :param date_checked: Строка с датой в формате YYYY-MM-DD HH:MM:SS.
    :return: Объект datetime, представляющий дату и время.
    :raises TypeError: Если передан неверный тип данных в date_checked (ожидается str).
    :raises ValueError: Если передан неверный формат даты (ожидается YYYY-MM-DD HH:MM:SS).
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result_date = None
    try:
        if not isinstance(date_checked, str):
            raise TypeError("Передан неверный тип данных, ожидается str")
        pattern = re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b")
        date_str = pattern.search(date_checked)
        if not date_str:
            raise ValueError("Передан неверный формат даты, ожидается YYYY-MM-DD HH:MM:SS")
        result_date = datetime.strptime(date_str[0], "%Y-%m-%d %H:%M:%S")
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result_date


def get_time_of_day() -> str:
    """
    Фунция вычисляет какое сейчас время суток и формирует
    приветственное сообщение

    :return: Приветственное сообщение
    """
    datetime_now = datetime.today()
    if datetime_now.hour >= 18:
        message = "Добрый вечер"
    elif datetime_now.hour >= 12:
        message = "Добрый день"
    elif datetime_now.hour >= 6:
        message = "Доброе утро"
    else:
        message = "Доброй ночи"
    return message


def get_df_by_interval(date: str) -> pd.DataFrame |tuple[None | pd.DataFrame, None | pd.Series]:
    """
    Получает операции пользователя из файла, в заданном временном интервале.

    :return: Кортеж из двух элементов: DataFrame с топ-5 транзакциями и Series с общей суммой платежей по картам.
    :raises TypeError: Если start_date или end_date не являются объектами datetime.
    :raises ValueError: Если файл с операциями не найден или если возникли проблемы с фильтрацией данных.
    """

    result_df: pd.DataFrame | None = None
    try:
        user_date = check_date(date)
        if not isinstance(user_date, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        start_date = datetime.replace(user_date, day=1)
        df = get_df_operations()
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Из files.py не получен DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        result_df = df[
            (df["Дата операции"] >= start_date)
            & (df["Дата операции"] <= user_date)
            & (df["Сумма платежа"] < 0)
            & (df["Статус"] == "OK")
        ]
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result_df


def get_filtered_df(date: str, range_data: str) -> pd.DataFrame | None:
    result_df: pd.DataFrame | None = None
    try:
        date_dt = check_date(date)
        if not isinstance(date_dt, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        if not isinstance(range_data, str) or range_data.upper() not in ["W", "M", "Y", "ALL"]:
            raise ValueError('Передан неверный диапазон данных, ожидается тип str. Возможные значения: "W", "M", "Y", "ALL"')
        df = get_df_operations()
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Из files.py не получен DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        if range_data == "W":
            weekday = date_dt.weekday()
            start_week = date_dt - timedelta(days=weekday)
            end_week = start_week + timedelta(days=6)
            result_df = df.loc[(df["Дата операции"] >= start_week) & (df["Дата операции"] <= end_week)]
        elif range_data == "M":
            result_df = df.loc[(df["Дата операции"].dt.year == date_dt.year) & (df["Дата операции"].dt.month == date_dt.month)]
        elif range_data == "Y":
            result_df = df.loc[df["Дата операции"].dt.year == date_dt.year]
        else:
            result_df = df
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result_df
    

def get_list_categories_with_amounts(df_to_handle: pd.Series) -> list:
    result = []
    try:
        if isinstance(df_to_handle, pd.Series) and not df_to_handle.empty:
            for category, sum_pay in df_to_handle.items():
                if isinstance(category, str) and isinstance(sum_pay, float):
                    result.append(
                        {"category": category, "amount": round(abs(sum_pay))}
                    )
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


def get_price_stocks_user(user_settings_dict: dict) -> list | list[dict[str, float]]:
    """
    Получает текущие цены акций из S&P 500.

    :param user_settings_dict: Словарь с настройками пользователя
    :return: Список словарей с ценами акций.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения цен акций.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result = []
    try:
        if not isinstance(user_settings_dict, dict) or "user_stocks" not in user_settings_dict.keys():
            raise ValueError("Ошибка в переданном объекте с настройками пользователя")
        tickers_stocks = {key: 0.0 for key in user_settings_dict["user_stocks"]}
        if tickers_stocks:
            symbols = ",".join(tickers_stocks.keys())
            params = {"access_key": API_MARKETSTACK, "symbols": symbols}
            url = "http://api.marketstack.com/v1/intraday/latest"
            response = requests.get(url, params)
            status_code = response.status_code
            if status_code == 401:
                raise ConnectionError("Проблема с API_MARKETSTACK")
            if not status_code == 200:
                raise ConnectionError(f"Ошибка подключения: {status_code}")
            json_data = response.json()
            for stock in json_data["data"]:
                result.append({"stock": stock["symbol"], "price": stock["last"]})
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


def get_price_currencies_user(user_settings_dict: dict) -> list | list[dict[str, float]]:
    """
    Получает текущие курсы валют.

    :param user_settings_dict: Словарь с настройками пользователя
    :return: Список словарей с курсами валют.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения курсов валют.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result = []
    try:
        if not isinstance(user_settings_dict, dict) or "user_currencies" not in user_settings_dict.keys():
            raise ValueError("Ошибка в переданном объекте с настройками пользователя")
        user_currency = user_settings_dict["user_currencies"]
        if user_currency:
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = requests.get(url)
            if not response.status_code == 200:
                raise ConnectionError("Ошибка подключения")
            currency_info = response.json()
            for curr in user_currency:
                result.append({"currency": curr, "rate": currency_info["Valute"][curr]["Value"]})
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result
