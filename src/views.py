import datetime
import json

from src.utils import get_user_operations_by_interval, get_range_dates, get_prices_user_tickers, get_time_of_day


def get_json_user_operations(user_date: str) -> None:
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
    json_result = {
        "greeting": widget_message,
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }

    start_date, end_date = get_range_dates(user_date)
    top_transactions, sum_pay_info = get_user_operations_by_interval(start_date, end_date)

    if not top_transactions.empty:
        for _, transaction in top_transactions.iterrows():
            json_result["top_transactions"].append(
                {
                    "date": transaction["Дата платежа"],
                    "amount": transaction["Сумма платежа"],
                    "category": transaction["Категория"],
                    "description": transaction["Описание"],
                }
            )

    if not sum_pay_info.empty:
        for card, sum_pay in sum_pay_info.items():
            json_result["cards"].append(
                {
                    "last_digits": card[1:],
                    "total_spent": round(abs(sum_pay), 2),
                    "cashback": round(abs(sum_pay / 100), 2),
                }
            )

    currencies_result, stocks_result = get_prices_user_tickers()
    if isinstance(currencies_result, dict):
        if currencies_result:
            for currency, rate in currencies_result.items():
                json_result["currency_rates"].append({"currency": currency, "rate": rate})
    

    if isinstance(stocks_result, dict):
        if stocks_result:
            for stock, price in stocks_result.items():
                json_result["stock_prices"].append({"stock": stock, "price": price})

    return json.dumps(json_result, indent=4, ensure_ascii=False)
