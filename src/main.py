import pandas as pd

from src.files import get_df_operations
from src.reports import spending_by_category
from src.services import get_categories_of_increased_cashback
from src.views import get_json_dashboard_info


def main() -> None:
    json_result = get_json_dashboard_info("2021-09-22 11:11:11")
    print(json_result)
    df_operations: pd.DataFrame | None = get_df_operations()
    if df_operations is not None:
        result_top_cashback = get_categories_of_increased_cashback(df_operations, 2021, 2)
        print(result_top_cashback)
        spending_by_category(df_operations, "Супермаркеты", "2019-01-22 11:11:11")
        print("OK")


if __name__ == "__main__":
    main()
