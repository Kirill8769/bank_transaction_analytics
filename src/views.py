import json
from datetime import datetime
from typing import Any

import pandas as pd

from src.files import user_settings
from src.loggers import logger
from src.utils import (
    check_date,
    get_filtered_df,
    get_list_categories_with_amounts,
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

        json_result["currency_rates"] = get_price_currencies_user(user_settings)
        json_result["stock_prices"] = get_price_stocks_user(user_settings)

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
                "total_amount": 0,
                "main": [],
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
            "total_amount": 0,
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
    try:
        filtered_df = get_filtered_df(date=date, range_data=range_data)
        if filtered_df is None:
            raise TypeError("Ожидается тип данных DataFrame")
        for column in ["Сумма платежа", "Статус", "Категория"]:
            if column not in filtered_df.columns:
                raise ValueError("Переданный DataFrame не содержит необходимые, для обработки, поля")

        # Сумма расходов
        df_costs = filtered_df.loc[(filtered_df["Сумма платежа"] < 0) & (filtered_df["Статус"] == "OK")]
        total_sum_costs = df_costs["Сумма платежа"].sum()
        json_result["expenses"]["total_amount"] = round(abs(total_sum_costs))

        # Основные расходы
        df_main = df_costs.loc[~df_costs["Категория"].isin(["Наличные", "Переводы"])]
        group_by_category_main = df_main.groupby(df_costs["Категория"])
        sum_by_category_main = group_by_category_main["Сумма платежа"].sum().sort_values(ascending=True).head(7)
        json_result["expenses"]["main"] = get_list_categories_with_amounts(sum_by_category_main)

        # Переводы и наличные
        df_transfer_cash = df_costs.loc[df_costs["Категория"].isin(["Наличные", "Переводы"])]
        group_by_category_tc = df_transfer_cash.groupby(df_costs["Категория"])
        sum_by_category_tc = group_by_category_tc["Сумма платежа"].sum().sort_values(ascending=True)
        json_result["expenses"]["transfers_and_cash"] = get_list_categories_with_amounts(sum_by_category_tc)

        # Сумма поступлений
        df_receipt = filtered_df.loc[(filtered_df["Сумма платежа"] > 0) & (filtered_df["Статус"] == "OK")]
        total_sum_receipt = df_receipt["Сумма платежа"].sum()
        json_result["income"]["total_amount"] = round(total_sum_receipt)

        # Поступления по категориям
        group_by_category_receipt = df_receipt.groupby(df_receipt["Категория"])
        sum_by_category_receipt = group_by_category_receipt["Сумма платежа"].sum().sort_values(ascending=False)
        json_result["income"]["main"] = get_list_categories_with_amounts(sum_by_category_receipt)

        # Валюта и акции
        json_result["currency_rates"] = get_price_currencies_user(user_settings)
        json_result["stock_prices"] = get_price_stocks_user(user_settings)





    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        return json.dumps(json_result, indent=4, ensure_ascii=False)





# res = get_json_events("2021-09-22 11:11:11", "M")
# print(res)

# cur = get_price_currencies_user(user_settings)
# print(cur)

# st = get_price_stocks_user(user_settings)
# print(st)
