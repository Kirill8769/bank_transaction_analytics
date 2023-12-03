import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture()
def user_transactions():
    transactions = {
        "Дата платежа": ["05.11.2022", "20.11.2022", "01.01.2023", "01.06.2023"],
        "Категория": ["Мебель", "Супермаркет", "Мебель", "Мебель"],
    }
    return pd.DataFrame(transactions)


def test_spending_by_category_correct_answer(user_transactions):
    expected = pd.DataFrame(
        {"Дата платежа": [pd.to_datetime("01.06.2023", format="%d.%m.%Y")], "Категория": ["Мебель"]}
    )
    result_1 = spending_by_category(user_transactions, "Мебель", "2023-06-22 00:00:00")
    pd.testing.assert_frame_equal(result_1.reset_index(drop=True), expected)


def test_spending_by_category_incorrect_args(user_transactions):
    assert spending_by_category("incorrect", "Мебель", "2023-06-22 00:00:00") is None
    assert spending_by_category(user_transactions, 123, "2023-06-22 00:00:00") is None
    assert spending_by_category(user_transactions, "Мебель", "2023-06-22") is None
