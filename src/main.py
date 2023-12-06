import os
import pandas as pd

from src.config import PATH_PROJECT
from src.files import get_df_operations, save_result_in_json
from src.reports import spending_by_category
from src.services import get_categories_of_increased_cashback
from src.views import get_json_dashboard_info, get_json_events


def main() -> None:
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
        get_categories_of_increased_cashback(df_operations, 2020, 3)
        print("[+] Save cashback")

        # Траты по категории
        spending_by_category(df_operations, "Супермаркеты", "2019-01-22 11:11:11")
        print("[+] Report OK")       
    print("[+] Finish")


if __name__ == "__main__":
    main()
