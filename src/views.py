import json
from datetime import datetime
from typing import Any

import pandas as pd

from src.files import user_settings
from src.loggers import logger
from src.utils import (
    check_date,
    get_filtered_df,
    get_price_currencies_user,
    get_price_stocks_user,
    get_time_of_day,
    get_user_operations_by_interval,
)


def get_json_dashboard_info(date: str) -> str:
    """
    Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    и возвращающую json-ответ со следующими данными:
    Приветствие, в зависимости от текущего времени
    Информацию по каждой карте (Последние 4 цифры карты, сумма расходов, кэшбэк)
    Топ-5 транзакции по сумме платежа
    Курсы валют и стоимость акций из S&P 500

    :param date: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS.
    :return: None
    """
    widget_message = get_time_of_day()
    json_result: dict[str, Any] = {
        "greeting": widget_message,
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }

    try:
        user_date = check_date(date)
        if not isinstance(user_date, datetime):
            raise ValueError("Проблема с переданной датой, смотрите логи")
        top_transactions, sum_pay_info = get_user_operations_by_interval(user_date)

        if isinstance(top_transactions, pd.DataFrame) and not top_transactions.empty:
            for _, transaction in top_transactions.iterrows():
                json_result["top_transactions"].append(
                    {
                        "date": transaction["Дата операции"].strftime("%d.%m.%Y"),
                        "amount": transaction["Сумма платежа"],
                        "category": transaction["Категория"],
                        "description": transaction["Описание"],
                    }
                )

        if isinstance(sum_pay_info, pd.Series) and not sum_pay_info.empty:
            for card, sum_pay in sum_pay_info.items():
                if isinstance(card, str) and isinstance(sum_pay, float):
                    json_result["cards"].append(
                        {
                            "last_digits": card[1:],
                            "total_spent": round(abs(sum_pay), 2),
                            "cashback": round(abs(sum_pay) / 100, 2),
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

    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return json.dumps(json_result, indent=4, ensure_ascii=False)


def get_json_events(date: str, range_data: str = "M"):
    json_result = {
        "expenses":
            {
                "total_amount": 32101,
                "main": [
                    {
                        "category": "Супермаркеты",
                        "amount": 17319
                    },
                    {
                        "category": "Фастфуд",
                        "amount": 3324
                    },
                    {
                        "category": "Топливо",
                        "amount": 2289
                    },
                    {
                        "category": "Развлечения",
                        "amount": 1850
                    },
                    {
                        "category": "Медицина",
                        "amount": 1350
                    },
                    {
                        "category": "Остальное",
                        "amount": 2954
                    }
                ],
                "transfers_and_cash": [
                    {
                        "category": "Наличные",
                        "amount": 500
                    },
                    {
                        "category": "Переводы",
                        "amount": 200
                    }
                ]
            },
        "income": {
            "total_amount": 54271,
            "main": [
                {
                    "category": "Пополнение_BANK007",
                    "amount": 33000
                },
                {
                    "category": "Проценты_на_остаток",
                    "amount": 1242
                },
                {
                    "category": "Кэшбэк",
                    "amount": 29
                }
            ]
        },
        "currency_rates": [],
        "stock_prices": []
    }
    filtered_df = get_filtered_df(date=date, range_data=range_data)
    if filtered_df is not None:
        df_costs = filtered_df.loc[(filtered_df["Сумма платежа"] < 0) & (filtered_df["Статус"] == "OK")]
        total_sum_costs = df_costs["Сумма платежа"].sum()
        print(total_sum_costs)
        # Траты по категориям и поступлениям
        group_by_category = df_costs.groupby(filtered_df["Категория"])
        print(group_by_category)
        sum_costs_by_category = group_by_category["Сумма платежа"].sum()
        print(sum_costs_by_category)
        top_sum_costs_by_category = sum_costs_by_category.sort_values(ascending=True).head(7)
        print(top_sum_costs_by_category)


get_json_events("2021-09-22 11:11:11", "Y")
