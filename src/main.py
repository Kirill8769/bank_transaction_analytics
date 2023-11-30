import os

import pandas as pd
from config import path_project
from src.reports import spending_by_category
from src.services import get_categories_of_increased_cashback
from src.views import get_json_user_operations


def main() -> None:
    transactions_file = os.path.join(path_project, "data", "operations.xls")
    df_transactions = pd.read_excel(transactions_file)
    get_json_user_operations("2021-12-22 11:11:11")
    result_top_cashback = get_categories_of_increased_cashback(df_transactions, 2021, 9)
    print(result_top_cashback)
    spending_by_category(df_transactions, "Супермаркеты", "2019-08-22 11:11:11")


if __name__ == "__main__":
    main()
