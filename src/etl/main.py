import argparse
import sys
from .extract import extract_data
from .transform import validate_data
from .load import upload_to_postgres

def run_pipeline(limit: int) -> None:
    print("Начинаем процесс...")
    try:
        df = extract_data(limit=limit)
        df = validate_data(df)
        upload_to_postgres(df)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Pipeline для загрузки данных домашних хозяйств.")
    parser.add_argument("--limit", type=int, default=100, help="Количество строк для загрузки (по умолчанию 100)")
    args = parser.parse_args()

    run_pipeline(limit=args.limit)
