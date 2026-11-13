import os
import hashlib
import pandas as pd
import gdown

DATA_PATH = 'data/synthetic_dataset.csv'
FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
EXPECTED_MD5 = 'e9c826d7cfa6f9d984caab27c74866ec'

def calculate_md5(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_file() -> None:
    # Создаем папку data, если ее нет
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    if os.path.exists(DATA_PATH):
        if calculate_md5(DATA_PATH) == EXPECTED_MD5:
            print(f"Файл {DATA_PATH} корректен. Пропускаем скачивание.")
            return
        else:
            print(f"Файл {DATA_PATH} поврежден. Удаляем и скачиваем заново.")
            os.remove(DATA_PATH)

    print("Скачиваем файл с Google Диска...")
    url = f'https://drive.google.com/uc?id={FILE_ID}'
    try:
        gdown.download(url, DATA_PATH, quiet=False)
    except Exception as e:
        raise RuntimeError(f"Ошибка скачивания: {e}")

   
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Файл не был скачан (возможно, сбой сети).")
    if calculate_md5(DATA_PATH) != EXPECTED_MD5:
        raise ValueError("Скачанный файл поврежден (MD5 не совпадает).")

def extract_data(limit: int = 100) -> pd.DataFrame:
    download_file()
    try:
        df = pd.read_csv(DATA_PATH, nrows=limit)
        return df
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения CSV: {e}")
