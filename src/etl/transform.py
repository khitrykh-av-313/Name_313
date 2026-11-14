import pandas as pd
import numpy as np

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Датасет пуст.")

   
    if 'education_level' in df.columns:
        df['education_level'] = df['education_level'].astype('object').fillna('Unknown').astype('category')

   
    if 'soc_percent' in df.columns:
        df['soc_percent'] = df['soc_percent'].clip(lower=0)

   
    cat_cols = ['gender', 'season', 'soil_texture', 'land_cover_type', 'soc_class_label']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')

    print(f"Данные трансформированы. Подготовлено {len(df)} строк.")
    return df
