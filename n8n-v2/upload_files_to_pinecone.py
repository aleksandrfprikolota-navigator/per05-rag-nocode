import os
import requests
import json
from pathlib import Path
from typing import List, Dict

def read_txt_files_from_directory(directory: str = "./data") -> List[Dict]:
    """
    Читает все .txt файлы из указанной директории.
    
    Args:
        directory: Путь к директории с .txt файлами
    
    Returns:
        Список словарей с данными файлов
    """
    files_data = []
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist")
    
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {directory}")
    
    for filename in txt_files:
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                files_data.append({
                    "fileName": filename,
                    "text": content
                })
                print(f"✓ Прочитан файл: {filename} ({len(content)} символов)")
        except Exception as e:
            print(f"✗ Ошибка чтения файла {filename}: {e}")
    
    return files_data


def upload_to_pinecone(files_data: List[Dict], webhook_url: str, namespace: str = "default") -> Dict:
    """
    Загружает файлы в Pinecone через n8n webhook.
    
    Args:
        files_data: Список словарей с данными файлов
        webhook_url: URL webhook из n8n
        namespace: Namespace в Pinecone
    
    Returns:
        Ответ от API
    """
    payload = {
        "files": files_data,
        "namespace": namespace
    }
    
    print(f"\n📤 Отправка {len(files_data)} файлов в Pinecone...")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Namespace: {namespace}")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        response.raise_for_status()
        
        if not response.text.strip():
            raise Exception(
                f"n8n вернул HTTP {response.status_code} с пустым телом. "
                "Сценарий остановился до ответа. Откройте последнее выполнение в Executions."
            )
        result = response.json()
        print(f"\n✅ Успешно загружено!")
        print(f"   Обработано файлов: {result.get('totalFiles', 0)}")
        print(f"   Векторов загружено: {result.get('totalUpserted', 0)}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к API: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Ошибка при парсинге JSON ответа: {e}")


def main():
    """
    Основная функция для загрузки файлов из /data в Pinecone.
    """
    # Настройки
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    WEBHOOK_URL = os.getenv("N8N_UPLOAD_WEBHOOK_URL", "http://localhost:5678/webhook/pinecone-upload")
    NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")
    
    print("=" * 80)
    print("📁 Загрузка файлов из директории в Pinecone")
    print("=" * 80)
    print(f"Директория: {DATA_DIR}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Namespace: {NAMESPACE}")
    print("=" * 80)
    
    try:
        # Читаем файлы
        files_data = read_txt_files_from_directory(DATA_DIR)
        
        if not files_data:
            print("❌ Нет файлов для загрузки")
            return
        
        # По одному файлу: вебхук отвечает после первого элемента пачки
        # и остальные файлы в том же запросе не записываются.
        total_upserted = 0
        for index, file_data in enumerate(files_data, 1):
            print(f"\n[{index}/{len(files_data)}] {file_data['fileName']}")
            result = upload_to_pinecone([file_data], WEBHOOK_URL, NAMESPACE)
            upserted = result.get("totalUpserted", 0)
            total_upserted += upserted
            print(f"   векторов: {upserted}")

        print(f"\n✅ Записано векторов: {total_upserted}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

