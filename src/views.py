import json

from src.utils import get_operations, get_range_dates, get_tickers_dicts, get_time_of_day


def get_json_user_operations(user_date: str) -> None:
    """
    Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    и возвращающую json-ответ со следующими данными:

    Приветствие, в зависимости от текущего времени
    Информацию по каждой карте (Последние 4 цифры карты, сумма расходов, кэшбэк)
    Топ-5 транзакции по сумме платежа
    Курс валют
    Стоимость акций из S&P 500

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
    top_transactions, sum_pay_info = get_operations(start_date, end_date)

    currencies_result, stocks_result = get_tickers_dicts()

    if not sum_pay_info.empty:
        for card, sum_pay in sum_pay_info.items():
            json_result["cards"].append(
                {
                    "last_digits": card[1:],
                    "total_spent": round(abs(sum_pay), 2),
                    "cashback": round(abs(sum_pay / 100), 2),
                }
            )

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

    if currencies_result:
        for currency, rate in currencies_result.items():
            json_result["currency_rates"].append({"currency": currency, "rate": rate})

    if stocks_result:
        for stock, price in stocks_result.items():
            json_result["stock_prices"].append({"stock": stock, "price": price})

    with open("result.json", "w", encoding="UTF-8") as file:
        json.dump(json_result, file, indent=4, ensure_ascii=False)
