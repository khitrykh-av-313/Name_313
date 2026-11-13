import sqlite3
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CREDS_DB_PATH = 'creds.db'
TABLE_NAME = 'khitrykhav'

def get_db_credentials() -> tuple:
    if not os.path.exists(CREDS_DB_PATH):
        raise FileNotFoundError(f"Файл {CREDS_DB_PATH} не найден.")

    with sqlite3.connect(CREDS_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, port, user, pass, db_name FROM access WHERE db_name = 'homeworks'")
        row = cursor.fetchone()
        if row is None:
            raise ValueError("В creds.db нет данных для 'homeworks'.")
        return row

def upload_to_postgres(df: pd.DataFrame) -> None:
    db_url, db_port, db_user, db_pass, db_name = get_db_credentials()

    url_object = URL.create(
        "postgresql+psycopg2",
        username=db_user, password=db_pass,
        host=db_url, port=db_port, database=db_name,
    )

    try:
        engine = create_engine(url_object)
        with engine.begin() as conn:
            # Используем replace для идемпотентности учебного пайплайна.
            # Это позволяет перезапускать скрипт без ошибок дублирования данных.
            df.to_sql(TABLE_NAME, con=conn, if_exists='replace', index=False)
            
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{TABLE_NAME}";'))
            db_count = result.fetchone()[0]
            
            if db_count == len(df):
                logging.info(f"Данные ({len(df)} строк) успешно загружены и проверены в таблице '{TABLE_NAME}'.")
            else:
                raise ValueError(f"Ошибка верификации: в БД {db_count} строк, ожидалось {len(df)}.")
                
    except SQLAlchemyError as e:
        logging.error(f"Ошибка базы данных: {e}")
        raise
