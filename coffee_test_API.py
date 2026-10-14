import logging
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
    """
    Собирает все страницы со всех страниц по очереди.

    Args:
        endpoint (str): Название раздела API.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными.
    """
    results: List[Dict[str, Any]] = []
    url: str | None = f"{BASE_URL}/{endpoint}/"

    while url:
        logging.info("Запрос: %s", url)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Ошибка при запросе к API: %s", e)
            break

        results.extend(data.get("results", []))
        url = data.get("next")
        time.sleep(0.2)  # Пауза между запросами

    return results


def fetch_variety_detail(slug: str) -> Dict[str, Any]:
    """
    Получает детальную информацию о конкретном сорте.

    Args:
        slug (str): Идентификатор сорта.

    Returns:
        Dict[str, Any]: Словарь с детальной информацией.
    """
    url = f"{BASE_URL}/varieties/{slug}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Ошибка при получении деталей для '%s': %s", slug, e)
        return {}


def collect_dataset() -> pd.DataFrame:
    """
    Собирает датасет из данных API.

    Returns:
        pd.DataFrame: Таблица с собранными данными.
    """
    logging.info("Начинаем сбор данных о сортах кофе...")
    varieties = fetch_all_pages("varieties")
    logging.info("Найдено сортов: %d", len(varieties))

    records: List[Dict[str, Any]] = []
    for i, var in enumerate(varieties, 1):
        slug = var.get("slug")
        if not slug:
            continue

        logging.info("[%d/%d] Обработка: %s", i, len(varieties), slug)
        detail = fetch_variety_detail(slug)

        # Извлекаем нужные поля
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
        time.sleep(0.3)  # Пауза между детальными запросами

    return pd.DataFrame(records)


def main() -> None:
    """Основная функция запуска скрипта."""
    df = collect_dataset()
    logging.info("Собрано записей: %d", len(df))
    preview_df = df.drop(columns=['description']).head(10)
    logging.info("Первые 10 строк (без колонки description):\n%s", preview_df.to_string())

    
    # Сохраняем отдельно в CSV
    output_filename = "coffee_varieties.csv"
    df.to_csv(output_filename, index=False)
    logging.info("Данные сохранены в %s", output_filename)


if __name__ == "__main__":
    main()
