import concurrent.futures
import logging
import sys
import time
from typing import Any, Dict, List

import pandas as pd
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

BASE_URL = "https://brewfyi.com/api/v1"


def fetch_all_pages(endpoint: str) -> List[Dict[str, Any]]:
    """Собирает данные со всех страниц API."""
    results: List[Dict[str, Any]] = []
    url: str | None = f"{BASE_URL}/{endpoint}/"

    while url:
        logging.info("Запрос списка: %s", url)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Ошибка при запросе к API: %s", e)
            break

        results.extend(data.get("results", []))
        url = data.get("next")
        time.sleep(0.2)
        
    return results


def fetch_variety_detail(slug: str) -> Dict[str, Any]:
    """Получает подробные данные о конкретном сорте."""
    url = f"{BASE_URL}/varieties/{slug}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Ошибка при получении деталей для '%s': %s", slug, e)
        return {}


def collect_dataset() -> pd.DataFrame:
    """Собирает датасет из данных API, используя многопоточность."""
    logging.info("Начинаем сбор данных о сортах кофе...")
    varieties = fetch_all_pages("varieties")
    logging.info("Найдено сортов: %d", len(varieties))

    slugs = [var.get("slug") for var in varieties if var.get("slug")]
    records: List[Dict[str, Any]] = []

    # Используем ThreadPoolExecutor для параллельных запросов
    # max_workers=5 означает, что мы делаем 5 запросов одновременно
    logging.info("Запускаем параллельную загрузку деталей...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Запускаем задачи
        future_to_slug = {executor.submit(fetch_variety_detail, slug): slug for slug in slugs}
        
        # Собираем результаты по мере их готовности
        for i, future in enumerate(concurrent.futures.as_completed(future_to_slug), 1):
            slug = future_to_slug[future]
            try:
                detail = future.result()
                if detail:
                    logging.info("[%d/%d] Получен: %s", i, len(slugs), slug)
                    record = {
                        "slug": detail.get("slug"),
                        "name": detail.get("name"),
                        "species": detail.get("species"),
                        "description": detail.get("description"),
                        "genetic_group": detail.get("genetic_group"),
                        "altitude_min": detail.get("altitude_min"),
                        "altitude_max": detail.get("altitude_max"),
                        "quality_rating": detail.get("quality_rating"),
                    }
                    records.append(record)
            except Exception as e:
                logging.error("Непредвиденная ошибка при обработке '%s': %s", slug, e)

    return pd.DataFrame(records)


def main() -> None:
    """Основная функция запуска скрипта."""
    df = collect_dataset()
    
    if df.empty:
        logging.error("Не удалось собрать данные. Датасет пуст.")
        sys.exit(1)
        
    logging.info("Успешно собрано записей: %d", len(df))
    
    # Вывод данных
    preview_df = df.drop(columns=['description']).head(10)
    logging.info("Первые 10 строк (без description):\n%s", preview_df.to_string())

    output_filename = "coffee_varieties.csv"
    df.to_csv(output_filename, index=False)
    logging.info("Данные сохранены в %s", output_filename)


if __name__ == "__main__":
    main()
