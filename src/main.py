import pandas as pd

from src.files import get_df_operations
from src.reports import spending_by_category, spending_by_weekday, spending_workday_weekend
from src.services import categories_of_increased_cashback, invest_moneybox, simple_search, search_by_phone_number, search_for_transfers_to_individuals
from src.views import get_json_dashboard_info, get_json_events


def main() -> None:
    """
    Основная функция программы.

    Выводит информацию о различных аспектах финансов и трат, такие как главная информация, события, категории повышенного кэшбэка,
    инвестиции в копилку, траты по категории, траты по дням недели и в рабочие/выходные дни, простой поиск, поиск по телефонным номерам
    и поиск переводов физическим лицам.

    :return: None
    """

    print("[+] Start")

    # Страница “Главная”
    get_json_dashboard_info(date="2020-09-22 11:11:11")
    print("[+] Save main")

    # Страница “События”
    get_json_events(date="2020-09-22 11:11:11", range_data="Y")
    print("[+] Save events")

    df_operations: pd.DataFrame | None = get_df_operations()
    if df_operations is not None:
        # Выгодные категории повышенного кэшбэка
        categories_of_increased_cashback(data=df_operations, year=2020, month=3)
        print("[+] Save cashback")

        # Инвесткопилка
        transactions: list[dict] = df_operations.to_dict(orient="records")
        invest_moneybox(month="2020-04", transactions=transactions, limit=50)
        print("[+] Save invest moneybox")

        # Траты по категории
        spending_by_category(df=df_operations, category="Супермаркеты", date="2019-01-22 11:11:11")
        print("[+] Report spending by category OK")

        # Траты по дням недели
        spending_by_weekday(df=df_operations, date="2020-10-22 11:11:11")
        print("[+] Report spending by weekday OK")

        # Траты в рабочий/выходной день
        spending_workday_weekend(df=df_operations, date="2020-10-22 11:11:11")
        print("[+] Report spending workday weekend OK")

    # Простой поиск
    simple_search(query="магнит")
    print("[+] Save simple search")

    # Поиск по телефонным номерам
    search_by_phone_number()
    print("[+] Save search by phone number")

    # Поиск переводов физическим лицам
    search_for_transfers_to_individuals()
    print("[+] search for transfers to individuals")
    print("[+] Finish")


if __name__ == "__main__":
    main()
