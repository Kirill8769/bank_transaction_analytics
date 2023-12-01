import os
import re
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from src.files import get_df_operations, user_settings
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


def get_range_dates(user_date: str) -> tuple[datetime | None, datetime | None]:
    """
    Возвращает начальную и конечную даты в виде кортежа на основе входной строки пользователя.

    :param user_date: Строка с датой в формате YYYY-MM-DD HH:MM:SS.
    :return: Кортеж из двух дат: начальной и конечной. Если произошла ошибка, возвращает (None, None)
    """
    start_date = None
    end_date = None
    try:
        end_date = check_date(user_date)
        if not isinstance(end_date, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        start_date = datetime(end_date.year, end_date.month, 1)
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return start_date, end_date


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


def get_user_operations_by_interval(
    start_date: datetime, end_date: datetime
) -> tuple[None | pd.DataFrame, None | pd.Series]:
    """
    Получает операции пользователя из файла, в заданном временном интервале.

    :param start_date: Начальная дата временного интервала.
    :param end_date: Конечная дата временного интервала.
    :return: Кортеж из двух элементов: DataFrame с топ-5 транзакциями и Series с общей суммой платежей по картам.
    :raises TypeError: Если start_date или end_date не являются объектами datetime.
    :raises ValueError: Если файл с операциями не найден или если возникли проблемы с фильтрацией данных.
    """
    result: tuple[None | pd.DataFrame, None | pd.Series] = (None, None)
    try:
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise TypeError("Ожидаются две даты с типом данных datetime")
        df = get_df_operations()
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Из files.py не получен DataFrame")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filter_by_date: pd.DataFrame = df[
            (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма платежа"] < 0)
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


def get_prices_user_tickers() -> tuple[dict[str, float] | dict[str, int] | None, dict[str, float] | dict[str, int] | None]:
    """
    Получает тикеры валют и акций из файла пользовательских настроек,
    с ними обращается к функциям для получения текущей цены на перечисленные
    акции и валюты

    :return: Кортеж с двумя словарями: с полученными курсами валют и ценами акций.
    :raises ValueError: Если файл с настройками пользователя не найден.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    result: tuple[dict[str, float] | dict[str, int] | None, dict[str, float] | dict[str, int] | None] = (None, None)
    print(result)
    try:
        tickers_currencies = {key: 0 for key in user_settings["user_currencies"]}
        currencies_result = get_price_currencies(tickers_currencies)
        tickers_stocks = {key: 0 for key in user_settings["user_stocks"]}
        stocks_result = get_price_stocks(tickers_stocks)
        result = (currencies_result, stocks_result)
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


def get_price_stocks(user_stocks: dict[str, int]) -> dict[str, float] | dict[str, int]:
    """
    Получает текущие цены акций из S&P 500.

    :param user_stocks: Словарь с тикерами акций и начальными значениями цен.
    :return: Словарь с обновленными ценами акций.
    :raises TypeError: Если user_stocks не является словарем с тикерами акций и начальными значениями цен.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения цен акций.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    try:
        if not isinstance(user_stocks, dict):
            raise TypeError("Передан неверный формат, ожидается словарь с акциями")
        if user_stocks:
            symbols = ",".join(user_stocks.keys())
            params = {"access_key": API_MARKETSTACK, "symbols": symbols}
            url = "http://api.marketstack.com/v1/intraday/latest"
            response = requests.get(url, params)
            if not response.status_code == 200:
                raise ConnectionError("Ошибка подключения")
            json_data = response.json()
            for stock in json_data["data"]:
                user_stocks[stock["symbol"]] = stock["last"]
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return user_stocks


def get_price_currencies(user_currencies: dict[str, int]) -> dict[str, float] | dict[str, int]:
    """
    Получает текущие курсы валют.

    :param user_currencies: Словарь с кодами валют и начальными значениями курсов.
    :return: Словарь с обновленными курсами валют.
    :raises TypeError: Если user_currencies не является словарем с кодами валют и начальными значениями курсов.
    :raises ConnectionError: Если возникает ошибка подключения к API для получения курсов валют.
    :raises Exception: Если возникает неожиданная ошибка при обработке данных.
    """
    try:
        if not isinstance(user_currencies, dict):
            raise TypeError("Передан неверный формат, ожидается словарь с валютами")
        if user_currencies:
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = requests.get(url)
            if not response.status_code == 200:
                raise ConnectionError("Ошибка подключения")
            currency_info = response.json()
            for currency in user_currencies:
                user_currencies[currency] = currency_info["Valute"][currency]["Value"]
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ConnectionError as conn_ex:
        logger.error(f"{conn_ex.__class__.__name__}: {conn_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return user_currencies
