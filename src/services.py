import pandas as pd
from datetime import datetime
from typing import Any
import re

from src.files import save_result_in_json
from src.loggers import logger


def categories_of_increased_cashback(data: pd.DataFrame, year: int, month: int) -> None:
    """
    Анализирует данные по кэшбэку за определенный год и месяц, и записывает в json файл список
    со словарями категорий с увеличенным кэшбэком, отсортированных по убыванию.

    :param data: Pandas DataFrame с данными о платежах.
    :param year: Год для анализа.
    :param month: Месяц для анализа.
    :return: None
    """
    json_result = []
    try:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Передан неверный тип данных объекта data, ожидается DataFrame")
        if not isinstance(year, int):
            raise TypeError("Передан неверный тип данных year, ожидается int")
        if not isinstance(month, int):
            raise TypeError("Передан неверный тип данных month, ожидается int")
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_of_ym = data.loc[(data["Дата операции"].dt.year == year) & (data["Дата операции"].dt.month == month)]
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


def invest_moneybox(month: str, transactions: list[dict[str, Any]], limit: int) -> None:
    """
    Функция рассчитывает возможные накопления по предоставленным данным и записывает в json файл
    сумму, которую удалось бы отложить в инвесткопилку.

    :param month: Месяц, для которого рассчитывается отложенная сумма (строка в формате YYYY-MM)
    :param transactions: Список словарей, содержащий информацию о транзакциях, в которых содержатся следующие поля:
        Дата операции - Дата, когда произошла транзакция (строка в формате YYYY-MM-DD) 
        Сумма операции - Сумма транзакции в оригинальной валюте (число)
    :param limit: Предел, до которого нужно округлять суммы операций (целое число)
    :return: None
    """
    total = 0.0
    json_result = [{"month": month, "limit": limit, "total": total}]
    try:
        if not isinstance(month, str):
            raise TypeError("Переден неверный тип данных объекта month, ожидатется строка")
        if not isinstance(transactions, list) or not isinstance(transactions[0], dict):
            raise TypeError("Переден неверный тип данных объекта transactions, ожидатется список словарей")
        if not isinstance(limit, int):
            raise TypeError("Переден неверный тип данных объекта limit, ожидатется целое число")
        re_date = re.search(r"\d{4}-\d{2}", month)
        if not re_date[0]:
            raise ValueError("Переден неверный формат объекта month, ожидается строка в формате YYYY-MM")
        format_date = datetime.strptime(re_date[0], "%Y-%m").strftime("%m.%Y")
        for transaction in transactions:
            if format_date in transaction["Дата операции"]\
                    and transaction["Статус"] == "OK"\
                    and transaction["Категория"] not in ["Переводы", "Наличные"]\
                    and transaction["Сумма операции"] < 0:
                sum_pay = abs(transaction["Сумма операции"])
                sum_pay_rounding = (sum_pay // limit) * limit + limit
                total += sum_pay_rounding - sum_pay
        else:
            json_result[0]["total"] = round(total, 2)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except ValueError as val_ex:
        logger.error(f"{val_ex.__class__.__name__}: {val_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
    finally:
        filename = f"invest_moneybox_info_{month}_limit_{limit}.json"
        save_result_in_json(filename=filename, json_obj=json_result)


