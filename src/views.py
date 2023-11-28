import json
import re
import os
import pandas as pd
from datetime import datetime

import requests
from dotenv import load_dotenv

from utils import logger

load_dotenv()
API_MARKETSTACK = os.getenv("API_MARKETSTACK")


def get_range_dates(user_date: str):
    start_date = None
    end_date = None
    try:
        if not isinstance(user_date, str):
            raise TypeError("Передан неверный тип данных, ожидается str")
        pattern = re.compile(r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b')
        date_str = pattern.search(user_date)
        if not date_str:
            raise ValueError("Передан неверный формат даты, ожидается YYYY-MM-DD HH:MM:SS")   
        end_date = datetime.strptime(date_str[0], "%Y-%m-%d %H:%M:%S")
        start_date = datetime(end_date.year, end_date.month, 1)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    finally:
        return start_date, end_date



def get_tickers_dict():
    settings_path = os.path.join("user_settings.json")
    if os.path.isfile(settings_path):
        with open(settings_path, encoding="UTF-8") as file:
            user_settings = json.load(file)
        tickers_currencies = {key: 0 for key in user_settings["user_currencies"]}
        tickers_stocks = {key: 0 for key in user_settings["user_stocks"]}
        return tickers_currencies, tickers_stocks
    else:
        print("tickers error")
        return None, None


def get_price_stocks(user_stocks: dict) -> dict:
    try:
        if not isinstance(user_stocks, dict):
            raise TypeError("Передан неверный формат, ожидается словарь с акциями")
        if user_stocks:
            symbols = ",".join(user_stocks.keys())
            params = {"access_key": API_MARKETSTACK, "symbols": symbols}
            url = f"http://api.marketstack.com/v1/intraday/latest"
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



def get_price_currencies(user_currencies: dict) -> dict:
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

    
    


currencies, stocks = get_tickers_dict()
# get_price_stocks(stocks)
get_price_currencies(currencies)


def get_operations(start_date, stop_date):
    filepath = os.path.join("data", "operations.xls")
    df = pd.read_excel(filepath)
    print(df.columns)
    # # ['Дата операции', 'Дата платежа', 'Номер карты', 'Статус',
    #    'Сумма операции', 'Валюта операции', 'Сумма платежа', 'Валюта платежа',
    #    'Кэшбэк', 'Категория', 'MCC', 'Описание', 'Бонусы (включая кэшбэк)',
    #    'Округление на инвесткопилку', 'Сумма операции с округлением']



#get_operations()






def get_time_of_day(user_date: datetime) -> str:
    message = ""
    try:
        if not isinstance(user_date, datetime):
            raise TypeError("Принимается только дата, тип - datetime")   
        if 0 <= user_date.hour < 6:
            message = "Доброй ночи"
        elif 6 <= user_date.hour < 12:
            message = "Доброе утро"
        elif 12 <= user_date.hour < 18:
            message = "Добрый день"
        elif 18 <= user_date.hour < 24:
            message = "Добрый вечер"
        else:
            raise ValueError("Не удалось определить время суток, проверьте передаваемую дату")
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    finally:
        return message




get_range_dates("2023-12-22 13:13:13")



