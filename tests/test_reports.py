import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_workday_weekend


@pytest.fixture()
def user_transactions():
    transactions = {
        "Дата операции": ["05.11.2022 00:00:00", "20.11.2022 00:00:00",
                          "01.01.2023 00:00:00", "01.06.2023 00:00:00"],
        "Категория": ["Мебель", "Супермаркет", "Мебель", "Мебель"],
        "Статус": ["OK", "OK", "OK", "OK",],
        "Сумма операции": [-120, -200, -100, -1500]

    }
    return pd.DataFrame(transactions)


def test_spending_by_category_correct_answer(user_transactions):
    expected = pd.DataFrame(
        {"Дата операции": [pd.to_datetime("01.06.2023 00:00:00", format="%d.%m.%Y %H:%M:%S")],
         "Категория": ["Мебель"],
         "Статус": ["OK"],
         "Сумма операции": [-1500]}
    )
    result = spending_by_category(user_transactions, "Мебель", "2023-06-22 00:00:00")
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_spending_by_category_incorrect_args(user_transactions):
    assert spending_by_category("incorrect", "Мебель", "2023-06-22 00:00:00") is None
    assert spending_by_category(user_transactions, 123, "2023-06-22 00:00:00") is None
    assert spending_by_category(user_transactions, "Мебель", "2023-06-22") is None


def test_spending_by_weekday_correct_answer(user_transactions):
    result = spending_by_weekday(user_transactions, "2023-06-22 00:00:00")
    assert type(result) == pd.DataFrame


def test_spending_by_weekday_incorrect_args(user_transactions):
    result_1 = spending_by_weekday("incorrect", "2023-06-22 00:00:00")
    assert type(result_1) == pd.DataFrame
    result_2 = spending_by_weekday(user_transactions, "2023-06-22")
    assert type(result_2) == pd.DataFrame


def test_spending_workday_weekend_correct_answer(user_transactions):
    result = spending_workday_weekend(user_transactions, "2023-06-22 00:00:00")
    assert type(result) == pd.DataFrame


def test_spending_workday_weekend_incorrect_args(user_transactions):
    result_1 = spending_workday_weekend("incorrect", "2023-06-22 00:00:00")
    assert type(result_1) == pd.DataFrame
    result_2 = spending_workday_weekend(user_transactions, "2023-06-22")
    assert type(result_2) == pd.DataFrame
