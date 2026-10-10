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


def convert_types(df):
    """
    Приводит типы данных датасета к правильным.
    """
    cat_cols = ['gender', 'education_level', 'season', 'soil_texture', 'land_cover_type', 'soc_class_label']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Сносим формат совсем, позволяя Pandas самому определить даты
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        nat_count = df['timestamp'].isna().sum()
        if nat_count > 0:
            print(f"⚠️ Внимание: {nat_count} дат не удалось распознать. Они заменены на NaT.")
            
    return df


def save_to_parquet(df, output_filename='synthetic_dataset.parquet'):
    """
    Сохраняет DataFrame в формат Parquet.
    """
    df.to_parquet(output_filename, index=False)
    print("Сохранение в Parquet завершено!")


if __name__ == '__main__':
    # ID файла на Google Диске
    FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
    
    # Загружаем данные
    dataset = load_dataset(FILE_ID)
    
    # Вывод размеров датасета
    print(f"Размер: {dataset.shape[0]} строк, {dataset.shape[1]} столбцов\n")
    
    # Вывод первых 10-ти строк
    preview_data(dataset, n=10)

    # Приводим типы и сохраняем в Parquet
    dataset = convert_types(dataset)
    save_to_parquet(dataset)
