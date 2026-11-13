import sqlite3
import os
import sys
import hashlib
import pandas as pd
import gdown
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

CREDS_DB_PATH = 'creds.db'
DATA_PATH = 'synthetic_dataset.csv'
FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
EXPECTED_MD5 = 'e9c826d7cfa6f9d984caab27c74866ec'
LIMIT_ROWS = 100
TABLE_NAME = 'khitrykhav'


def get_db_credentials():
    if not os.path.exists(CREDS_DB_PATH):
        raise FileNotFoundError(f"Файл {CREDS_DB_PATH} не найден.")
        
    with sqlite3.connect(CREDS_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, port, user, pass, db_name FROM access WHERE db_name = 'homeworks'")
        row = cursor.fetchone()
        
        if row is None:
            raise ValueError("В creds.db нет данных для 'homeworks'.")
        return row


def calculate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download_file():
    if os.path.exists(DATA_PATH):
        if calculate_md5(DATA_PATH) == EXPECTED_MD5:
            print(f"Файл {DATA_PATH} найден и корректен. Пропускаем скачивание.")
            return
        else:
            print(f"Файл {DATA_PATH} поврежден или изменился. Скачиваем заново.")
            os.remove(DATA_PATH)
            
    print("Скачиваем файл с Google Диска...")
    url = f'https://drive.google.com/uc?id={FILE_ID}'
    try:
        gdown.download(url, DATA_PATH, quiet=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка скачивания: {e}")


def extract_data():
    download_file()
    try:
        df = pd.read_csv(DATA_PATH, nrows=LIMIT_ROWS)
        return df
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения CSV: {e}")


def validate_data(df):
    if df.empty:
        raise ValueError("Датасет пуст.")
    print(f"Подготовлено {len(df)} строк для загрузки.")
    return df


def upload_to_postgres(df):
    db_url, db_port, db_user, db_pass, db_name = get_db_credentials()
    
    url_object = URL.create(
        "postgresql+psycopg2",
        username=db_user,
        password=db_pass,
        host=db_url,
        port=db_port,
        database=db_name,
    )

    try:
        engine = create_engine(url_object)
        with engine.begin() as conn:
            df.to_sql(TABLE_NAME, con=conn, if_exists='replace', index=False)
            
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{TABLE_NAME}";'))
            db_count = result.fetchone()[0]
            
            if db_count == len(df):
                print(f"Данные ({len(df)} строк) успешно загружены и проверены в таблице '{TABLE_NAME}'.")
            else:
                raise ValueError(f"Ошибка верификации: в БД {db_count} строк, ожидалось {len(df)}.")
                
    except SQLAlchemyError as e:
        raise RuntimeError(f"Ошибка базы данных: {e}")


if __name__ == '__main__':
    print("Начинаем процесс...")
    try:
        credentials = get_db_credentials()
        dataset = extract_data()
        dataset = validate_data(dataset)
        upload_to_postgres(dataset)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)
