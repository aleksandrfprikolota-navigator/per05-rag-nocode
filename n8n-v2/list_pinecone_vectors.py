import os
from collections import Counter

import requests

HOST = os.getenv(
    "PINECONE_HOST",
    "https://rag-company-index-d7ivl8s.svc.aped-4627-b74a.pinecone.io",
)
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")


def headers():
    api_key = (os.getenv("PINECONE_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("Задайте PINECONE_API_KEY в этом окне PowerShell.")
    return {"Api-Key": api_key}


def list_ids():
    ids = []
    token = None
    while True:
        params = {"namespace": NAMESPACE, "limit": 100}
        if token:
            params["paginationToken"] = token
        response = requests.get(
            f"{HOST}/vectors/list",
            headers=headers(),
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        ids.extend(item["id"] for item in data.get("vectors", []))
        token = (data.get("pagination") or {}).get("next")
        if not token:
            return ids


def fetch_sources(ids):
    counts = Counter()
    for start in range(0, len(ids), 100):
        batch = ids[start : start + 100]
        response = requests.get(
            f"{HOST}/vectors/fetch",
            headers=headers(),
            params=[("namespace", NAMESPACE), *[("ids", item_id) for item_id in batch]],
            timeout=60,
        )
        response.raise_for_status()
        vectors = response.json().get("vectors", {})
        for item_id in batch:
            meta = vectors.get(item_id, {}).get("metadata") or {}
            counts[meta.get("source") or item_id] += 1
    return counts


def main():
    ids = list_ids()
    print(f"Записей в namespace {NAMESPACE}: {len(ids)}\n")
    print("По источникам:")
    for source, count in fetch_sources(ids).most_common():
        print(f"  {count:4}  {source}")
    print("\nИдентификаторы:")
    for item_id in ids:
        print(item_id)


if __name__ == "__main__":
    main()
