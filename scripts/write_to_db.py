import sqlite3
import os
import sys 
import pandas as pd
import gdown
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

# ВСЕ ПУТИ
CREDS_DB_PATH = 'creds.db'
DATA_PATH = 'synthetic_dataset.csv'
FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
LIMIT_ROWS = 100

TABLE_NAME = 'Khitrykh_Alyona' 

def get_homeworks_credentials():
    """
    Читает логин и пароль для базы homeworks из локального файла creds.db.
    """
    if not os.path.exists(CREDS_DB_PATH):
        raise FileNotFoundError(f"Файл {CREDS_DB_PATH} не найден. Положите его в корень проекта.")

    try:
        with sqlite3.connect(CREDS_DB_PATH) as conn:
            cursor = conn.cursor()
            # Поиск заданного юзера
            cursor.execute("SELECT url, port, user, pass, db_name FROM access WHERE db_name = 'homeworks'")
            row = cursor.fetchone()
            
            if row is None:
                raise ValueError("В базе не найдена запись для 'homeworks'. Проверьте содержимое creds.db.")
            
            # Возвращаем кортеж: (url, port, user, password, dbname)
            return row
    except sqlite3.Error as e:
        raise RuntimeError(f"Ошибка чтения creds.db: {e}")

def load_data():
    """
    Загружает первые 100 строк из датасета.
    Если файла нет — скачивает его.
    """
    if not os.path.exists(DATA_PATH):
        print("Локальный датасет не найден. Скачиваем с Google Диска...")
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        try:
            gdown.download(url, DATA_PATH, quiet=False)
            print("Загрузка завершена!")
        except Exception as e:
            raise RuntimeError(f"Ошибка скачивания датасета: {e}")
    else:
        print(f"Файл '{DATA_PATH}' найден локально. Пропускаем скачивание.")
    
    try:
        df = pd.read_csv(DATA_PATH, nrows=LIMIT_ROWS)
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения CSV: {e}")
        
    if df.empty:
        raise ValueError("Датасет пуст (0 строк).")
    
    print(f"Подготовлено {len(df)} строк для загрузки.")
    return df

def upload_to_postgres(df):
    """
    Подключается к удаленной БД, загружает данные и добавляет Primary Key.
    """
    try:
        db_url, db_port, db_user, db_pass, db_name = get_homeworks_credentials()
        print("Учетные данные успешно получены из creds.db.")
    except Exception as e:
        print(f"Критическая ошибка получения доступов: {e}")
        return

    # Безопасное создание объекта подключения
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
        print(f"Подключаемся к БД {db_name} на сервере {db_url}...")
        
        with engine.begin() as conn:
            # if_exists='replace' выбран намеренно: это позволяет многократно запускать скрипт
            df.to_sql(TABLE_NAME, con=conn, if_exists='replace', index=False)
            print(f"Данные ({len(df)} строк) успешно загружены в таблицу '{TABLE_NAME}'.")
            
            # Добавляем первичный ключ
            alter_query = text(f'ALTER TABLE "{TABLE_NAME}" ADD PRIMARY KEY (household_id);')
            conn.execute(alter_query)
            print(f"Первичный ключ (household_id) успешно добавлен в таблицу '{TABLE_NAME}'.")
        
    except SQLAlchemyError as e:
        print(f"Ошибка при записи в базу данных: {e}")
        raise

if __name__ == '__main__':
    print("Начинаем процесс...")
    try:
        dataset = load_data()
        if dataset is not None:
            upload_to_postgres(dataset)
    except Exception as e:
        print(f"Критическая ошибка выполнения: {e}")
        sys.exit(1)
