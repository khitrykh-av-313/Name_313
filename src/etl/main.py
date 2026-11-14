import argparse
import sys
import traceback
from .extract import extract_data
from .transform import transform_data
from .load import upload_to_postgres

def run_pipeline(limit: int) -> None:
    print("Начинаем процесс...")
    try:
        df = extract_data(limit=limit)
        df = transform_data(df)
        upload_to_postgres(df)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Pipeline")
    parser.add_argument("--limit", type=int, default=100, help="Количество строк (default: 100)")
    args = parser.parse_args()
    run_pipeline(limit=args.limit)
