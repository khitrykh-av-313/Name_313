import pandas as pd
import gdown
import os

def load_dataset(file_id, output_filename='synthetic_dataset.csv'):
    """
    Функция для загрузки датасета с Google Диска.
    """
    # Проверяем, скачан ли уже файл
    if not os.path.exists(output_filename):
        print("Файл не найден. Скачиваем с Google Диска...")
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, output_filename, quiet=False)
        print("Загрузка завершена!")
    else:
        print(f"Файл '{output_filename}' уже существует. Пропускаем скачивание.")
        
    # Читаем скачанный файл
    df = pd.read_csv(output_filename)
    return df

def preview_data(df, n=10):
    """
    Выводит первые n строк датасета.
    """
    print(f"Первые {n} строк датасета:")
    print(df.head(n))

if __name__ == '__main__':
    # ID файла на Google Диске
    FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
    
    # Загружаем данные
    dataset = load_dataset(FILE_ID)
    
    # Вывод размеров датасета
    print(f"Размер: {dataset.shape[0]} строк, {dataset.shape[1]} столбцов\n")
    
    # Вывод первых 10-ти строк
    preview_data(dataset, n=10)
