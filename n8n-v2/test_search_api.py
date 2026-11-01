import requests
import json
from typing import Dict, List, Optional

class PineconeSearchAPIClient:
    def __init__(self, webhook_url: str):
        """
        Инициализация клиента для работы с Pinecone Search API через n8n webhook.
        
        Args:
            webhook_url: URL webhook из n8n (например: https://your-n8n-instance.com/webhook/pinecone-search)
        """
        self.webhook_url = webhook_url
    
    def search(self, query: str, namespace: str = "default") -> List[Dict]:
        """
        Выполняет поиск в Pinecone по текстовому запросу.
        
        Args:
            query: Текстовый запрос для поиска
            namespace: Namespace в Pinecone (по умолчанию "default")
        
        Returns:
            Список словарей с результатами поиска:
            [
                {
                    "text": "текст чанка",
                    "score": 0.95,
                    "source": "document1",
                    "chunk_index": 0,
                    "id": "chunk_1234567890_0"
                },
                ...
            ]
        """
        payload = {
            "query": query,
            "namespace": namespace
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            results = response.json()
            
            if isinstance(results, list):
                return results
            elif isinstance(results, dict) and "data" in results:
                return results["data"]
            else:
                return [results] if results else []
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к API: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка при парсинге JSON ответа: {e}")
    
    def print_results(self, results: List[Dict]):
        """
        Красиво выводит результаты поиска.
        
        Args:
            results: Список результатов поиска
        """
        if not results:
            print("Результаты не найдены.")
            return
        
        print(f"\nНайдено результатов: {len(results)}\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\nРезультат #{i}:")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Source: {result.get('source', 'unknown')}")
            print(f"  Chunk Index: {result.get('chunk_index', -1)}")
            print(f"  ID: {result.get('id', 'N/A')}")
            print(f"  Text: {result.get('text', '')[:200]}...")
            print("-" * 80)


def main():
    """
    Пример использования API клиента.
    """
    # Webhook URL для локального n8n
    # URL можно найти в узле Webhook после активации workflow
    import os
    WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/pinecone-search")
    webhook_url = WEBHOOK_URL
    
    print(f"📡 Используется webhook URL: {webhook_url}")
    print("   Для изменения установите переменную окружения: export N8N_WEBHOOK_URL='your-url'")
    
    client = PineconeSearchAPIClient(webhook_url)
    
    # Примеры запросов
    test_queries = [
        {
            "query": "тестовый запрос",
            "namespace": "default"
        },
        {
            "query": "информация о работе",
            "namespace": "default"
        }
    ]
    
    print("🚀 Тестирование Pinecone Search API через n8n Webhook\n")
    print(f"Webhook URL: {webhook_url}\n")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Тест #{i}: {test['query']}")
        print(f"{'='*80}")
        
        try:
            results = client.search(
                query=test["query"],
                namespace=test["namespace"]
            )
            client.print_results(results)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # Интерактивный режим
    print("\n\n" + "="*80)
    print("Интерактивный режим (для выхода введите 'exit'):")
    print("="*80)
    
    while True:
        try:
            query = input("\nВведите запрос для поиска: ").strip()
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            if not query:
                continue
            
            namespace = input("Введите namespace (Enter для 'default'): ").strip() or "default"
            
            results = client.search(query=query, namespace=namespace)
            client.print_results(results)
            
        except KeyboardInterrupt:
            print("\n\nВыход...")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()

