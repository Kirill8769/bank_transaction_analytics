import json
import re
import os
import pandas as pd
from datetime import datetime

import requests

from utils import logger


def foo(user_date: str):
    if not isinstance(user_date, str):
        raise TypeError("Передан неверный тип данных, ожидается str")
    pattern = re.compile(r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b')
    date_str = pattern.search(user_date)
    if not date_str:
        raise ValueError("Передан неверный формат даты, ожидается YYYY-MM-DD HH:MM:SS")
    
    end_date = datetime.strptime(date_str[0], "%Y-%m-%d %H:%M:%S")
    start_date = datetime(end_date.year, end_date.month, 1)
    print(end_date, start_date)
    print(get_time_of_day(end_date))

    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    result = json.loads(response.text)
    #print(result)

    
    settings_path = os.path.join("user_settings.json")
    if os.path.isfile(settings_path):
        with open(settings_path, encoding="UTF-8") as file:
            user_settings = json.load(file)
            print(user_settings)
    else:
        # log , raise
        pass
    
    filter_result = []
    for k, v in result["Valute"].items():
        if k in user_settings["user_currencies"] or k in user_settings["user_stocks"]:
            print(k, v["Value"])




def get_operations(start_date, stop_date):
    filepath = os.path.join("data", "operations.xls")
    df = pd.read_excel(filepath)
    print(df.columns)
    # # ['Дата операции', 'Дата платежа', 'Номер карты', 'Статус',
    #    'Сумма операции', 'Валюта операции', 'Сумма платежа', 'Валюта платежа',
    #    'Кэшбэк', 'Категория', 'MCC', 'Описание', 'Бонусы (включая кэшбэк)',
    #    'Округление на инвесткопилку', 'Сумма операции с округлением']



get_operations()






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




foo("2023-12-22 13:13:13")



