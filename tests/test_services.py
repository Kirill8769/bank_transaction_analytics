import json

import pandas as pd
import pytest

from src.services import get_categories_of_increased_cashback


@pytest.fixture()
def test_operations():
    operations = {
        "Дата платежа": ["01.11.2022", "20.11.2022", "01.11.2022", "01.06.2023"],
        "Категория": ["Мебель", "Супермаркет", "Мебель", "Мебель"],
        "Кэшбэк": [10, 5, 7, 40],
    }
    return pd.DataFrame(operations)


@pytest.mark.parametrize(
    "year, month, expected",
    [(2023, 6, [{"Мебель": 40}]), (2022, 11, [{"Мебель": 17}, {"Супермаркет": 5}]), (2022, 2, [])],
)
def test_get_categories_of_increased_cashback_correct(test_operations, year, month, expected):
    result = get_categories_of_increased_cashback(test_operations, year, month)
    json_result = json.loads(result)
    assert json_result == expected


@pytest.mark.parametrize(
    "year, month, expected",
    [
        ("incorrect_type", 11, []),
        (2023, "incorrect_type", []),
    ],
)
def test_get_categories_of_increased_cashback_type_error(test_operations, year, month, expected):
    result = get_categories_of_increased_cashback(test_operations, year, month)
    json_result = json.loads(result)
    assert json_result == expected


def test_get_categories_of_increased_cashback_key_error():
    operations = pd.DataFrame({"A": [1, 2, 3]}, {"B": [1, 2, 3]}, {"C": [1, 2, 3]})
    result = get_categories_of_increased_cashback(operations, 2023, 6)
    assert result == "[]"


def test_get_categories_of_increased_cashback_incorrect_type_data():
    result = get_categories_of_increased_cashback("incorrect_data", 2023, 6)
    assert result == "[]"
