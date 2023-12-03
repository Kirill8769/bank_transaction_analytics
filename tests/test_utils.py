from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (
    API_MARKETSTACK,
    check_date,
    get_price_currencies_user,
    get_price_stocks_user,
    get_time_of_day,
    get_user_operations_by_interval,
)


def test_check_date_correct():
    assert check_date("2021-10-22 11:11:11") == datetime(2021, 10, 22, 11, 11, 11)


@pytest.mark.parametrize("date, expected", [("2021-10-22", None), (2021, None)])
def test_check_date_incorrect(date, expected):
    assert check_date(date) == expected


@pytest.mark.parametrize(
    "current_time, expected",
    [
        (datetime(2023, 1, 1, 20, 0, 0), "Добрый вечер"),
        (datetime(2023, 1, 1, 14, 0, 0), "Добрый день"),
        (datetime(2023, 1, 1, 8, 0, 0), "Доброе утро"),
        (datetime(2023, 1, 1, 2, 0, 0), "Доброй ночи"),
    ],
)
@patch("src.utils.datetime")
def test_get_time_of_day_all_days(mock_datetime, current_time, expected):
    mock_datetime.today.return_value = current_time
    result = get_time_of_day()
    assert result == expected
    mock_datetime.today.assert_called_once_with()


def test_get_user_operations_by_interval_correct():
    result = get_user_operations_by_interval("2021-10-22 10:10:10")
    assert type(result) == tuple
    assert type(result[0]) == pd.DataFrame
    assert type(result[1]) == pd.Series


def test_get_user_operations_by_interval_incorrect():
    assert get_user_operations_by_interval("2021-10-22") == (None, None)


@pytest.fixture
def fix_user_settings():
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["TSLA"]}
    return settings


@patch("requests.get")
def test_get_price_currencies_user_ok_connect(mock_get, fix_user_settings):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 35.0}, "EUR": {"Value": 40.0}}}
    mock_get.return_value = mock_response
    assert get_price_currencies_user(fix_user_settings) == {"USD": 35.0, "EUR": 40.0}
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


@patch("requests.get")
def test_get_price_currencies_user_bad_connect(mock_get, fix_user_settings):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"Page not found"}
    mock_get.return_value = mock_response
    assert get_price_currencies_user(fix_user_settings) == None
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


def test_get_price_currencies_user_value_error():
    assert get_price_currencies_user({"A": ["B", "C"]}) == None


@patch("requests.get")
def test_get_price_currencies_user_other_exception(mock_get, fix_user_settings):
    mock_get.side_effect = Exception("Some error")
    assert get_price_currencies_user(fix_user_settings) == None
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


@patch("requests.get")
def test_get_price_stocks_user_ok_connect(mock_get, fix_user_settings):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"symbol": "TSLA", "last": 600.0}]}
    mock_get.return_value = mock_response
    assert get_price_stocks_user(fix_user_settings) == {"TSLA": 600.0}
    params = {"access_key": API_MARKETSTACK, "symbols": "TSLA"}
    mock_get.assert_called_once_with("http://api.marketstack.com/v1/intraday/latest", params)


@patch("requests.get")
def test_get_price_stocks_user_bad_connect(mock_get, fix_user_settings):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"Page not found"}
    mock_get.return_value = mock_response
    assert get_price_stocks_user(fix_user_settings) == None
    params = {"access_key": API_MARKETSTACK, "symbols": "TSLA"}
    mock_get.assert_called_once_with("http://api.marketstack.com/v1/intraday/latest", params)


def test_get_price_stocks_user_value_error():
    assert get_price_stocks_user({"A": ["B", "C"]}) == None


@patch("requests.get")
def test_get_price_stocks_user_other_exception(mock_get, fix_user_settings):
    mock_get.side_effect = Exception("Some error")
    assert get_price_stocks_user(fix_user_settings) == None
    params = {"access_key": API_MARKETSTACK, "symbols": "TSLA"}
    mock_get.assert_called_once_with("http://api.marketstack.com/v1/intraday/latest", params)
