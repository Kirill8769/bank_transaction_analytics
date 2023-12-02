import json
from typing import Any

import pandas as pd

from src.files import user_settings
from src.utils import get_price_currencies_user, get_price_stocks_user, get_time_of_day, get_user_operations_by_interval


def get_json_dashboard_info(user_date: str) -> str:
    """
    Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    и возвращающую json-ответ со следующими данными:
    Приветствие, в зависимости от текущего времени
    Информацию по каждой карте (Последние 4 цифры карты, сумма расходов, кэшбэк)
    Топ-5 транзакции по сумме платежа
    Курсы валют и стоимость акций из S&P 500

    :param user_date: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS.
    :return: None
    """
    widget_message = get_time_of_day()
    json_result: dict[str, str | list[Any]] = {
        "greeting": widget_message,
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }

    top_transactions, sum_pay_info = get_user_operations_by_interval(user_date)

    if isinstance(top_transactions, pd.DataFrame) and not top_transactions.empty:
        for _, transaction in top_transactions.iterrows():
            json_result["top_transactions"].append(
                {
                    "date": transaction["Дата платежа"],
                    "amount": transaction["Сумма платежа"],
                    "category": transaction["Категория"],
                    "description": transaction["Описание"],
                }
            )

    if isinstance(sum_pay_info, pd.Series) and not sum_pay_info.empty:
        for card, sum_pay in sum_pay_info.items():
            json_result["cards"].append(
                {
                    "last_digits": card[1:],
                    "total_spent": round(abs(sum_pay), 2),
                    "cashback": round(abs(sum_pay / 100), 2),
                }
            )

    currencies_result = get_price_currencies_user(user_settings)
    if isinstance(currencies_result, dict):
        if currencies_result:
            for currency, rate in currencies_result.items():
                json_result["currency_rates"].append({"currency": currency, "rate": rate})

    stocks_result = get_price_stocks_user(user_settings)
    if isinstance(stocks_result, dict):
        if stocks_result:
            for stock, price in stocks_result.items():
                json_result["stock_prices"].append({"stock": stock, "price": price})

    return json.dumps(json_result, indent=4, ensure_ascii=False)
