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




def get_range_dates(user_date: str): # USED
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



def get_time_of_day() -> str: # USED
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



def get_operations(start_date, end_date):
    filepath = os.path.join("data", "operations.xls")
    df = pd.read_excel(filepath)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filter_by_date: pd.DataFrame = df[(df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date) & (df["Сумма платежа"] < 0)]
    top_transactions = filter_by_date.sort_values(by="Сумма платежа", ascending=True).head(5)
    group_num_cards = filter_by_date.groupby(filter_by_date["Номер карты"])
    sum_pay_cards = group_num_cards["Сумма платежа"].sum()
    print(top_transactions)
    print(sum_pay_cards)
    # print(group_num_cards)
    return top_transactions, sum_pay_cards







def get_tickers_dicts() -> tuple:
    result = (None, None)
    settings_path = os.path.join("user_settings.json")
    try:
        if os.path.isfile(settings_path):
            with open(settings_path, encoding="UTF-8") as file:
                user_settings = json.load(file)
            tickers_currencies = {key: 0 for key in user_settings["user_currencies"]}
            tickers_stocks = {key: 0 for key in user_settings["user_stocks"]}
            result = (tickers_currencies, tickers_stocks)
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return result


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


def get_json_user_operations():
    user_date = "2021-12-22 13:13:13" # input("Укажите дату в формате YYYY-MM-DD HH:MM:SS: ")
    start_date, end_date = get_range_dates(user_date)
    if start_date and end_date:
        top_transactions, sum_pay_info = get_operations(start_date, end_date)
    widget_message = get_time_of_day()
    tickers_currencies, tickers_stocks = get_tickers_dicts()
    # currencies_result = get_price_currencies(tickers_currencies)
    # stocks_result = get_price_stocks(tickers_stocks)

    json_result = {
        "greeting": widget_message,
        "cards": [],
        "top_transactions": []}
    
    for card in sum_pay_info.items():
        print(card)
        json_result["cards"].append({
            "last_digits": card[0][1:],
            "total_spent": round(abs(card[1]), 2),
            "cashback": round(abs(card[1] / 100), 2)
        })

    for transaction in top_transactions:
        print(transaction)
        json_result["top_transactions"].append({
            "date": transaction["Дата платежа"],
            "amount": transaction["Сумма платежа"],
            "category": transaction["Категория"],
            "description": transaction["Описание"]
        })
    print(json_result)



get_json_user_operations()