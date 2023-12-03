import os
import re
from datetime import datetime

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


def get_user_operations_by_interval(user_date: str) -> tuple[None | pd.DataFrame, None | pd.Series]:
    """
    Получает операции пользователя из файла, в заданном временном интервале.

    :return: Кортеж из двух элементов: DataFrame с топ-5 транзакциями и Series с общей суммой платежей по картам.
    :raises TypeError: Если start_date или end_date не являются объектами datetime.
    :raises ValueError: Если файл с операциями не найден или если возникли проблемы с фильтрацией данных.
    """

    result: tuple[None | pd.DataFrame, None | pd.Series] = (None, None)
    try:
        end_date = check_date(user_date)
        if not isinstance(end_date, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        start_date = datetime(end_date.year, end_date.month, 1)
        df = get_df_operations()
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Из files.py не получен DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filter_by_date: pd.DataFrame = df[
            (df["Дата операции"] >= start_date)
            & (df["Дата операции"] <= end_date)
            & (df["Сумма платежа"] < 0)
            & (df["Статус"] == "OK")
        ]
        top_transactions = filter_by_date.sort_values(by="Сумма платежа", ascending=True).head(5)
        group_num_cards = filter_by_date.groupby(filter_by_date["Номер карты"])
        sum_pay_cards = group_num_cards["Сумма платежа"].sum()
        result = (top_transactions, sum_pay_cards)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


def get_price_stocks_user(user_settings_dict: dict) -> dict[str, float] | None:
    """
    Получает текущие цены акций из S&P 500.

    :param user_settings_dict: Словарь с настройками пользователя
    :return: Словарь с обновленными ценами акций.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения цен акций.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result = None
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
                tickers_stocks[stock["symbol"]] = stock["last"]
            result = tickers_stocks
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


def get_price_currencies_user(user_settings_dict: dict) -> dict[str, float] | None:
    """
    Получает текущие курсы валют.

    :param user_settings_dict: Словарь с настройками пользователя
    :return: Словарь с обновленными курсами валют.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения курсов валют.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result = None
    try:
        if not isinstance(user_settings_dict, dict) or "user_currencies" not in user_settings_dict.keys():
            raise ValueError("Ошибка в переданном объекте с настройками пользователя")
        tickers_currencies = {key: 0.0 for key in user_settings_dict["user_currencies"]}
        if tickers_currencies:
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = requests.get(url)
            if not response.status_code == 200:
                raise ConnectionError("Ошибка подключения")
            currency_info = response.json()
            for currency in tickers_currencies:
                tickers_currencies[currency] = currency_info["Valute"][currency]["Value"]
            result = tickers_currencies
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result
