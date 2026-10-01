import pandas as pd

def load_dataset(file_id):
    """
    Функция для загрузки датасета с Google Диска.
    
    Args:
        file_id (str): ID файла на Google Диске.
    
    Returns:
        pd.DataFrame: Загруженный датасет.
    """
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    df = pd.read_csv(url)
    return df

def preview_data(df, n=10):
    """
    Выводит первые n строк датасета и его размер.
    
    Args:
        df (pd.DataFrame): Исходный датасет.
        n (int): Количество строк для вывода.
    """
    print(f"Размер: {df.shape[0]} строк, {df.shape[1]} столбцов\n")
    print(f"Первые {n} строк датасета:")
    print(df.head(n))

if __name__ == '__main__':
    # ID вашего файла на Google Диске
    FILE_ID = '10zWddY15usCdpocAaw-xI-Ixy0sHwi8w'
    
    # Загружаем данные
    dataset = load_dataset(FILE_ID)
    
    # Выводим результат
    preview_data(dataset, n=10)
