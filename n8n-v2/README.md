# Pinecone + n8n Workflows

Два workflow для работы с Pinecone векторной базой через n8n.

## Файлы

- `workflow1-pinecone-upload.json` - Загрузка текстов в Pinecone
- `workflow2-pinecone-search.json` - Поиск по Pinecone
- `upload_files_to_pinecone.py` - Python скрипт для загрузки файлов из `/data`
- `test_search_api.py` - Python клиент для тестирования поиска

## Настройка

### 1. Запустите n8n

```bash
docker-compose up -d
```

n8n будет доступен по адресу: http://localhost:5678

### 2. Импортируйте workflows

1. Откройте n8n: http://localhost:5678
2. Импортируйте `workflow1-pinecone-upload.json`
3. Импортируйте `workflow2-pinecone-search.json`

### 3. Настройте Credentials

#### OpenAI API Credentials
- Тип: **HTTP Header Auth**
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_OPENAI_API_KEY`
- Используется в узлах: "Get Embeddings" (оба workflow)

#### Pinecone API Credentials
- Тип: **HTTP Header Auth**
- Header Name: `Api-Key`
- Header Value: `YOUR_PINECONE_API_KEY`
- Используется в узлах: "Upsert to Pinecone" и "Query Pinecone"

### 4. Настройте Environment Variables

В настройках n8n или в `docker-compose.yml` добавьте:

```yaml
environment:
  - PINECONE_ENDPOINT=https://your-index.svc.region.pinecone.io
```

Или установите в настройках n8n: Settings → Environment Variables

### 5. Активируйте workflows

В каждом workflow нажмите кнопку **"Active"** в правом верхнем углу.

## Использование

### Workflow 1: Загрузка данных

**Вариант 1: Через Python скрипт (рекомендуется)**

1. Поместите `.txt` файлы в директорию `/data`
2. Запустите скрипт:

```bash
python upload_files_to_pinecone.py
```

Или с переменными окружения:

```bash
export DATA_DIR="/path/to/your/data"
export N8N_UPLOAD_WEBHOOK_URL="http://localhost:5678/webhook/pinecone-upload"
export PINECONE_NAMESPACE="my-namespace"
python upload_files_to_pinecone.py
```

**Вариант 2: Через API напрямую**

```bash
curl -X POST http://localhost:5678/webhook/pinecone-upload \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {
        "fileName": "document1.txt",
        "text": "Содержимое первого документа..."
      },
      {
        "fileName": "document2.txt",
        "text": "Содержимое второго документа..."
      }
    ],
    "namespace": "default"
  }'
```

**Формат запроса:**
```json
{
  "files": [
    {
      "fileName": "document1.txt",
      "text": "Текст документа..."
    }
  ],
  "namespace": "default"
}
```

**Ответ:**
```json
{
  "status": "success",
  "totalFiles": 2,
  "totalUpserted": 150,
  "fileResults": [
    {"fileIndex": 1, "upserted": 75},
    {"fileIndex": 2, "upserted": 75}
  ]
}
```

### Workflow 2: Поиск

**Через Python клиент:**

```bash
python test_search_api.py
```

**Через API:**

```bash
curl -X POST http://localhost:5678/webhook/pinecone-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ваш поисковый запрос",
    "namespace": "default"
  }'
```

**Формат запроса:**
```json
{
  "query": "текст запроса",
  "namespace": "default"
}
```

**Ответ:**
```json
[
  {
    "text": "найденный текст чанка",
    "score": 0.95,
    "source": "document1",
    "chunk_index": 0,
    "id": "chunk_document1_1234567890_0"
  }
]
```

## Настройки

### Параметры чанков

В узле "Chunk Text" можно настроить:
- `chunkSize` - размер чанка (по умолчанию 600 символов)
- `overlap` - перекрытие между чанками (по умолчанию 100 символов)

### Модель embeddings

В узлах "Get Embeddings":
- Модель: `text-embedding-3-large`
- Размерность: `1024` (соответствует вашему Pinecone индексу)

### Количество результатов поиска

В workflow 2, узел "Query Pinecone":
- `topK` - количество результатов (по умолчанию 5)

## Troubleshooting

### "Cannot find module 'fs'"
Используйте webhook вариант (текущая версия) вместо executeCommand.

### "Blocks are not connected"
1. Закройте workflow в n8n
2. Удалите старый workflow
3. Импортируйте заново
4. Обновите страницу (F5)

### Docker pull висит
```bash
docker-compose down
docker pull n8nio/n8n:latest
docker-compose up -d
```

## Структура workflows

### Workflow 1 (Upload)
```
Webhook → Parse Input → Chunk Text → Prepare Batch → 
Get Embeddings → Format for Pinecone → Upsert to Pinecone → 
Aggregate Results → Respond to Webhook
```

### Workflow 2 (Search)
```
Webhook → Process Query → Get Query Embedding → 
Query Pinecone → Format Results → Respond to Webhook
```

## Примеры использования

### Загрузка документации проекта

```python
import os
import requests

files_data = []
for filename in os.listdir('./docs'):
    if filename.endswith('.txt'):
        with open(f'./docs/{filename}', 'r') as f:
            files_data.append({
                'fileName': filename,
                'text': f.read()
            })

response = requests.post(
    'http://localhost:5678/webhook/pinecone-upload',
    json={'files': files_data, 'namespace': 'documentation'}
)
print(response.json())
```

### Поиск по документации

```python
import requests

response = requests.post(
    'http://localhost:5678/webhook/pinecone-search',
    json={'query': 'How to install?', 'namespace': 'documentation'}
)

for result in response.json():
    print(f"Score: {result['score']:.4f}")
    print(f"Source: {result['source']}")
    print(f"Text: {result['text'][:200]}...")
    print('-' * 80)
```

## Лицензия

MIT

