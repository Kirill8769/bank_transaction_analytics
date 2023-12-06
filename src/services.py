import pandas as pd
from datetime import datetime
from typing import Any

from src.files import save_result_in_json
from src.loggers import logger


def categories_of_increased_cashback(data: pd.DataFrame, year: int, month: int) -> str:
    """
    Анализирует данные по кэшбэку за определенный год и месяц, возвращает JSON-строку со списком
    категорий с увеличенным кэшбэком, отсортированных по убыванию.

    :param data: Pandas DataFrame с данными о платежах.
    :param year: Год для анализа.
    :param month: Месяц для анализа.
    :return: Отформатированная JSON-строка, представляющая список словарей.
             Каждый словарь представляет собой категорию и ее общий кэшбэк.
             Категории отсортированы по убыванию кэшбэка.
    """
    json_result = []
    try:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Передан неверный тип данных объекта data, ожидается DataFrame")
        if not isinstance(year, int):
            raise TypeError("Передан неверный тип данных year, ожидается int")
        if not isinstance(month, int):
            raise TypeError("Передан неверный тип данных month, ожидается int")
        data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], format="%d.%m.%Y")
        filtered_of_ym = data.loc[(data["Дата платежа"].dt.year == year) & (data["Дата платежа"].dt.month == month)]
        group_by_category = filtered_of_ym.groupby(filtered_of_ym["Категория"])
        analysis_result = group_by_category["Кэшбэк"].sum()
        sorted_result = analysis_result.sort_values(ascending=False)
        for category, cashback in sorted_result.items():
            if cashback <= 0:
                break
            json_result.append({category: cashback})
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except KeyError as key_ex:
        logger.error(f"{key_ex.__class__.__name__}: {key_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        filename = f"cashback_info_{year}_{month}.json"
        save_result_in_json(filename=filename, json_obj=json_result)


def invest_copilka(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """
    Функция рассчитывает возможные накопления по предоставленным данным

    :param month: Месяц, для которого рассчитывается отложенная сумма (строка в формате YYYY-MM)
    :param transactions: Список словарей, содержащий информацию о транзакциях, в которых содержатся следующие поля:
        Дата операции - Дата, когда произошла транзакция (строка в формате YYYY-MM-DD) 
        Сумма операции - Сумма транзакции в оригинальной валюте (число)
    :param limit: Предел, до которого нужно округлять суммы операций (целое число)
    :return: Возвращает сумму, которую удалось бы отложить в инвесткопилку.
    """
    format_date = datetime.strptime(month, "%Y-%m").strftime("%m.%Y")
    print(format_date)
    for transaction in transactions:
        print(transaction)
        if format_date in transaction["Дата операции"]:
            print("OK")
            break
