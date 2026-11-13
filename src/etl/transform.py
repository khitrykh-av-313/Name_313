import pandas as pd

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Датасет пуст.")
    print(f"Подготовлено {len(df)} строк для загрузки.")
    return df
